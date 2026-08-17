"use client";

import { FormEvent, useState } from "react";

interface QuestionInputProps {
  onSubmit: (question: string) => Promise<void>;
  loading: boolean;
}

export default function QuestionInput({
  onSubmit,
  loading,
}: QuestionInputProps) {
  const [question, setQuestion] = useState("Why did revenue fall in July?");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    await onSubmit(trimmedQuestion);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <textarea
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="Ask a business question..."
        rows={4}
        className="w-full rounded-xl border border-zinc-300 bg-white p-4 text-sm outline-none transition focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200"
      />

      <button
        type="submit"
        disabled={loading}
        className="rounded-xl bg-zinc-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Investigating..." : "Investigate"}
      </button>
    </form>
  );
}
