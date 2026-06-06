import { ProductCard } from "@/components/product-card"
import type { Product } from "@/lib/types"

export function ProductRow({
  title,
  description,
  products,
}: {
  title: string
  description?: string
  products: Product[]
}) {
  return (
    <section className="mx-auto max-w-7xl px-4 pt-12 sm:px-6 lg:px-8">
      <div className="mb-4">
        <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      <div className="no-scrollbar -mx-4 flex gap-4 overflow-x-auto px-4 pb-2 sm:mx-0 sm:px-0">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} className="w-[180px] shrink-0 sm:w-[220px]" />
        ))}
      </div>
    </section>
  )
}
