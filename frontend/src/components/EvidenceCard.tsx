import { Evidence } from "@/lib/api";

interface EvidenceCardProps {
  evidence: Evidence;
}

export default function EvidenceCard({ evidence }: EvidenceCardProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4">
      <p className="text-sm font-medium text-zinc-900">{evidence.finding}</p>

      <p className="mt-2 text-lg font-semibold text-zinc-900">
        {evidence.value}
      </p>

      <p className="mt-1 text-xs text-zinc-500">Source: {evidence.source}</p>
    </div>
  );
}
