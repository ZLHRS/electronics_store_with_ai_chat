"use client"

import Link from "next/link"
import { Sparkles, Truck, ShieldCheck, CreditCard, Headset } from "lucide-react"

const features = [
  { icon: Truck, title: "Быстрая доставка", text: "По всему Казахстану за 1–3 дня" },
  { icon: ShieldCheck, title: "Гарантия качества", text: "Официальная гарантия на всё" },
  { icon: CreditCard, title: "Удобная оплата", text: "Рассрочка 0% и любые карты" },
  { icon: Headset, title: "Поддержка 24/7", text: "AI-ассистент и живые операторы" },
]

export function SiteFooter() {
  return (
    <footer className="mt-20 border-t bg-card">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-6 border-b py-10 md:grid-cols-4">
          {features.map((f) => (
            <div key={f.title} className="flex items-start gap-3">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <f.icon className="size-5" />
              </span>
              <div>
                <p className="text-sm font-medium">{f.title}</p>
                <p className="text-sm text-muted-foreground">{f.text}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-col items-center justify-between gap-4 py-8 text-sm text-muted-foreground sm:flex-row">
          <Link href="/" className="flex items-center gap-2 text-foreground">
            <span className="flex size-8 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <Sparkles className="size-4.5" />
            </span>
            <span className="text-base font-semibold tracking-tight">Shop</span>
          </Link>

          <p className="text-center text-sm text-muted-foreground sm:text-left">
            © 2026 Shop. Все права защищены.
          </p>

          <div className="flex gap-5">
            <span className="cursor-pointer hover:text-foreground">Конфиденциальность</span>
            <span className="cursor-pointer hover:text-foreground">Условия</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
