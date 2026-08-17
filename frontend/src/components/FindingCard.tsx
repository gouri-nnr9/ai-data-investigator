import { Finding } from "@/lib/api";

interface FindingCardProps {
  finding: Finding;
}

export default function FindingCard({ finding }: FindingCardProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4">
      <div className="mb-2 flex items-center justify-between gap-4">
        <h3 className="font-semibold text-zinc-900">{finding.title}</h3>

        <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-xs text-zinc-600">
          {finding.severity}
        </span>
      </div>

      <p className="text-sm leading-6 text-zinc-600">{finding.description}</p>
    </div>
  );
}
