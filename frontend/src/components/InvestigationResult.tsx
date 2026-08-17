import { InvestigationResponse } from "@/lib/api";

import FindingCard from "./FindingCard";
import EvidenceCard from "./EvidenceCard";

interface InvestigationResultProps {
  result: InvestigationResponse;
}

export default function InvestigationResult({
  result,
}: InvestigationResultProps) {
  return (
    <div className="space-y-8">
      <section>
        <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
          Executive finding
        </p>

        <h2 className="mt-2 text-2xl font-semibold text-zinc-900">
          {result.summary}
        </h2>
      </section>

      {result.findings.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-zinc-900">Findings</h3>

          <div className="grid gap-3 md:grid-cols-2">
            {result.findings.map((finding, index) => (
              <FindingCard
                key={`${finding.title}-${index}`}
                finding={finding}
              />
            ))}
          </div>
        </section>
      )}

      {result.evidence.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-zinc-900">Evidence</h3>

          <div className="grid gap-3 md:grid-cols-3">
            {result.evidence.map((item, index) => (
              <EvidenceCard key={`${item.finding}-${index}`} evidence={item} />
            ))}
          </div>
        </section>
      )}

      {result.queries.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-zinc-900">
            Investigation queries
          </h3>

          <div className="space-y-3">
            {result.queries.map((query, index) => (
              <pre
                key={index}
                className="overflow-x-auto rounded-xl bg-zinc-950 p-4 text-xs leading-6 text-zinc-200"
              >
                {query}
              </pre>
            ))}
          </div>
        </section>
      )}

      {result.limitations.length > 0 && (
        <section>
          <h3 className="mb-3 text-lg font-semibold text-zinc-900">
            Limitations
          </h3>

          <div className="space-y-2">
            {result.limitations.map((limitation, index) => (
              <p
                key={index}
                className="rounded-lg bg-amber-50 p-3 text-sm text-amber-900"
              >
                {limitation}
              </p>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
