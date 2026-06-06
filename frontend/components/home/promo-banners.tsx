import { Sparkles, Truck, Percent } from "lucide-react"

const promos = [
  {
    title: "AI подберёт за 30 секунд",
    text: "Опишите задачу — получите готовую подборку",
    icon: Sparkles,
    className: "bg-primary text-primary-foreground",
    sub: "Новая функция",
  },
  {
    title: "Скидки до 40%",
    text: "На технику недели — успейте купить выгодно",
    icon: Percent,
    className: "bg-warning text-warning-foreground",
    sub: "Распродажа",
  },
  {
    title: "Бесплатная доставка",
    text: "При заказе от 300 000 ₸ по всему Казахстану",
    icon: Truck,
    className: "bg-success text-success-foreground",
    sub: "Каждый день",
  },
]

export function PromoBanners() {
  return (
    <section className="mx-auto max-w-7xl px-4 pt-10 sm:px-6 lg:px-8">
      <div className="grid gap-4 md:grid-cols-3">
        {promos.map((p) => (
          <div key={p.title} className={`relative overflow-hidden rounded-2xl p-6 ${p.className}`}>
            <div className="pointer-events-none absolute -right-8 -top-8 size-32 rounded-full bg-white/10 blur-2xl" />
            <span className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-black/10 px-2.5 py-1 text-xs font-medium">
              {p.sub}
            </span>
            <p.icon className="mb-3 size-7" />
            <h3 className="text-lg font-semibold tracking-tight">{p.title}</h3>
            <p className="mt-1 text-sm opacity-90">{p.text}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
