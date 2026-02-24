export interface ExtractionResult {
  classification: string;
  sender: string;
  subject: string;
  extracted_fields: Record<string, string>;
  raw_body: string;
}

export async function uploadFile(file: File): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Upload failed (${response.status}): ${text}`);
  }

  return response.json();
}
