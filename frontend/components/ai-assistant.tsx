"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import Image from "next/image"
import Link from "next/link"
import { Sparkles, X, ArrowUp, ShoppingCart, Star, Bot, LogIn } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { formatPrice } from "@/lib/data"
import { fetchProductById } from "@/lib/api/products"
import { createChatSession, sendChatMessage } from "@/lib/api/chat"
import type { Product } from "@/lib/types"
import { useCart } from "@/components/cart-provider"
import { useAuth } from "@/components/auth-provider"

type Message = {
  id: number
  role: "user" | "assistant"
  text: string
  products?: Product[]
}

function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split("\n")
  return lines.map((line, i) => {
    const parts = line.split(/\*\*(.+?)\*\*/g)
    const rendered = parts.map((part, j) =>
      j % 2 === 1 ? <strong key={j}>{part}</strong> : part,
    )
    return (
      <span key={i}>
        {rendered}
        {i < lines.length - 1 && <br />}
      </span>
    )
  })
}

const promptChips = [
  "Ноутбук до 400 000 ₸",
  "Игровой ПК для CS2",
  "Смартфон до 150 000 ₸",
  "Подарок маме",
  "Что сейчас популярно?",
]

const greeting: Message = {
  id: 0,
  role: "assistant",
  text: "Привет! Я AI-ассистент Shop. Опишите, что вы ищете, а я подберу лучшие варианты под ваш бюджет и задачи.",
}

function ChatProductCard({ product, onClose }: { product: Product; onClose: () => void }) {
  const { add } = useCart()
  return (
    <div className="flex gap-3 rounded-2xl border bg-card p-2.5">
      <Link
        href={`/product/${product.id}`}
        onClick={onClose}
        className="relative size-16 shrink-0 overflow-hidden rounded-xl bg-muted"
      >
        <Image src={product.image || "/placeholder.svg"} alt={product.name} fill sizes="64px" className="object-contain p-1.5" />
      </Link>
      <div className="flex min-w-0 flex-1 flex-col">
        <Link href={`/product/${product.id}`} onClick={onClose} className="line-clamp-2 text-xs font-medium leading-snug hover:text-primary">
          {product.name}
        </Link>
        {product.rating != null && (
          <div className="mt-0.5 flex items-center gap-1 text-[11px] text-muted-foreground">
            <Star className="size-3 fill-warning text-warning" />
            {product.rating}
          </div>
        )}
        <div className="mt-auto flex items-center justify-between gap-2 pt-1">
          <span className="text-sm font-semibold">{formatPrice(product.price)}</span>
          <Button
            size="sm"
            className="h-8 rounded-lg px-2.5 text-xs"
            onClick={() => add(product)}
          >
            <ShoppingCart data-icon="inline-start" />В корзину
          </Button>
        </div>
      </div>
    </div>
  )
}

