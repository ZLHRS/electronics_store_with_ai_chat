export type ChatSession = {
  id: string
  title: string | null
  created_at: string
  updated_at: string
}

export type ChatMessage = {
  id: string
  session_id: string
  role: "user" | "assistant"
  content: string
  created_at: string
  product_ids: string[] | null
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(path, { ...init, credentials: "include" })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

export async function createChatSession(): Promise<ChatSession | null> {
  return apiFetch<ChatSession>("/api/v1/chat/sessions", { method: "POST" })
}

export async function sendChatMessage(
  sessionId: string,
  content: string,
): Promise<ChatMessage | null> {
  return apiFetch<ChatMessage>(`/api/v1/chat/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  })
}

export async function getChatMessages(sessionId: string): Promise<ChatMessage[]> {
  const data = await apiFetch<ChatMessage[]>(
    `/api/v1/chat/sessions/${sessionId}/messages`,
  )
  return data ?? []
}
