import json
import os
import tempfile
from email import policy
from email.parser import BytesParser

import anthropic
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ANTHROPIC_AUTH_TOKEN="" in this environment poisons the Bearer header; unset it so
# the SDK falls back to the X-Api-Key header using ANTHROPIC_API_KEY instead.
os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

app = FastAPI(title="OfferAssistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY; ANTHROPIC_AUTH_TOKEN already removed above


class ExtractionResult(BaseModel):
    classification: str
    sender: str
    subject: str
    extracted_fields: dict[str, str]
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


EXTRACTION_PROMPT = """\
You are an assistant that processes insurance inquiry emails.

Given the email below, return a JSON object with exactly these fields:
- "classification": a short label for the type of insurance being requested \
(e.g. "Professional Liability", "Property Insurance", "Berufshaftpflicht")
- "extracted_fields": an object of relevant structured fields extracted from the body \
(e.g. customer_name, profession, location, coverage_amount, deductible, insurance_year, etc.)

Respond with ONLY a valid JSON object, no markdown fences, no explanation.

Email Subject: {subject}
From: {sender}
Body:
{body}
"""


def extract_with_claude(sender: str, subject: str, body: str) -> ExtractionResult:
    prompt = EXTRACTION_PROMPT.format(subject=subject, sender=sender, body=body)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw_json = message.content[0].text.strip()
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {e}") from e

    return ExtractionResult(
        classification=data.get("classification", ""),
        sender=sender,
        subject=subject,
        extracted_fields={k: str(v) for k, v in data.get("extracted_fields", {}).items()},
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

    return extract_with_claude(sender, subject, body)
