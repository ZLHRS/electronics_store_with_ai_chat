"use client"

import { Heart } from "lucide-react"
import Link from "next/link"
import { useFavorites } from "@/components/favorites-provider"
import { useAuth } from "@/components/auth-provider"
import { ProductCard } from "@/components/product-card"
import { products } from "@/lib/data"

export default function FavoritesPage() {
  const { user, loading } = useAuth()
  const { ids } = useFavorites()

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 py-24 text-center">
          <div className="size-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 py-24 text-center">
          <Heart className="size-12 text-muted-foreground/40" />
          <h1 className="text-2xl font-semibold">Избранное</h1>
          <p className="text-muted-foreground">Войдите в аккаунт, чтобы сохранять понравившиеся товары</p>
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

  const favoriteProducts = products.filter((p) => ids.has(p.id))

  if (favoriteProducts.length === 0) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <h1 className="mb-8 text-2xl font-semibold tracking-tight">Избранное</h1>
        <div className="flex flex-col items-center gap-4 py-20 text-center">
          <Heart className="size-12 text-muted-foreground/40" />
          <p className="text-lg font-medium">Здесь пока пусто</p>
          <p className="text-sm text-muted-foreground">
            Нажмите <Heart className="inline size-4 text-muted-foreground" /> на карточке товара, чтобы добавить в
            избранное
          </p>
          <Link
            href="/"
            className="mt-2 inline-flex h-9 items-center rounded-full bg-primary px-5 text-sm font-medium text-primary-foreground hover:bg-primary/80"
          >
            Перейти в каталог
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">Избранное</h1>
        <span className="rounded-full bg-muted px-2.5 py-0.5 text-sm text-muted-foreground">
          {favoriteProducts.length}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {favoriteProducts.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  )
}
