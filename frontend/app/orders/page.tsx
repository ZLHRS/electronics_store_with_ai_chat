"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { Package, ChevronRight, Clock, CheckCircle2, Truck, XCircle, Loader2 } from "lucide-react"
import { useAuth } from "@/components/auth-provider"
import { orders, formatPrice } from "@/lib/data"
import { cn } from "@/lib/utils"
import type { OrderStatus } from "@/lib/types"

const statusConfig: Record<OrderStatus, { label: string; icon: React.ElementType; badgeClass: string }> = {
  processing: {
    label: "Обрабатывается",
    icon: Clock,
    badgeClass: "bg-orange-50 text-orange-600 dark:bg-orange-950/30 dark:text-orange-400",
  },
  shipped: {
    label: "В пути",
    icon: Truck,
    badgeClass: "bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400",
  },
  delivered: {
    label: "Доставлен",
    icon: CheckCircle2,
    badgeClass: "bg-green-50 text-green-700 dark:bg-green-950/30 dark:text-green-400",
  },
  cancelled: {
    label: "Отменён",
    icon: XCircle,
    badgeClass: "bg-destructive/10 text-destructive",
  },
}

type FilterTab = "all" | OrderStatus

const tabs: { id: FilterTab; label: string }[] = [
  { id: "all", label: "Все" },
  { id: "shipped", label: "В пути" },
  { id: "delivered", label: "Доставлены" },
  { id: "processing", label: "Обрабатываются" },
  { id: "cancelled", label: "Отменены" },
]

function pluralItems(n: number) {
  if (n === 1) return "товар"
  if (n >= 2 && n <= 4) return "товара"
  return "товаров"
}

export default function OrdersPage() {
  const { user, loading } = useAuth()
  const [activeTab, setActiveTab] = useState<FilterTab>("all")

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex items-center justify-center py-24">
          <Loader2 className="size-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 py-24 text-center">
          <Package className="size-12 text-muted-foreground/40" />
          <h1 className="text-2xl font-semibold">Мои заказы</h1>
          <p className="text-muted-foreground">Войдите в аккаунт, чтобы просматривать заказы</p>
          <Link
            href="/auth/login"
            className="mt-2 inline-flex h-9 items-center rounded-full bg-primary px-5 text-sm font-medium text-primary-foreground hover:bg-primary/80"
          >
            Войти
          </Link>
        </div>
      </div>
    )
  }

  const filtered = activeTab === "all" ? orders : orders.filter((o) => o.status === activeTab)

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Мои заказы</h1>
        <span className="rounded-full bg-muted px-2.5 py-0.5 text-sm text-muted-foreground">{orders.length}</span>
      </div>

      <div className="mb-6 flex gap-1.5 overflow-x-auto pb-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "shrink-0 rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors",
              activeTab === tab.id
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="flex flex-col items-center gap-3 py-24 text-center">
          <Package className="size-10 text-muted-foreground/40" />
          <p className="text-muted-foreground">Заказов нет</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {filtered.map((order) => {
            const cfg = statusConfig[order.status]
            const StatusIcon = cfg.icon
            const preview = order.items.slice(0, 3)
            const extra = order.items.length - 3

            return (
              <Link
                key={order.id}
                href={`/orders/${order.id}`}
                className="group flex items-center gap-4 rounded-2xl border bg-card p-4 transition-shadow hover:shadow-md"
              >
                <div className="flex -space-x-3">
                  {preview.map(({ product }, i) => (
                    <div
                      key={`${product.id}-${i}`}
                      className="relative size-14 shrink-0 overflow-hidden rounded-xl border-2 border-background bg-muted/60"
                      style={{ zIndex: preview.length - i }}
                    >
                      <Image
                        src={product.image || "/placeholder.svg"}
                        alt={product.name}
                        fill
                        sizes="56px"
                        className="object-contain p-1.5"
                      />
                    </div>
                  ))}
                  {extra > 0 && (
                    <div className="relative flex size-14 shrink-0 items-center justify-center rounded-xl border-2 border-background bg-muted text-xs font-medium text-muted-foreground">
                      +{extra}
                    </div>
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold">#{order.id}</p>
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
                        cfg.badgeClass,
                      )}
                    >
                      <StatusIcon className="size-3" />
                      {cfg.label}
                    </span>
                  </div>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {order.date} · {order.items.length} {pluralItems(order.items.length)}
                  </p>
                </div>

                <div className="flex shrink-0 items-center gap-1.5">
                  <p className="text-sm font-semibold">{formatPrice(order.total)}</p>
                  <ChevronRight className="size-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
