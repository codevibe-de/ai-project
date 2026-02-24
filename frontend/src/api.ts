export interface InsuranceInquiryData {
  customer_name: string | null;
  profession: string | null;
  location: string | null;
  insurance_type: string | null;
  coverage_amount: string | null;
  deductible: string | null;
  insurance_year: number | null;
  broker_name: string | null;
  broker_email: string | null;
  broker_phone: string | null;
}

export interface ExtractionResult {
  sender: string;
  subject: string;
  risk_type_code: string | null;
  risk_type_name: string | null;
  data: InsuranceInquiryData;
  raw_body: string;
}

export async function uploadFile(file: File): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Upload failed (${response.status}): ${text}`);
  }

  return response.json();
}
