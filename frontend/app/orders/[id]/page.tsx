"use client"

import { use, useEffect, useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, Clock, CheckCircle2, Truck, XCircle, Package, Check, Loader2, CreditCard } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/components/auth-provider"
import {
  fetchOrderById,
  cancelOrder,
  buildTimeline,
  formatOrderDate,
  type FrontendOrder,
  type ApiOrderStatus,
} from "@/lib/api/orders"
import { fetchProductById } from "@/lib/api/products"
import { formatPrice } from "@/lib/data"
import { cn } from "@/lib/utils"

const statusConfig: Record<ApiOrderStatus, { label: string; icon: React.ElementType; badgeClass: string }> = {
  created: {
    label: "Создан",
    icon: Clock,
    badgeClass: "bg-muted text-muted-foreground",
  },
  pending_payment: {
    label: "Ожидает оплаты",
    icon: CreditCard,
    badgeClass: "bg-yellow-50 text-yellow-700 dark:bg-yellow-950/30 dark:text-yellow-400",
  },
  paid: {
    label: "Оплачен",
    icon: CheckCircle2,
    badgeClass: "bg-blue-50 text-blue-600 dark:bg-blue-950/30 dark:text-blue-400",
  },
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

export default function OrderPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const { user, loading: authLoading } = useAuth()
  const [order, setOrder] = useState<FrontendOrder | null>(null)
  const [loading, setLoading] = useState(true)
  const [cancelling, setCancelling] = useState(false)
  const [itemImages, setItemImages] = useState<Record<string, string>>({})

  useEffect(() => {
    if (!user) return
    fetchOrderById(id)
      .then((o) => {
        setOrder(o)
        if (o) {
          Promise.all(o.items.map((item) => fetchProductById(item.product_id))).then((products) => {
            const map: Record<string, string> = {}
            products.forEach((p, i) => {
              if (p?.image) map[o.items[i].product_id] = p.image
            })
            setItemImages(map)
          })
        }
      })
      .finally(() => setLoading(false))
  }, [id, user])

  async function handleCancel() {
    if (!order) return
    setCancelling(true)
    const updated = await cancelOrder(order.id)
    if (updated) setOrder(updated)
    setCancelling(false)
  }

  if (authLoading || loading) {
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
  const timeline = buildTimeline(order.status)
  const itemsTotal = order.items.reduce((sum, i) => sum + i.total_price, 0)
  const totalQty = order.items.reduce((sum, i) => sum + i.quantity, 0)
  const canCancel = order.status === "created" || order.status === "pending_payment"

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
          <h1 className="text-2xl font-semibold tracking-tight">Заказ #{order.id.slice(0, 8)}</h1>
          <p className="mt-0.5 text-sm text-muted-foreground">{formatOrderDate(order.created_at)}</p>
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
          {timeline.map((step, i) => {
            const isLast = i === timeline.length - 1
            const isCancelStep = order.status === "cancelled" && isLast

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
                    )}
                  >
                    {step.label}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      <div className="mb-4 rounded-2xl border bg-card p-4 text-sm">
        <p className="mb-1 text-xs text-muted-foreground">Адрес доставки</p>
        <p className="font-medium">{order.delivery_address}</p>
        <p className="mt-2 text-xs text-muted-foreground">Способ оплаты</p>
        <p className="font-medium capitalize">{order.payment_method}</p>
      </div>

      <div className="rounded-2xl border bg-card">
        <div className="px-5 py-4">
          <h2 className="font-semibold">Состав заказа</h2>
        </div>
        <Separator />
        <div className="divide-y">
          {order.items.map((item) => (
            <div key={item.id} className="flex items-center gap-4 px-5 py-4">
              <div className="relative flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-muted/60">
                {itemImages[item.product_id] ? (
                  <Image
                    src={itemImages[item.product_id]}
                    alt={item.product_name}
                    fill
                    sizes="64px"
                    className="object-contain p-1.5"
                  />
                ) : (
                  <Package className="size-6 text-muted-foreground/50" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <Link
                  href={`/product/${item.product_id}`}
                  className="line-clamp-2 text-sm font-medium hover:text-primary"
                >
                  {item.product_name}
                </Link>
                <p className="mt-0.5 text-xs text-muted-foreground">{item.quantity} шт.</p>
              </div>
              <p className="shrink-0 text-sm font-semibold">{formatPrice(item.total_price)}</p>
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
            <span>{formatPrice(order.total_amount)}</span>
          </div>
        </div>
      </div>

      {canCancel && (
        <button
          onClick={handleCancel}
          disabled={cancelling}
          className="mt-4 w-full rounded-xl border border-destructive/50 py-2.5 text-sm font-medium text-destructive transition-colors hover:bg-destructive/5 disabled:opacity-50"
        >
          {cancelling ? "Отменяем..." : "Отменить заказ"}
        </button>
      )}
    </div>
  )
}
