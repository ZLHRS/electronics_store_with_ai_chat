import { Suspense } from "react"
import { HomeHero } from "@/components/home/hero"
import { CategoryStrip } from "@/components/home/category-strip"
import { PromoBanners } from "@/components/home/promo-banners"
import { ProductRow } from "@/components/home/product-row"
import { Catalog } from "@/components/home/catalog"
import { Skeleton } from "@/components/ui/skeleton"
import { products } from "@/lib/data"

const popular = [...products].sort((a, b) => b.reviews - a.reviews).slice(0, 6)
const deals = products.filter((p) => p.oldPrice).slice(0, 6)

export default function HomePage() {
  return (
    <div className="pb-10">
      <HomeHero />
      <CategoryStrip />
      <PromoBanners />
      <ProductRow title="Популярные товары" description="Чаще всего покупают на этой неделе" products={popular} />
      <ProductRow title="Выгодные предложения" description="Товары со скидкой" products={deals} />
      <Suspense fallback={<CatalogSkeleton />}>
        <Catalog />
      </Suspense>
    </div>
  )
}

function CatalogSkeleton() {
  return (
    <div className="mx-auto max-w-7xl px-4 pt-12 sm:px-6 lg:px-8">
      <Skeleton className="mb-5 h-8 w-40" />
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="aspect-[3/4] rounded-2xl" />
        ))}
      </div>
    </div>
  )
}
