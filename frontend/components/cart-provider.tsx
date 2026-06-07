"use client"

import { createContext, useContext, useState, useCallback, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import type { Product, CartItem } from "@/lib/types"
import { useAuth } from "@/components/auth-provider"

type CartContextType = {
  items: CartItem[]
  count: number
  subtotal: number
  isOpen: boolean
  setOpen: (open: boolean) => void
  add: (product: Product, qty?: number) => void
  remove: (id: string) => void
  setQty: (id: string, qty: number) => void
  clear: () => void
}

const CartContext = createContext<CartContextType | null>(null)

export function CartProvider({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { user } = useAuth()
  const [items, setItems] = useState<CartItem[]>([])
  const [isOpen, setOpen] = useState(false)

  const add = useCallback((product: Product, qty = 1) => {
    if (!user) {
      toast("Войдите в аккаунт", {
        description: "Чтобы добавить товар в корзину, нужно авторизоваться",
        action: {
          label: "Войти",
          onClick: () => router.push("/auth/login"),
        },
      })
      return
    }
    setItems((prev) => {
      const existing = prev.find((i) => i.product.id === product.id)
      if (existing) {
        return prev.map((i) => (i.product.id === product.id ? { ...i, qty: i.qty + qty } : i))
      }
      return [...prev, { product, qty }]
    })
    setOpen(true)
    toast.success("Добавлено в корзину", { description: product.name })
  }, [user, router])

  const remove = useCallback((id: string) => {
    setItems((prev) => prev.filter((i) => i.product.id !== id))
  }, [])

  const setQty = useCallback((id: string, qty: number) => {
    if (qty < 1) return
    setItems((prev) => prev.map((i) => (i.product.id === id ? { ...i, qty } : i)))
  }, [])

  const clear = useCallback(() => setItems([]), [])

  const count = items.reduce((acc, i) => acc + i.qty, 0)
  const subtotal = items.reduce((acc, i) => acc + i.product.price * i.qty, 0)

  return (
    <CartContext.Provider value={{ items, count, subtotal, isOpen, setOpen, add, remove, setQty, clear }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error("useCart must be used within CartProvider")
  return ctx
}
