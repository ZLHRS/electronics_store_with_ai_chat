"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Laptop, Smartphone, Headphones, Gamepad2, Tablet, House, Camera, Watch, Package } from "lucide-react"
import { fetchCategories, type DisplayCategory } from "@/lib/api/categories"

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  Laptop,
  Smartphone,
  Headphones,
  Gamepad2,
  Tablet,
  House,
  Camera,
  Watch,
  Package,
}

export function CategoryStrip() {
  const [categories, setCategories] = useState<DisplayCategory[]>([])

  useEffect(() => {
    fetchCategories().then(setCategories)
  }, [])

  if (categories.length === 0) return null

  return (
    <section className="mx-auto max-w-7xl px-4 pt-10 sm:px-6 lg:px-8">
      <h2 className="mb-4 text-lg font-semibold tracking-tight">Категории</h2>
      <div className="grid grid-cols-4 gap-3 md:grid-cols-8">
        {categories.map((c) => {
          const Icon = iconMap[c.icon] ?? Package
          return (
            <Link
              key={c.uuid}
              href={`/?category=${c.slug}`}
              className="flex flex-col items-center gap-2.5 rounded-2xl border bg-card p-4 text-center transition-colors hover:border-primary hover:bg-accent"
            >
              <span className="flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <Icon className="size-6" />
              </span>
              <span className="text-xs font-medium leading-tight">{c.name}</span>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
