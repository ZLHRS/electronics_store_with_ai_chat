"use server"

import { cookies } from "next/headers"
import { redirect } from "next/navigation"
import { serverLogout } from "@/lib/api/auth"

export async function logoutAction() {
  const cookieStore = await cookies()
  const cookieHeader = cookieStore
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ")

  await serverLogout(cookieHeader)

  cookieStore.delete("access_token")
  cookieStore.delete("refresh_token")

  redirect("/")
}
