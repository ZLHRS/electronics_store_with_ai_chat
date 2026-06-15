"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, CreditCard, Banknote, Smartphone, MapPin, Loader2, CheckCircle2, ShoppingBag, BadgeCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useCart } from "@/components/cart-provider"
import { useAuth } from "@/components/auth-provider"
import { createOrder } from "@/lib/api/orders"
import { formatPrice } from "@/lib/data"
import { cn } from "@/lib/utils"

type Phase = "form" | "processing" | "success"

const PAYMENT_OPTIONS = [
  { value: "card", label: "Банковская карта", icon: CreditCard },
  { value: "cash", label: "Наличными при получении", icon: Banknote },
  { value: "online", label: "Онлайн-оплата", icon: Smartphone },
]

export default function CheckoutPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const { items, subtotal, isLoading: cartLoading, clear, setOpen } = useCart()
  const [address, setAddress] = useState("")
  const [paymentMethod, setPaymentMethod] = useState("card")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>("form")
  const [successVisible, setSuccessVisible] = useState(false)
  const [completedTotal, setCompletedTotal] = useState(0)
  const [orderId, setOrderId] = useState<string | null>(null)

  const delivery = subtotal > 0 && subtotal < 300000 ? 2990 : 0
  const total = subtotal + delivery

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/auth/login")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (phase === "success") {
      const t = setTimeout(() => setSuccessVisible(true), 50)
      return () => clearTimeout(t)
    }
  }, [phase])

  if (authLoading || cartLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!user) return null

  if (phase === "processing") {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center gap-6 text-center">
        <div className="relative flex size-24 items-center justify-center rounded-full bg-primary/10">
          <Loader2 className="size-12 animate-spin text-primary" />
        </div>
        <div>
          <p className="text-xl font-semibold">Обрабатываем заказ...</p>
          <p className="mt-1.5 text-sm text-muted-foreground">Это займёт буквально секунду</p>
        </div>
      </div>
    )
  }

  if (phase === "success") {
    return (
      <div
        className={cn(
          "flex min-h-[70vh] flex-col items-center justify-center gap-8 px-4 text-center transition-all duration-500",
          successVisible ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0",
        )}
      >
        <div className="relative">
          <span className="absolute inset-0 animate-ping rounded-full bg-success/20 [animation-duration:1.2s] [animation-iteration-count:2]" />
          <div className="relative flex size-28 items-center justify-center rounded-full bg-success/10">
            <div className="flex size-20 items-center justify-center rounded-full bg-success/20">
              <CheckCircle2 className="size-12 text-success" strokeWidth={1.5} />
            </div>
          </div>
        </div>

        <div className="flex flex-col items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight">Спасибо за покупку!</h1>
          <div className="flex items-center gap-2 rounded-full border border-success/30 bg-success/10 px-4 py-1.5 text-sm font-medium text-success">
            <BadgeCheck className="size-4" />
            Оплачено · {formatPrice(completedTotal)}
          </div>
          <p className="max-w-xs text-sm text-muted-foreground">
            Заказ успешно оформлен. Мы уже готовим его к отправке.
          </p>
        </div>

        <div className="flex w-full max-w-xs flex-col gap-3">
          <Button
            size="lg"
            className="rounded-xl"
            onClick={() => router.push(orderId ? `/orders/${orderId}` : "/orders")}
          >
            <ShoppingBag className="mr-2 size-4" />
            Мои заказы
          </Button>
          <Button variant="ghost" className="rounded-xl" onClick={() => router.push("/")}>
            Продолжить покупки
          </Button>
        </div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Корзина пуста</p>
        <Button render={<Link href="/" />}>Перейти к покупкам</Button>
      </div>
    )
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!address.trim()) {
      setError("Укажите адрес доставки")
      return
    }
    setError(null)
    setSubmitting(true)
    const order = await createOrder(address.trim(), paymentMethod)
    setSubmitting(false)
    if (!order) {
      setError("Не удалось оформить заказ. Попробуйте ещё раз.")
      return
    }
    setCompletedTotal(total)
    setOrderId(order.id)
    clear()
    setOpen(false)
    setPhase("processing")
    setTimeout(() => setPhase("success"), 1500)
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center gap-3">
        <Button variant="ghost" size="icon" className="rounded-full" render={<Link href="/" />} aria-label="Назад">
          <ArrowLeft />
        </Button>
        <h1 className="text-xl font-semibold">Оформление заказа</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <form onSubmit={handleSubmit} className="flex flex-col gap-5 lg:col-span-3">
          <section className="rounded-2xl border p-5">
            <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold">
              <MapPin className="size-4 text-primary" />
              Адрес доставки
            </h2>
            <textarea
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Город, улица, дом, квартира"
              rows={3}
              className="w-full resize-none rounded-xl border bg-muted/40 px-4 py-3 text-sm outline-none transition placeholder:text-muted-foreground focus:border-ring focus:bg-background"
            />
          </section>

          <section className="rounded-2xl border p-5">
            <h2 className="mb-4 text-sm font-semibold">Способ оплаты</h2>
            <div className="flex flex-col gap-2">
              {PAYMENT_OPTIONS.map(({ value, label, icon: Icon }) => (
                <label
                  key={value}
                  className={cn(
                    "flex cursor-pointer items-center gap-3 rounded-xl border p-3.5 transition-colors",
                    paymentMethod === value
                      ? "border-primary bg-primary/5"
                      : "hover:border-muted-foreground/30",
                  )}
                >
                  <input
                    type="radio"
                    name="payment"
                    value={value}
                    checked={paymentMethod === value}
                    onChange={() => setPaymentMethod(value)}
                    className="accent-primary"
                  />
                  <Icon className="size-4 text-muted-foreground" />
                  <span className="text-sm">{label}</span>
                </label>
              ))}
            </div>
          </section>

          {error && (
            <p className="rounded-xl bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>
          )}

          <Button
            type="submit"
            size="lg"
            disabled={submitting}
            className="rounded-xl"
          >
            {submitting ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" />
                Оформляем...
              </>
            ) : (
              <>
                <CheckCircle2 className="mr-2 size-4" />
                Подтвердить заказ · {formatPrice(total)}
              </>
            )}
          </Button>
        </form>

        <aside className="flex flex-col gap-4 lg:col-span-2">
          <div className="rounded-2xl border p-5">
            <h2 className="mb-4 text-sm font-semibold">
              Товары · {items.length}
            </h2>
            <div className="flex flex-col gap-3">
              {items.map((item) => (
                <div key={item.product.id} className="flex gap-3">
                  <div className="relative size-14 shrink-0 overflow-hidden rounded-xl bg-muted">
                    <Image
                      src={item.product.image || "/placeholder.svg"}
                      alt={item.product.name}
                      fill
                      sizes="56px"
                      className="object-contain p-1.5"
                    />
                  </div>
                  <div className="flex flex-1 flex-col justify-center">
                    <p className="line-clamp-2 text-xs leading-snug">{item.product.name}</p>
                    <div className="mt-1 flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">× {item.qty}</span>
                      <span className="text-xs font-semibold">{formatPrice(item.product.price * item.qty)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <Separator className="my-4" />

            <div className="flex flex-col gap-2 text-sm">
              <div className="flex justify-between text-muted-foreground">
                <span>Товары</span>
                <span className="text-foreground">{formatPrice(subtotal)}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Доставка</span>
                <span className="text-foreground">{delivery === 0 ? "Бесплатно" : formatPrice(delivery)}</span>
              </div>
              <Separator className="my-1" />
              <div className="flex justify-between font-semibold">
                <span>Итого</span>
                <span>{formatPrice(total)}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>
  )
}
