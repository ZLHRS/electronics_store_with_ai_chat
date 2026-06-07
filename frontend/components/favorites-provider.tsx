"use client"

import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { useAuth } from "@/components/auth-provider"

const STORAGE_KEY = "shop:favorites"

type FavoritesContextType = {
  ids: Set<string>
  toggle: (productId: string, productName: string) => void
  has: (productId: string) => boolean
  count: number
}

const FavoritesContext = createContext<FavoritesContextType | null>(null)

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const router = useRouter()
  const { user } = useAuth()
  const [ids, setIds] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!user) {
      setIds(new Set())
      return
    }
    try {
      const stored = localStorage.getItem(`${STORAGE_KEY}:${user.id}`)
      setIds(stored ? new Set(JSON.parse(stored)) : new Set())
    } catch {
      setIds(new Set())
    }
  }, [user])

  const persist = useCallback((next: Set<string>, userId: string) => {
    try {
      localStorage.setItem(`${STORAGE_KEY}:${userId}`, JSON.stringify([...next]))
    } catch {}
  }, [])

  const toggle = useCallback((productId: string, productName: string) => {
    if (!user) {
      toast("Войдите в аккаунт", {
        description: "Чтобы добавить в избранное, нужно авторизоваться",
        action: { label: "Войти", onClick: () => router.push("/auth/login") },
      })
      return
    }
    setIds((prev) => {
      const next = new Set(prev)
      if (next.has(productId)) {
        next.delete(productId)
        toast("Удалено из избранного", { description: productName })
      } else {
        next.add(productId)
        toast.success("Добавлено в избранное", { description: productName })
      }
      persist(next, user.id)
      return next
    })
  }, [user, router, persist])

  const has = useCallback((productId: string) => ids.has(productId), [ids])

  return (
    <FavoritesContext.Provider value={{ ids, toggle, has, count: ids.size }}>
      {children}
    </FavoritesContext.Provider>
  )
}

export function useFavorites() {
  const ctx = useContext(FavoritesContext)
  if (!ctx) throw new Error("useFavorites must be used within FavoritesProvider")
  return ctx
}
