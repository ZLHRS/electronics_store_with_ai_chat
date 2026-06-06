"use client"

import Link from "next/link"
import Image from "next/image"
import { Star, ShoppingCart, Heart } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { formatPrice } from "@/lib/data"
import type { Product } from "@/lib/types"
import { useCart } from "@/components/cart-provider"
import { toast } from "sonner"

const badgeMap: Record<string, { label: string; className: string }> = {
  hit: { label: "Хит", className: "bg-primary text-primary-foreground" },
  new: { label: "Новинка", className: "bg-success text-success-foreground" },
  sale: { label: "Скидка", className: "bg-warning text-warning-foreground" },
}

export function ProductCard({ product, className }: { product: Product; className?: string }) {
  const { add } = useCart()
  const discount = product.oldPrice
    ? Math.round((1 - product.price / product.oldPrice) * 100)
    : 0

  return (
    <Card
      className={cn(
        "group relative flex flex-col gap-0 overflow-hidden rounded-2xl py-0 transition-shadow hover:shadow-lg",
        className,
      )}
    >
      <Link href={`/product/${product.id}`} className="relative block aspect-square overflow-hidden bg-muted/50">
        <Image
          src={product.image || "/placeholder.svg"}
          alt={product.name}
          fill
          sizes="(max-width: 768px) 50vw, 25vw"
          className="object-contain p-6 transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute left-3 top-3 flex flex-col gap-1.5">
          {product.badge && (
            <Badge className={cn("rounded-full border-0 px-2.5 text-xs", badgeMap[product.badge].className)}>
              {badgeMap[product.badge].label}
            </Badge>
          )}
          {discount > 0 && (
            <Badge variant="secondary" className="rounded-full px-2.5 text-xs text-destructive">
              −{discount}%
            </Badge>
          )}
        </div>
        <Button
          variant="secondary"
          size="icon"
          aria-label="В избранное"
          className="absolute right-3 top-3 size-9 rounded-full bg-background/80 opacity-0 backdrop-blur transition-opacity group-hover:opacity-100"
          onClick={(e) => {
            e.preventDefault()
            toast.success("Добавлено в избранное", { description: product.name })
          }}
        >
          <Heart />
        </Button>
      </Link>

      <div className="flex flex-1 flex-col gap-2.5 p-4">
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Star className="size-3.5 fill-warning text-warning" />
          <span className="font-medium text-foreground">{product.rating}</span>
          <span>· {product.reviews} отзывов</span>
        </div>
        <Link
          href={`/product/${product.id}`}
          className="line-clamp-2 text-sm font-medium leading-snug hover:text-primary"
        >
          {product.name}
        </Link>

        <div className="mt-auto flex items-end justify-between gap-2 pt-2">
          <div className="flex flex-col">
            {product.oldPrice && (
              <span className="text-xs text-muted-foreground line-through">{formatPrice(product.oldPrice)}</span>
            )}
            <span className="text-base font-semibold tracking-tight">{formatPrice(product.price)}</span>
          </div>
          <Button
            size="icon"
            aria-label="В корзину"
            disabled={!product.inStock}
            className="size-10 shrink-0 rounded-xl"
            onClick={() => {
              add(product)
              toast.success("Добавлено в корзину", { description: product.name })
            }}
          >
            <ShoppingCart />
          </Button>
        </div>
        {!product.inStock && <span className="text-xs text-destructive">Нет в наличии</span>}
      </div>
    </Card>
  )
}
