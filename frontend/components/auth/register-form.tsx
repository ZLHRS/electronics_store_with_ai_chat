"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Eye, EyeOff, Loader2, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { apiRegister, apiLogin } from "@/lib/api/auth"

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: "Минимум 8 символов", ok: password.length >= 8 },
    { label: "Буквы и цифры", ok: /[a-zA-Z]/.test(password) && /\d/.test(password) },
  ]
  if (!password) return null
  return (
    <div className="flex flex-col gap-1 pt-1">
      {checks.map((c) => (
        <span key={c.label} className={`flex items-center gap-1.5 text-xs ${c.ok ? "text-green-600" : "text-muted-foreground"}`}>
          <Check className={`size-3 ${c.ok ? "opacity-100" : "opacity-30"}`} />
          {c.label}
        </span>
      ))}
    </div>
  )
}

export function RegisterForm() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await apiRegister(email, password)
      await apiLogin(email, password)
      router.push("/profile")
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка регистрации")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-sm">
      <div className="rounded-2xl border bg-background p-8 shadow-sm">
        <h1 className="mb-1 text-xl font-semibold tracking-tight">Создать аккаунт</h1>
        <p className="mb-6 text-sm text-muted-foreground">Быстро и бесплатно</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="h-11"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <Label htmlFor="password">Пароль</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Минимум 8 символов"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                className="h-11 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label={showPassword ? "Скрыть пароль" : "Показать пароль"}
              >
                {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              </button>
            </div>
            <PasswordStrength password={password} />
          </div>

          {error && (
            <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {error}
            </p>
          )}

          <Button type="submit" className="h-11 w-full rounded-xl" disabled={loading || password.length < 8}>
            {loading && <Loader2 className="mr-2 size-4 animate-spin" />}
            Зарегистрироваться
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted-foreground">
          Уже есть аккаунт?{" "}
          <Link href="/auth/login" className="font-medium text-primary hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}
