import { redirect } from "next/navigation"
import { LoginForm } from "@/components/auth/login-form"
import { getCurrentUser } from "@/lib/auth"

export const metadata = { title: "Вход — Kvant" }

export default async function LoginPage() {
  const user = await getCurrentUser()
  if (user) redirect("/profile")
  return <LoginForm />
}
