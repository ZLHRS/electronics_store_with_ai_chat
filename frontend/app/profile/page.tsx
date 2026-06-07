import { redirect } from "next/navigation"
import Link from "next/link"
import {
  User,
  Mail,
  ShieldCheck,
  Package,
  ChevronRight,
  Clock,
  CheckCircle2,
  Truck,
  XCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { getCurrentUser } from "@/lib/auth"
import { LogoutButton } from "@/components/auth/logout-button"
import { orders, formatPrice } from "@/lib/data"

export const metadata = { title: "Профиль — Shop" }

const statusConfig = {
  processing: { label: "Обрабатывается", icon: Clock, color: "text-orange-500" },
  shipped: { label: "В пути", icon: Truck, color: "text-blue-500" },
  delivered: { label: "Доставлен", icon: CheckCircle2, color: "text-green-600" },
  cancelled: { label: "Отменён", icon: XCircle, color: "text-destructive" },
}

export default async function ProfilePage() {
  const user = await getCurrentUser()

  if (!user) {
    redirect("/auth/login")
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
          <div className="flex-1 min-w-0">
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
            <span className="text-sm text-muted-foreground">· {orders.length}</span>
          </div>
          <Link href="/orders" className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-sm font-medium text-primary hover:bg-accent">
            Все заказы
            <ChevronRight className="size-4" />
          </Link>
        </div>
        <Separator />
        <div className="divide-y">
          {orders.slice(0, 3).map((order) => {
            const cfg = statusConfig[order.status]
            const StatusIcon = cfg.icon
            return (
              <div key={order.id} className="flex items-center gap-4 px-6 py-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium">#{order.id}</p>
                    <span className={`flex items-center gap-1 text-xs ${cfg.color}`}>
                      <StatusIcon className="size-3" />
                      {cfg.label}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {order.date} · {order.items.length} {order.items.length === 1 ? "товар" : "товара"}
                  </p>
                </div>
                <p className="shrink-0 text-sm font-semibold">{formatPrice(order.total)}</p>
              </div>
            )
          })}
        </div>
      </div>

      <LogoutButton />
    </div>
  )
}
