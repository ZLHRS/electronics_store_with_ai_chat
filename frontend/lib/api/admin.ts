import type { Product } from "@/lib/types"
import type { DisplayCategory } from "@/lib/api/categories"

type ApiImage = { id: string; product_id: string; image_url: string; sort_order: number }
type ApiAttribute = { id: string; product_id: string; name: string; value: string }

export type AdminProduct = {
  id: string
  name: string
  slug: string
  description: string | null
  price: string
  category_id: string | null
  brand_id: string | null
  status: string
  created_at: string
  updated_at: string
  images: ApiImage[]
  attributes: ApiAttribute[]
}

export type AdminCategory = { id: string; name: string; slug: string; parent_id: string | null }
export type AdminBrand = { id: string; name: string; slug: string }

type ProductListResponse = { items: AdminProduct[]; total: number; page: number; limit: number }

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T | null> {
  try {
    const res = await fetch(path, {
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      ...options,
    })
    if (res.status === 204) return null
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`)
    }
    return res.json() as Promise<T>
  } catch (e) {
    throw e
  }
}

export async function adminListProducts(
  page = 1,
  limit = 50,
  status?: string,
  search?: string,
): Promise<{ items: AdminProduct[]; total: number }> {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
    ...(status ? { status } : {}),
    ...(search ? { search } : {}),
  })
  const data = await apiFetch<ProductListResponse>(`/api/v1/products?${params}`)
  return { items: data?.items ?? [], total: data?.total ?? 0 }
}

export async function adminListAllProducts(): Promise<AdminProduct[]> {
  const [active, draft, archived] = await Promise.all([
    adminListProducts(1, 100, "active"),
    adminListProducts(1, 100, "draft"),
    adminListProducts(1, 100, "archived"),
  ])
  return [...active.items, ...draft.items, ...archived.items]
}

export type CreateProductPayload = {
  name: string
  price: number
  description?: string
  category_id?: string | null
  brand_id?: string | null
  status: string
  images: { image_url: string; sort_order: number }[]
  attributes: { name: string; value: string }[]
}

export async function adminCreateProduct(data: CreateProductPayload): Promise<AdminProduct> {
  const result = await apiFetch<AdminProduct>("/api/v1/products", {
    method: "POST",
    body: JSON.stringify(data),
  })
  if (!result) throw new Error("No response")
  return result
}

export async function adminUpdateProduct(
  id: string,
  data: Partial<CreateProductPayload>,
): Promise<AdminProduct> {
  const result = await apiFetch<AdminProduct>(`/api/v1/products/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
  if (!result) throw new Error("No response")
  return result
}

export async function adminDeleteProduct(id: string): Promise<void> {
  await apiFetch<null>(`/api/v1/products/${id}`, { method: "DELETE" })
}

export async function adminListCategories(): Promise<AdminCategory[]> {
  const data = await apiFetch<AdminCategory[]>("/api/v1/categories")
  return data ?? []
}

export async function adminCreateCategory(data: {
  name: string
  slug?: string
  parent_id?: string | null
}): Promise<AdminCategory> {
  const result = await apiFetch<AdminCategory>("/api/v1/categories", {
    method: "POST",
    body: JSON.stringify(data),
  })
  if (!result) throw new Error("No response")
  return result
}

export async function adminUpdateCategory(
  id: string,
  data: { name?: string; slug?: string },
): Promise<AdminCategory> {
  const result = await apiFetch<AdminCategory>(`/api/v1/categories/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
  if (!result) throw new Error("No response")
  return result
}

export async function adminDeleteCategory(id: string): Promise<void> {
  await apiFetch<null>(`/api/v1/categories/${id}`, { method: "DELETE" })
}

export async function adminListBrands(): Promise<AdminBrand[]> {
  const data = await apiFetch<AdminBrand[]>("/api/v1/brands")
  return data ?? []
}

export async function adminCreateBrand(data: {
  name: string
  slug?: string
}): Promise<AdminBrand> {
  const result = await apiFetch<AdminBrand>("/api/v1/brands", {
    method: "POST",
    body: JSON.stringify(data),
  })
  if (!result) throw new Error("No response")
  return result
}

export async function adminUpdateBrand(
  id: string,
  data: { name?: string; slug?: string },
): Promise<AdminBrand> {
  const result = await apiFetch<AdminBrand>(`/api/v1/brands/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  })
  if (!result) throw new Error("No response")
  return result
}

export async function adminDeleteBrand(id: string): Promise<void> {
  await apiFetch<null>(`/api/v1/brands/${id}`, { method: "DELETE" })
}
