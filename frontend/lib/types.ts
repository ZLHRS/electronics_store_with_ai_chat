export type Category = {
  id: string
  name: string
  icon: string
}

export type Product = {
  id: string
  slug?: string
  name: string
  brand: string
  category: string
  price: number
  oldPrice?: number
  rating?: number
  reviews?: number
  image: string
  images: string[]
  badge?: "hit" | "new" | "sale"
  inStock: boolean
  description: string
  specs: { label: string; value: string }[]
}

export type CartItem = {
  product: Product
  qty: number
}

export type OrderStatus = "processing" | "shipped" | "delivered" | "cancelled"

export type Order = {
  id: string
  date: string
  total: number
  status: OrderStatus
  items: { product: Product; qty: number }[]
  timeline: { label: string; date: string; done: boolean }[]
}
