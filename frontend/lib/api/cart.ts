type CartItemSnapshot = {
  name: string
  image_url: string | null
  current_price: string
  status: string
}

export type CartItemApi = {
  id: string
  product_id: string
  quantity: number
  unit_price: string
  product: CartItemSnapshot | null
}

export type CartApi = {
  id: string
  items: CartItemApi[]
  total: string
}

async function cartFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...init,
  })
  if (!res.ok) throw new Error(`cart ${res.status}`)
  return res.json()
}

export const apiGetCart = () =>
  cartFetch<CartApi>("/api/v1/cart")

export const apiAddItem = (productId: string, quantity: number) =>
  cartFetch<CartApi>("/api/v1/cart/items", {
    method: "POST",
    body: JSON.stringify({ product_id: productId, quantity }),
  })

export const apiUpdateItem = (productId: string, quantity: number) =>
  cartFetch<CartApi>(`/api/v1/cart/items/${productId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  })

export const apiRemoveItem = (productId: string) =>
  cartFetch<CartApi>(`/api/v1/cart/items/${productId}`, { method: "DELETE" })

export const apiClearCart = () =>
  cartFetch<CartApi>("/api/v1/cart", { method: "DELETE" })
