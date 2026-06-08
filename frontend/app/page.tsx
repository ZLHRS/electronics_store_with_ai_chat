import { Suspense } from "react"
import { HomeHero } from "@/components/home/hero"
import { CategoryStrip } from "@/components/home/category-strip"
import { PromoBanners } from "@/components/home/promo-banners"
import { PopularProductsRow } from "@/components/home/popular-row"
import { Catalog } from "@/components/home/catalog"
import { Skeleton } from "@/components/ui/skeleton"

export default function HomePage() {
  return (
    <div className="pb-10">
      <HomeHero />
      <CategoryStrip />
      <PromoBanners />
      <PopularProductsRow />
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
