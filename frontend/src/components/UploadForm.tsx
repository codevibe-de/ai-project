import { useRef, useState } from "react";
import { uploadFile, ExtractionResult } from "../api";

interface Props {
  onResult: (result: ExtractionResult) => void;
  onError: (msg: string) => void;
}

export default function UploadForm({ onResult, onError }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFile = async (file: File) => {
    setFileName(file.name);
    setLoading(true);
    try {
      const result = await uploadFile(file);
      onResult(result);
    } catch (e) {
      onError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center cursor-pointer hover:border-blue-400 transition-colors"
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".msg,.eml"
        className="hidden"
        onChange={handleChange}
      />
      {loading ? (
        <p className="text-blue-500 font-medium animate-pulse">Processing…</p>
      ) : (
        <>
          <p className="text-gray-500 text-sm">
            Drag & drop a <span className="font-semibold">.msg</span> or{" "}
            <span className="font-semibold">.eml</span> file here, or click to
            select
          </p>
          {fileName && (
            <p className="mt-2 text-xs text-gray-400">Selected: {fileName}</p>
          )}
        </>
      )}
    </div>
  );
}
