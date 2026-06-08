"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  User,
  Mail,
  ShieldCheck,
  Package,
  ChevronRight,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/components/auth-provider"
import { LogoutButton } from "@/components/auth/logout-button"

export default function ProfilePage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/auth/login")
    }
  }, [loading, user, router])

  if (loading || !user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <div className="flex items-center justify-center py-24">
          <div className="size-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </div>
    )
  }

  const initials = user.email.slice(0, 2).toUpperCase()
  const isAdmin = user.roles.includes("admin")

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <h1 className="mb-6 text-2xl font-semibold tracking-tight">Профиль</h1>

      <div className="mb-6 overflow-hidden rounded-2xl border bg-card">
        <div className="flex items-center gap-4 bg-primary/5 px-6 py-6">
          <div className="flex size-16 items-center justify-center rounded-full bg-primary text-xl font-semibold text-primary-foreground">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate font-semibold">{user.email}</p>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              {user.roles.map((role) => (
                <Badge
                  key={role}
                  variant={role === "admin" ? "default" : "secondary"}
                  className="text-xs"
                >
                  {role === "admin" ? "Администратор" : "Покупатель"}
                </Badge>
              ))}
              {user.is_active && (
                <span className="flex items-center gap-1 text-xs text-green-600">
                  <span className="size-1.5 rounded-full bg-green-500" />
                  Активен
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="divide-y">
          <div className="flex items-center gap-3 px-6 py-4">
            <Mail className="size-4 shrink-0 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Email</p>
              <p className="text-sm font-medium">{user.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-6 py-4">
            <ShieldCheck className="size-4 shrink-0 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">Роль</p>
              <p className="text-sm font-medium capitalize">
                {isAdmin ? "Администратор" : "Покупатель"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-6 py-4">
            <User className="size-4 shrink-0 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground">ID аккаунта</p>
              <p className="text-sm font-mono text-muted-foreground">{user.id}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mb-6 rounded-2xl border bg-card">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <Package className="size-5 text-primary" />
            <h2 className="font-semibold">Мои заказы</h2>
          </div>
          <Link href="/orders" className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-sm font-medium text-primary hover:bg-accent">
            Все заказы
            <ChevronRight className="size-4" />
          </Link>
        </div>
        <Separator />
        <div className="px-6 py-8 text-center text-sm text-muted-foreground">
          История заказов доступна на странице заказов
        </div>
      </div>

      {isAdmin && (
        <div className="mb-6">
          <Link
            href="/admin"
            className="flex items-center justify-between rounded-2xl border bg-primary/5 px-6 py-4 transition-colors hover:bg-primary/10"
          >
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-5 text-primary" />
              <span className="font-medium text-primary">Панель администратора</span>
            </div>
            <ChevronRight className="size-4 text-primary" />
          </Link>
        </div>
      )}

      <LogoutButton />
    </div>
  )
}
