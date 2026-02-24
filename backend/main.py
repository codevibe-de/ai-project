import json
import os
import tempfile
from contextlib import asynccontextmanager
from email import policy
from email.parser import BytesParser
from typing import Any

import anthropic
import asyncpg
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ANTHROPIC_AUTH_TOKEN="" in this environment poisons the Bearer header; unset it so
# the SDK falls back to the X-Api-Key header using ANTHROPIC_API_KEY instead.
os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydb"
)

db_pool: asyncpg.Pool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}. Risk type classification will be unavailable.")
        db_pool = None
    yield
    if db_pool:
        await db_pool.close()


app = FastAPI(title="OfferAssistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

client = anthropic.AsyncAnthropic()  # reads ANTHROPIC_API_KEY; ANTHROPIC_AUTH_TOKEN already removed above


class InsuranceInquiryData(BaseModel):
    customer_name: str | None = None
    profession: str | None = None
    location: str | None = None
    insurance_type: str | None = None
    coverage_amount: str | None = None
    deductible: str | None = None
    insurance_year: int | None = None
    broker_name: str | None = None
    broker_email: str | None = None
    broker_phone: str | None = None


class ExtractionResult(BaseModel):
    sender: str
    subject: str
    risk_type_code: str | None
    risk_type_name: str | None
    data: InsuranceInquiryData
    raw_body: str


def parse_eml(data: bytes) -> tuple[str, str, str]:
    msg = BytesParser(policy=policy.default).parsebytes(data)
    sender = str(msg.get("From", ""))
    subject = str(msg.get("Subject", ""))
    body_part = msg.get_body(preferencelist=("plain",))
    raw_body = body_part.get_content() if body_part else ""
    return sender, subject, raw_body


def parse_msg(data: bytes) -> tuple[str, str, str]:
    try:
        import extract_msg
    except ImportError as err:
        raise HTTPException(status_code=500, detail="extract-msg not installed") from err

    with tempfile.NamedTemporaryFile(suffix=".msg", delete=False) as f:
        f.write(data)
        tmp_path = f.name
    try:
        msg = extract_msg.Message(tmp_path)
        sender = msg.sender or ""
        subject = msg.subject or ""
        raw_body = msg.body or ""
        return sender, subject, raw_body
    finally:
        os.unlink(tmp_path)


async def fetch_risk_types() -> list[dict[str, str]]:
    """Fetch active risk types joined through active product from DB."""
    if db_pool is None:
        return []
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT rt.code, rt.name
                FROM risk_type rt
                JOIN product p ON rt.product_id = p.id
                WHERE rt.is_active = TRUE AND p.is_active = TRUE
                ORDER BY rt.code
                """
            )
        return [{"code": row["code"], "name": row["name"]} for row in rows]
    except Exception as e:
        print(f"Warning: Failed to fetch risk types: {e}")
        return []


EXTRACTION_PROMPT = """\
You are an assistant that processes insurance inquiry emails.

Given the email below, return a JSON object with exactly these fields:
- "data": an object with these fields (use null if not found):
  - "customer_name": full name of the customer
  - "profession": the customer's profession or trade
  - "location": city or region
  - "insurance_type": type of insurance requested
  - "coverage_amount": desired coverage/sum insured
  - "deductible": deductible amount if mentioned
  - "insurance_year": year the insurance should start (integer)
  - "broker_name": name of the broker if mentioned
  - "broker_email": broker's email address
  - "broker_phone": broker's phone number
- "risk_type_code": pick the single best matching code from the list below, or null if none fit:
{risk_types_json}

Respond with ONLY a valid JSON object, no markdown fences, no explanation.

Email Subject: {subject}
From: {sender}
Body:
{body}
"""


async def extract_with_claude(
    sender: str, subject: str, body: str, risk_types: list[dict[str, str]]
) -> ExtractionResult:
    risk_types_json = json.dumps(risk_types, ensure_ascii=False)
    prompt = EXTRACTION_PROMPT.format(
        risk_types_json=risk_types_json,
        subject=subject,
        sender=sender,
        body=body,
    )
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_json = message.content[0].text.strip()
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {e}") from e

    risk_type_code: str | None = payload.get("risk_type_code") or None
    risk_type_name: str | None = None
    if risk_type_code:
        for rt in risk_types:
            if rt["code"] == risk_type_code:
                risk_type_name = rt["name"]
                break

    data_payload: dict[str, Any] = payload.get("data") or {}
    inquiry_data = InsuranceInquiryData(
        customer_name=data_payload.get("customer_name"),
        profession=data_payload.get("profession"),
        location=data_payload.get("location"),
        insurance_type=data_payload.get("insurance_type"),
        coverage_amount=data_payload.get("coverage_amount"),
        deductible=data_payload.get("deductible"),
        insurance_year=data_payload.get("insurance_year"),
        broker_name=data_payload.get("broker_name"),
        broker_email=data_payload.get("broker_email"),
        broker_phone=data_payload.get("broker_phone"),
    )

    return ExtractionResult(
        sender=sender,
        subject=subject,
        risk_type_code=risk_type_code,
        risk_type_name=risk_type_name,
        data=inquiry_data,
        raw_body=body,
    )


@app.post("/upload", response_model=ExtractionResult)
async def upload(file: UploadFile = File()):
    filename = file.filename or ""
    if not (filename.lower().endswith(".eml") or filename.lower().endswith(".msg")):
        raise HTTPException(status_code=400, detail="Only .eml and .msg files are supported")

    data = await file.read()

    if filename.lower().endswith(".eml"):
        sender, subject, body = parse_eml(data)
    else:
        sender, subject, body = parse_msg(data)

    if not body.strip():
        raise HTTPException(status_code=422, detail="Could not extract text body from file")

    risk_types = await fetch_risk_types()
    return await extract_with_claude(sender, subject, body, risk_types)
