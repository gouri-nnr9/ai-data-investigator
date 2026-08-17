export interface Finding {
  title: string;
  description: string;
  severity: string;
}

export interface Evidence {
  finding: string;
  value: string;
  source: string;
}

export interface InvestigationResponse {
  question: string;
  status: string;
  summary: string;
  findings: Finding[];
  evidence: Evidence[];
  queries: string[];
  limitations: string[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function investigate(
  question: string,
): Promise<InvestigationResponse> {
  const response = await fetch(`${API_BASE_URL}/investigate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(errorText || "Investigation request failed.");
  }

  return response.json();
}
