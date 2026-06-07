export type User = {
  id: string
  email: string
  is_active: boolean
  roles: string[]
}

const SERVER_API = process.env.API_URL ?? "http://localhost:8000"

export async function apiLogin(email: string, password: string) {
  const res = await fetch("/api/v1/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(
      Array.isArray(data.detail)
        ? data.detail.map((e: { msg: string }) => e.msg).join(", ")
        : (data.detail ?? "Ошибка входа")
    )
  }
  return res.json() as Promise<{ access_token: string }>
}

export async function apiRegister(email: string, password: string) {
  const res = await fetch("/api/v1/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(
      Array.isArray(data.detail)
        ? data.detail.map((e: { msg: string }) => e.msg).join(", ")
        : (data.detail ?? "Ошибка регистрации")
    )
  }
  return res.json() as Promise<{ id: string; email: string }>
}

export async function apiLogout() {
  await fetch("/api/v1/logout", {
    method: "POST",
    credentials: "include",
  })
}

export async function apiGetMe(): Promise<User | null> {
  try {
    const res = await fetch("/api/v1/me", {
      credentials: "include",
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function serverGetMe(cookieHeader: string): Promise<User | null> {
  try {
    const res = await fetch(`${SERVER_API}/api/v1/me`, {
      headers: { Cookie: cookieHeader },
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

export async function serverLogout(cookieHeader: string) {
  try {
    await fetch(`${SERVER_API}/api/v1/logout`, {
      method: "POST",
      headers: { Cookie: cookieHeader },
    })
  } catch {
  }
}
