import type { Product } from "@/lib/types"

type ApiImage = { id: string; product_id: string; image_url: string; sort_order: number }
type ApiAttribute = { id: string; product_id: string; name: string; value: string }

type ApiProduct = {
  id: string
  name: string
  slug: string
  description: string | null
  price: string
  category_id: string | null
  brand_id: string | null
  status: string
  images: ApiImage[]
  attributes: ApiAttribute[]
}

type ApiListResponse = { items: ApiProduct[]; total: number; page: number; limit: number }
type ApiBrand = { id: string; name: string; slug: string }
type ApiCategory = { id: string; name: string; slug: string; parent_id: string | null }

async function apiFetch<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(path, { cache: "no-store" })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

function adaptProduct(
  p: ApiProduct,
  brandMap: Map<string, string>,
  catMap: Map<string, string>,
): Product {
  return {
    id: p.id,
    slug: p.slug,
    name: p.name,
    brand: brandMap.get(p.brand_id ?? "") ?? "",
    category: catMap.get(p.category_id ?? "") ?? "",
    price: parseFloat(p.price),
    rating: undefined,
    reviews: undefined,
    image: p.images[0]?.image_url ?? "/placeholder.svg",
    images: p.images.map((i) => i.image_url),
    inStock: p.status === "active",
    description: p.description ?? "",
    specs: p.attributes.map((a) => ({ label: a.name, value: a.value })),
  }
}

async function fetchMaps() {
  const [brands, categories] = await Promise.all([
    apiFetch<ApiBrand[]>("/api/v1/brands"),
    apiFetch<ApiCategory[]>("/api/v1/categories"),
  ])
  const brandMap = new Map<string, string>((brands ?? []).map((b) => [b.id, b.name]))
  const catMap = new Map<string, string>((categories ?? []).map((c) => [c.id, c.slug]))
  return { brandMap, catMap }
}

export async function fetchProducts(limit = 100): Promise<Product[]> {
  const [data, { brandMap, catMap }] = await Promise.all([
    apiFetch<ApiListResponse>(`/api/v1/products?limit=${limit}&status=active`),
    fetchMaps(),
  ])
  if (!data) return []
  return data.items.map((p) => adaptProduct(p, brandMap, catMap))
}

export async function fetchProductBySlug(slug: string): Promise<Product | null> {
  const [data, { brandMap, catMap }] = await Promise.all([
    apiFetch<ApiListResponse>(`/api/v1/products?limit=1&status=active`),
    fetchMaps(),
  ])
  if (!data) return null
  const all = await apiFetch<ApiListResponse>(`/api/v1/products?limit=200`)
  if (!all) return null
  const found = all.items.find((p) => p.slug === slug)
  if (!found) return null
  return adaptProduct(found, brandMap, catMap)
}

export async function fetchProductById(id: string): Promise<Product | null> {
  const [product, { brandMap, catMap }] = await Promise.all([
    apiFetch<ApiProduct>(`/api/v1/products/${id}`),
    fetchMaps(),
  ])
  if (!product) return null
  return adaptProduct(product, brandMap, catMap)
}
