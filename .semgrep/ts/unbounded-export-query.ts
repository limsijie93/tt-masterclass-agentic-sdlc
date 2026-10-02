// Fixture for unbounded-export-query, TypeScript side. Not application code.
// Run: semgrep test .semgrep/
//
// The TypeScript twin of ../unbounded-export-query.py. Same defect, different grammar.
// A single multi-language rule was tried and measurably breaks the Python negation —
// see this rule's metadata and ../README.md.

function buildExportQuery(tenant: string, opts?: { chunkSize?: number; format?: string }) {
  return { tenant, ...opts };
}

export function theBug(tenant: string) {
  // ruleid: unbounded-export-query-ts
  return buildExportQuery(tenant);
}

export function theFix(tenant: string) {
  // ok: unbounded-export-query-ts
  return buildExportQuery(tenant, { chunkSize: 5000 });
}

// --- Qualified calls. The form the Python twin silently failed to match. Do not delete.

const service = { buildExportQuery };

export function theBugQualified(tenant: string) {
  // ruleid: unbounded-export-query-ts
  return service.buildExportQuery(tenant);
}

export function theFixQualified(tenant: string) {
  // ok: unbounded-export-query-ts
  return service.buildExportQuery(tenant, { chunkSize: 5000 });
}
