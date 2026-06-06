"use client"

import { useState, useMemo } from "react"
import { useSearchParams } from "next/navigation"
import { SlidersHorizontal, LayoutGrid, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Slider } from "@/components/ui/slider"
import { Separator } from "@/components/ui/separator"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger, SheetFooter } from "@/components/ui/sheet"
import { Field, FieldLabel } from "@/components/ui/field"
import { ProductCard } from "@/components/product-card"
import { products, categories, formatPrice } from "@/lib/data"
import { cn } from "@/lib/utils"

const brands = Array.from(new Set(products.map((p) => p.brand)))
const MAX_PRICE = 1300000

type SortKey = "popular" | "price-asc" | "price-desc" | "rating"

function FilterControls({
  selectedCats,
  toggleCat,
  selectedBrands,
  toggleBrand,
  price,
  setPrice,
  inStockOnly,
  setInStockOnly,
  onReset,
}: {
  selectedCats: string[]
  toggleCat: (id: string) => void
  selectedBrands: string[]
  toggleBrand: (b: string) => void
  price: number
  setPrice: (n: number) => void
  inStockOnly: boolean
  setInStockOnly: (b: boolean) => void
  onReset: () => void
}) {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="mb-3 text-sm font-medium">Категории</p>
        <div className="flex flex-col gap-2.5">
          {categories.map((c) => (
            <Field key={c.id} orientation="horizontal" className="gap-2.5">
              <Checkbox
                id={`cat-${c.id}`}
                checked={selectedCats.includes(c.id)}
                onCheckedChange={() => toggleCat(c.id)}
              />
              <FieldLabel htmlFor={`cat-${c.id}`} className="font-normal text-muted-foreground">
                {c.name}
              </FieldLabel>
            </Field>
          ))}
        </div>
      </div>
      <Separator />
      <div>
        <p className="mb-3 text-sm font-medium">Цена до</p>
        <Slider value={[price]} max={MAX_PRICE} min={50000} step={10000} onValueChange={(v) => setPrice(v[0])} />
        <p className="mt-3 text-sm text-muted-foreground">{formatPrice(price)}</p>
      </div>
      <Separator />
      <div>
        <p className="mb-3 text-sm font-medium">Бренд</p>
        <div className="flex flex-col gap-2.5">
          {brands.map((b) => (
            <Field key={b} orientation="horizontal" className="gap-2.5">
              <Checkbox id={`brand-${b}`} checked={selectedBrands.includes(b)} onCheckedChange={() => toggleBrand(b)} />
              <FieldLabel htmlFor={`brand-${b}`} className="font-normal text-muted-foreground">
                {b}
              </FieldLabel>
            </Field>
          ))}
        </div>
      </div>
      <Separator />
      <Field orientation="horizontal" className="gap-2.5">
        <Checkbox id="instock" checked={inStockOnly} onCheckedChange={(v) => setInStockOnly(Boolean(v))} />
        <FieldLabel htmlFor="instock" className="font-normal text-muted-foreground">
          Только в наличии
        </FieldLabel>
      </Field>
      <Button variant="outline" className="rounded-xl" onClick={onReset}>
        Сбросить фильтры
      </Button>
    </div>
  )
}

export function Catalog() {
  const searchParams = useSearchParams()
  const initialCat = searchParams.get("category")
  const [selectedCats, setSelectedCats] = useState<string[]>(
    initialCat && categories.some((c) => c.id === initialCat) ? [initialCat] : [],
  )
  const [selectedBrands, setSelectedBrands] = useState<string[]>([])
  const [price, setPrice] = useState(MAX_PRICE)
  const [inStockOnly, setInStockOnly] = useState(false)
  const [sort, setSort] = useState<SortKey>("popular")

  const toggleCat = (id: string) =>
    setSelectedCats((p) => (p.includes(id) ? p.filter((c) => c !== id) : [...p, id]))
  const toggleBrand = (b: string) =>
    setSelectedBrands((p) => (p.includes(b) ? p.filter((x) => x !== b) : [...p, b]))
  const reset = () => {
    setSelectedCats([])
    setSelectedBrands([])
    setPrice(MAX_PRICE)
    setInStockOnly(false)
  }

  const filtered = useMemo(() => {
    let list = products.filter((p) => {
      if (selectedCats.length && !selectedCats.includes(p.category)) return false
      if (selectedBrands.length && !selectedBrands.includes(p.brand)) return false
      if (p.price > price) return false
      if (inStockOnly && !p.inStock) return false
      return true
    })
    switch (sort) {
      case "price-asc":
        list = [...list].sort((a, b) => a.price - b.price)
        break
      case "price-desc":
        list = [...list].sort((a, b) => b.price - a.price)
        break
      case "rating":
        list = [...list].sort((a, b) => b.rating - a.rating)
        break
      default:
        list = [...list].sort((a, b) => b.reviews - a.reviews)
    }
    return list
  }, [selectedCats, selectedBrands, price, inStockOnly, sort])

  const filterProps = {
    selectedCats,
    toggleCat,
    selectedBrands,
    toggleBrand,
    price,
    setPrice,
    inStockOnly,
    setInStockOnly,
    onReset: reset,
  }

  const activeCount = selectedCats.length + selectedBrands.length + (inStockOnly ? 1 : 0)

  return (
    <section className="mx-auto max-w-7xl px-4 pt-12 sm:px-6 lg:px-8">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <h2 className="flex items-center gap-2 text-xl font-semibold tracking-tight">
            <LayoutGrid className="size-5 text-primary" />
            Каталог
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">{filtered.length} товаров</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Mobile filter */}
          <Sheet>
            <SheetTrigger
              render={
                <Button variant="outline" className="rounded-xl lg:hidden">
                  <SlidersHorizontal data-icon="inline-start" />
                  Фильтры
                  {activeCount > 0 && (
                    <Badge className="ml-1 size-5 justify-center rounded-full p-0 text-[10px]">{activeCount}</Badge>
                  )}
                </Button>
              }
            />
            <SheetContent side="left" className="w-80 overflow-y-auto">
              <SheetHeader>
                <SheetTitle>Фильтры</SheetTitle>
              </SheetHeader>
              <div className="px-4 pb-4">
                <FilterControls {...filterProps} />
              </div>
            </SheetContent>
          </Sheet>

          <Select value={sort} onValueChange={(v) => setSort(v as SortKey)}>
            <SelectTrigger className="w-44 rounded-xl">
              <SelectValue placeholder="Сортировка" />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="popular">По популярности</SelectItem>
                <SelectItem value="price-asc">Сначала дешевле</SelectItem>
                <SelectItem value="price-desc">Сначала дороже</SelectItem>
                <SelectItem value="rating">По рейтингу</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex gap-8">
        {/* Desktop filters */}
        <aside className="hidden w-64 shrink-0 lg:block">
          <div className="sticky top-32 rounded-2xl border bg-card p-5">
            <FilterControls {...filterProps} />
          </div>
        </aside>

        <div className="flex-1">
          {filtered.length > 0 ? (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
              {filtered.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed py-20 text-center">
              <span className="flex size-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
                <X className="size-6" />
              </span>
              <p className="text-sm font-medium">Ничего не найдено</p>
              <p className="text-sm text-muted-foreground">Попробуйте изменить параметры фильтра</p>
              <Button variant="outline" className="mt-2 rounded-xl" onClick={reset}>
                Сбросить фильтры
              </Button>
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
