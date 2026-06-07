import { cookies } from "next/headers"
import { serverGetMe, type User } from "@/lib/api/auth"

export async function getCurrentUser(): Promise<User | null> {
  const cookieStore = await cookies()
  const cookieHeader = cookieStore
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ")
  if (!cookieHeader) return null
  return serverGetMe(cookieHeader)
}
