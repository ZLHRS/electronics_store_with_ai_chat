"use client"

import { useEffect, useState } from "react"
import { ProductRow } from "@/components/home/product-row"
import { fetchProducts } from "@/lib/api/products"
import { Skeleton } from "@/components/ui/skeleton"
import type { Product } from "@/lib/types"

export function PopularProductsRow() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProducts(6)
      .then(setProducts)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <section className="mx-auto max-w-7xl px-4 pt-12 sm:px-6 lg:px-8">
        <Skeleton className="mb-4 h-7 w-48" />
        <div className="flex gap-4 overflow-hidden">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-72 w-[180px] shrink-0 rounded-2xl sm:w-[220px]" />
          ))}
        </div>
      </section>
    )
  }

  if (products.length === 0) return null

  return (
    <ProductRow
      title="Популярные товары"
      description="Чаще всего покупают на этой неделе"
      products={products}
    />
  )
}
