import { normalizeApiError } from "@/core/lib/errors";

/** The one place an API error becomes user-facing text — every feature
 * passes its mutation/query `error` here instead of rendering `error.message`
 * directly, so validation `fields` and unexpected errors read consistently. */
export function ErrorBanner({ error }: { error: unknown }) {
  if (!error) return null;
  const normalized = normalizeApiError(error);

  return (
    <div role="alert" className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
      <p>{normalized.message}</p>
      {normalized.fields && (
        <ul className="mt-1 list-disc pl-5">
          {Object.entries(normalized.fields).map(([field, messages]) => (
            <li key={field}>
              {field !== "_" && <strong>{field}: </strong>}
              {messages.join(", ")}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
