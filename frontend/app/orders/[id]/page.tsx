"use client"

import { use } from "react"
import Link from "next/link"
import Image from "next/image"
import { ArrowLeft, Clock, CheckCircle2, Truck, XCircle, Package, Check, Loader2 } from "lucide-react"
import { Separator } from "@/components/ui/separator"
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

function pluralItems(n: number) {
  if (n === 1) return "шт."
  return "шт."
}

export default function OrderPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { user, loading } = useAuth()

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

  const order = orders.find((o) => o.id === id)

  if (!order) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <Link
          href="/orders"
          className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Мои заказы
        </Link>
        <div className="flex flex-col items-center gap-4 py-24 text-center">
          <Package className="size-12 text-muted-foreground/40" />
          <h1 className="text-xl font-semibold">Заказ не найден</h1>
          <Link
            href="/orders"
            className="mt-2 inline-flex h-9 items-center rounded-full bg-primary px-5 text-sm font-medium text-primary-foreground hover:bg-primary/80"
          >
            К заказам
          </Link>
        </div>
      </div>
    )
  }

  const cfg = statusConfig[order.status]
  const StatusIcon = cfg.icon
  const itemsTotal = order.items.reduce((sum, { product, qty }) => sum + product.price * qty, 0)
  const totalQty = order.items.reduce((sum, { qty }) => sum + qty, 0)

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/orders"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Мои заказы
      </Link>

      <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Заказ #{order.id}</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">{order.date}</p>
        </div>
        <span
          className={cn(
            "inline-flex items-center gap-1.5 self-start rounded-full px-3 py-1.5 text-sm font-medium sm:mt-1",
            cfg.badgeClass,
          )}
        >
          <StatusIcon className="size-4" />
          {cfg.label}
        </span>
      </div>

      <div className="mb-4 rounded-2xl border bg-card p-5">
        <h2 className="mb-5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Статус доставки
        </h2>
        <div className="flex flex-col">
          {order.timeline.map((step, i) => {
            const isLast = i === order.timeline.length - 1
            const isCancelStep = order.status === "cancelled" && isLast
            const isActiveStep = step.done && !isLast && !order.timeline[i + 1]?.done

            return (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "flex size-6 shrink-0 items-center justify-center rounded-full border-2 transition-colors",
                      isCancelStep
                        ? "border-destructive bg-destructive text-destructive-foreground"
                        : step.done
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-muted-foreground/25 bg-background",
                    )}
                  >
                    {step.done &&
                      (isCancelStep ? (
                        <XCircle className="size-3.5" />
                      ) : (
                        <Check className="size-3" strokeWidth={3} />
                      ))}
                  </div>
                  {!isLast && (
                    <div
                      className={cn(
                        "mt-0.5 min-h-6 w-0.5 flex-1",
                        step.done && !isCancelStep ? "bg-primary" : "bg-border",
                      )}
                    />
                  )}
                </div>
                <div className={cn("flex-1 pb-5", isLast && "pb-0")}>
                  <p
                    className={cn(
                      "text-sm font-medium leading-6",
                      isCancelStep && "text-destructive",
                      !step.done && "text-muted-foreground",
                      isActiveStep && "text-primary",
                    )}
                  >
                    {step.label}
                  </p>
                  <p className="text-xs text-muted-foreground">{step.date}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="rounded-2xl border bg-card">
        <div className="px-5 py-4">
          <h2 className="font-semibold">Состав заказа</h2>
        </div>
        <Separator />
        <div className="divide-y">
          {order.items.map(({ product, qty }) => (
            <div key={product.id} className="flex items-center gap-4 px-5 py-4">
              <div className="relative size-16 shrink-0 overflow-hidden rounded-xl bg-muted/60">
                <Image
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  fill
                  sizes="64px"
                  className="object-contain p-2"
                />
              </div>
              <div className="min-w-0 flex-1">
                <Link
                  href={`/product/${product.id}`}
                  className="line-clamp-2 text-sm font-medium hover:text-primary"
                >
                  {product.name}
                </Link>
                <p className="mt-0.5 text-xs text-muted-foreground">{qty} {pluralItems(qty)}</p>
              </div>
              <p className="shrink-0 text-sm font-semibold">{formatPrice(product.price * qty)}</p>
            </div>
          ))}
        </div>
        <Separator />
        <div className="flex flex-col gap-2.5 px-5 py-4">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Товары ({totalQty} шт.)</span>
            <span>{formatPrice(itemsTotal)}</span>
          </div>
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Доставка</span>
            <span className="text-green-600 dark:text-green-400">Бесплатно</span>
          </div>
          <Separator />
          <div className="flex justify-between text-base font-semibold">
            <span>Итого</span>
            <span>{formatPrice(order.total)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
