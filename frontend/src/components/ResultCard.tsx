import type { ExtractionResult } from "../api";

interface Props {
  result: ExtractionResult;
}

export default function ResultCard({ result }: Props) {
  const dataEntries = Object.entries(result.data).filter(
    ([, value]) => value !== null && value !== undefined
  ) as [string, string | number][];

  return (
    <div className="mt-8 bg-white rounded-xl shadow p-6 space-y-4">
      <div className="flex items-center gap-3">
        <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-1 rounded-full">
          {result.risk_type_name ?? "Unknown"}
          {result.risk_type_code && (
            <span className="ml-1 text-blue-500 font-normal">
              ({result.risk_type_code})
            </span>
          )}
        </span>
        <span className="text-gray-500 text-sm">{result.sender}</span>
      </div>

      <h2 className="text-lg font-semibold text-gray-800">{result.subject}</h2>

      {dataEntries.length > 0 && (
        <table className="w-full text-sm border-collapse">
          <tbody>
            {dataEntries.map(([key, value]) => (
              <tr key={key} className="border-t border-gray-100">
                <td className="py-1.5 pr-4 font-medium text-gray-600 w-40 capitalize">
                  {key.replace(/_/g, " ")}
                </td>
                <td className="py-1.5 text-gray-800">{String(value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <details className="text-sm">
        <summary className="cursor-pointer text-gray-400 hover:text-gray-600">
          Raw body
        </summary>
        <pre className="mt-2 whitespace-pre-wrap text-xs text-gray-500 bg-gray-50 rounded p-3">
          {result.raw_body}
        </pre>
      </details>
    </div>
  );
}
