"use client"

import { createContext, useContext, useState, useCallback, useEffect, useRef, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import type { Product, CartItem } from "@/lib/types"
import { useAuth } from "@/components/auth-provider"
import {
  apiGetCart,
  apiAddItem,
  apiUpdateItem,
  apiRemoveItem,
  apiClearCart,
  type CartApi,
} from "@/lib/api/cart"

type CartContextType = {
  items: CartItem[]
  count: number
  subtotal: number
  isLoading: boolean
  isOpen: boolean
  setOpen: (open: boolean) => void
  add: (product: Product, qty?: number) => void
  remove: (id: string) => void
  setQty: (id: string, qty: number) => void
  clear: () => void
}

const CartContext = createContext<CartContextType | null>(null)

function toItems(cart: CartApi): CartItem[] {
  return cart.items.map((item) => ({
    product: {
      id: item.product_id,
      name: item.product?.name ?? "Товар",
      price: parseFloat(item.unit_price),
      image: item.product?.image_url ?? "",
      images: [],
      brand: "",
      category: "",
      inStock: item.product?.status === "active",
      description: "",
      specs: [],
    },
    qty: item.quantity,
  }))
}

export function CartProvider({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { user } = useAuth()
  const [items, setItems] = useState<CartItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isOpen, setOpen] = useState(false)
  const itemsRef = useRef<CartItem[]>([])

  const sync = useCallback((cart: CartApi) => {
    const next = toItems(cart)
    itemsRef.current = next
    setItems(next)
  }, [])

  const revert = useCallback(() => {
    setItems(itemsRef.current)
  }, [])

  useEffect(() => {
    if (!user) {
      setItems([])
      itemsRef.current = []
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    apiGetCart().then(sync).catch(() => {}).finally(() => setIsLoading(false))
  }, [user, sync])

  const add = useCallback(async (product: Product, qty = 1) => {
    if (!user) {
      toast("Войдите в аккаунт", {
        description: "Чтобы добавить товар в корзину, нужно авторизоваться",
        action: { label: "Войти", onClick: () => router.push("/auth/login") },
      })
      return
    }

    setItems((prev) => {
      const exists = prev.find((i) => i.product.id === product.id)
      return exists
        ? prev.map((i) => (i.product.id === product.id ? { ...i, qty: i.qty + qty } : i))
        : [...prev, { product, qty }]
    })
    setOpen(true)
    toast.success("Добавлено в корзину", { description: product.name })

    try {
      sync(await apiAddItem(product.id, qty))
    } catch {
      revert()
      toast.error("Не удалось добавить товар")
    }
  }, [user, router, sync, revert])

  const remove = useCallback(async (id: string) => {
    setItems((prev) => prev.filter((i) => i.product.id !== id))
    try {
      sync(await apiRemoveItem(id))
    } catch {
      revert()
      toast.error("Не удалось удалить товар")
    }
  }, [sync, revert])

  const setQty = useCallback(async (id: string, qty: number) => {
    if (qty < 1) {
      setItems((prev) => prev.filter((i) => i.product.id !== id))
      try {
        sync(await apiRemoveItem(id))
      } catch {
        revert()
      }
      return
    }
    setItems((prev) => prev.map((i) => (i.product.id === id ? { ...i, qty } : i)))
    try {
      sync(await apiUpdateItem(id, qty))
    } catch {
      revert()
      toast.error("Ошибка обновления корзины")
    }
  }, [sync, revert])

  const clear = useCallback(async () => {
    setItems([])
    try {
      sync(await apiClearCart())
    } catch {
      revert()
      toast.error("Не удалось очистить корзину")
    }
  }, [sync, revert])

  const count = items.reduce((acc, i) => acc + i.qty, 0)
  const subtotal = items.reduce((acc, i) => acc + i.product.price * i.qty, 0)

  return (
    <CartContext.Provider value={{ items, count, subtotal, isLoading, isOpen, setOpen, add, remove, setQty, clear }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error("useCart must be used within CartProvider")
  return ctx
}