export function AiAssistant() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([greeting])
  const [input, setInput] = useState("")
  const [typing, setTyping] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const idRef = useRef(1)
  const pendingQueryRef = useRef<{ query: string; autoSend: boolean } | null>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, typing])

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : ""
    return () => {
      document.body.style.overflow = ""
    }
  }, [open])

  const send = useCallback(async (text: string) => {
    const value = text.trim()
    if (!value || typing) return

    if (!user) {
      setMessages((prev) => [
        ...prev,
        { id: idRef.current++, role: "user", text: value },
        {
          id: idRef.current++,
          role: "assistant",
          text: "Чтобы использовать AI-ассистента, нужно войти в аккаунт.",
        },
      ])
      return
    }

    setMessages((prev) => [...prev, { id: idRef.current++, role: "user", text: value }])
    setInput("")
    setTyping(true)

    let currentSessionId = sessionId
    if (!currentSessionId) {
      const session = await createChatSession()
      if (!session) {
        setTyping(false)
        setMessages((prev) => [
          ...prev,
          { id: idRef.current++, role: "assistant", text: "Не удалось создать сессию. Попробуйте позже." },
        ])
        return
      }
      currentSessionId = session.id
      setSessionId(session.id)
    }

    const response = await sendChatMessage(currentSessionId, value)
    setTyping(false)

    if (!response) {
      setMessages((prev) => [
        ...prev,
        { id: idRef.current++, role: "assistant", text: "Произошла ошибка. Попробуйте ещё раз." },
      ])
      return
    }

    const products: Product[] = []
    if (response.product_ids && response.product_ids.length > 0) {
      const fetched = await Promise.all(
        response.product_ids.slice(0, 3).map((id) => fetchProductById(id)),
      )
      products.push(...(fetched.filter(Boolean) as Product[]))
    }

    setMessages((prev) => [
      ...prev,
      {
        id: idRef.current++,
        role: "assistant",
        text: response.content,
        products: products.length > 0 ? products : undefined,
      },
    ])
  }, [typing, user, sessionId])

  const openWithQuery = useCallback((query: string, autoSend: boolean) => {
    setOpen(true)
    if (query) {
      pendingQueryRef.current = { query, autoSend }
    }
  }, [])

  useEffect(() => {
    function onOpenAI(e: Event) {
      const query = (e as CustomEvent<{ query: string }>).detail?.query ?? ""
      openWithQuery(query, !!query)
    }
    window.addEventListener("openAI", onOpenAI)
    return () => window.removeEventListener("openAI", onOpenAI)
  }, [openWithQuery])

  useEffect(() => {
    if (open && pendingQueryRef.current) {
      const { query, autoSend } = pendingQueryRef.current
      pendingQueryRef.current = null
      if (autoSend) {
        send(query)
      } else {
        setInput(query)
      }
    }
  }, [open, send])

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          aria-label="Открыть AI-ассистента"
          className="group fixed bottom-5 right-5 z-50 flex items-center gap-2.5 rounded-full bg-primary py-3.5 pl-4 pr-5 text-primary-foreground shadow-xl shadow-primary/30 transition-transform hover:scale-105 sm:bottom-6 sm:right-6"
        >
          <span className="relative flex size-6 items-center justify-center">
            <Sparkles className="size-6" />
            <span className="absolute -right-1 -top-1 flex size-2.5">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-success opacity-75" />
              <span className="relative inline-flex size-2.5 rounded-full bg-success" />
            </span>
          </span>
          <span className="text-sm font-semibold">AI-помощник</span>
        </button>
      )}

      <div
        onClick={() => setOpen(false)}
        className={cn(
          "fixed inset-0 z-50 bg-foreground/20 backdrop-blur-sm transition-opacity duration-300",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
      />

      <aside
        role="dialog"
        aria-label="AI-ассистент"
        className={cn(
          "fixed z-50 flex flex-col bg-background shadow-2xl transition-transform duration-300 ease-out",
          "inset-0 sm:inset-y-0 sm:right-0 sm:left-auto sm:w-[450px] sm:border-l",
          open ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className="flex items-center gap-3 border-b px-4 py-3.5">
          <span className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
            <Bot className="size-5" />
          </span>
          <div className="flex-1">
            <p className="flex items-center gap-1.5 text-sm font-semibold">
              AI-ассистент Shop
              <Sparkles className="size-3.5 text-primary" />
            </p>
            <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="size-1.5 rounded-full bg-success" />
              {user ? "Онлайн · Claude + RAG" : "Войдите для полного доступа"}
            </p>
          </div>
          <Button variant="ghost" size="icon" className="rounded-full" aria-label="Закрыть" onClick={() => setOpen(false)}>
            <X />
          </Button>
        </div>

        {!user && (
          <div className="mx-4 mt-4 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-800/50 dark:bg-amber-950/20">
            <LogIn className="mt-0.5 size-4 shrink-0 text-amber-600 dark:text-amber-400" />
            <div className="text-xs text-amber-800 dark:text-amber-300">
              <span className="font-medium">Войдите в аккаунт</span> — чтобы AI-ассистент подбирал товары с учётом контекста.{" "}
              <Link href="/auth/login" onClick={() => setOpen(false)} className="underline underline-offset-2">
                Войти
              </Link>
            </div>
          </div>
        )}

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-5">
          <div className="flex flex-col gap-5">
            {messages.map((m) => (
              <div key={m.id} className={cn("flex gap-2.5", m.role === "user" && "flex-row-reverse")}>
                <span
                  className={cn(
                    "flex size-8 shrink-0 items-center justify-center rounded-full",
                    m.role === "assistant" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground",
                  )}
                >
                  {m.role === "assistant" ? <Bot className="size-4" /> : <span className="text-xs font-medium">Вы</span>}
                </span>
                <div className={cn("flex max-w-[82%] flex-col gap-2.5", m.role === "user" && "items-end")}>
                  <div
                    className={cn(
                      "rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed",
                      m.role === "assistant"
                        ? "rounded-tl-md bg-muted text-foreground"
                        : "rounded-tr-md bg-primary text-primary-foreground",
                    )}
                  >
                    {m.role === "assistant" ? renderMarkdown(m.text) : m.text}
                  </div>
                  {m.products && m.products.length > 0 && (
                    <div className="flex w-full flex-col gap-2">
                      {m.products.map((p) => (
                        <ChatProductCard key={p.id} product={p} onClose={() => setOpen(false)} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {typing && (
              <div className="flex gap-2.5">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <Bot className="size-4" />
                </span>
                <div className="flex items-center gap-1 rounded-2xl rounded-tl-md bg-muted px-4 py-3.5">
                  <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.3s]" />
                  <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.15s]" />
                  <span className="size-2 animate-bounce rounded-full bg-muted-foreground/60" />
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="no-scrollbar flex gap-2 overflow-x-auto px-4 pb-2">
          {promptChips.map((chip) => (
            <button
              key={chip}
              onClick={() => send(chip)}
              className="shrink-0 whitespace-nowrap rounded-full border bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:border-primary hover:text-primary"
            >
              {chip}
            </button>
          ))}
        </div>

        <div className="border-t p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              send(input)
            }}
            className="flex items-center gap-2 rounded-full border bg-card py-1.5 pl-4 pr-1.5 focus-within:border-ring"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Спросите что-нибудь..."
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
            <Button type="submit" size="icon" disabled={!input.trim() || typing} className="size-9 shrink-0 rounded-full" aria-label="Отправить">
              <ArrowUp />
            </Button>
          </form>
          <p className="mt-2 text-center text-[11px] text-muted-foreground">
            AI может ошибаться. Проверяйте важные характеристики.
          </p>
        </div>
      </aside>
    </>
  )
}
