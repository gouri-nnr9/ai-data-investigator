"use client";

import { useState } from "react";

import InvestigationResult from "@/components/InvestigationResult";
import QuestionInput from "@/components/QuestionInput";

import { investigate, InvestigationResponse } from "@/lib/api";

export default function Home() {
  const [result, setResult] = useState<InvestigationResponse | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  async function handleInvestigation(question: string) {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await investigate(question);

      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-zinc-50">
      <div className="mx-auto max-w-5xl px-6 py-12">
        <header className="mb-10">
          <p className="text-sm font-medium text-zinc-500">
            AI DATA INVESTIGATOR
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-tight text-zinc-950">
            Find out what changed.
          </h1>

          <p className="mt-3 max-w-2xl text-zinc-600">
            Ask a business question and let the investigator analyze the
            available data.
          </p>
        </header>

        <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          <QuestionInput onSubmit={handleInvestigation} loading={loading} />
        </section>

        {loading && (
          <div className="mt-8 rounded-2xl border border-zinc-200 bg-white p-6">
            <p className="text-sm text-zinc-500">
              Investigating your question...
            </p>
          </div>
        )}

        {error && (
          <div className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-6">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-8">
            <InvestigationResult result={result} />
          </div>
        )}
      </div>
    </main>
  );
}
