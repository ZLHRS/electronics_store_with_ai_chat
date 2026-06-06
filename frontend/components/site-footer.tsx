import Link from "next/link"
import { Sparkles, Truck, ShieldCheck, CreditCard, Headset } from "lucide-react"
import { categories } from "@/lib/data"

const features = [
  { icon: Truck, title: "Быстрая доставка", text: "По всему Казахстану за 1–3 дня" },
  { icon: ShieldCheck, title: "Гарантия качества", text: "Официальная гарантия на всё" },
  { icon: CreditCard, title: "Удобная оплата", text: "Рассрочка 0% и любые карты" },
  { icon: Headset, title: "Поддержка 24/7", text: "AI-ассистент и живые операторы" },
]

const columns = [
  { title: "Покупателям", links: ["Как сделать заказ", "Доставка и оплата", "Возврат товара", "Гарантия", "Часто задаваемые вопросы"] },
  { title: "Компания", links: ["О нас", "Вакансии", "Партнёрам", "Пресс-центр", "Контакты"] },
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

        <div className="grid grid-cols-2 gap-8 py-12 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2">
              <span className="flex size-8 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                <Sparkles className="size-4.5" />
              </span>
              <span className="text-lg font-semibold tracking-tight">Shop</span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Умный маркетплейс электроники с AI-ассистентом, который поможет выбрать идеальный товар.
            </p>
          </div>

          <div>
            <p className="mb-4 text-sm font-medium">Категории</p>
            <ul className="flex flex-col gap-2.5">
              {categories.slice(0, 5).map((c) => (
                <li key={c.id}>
                  <Link href={`/?category=${c.id}`} className="text-sm text-muted-foreground hover:text-foreground">
                    {c.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <p className="mb-4 text-sm font-medium">{col.title}</p>
              <ul className="flex flex-col gap-2.5">
                {col.links.map((l) => (
                  <li key={l}>
                    <span className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">{l}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex flex-col items-center justify-between gap-4 border-t py-6 text-sm text-muted-foreground sm:flex-row">
          <p>© 2026 Shop. Все права защищены.</p>
          <div className="flex gap-6">
            <span className="cursor-pointer hover:text-foreground">Политика конфиденциальности</span>
            <span className="cursor-pointer hover:text-foreground">Условия использования</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
