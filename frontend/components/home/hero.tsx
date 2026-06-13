"use client"

import { useRef } from "react"
import { Sparkles, ArrowRight, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

const chips = ["Ноутбук для работы", "Игровой ПК", "Подарок маме", "Что популярно?"]

function dispatchOpenAI(query: string) {
  window.dispatchEvent(new CustomEvent("openAI", { detail: { query } }))
}

export function HomeHero() {
  const inputRef = useRef<HTMLInputElement>(null)

  function handleAskAI() {
    const query = inputRef.current?.value.trim() ?? ""
    dispatchOpenAI(query)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleAskAI()
  }

  return (
    <section className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8">
      <div className="relative overflow-hidden rounded-3xl bg-primary px-6 py-12 text-primary-foreground sm:px-12 sm:py-16 lg:py-20">
        <div className="pointer-events-none absolute -right-20 -top-20 size-80 rounded-full bg-primary-foreground/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 left-1/3 size-72 rounded-full bg-primary-foreground/10 blur-3xl" />

        <div className="relative max-w-2xl">
          <Badge className="mb-5 gap-1.5 rounded-full border-0 bg-primary-foreground/15 px-3 py-1 text-primary-foreground backdrop-blur">
            <Sparkles className="size-3.5" />
            Маркетплейс с AI-ассистентом
          </Badge>
          <h1 className="text-balance text-3xl font-semibold leading-tight tracking-tight sm:text-4xl lg:text-5xl">
            Найдём идеальный товар по вашему запросу
          </h1>
          <p className="mt-4 max-w-lg text-pretty text-base leading-relaxed text-primary-foreground/80">
            Опишите задачу обычными словами — AI подберёт технику под бюджет и потребности. Быстро, просто и без лишних характеристик.
          </p>

          <div className="mt-7 flex max-w-lg items-center gap-2 rounded-full bg-background p-1.5 shadow-lg">
            <Search className="ml-3 size-5 shrink-0 text-muted-foreground" />
            <Input
              ref={inputRef}
              placeholder="Например: ноутбук до 400 000 ₸"
              className="h-10 border-0 bg-transparent text-foreground shadow-none focus-visible:ring-0"
              onKeyDown={handleKeyDown}
            />
            <Button className="h-10 shrink-0 rounded-full px-5" onClick={handleAskAI}>
              Спросить AI
              <ArrowRight data-icon="inline-end" />
            </Button>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {chips.map((c) => (
              <button
                key={c}
                onClick={() => dispatchOpenAI(c)}
                className="rounded-full bg-primary-foreground/10 px-3 py-1.5 text-sm text-primary-foreground/90 backdrop-blur transition-colors hover:bg-primary-foreground/20"
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
