import { useState } from "react";
import type { ExtractionResult } from "./api";
import UploadForm from "./components/UploadForm";
import ResultCard from "./components/ResultCard";

export default function App() {
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleResult = (r: ExtractionResult) => {
    setError(null);
    setResult(r);
  };

  const handleError = (msg: string) => {
    setResult(null);
    setError(msg);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-16 px-4">
      <div className="w-full max-w-2xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          OfferAssistant
        </h1>
        <p className="text-gray-500 mb-8 text-sm">
          Upload an insurance inquiry email (.msg / .eml) to extract structured
          data.
        </p>

        <UploadForm onResult={handleResult} onError={handleError} />

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {result && <ResultCard result={result} />}
      </div>
    </div>
  );
}
