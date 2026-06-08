"use client"

import { use, useEffect, useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { ChevronRight, Heart, ShoppingCart, Star, Package, CheckCircle, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"
import { formatPrice } from "@/lib/data"
import { fetchProductById } from "@/lib/api/products"
import { useCart } from "@/components/cart-provider"
import { useFavorites } from "@/components/favorites-provider"
import type { Product } from "@/lib/types"

const badgeMap: Record<string, { label: string; className: string }> = {
  hit: { label: "Хит", className: "bg-primary text-primary-foreground" },
  new: { label: "Новинка", className: "bg-success text-success-foreground" },
  sale: { label: "Скидка", className: "bg-warning text-warning-foreground" },
}

export default function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeImage, setActiveImage] = useState(0)
  const [added, setAdded] = useState(false)

  const { add } = useCart()
  const { toggle, has } = useFavorites()

  useEffect(() => {
    fetchProductById(id)
      .then(setProduct)
      .finally(() => setLoading(false))
  }, [id])

  const isFav = product ? has(product.id) : false

  function handleAddToCart() {
    if (!product) return
    add(product)
    setAdded(true)
    setTimeout(() => setAdded(false), 1500)
  }

  if (loading) return <ProductSkeleton />

  if (!product) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 text-center">
          <Package className="size-16 text-muted-foreground/30" />
          <h1 className="text-2xl font-semibold">Товар не найден</h1>
          <p className="text-muted-foreground">Возможно, он был удалён или ссылка устарела</p>
          <Link
            href="/"
            className="mt-2 inline-flex h-9 items-center rounded-full bg-primary px-5 text-sm font-medium text-primary-foreground hover:bg-primary/80"
          >
            В каталог
          </Link>
        </div>
      </div>
    )
  }

  const images = product.images.length > 0 ? product.images : ["/placeholder.svg"]
  const discount = product.oldPrice
    ? Math.round((1 - product.price / product.oldPrice) * 100)
    : 0

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <nav className="mb-6 flex items-center gap-1.5 text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground">Главная</Link>
        <ChevronRight className="size-3.5" />
        <span className="line-clamp-1 text-foreground">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
        <div className="flex flex-col-reverse gap-4 sm:flex-row">
          {images.length > 1 && (
            <div className="flex flex-row gap-2 overflow-x-auto sm:flex-col sm:overflow-y-auto">
              {images.map((src, i) => (
                <button
                  key={i}
                  onClick={() => setActiveImage(i)}
                  className={cn(
                    "relative size-16 shrink-0 overflow-hidden rounded-xl border-2 bg-muted/50 transition-colors",
                    i === activeImage ? "border-primary" : "border-transparent hover:border-border",
                  )}
                >
                  <Image src={src} alt={product.name} fill className="object-contain p-1.5" sizes="64px" />
                </button>
              ))}
            </div>
          )}
          <div className="relative flex-1 overflow-hidden rounded-2xl bg-muted/40">
            <div className="relative aspect-square">
              <Image
                src={images[activeImage] ?? "/placeholder.svg"}
                alt={product.name}
                fill
                sizes="(max-width: 1024px) 100vw, 50vw"
                className="object-contain p-8"
                priority
              />
            </div>
            {product.badge && (
              <div className="absolute left-4 top-4">
                <Badge className={cn("rounded-full border-0 px-3 py-1 text-xs", badgeMap[product.badge].className)}>
                  {badgeMap[product.badge].label}
                </Badge>
              </div>
            )}
            {discount > 0 && (
              <div className="absolute left-4 top-10">
                <Badge variant="secondary" className="rounded-full px-3 py-1 text-xs text-destructive">
                  −{discount}%
                </Badge>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-5">
          {product.brand && (
            <p className="text-sm font-medium text-primary">{product.brand}</p>
          )}

          <h1 className="text-2xl font-bold leading-tight tracking-tight sm:text-3xl">{product.name}</h1>

          {product.rating != null && (
            <div className="flex items-center gap-2 text-sm">
              <div className="flex items-center gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={cn(
                      "size-4",
                      i < Math.round(product.rating!) ? "fill-warning text-warning" : "fill-muted text-muted",
                    )}
                  />
                ))}
              </div>
              <span className="font-semibold">{product.rating}</span>
              {product.reviews != null && (
                <span className="text-muted-foreground">· {product.reviews} отзывов</span>
              )}
            </div>
          )}

          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-bold tracking-tight">{formatPrice(product.price)}</span>
            {product.oldPrice && (
              <span className="text-base text-muted-foreground line-through">{formatPrice(product.oldPrice)}</span>
            )}
          </div>

          <div className="flex items-center gap-2 text-sm">
            {product.inStock ? (
              <>
                <CheckCircle className="size-4 text-success" />
                <span className="text-success font-medium">В наличии</span>
              </>
            ) : (
              <>
                <XCircle className="size-4 text-destructive" />
                <span className="text-destructive font-medium">Нет в наличии</span>
              </>
            )}
          </div>

          <div className="flex gap-3">
            <Button
              size="lg"
              disabled={!product.inStock}
              className={cn("flex-1 rounded-xl gap-2 transition-all", added && "bg-success hover:bg-success")}
              onClick={handleAddToCart}
            >
              {added ? (
                <>
                  <CheckCircle className="size-5" />
                  Добавлено
                </>
              ) : (
                <>
                  <ShoppingCart className="size-5" />
                  В корзину
                </>
              )}
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="rounded-xl px-4"
              aria-label={isFav ? "Убрать из избранного" : "В избранное"}
              onClick={() => toggle(product.id, product.name)}
            >
              <Heart className={cn("size-5", isFav && "fill-destructive text-destructive")} />
            </Button>
          </div>

          {product.specs.length > 0 && (
            <div className="rounded-2xl border bg-card">
              <p className="border-b px-4 py-3 text-sm font-semibold">Характеристики</p>
              <div className="divide-y">
                {product.specs.map((s, i) => (
                  <div key={i} className="flex items-start gap-4 px-4 py-3 text-sm">
                    <span className="min-w-[140px] shrink-0 text-muted-foreground">{s.label}</span>
                    <span className="font-medium">{s.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {product.description && (
        <div className="mt-12">
          <h2 className="mb-4 text-xl font-semibold tracking-tight">Описание</h2>
          <p className="max-w-3xl leading-relaxed text-muted-foreground">{product.description}</p>
        </div>
      )}
    </div>
  )
}

function ProductSkeleton() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <Skeleton className="mb-6 h-5 w-56" />
      <div className="grid grid-cols-1 gap-10 lg:grid-cols-2">
        <Skeleton className="aspect-square rounded-2xl" />
        <div className="flex flex-col gap-4">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-9 w-3/4" />
          <Skeleton className="h-10 w-40" />
          <Skeleton className="h-5 w-28" />
          <div className="flex gap-3">
            <Skeleton className="h-11 flex-1 rounded-xl" />
            <Skeleton className="h-11 w-14 rounded-xl" />
          </div>
          <Skeleton className="h-48 rounded-2xl" />
        </div>
      </div>
    </div>
  )
}
