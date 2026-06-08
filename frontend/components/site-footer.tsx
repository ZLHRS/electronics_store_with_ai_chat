"use client"

import Link from "next/link"
import { Sparkles } from "lucide-react"
import { Separator } from "@/components/ui/separator"

export function SiteFooter() {
  return (
    <footer className="mt-20 border-t bg-card">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-4 py-10 sm:flex-row sm:items-center sm:justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex size-8 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <Sparkles className="size-4.5" />
            </span>
            <span className="text-base font-semibold tracking-tight">Shop</span>
          </Link>

          <p className="text-center text-sm text-muted-foreground">
            Умный маркетплейс электроники с AI-ассистентом
          </p>

          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <span className="cursor-pointer hover:text-foreground">Конфиденциальность</span>
            <Separator orientation="vertical" className="h-3.5" />
            <span className="cursor-pointer hover:text-foreground">Условия</span>
          </div>
        </div>

        <div className="border-t py-4 text-center text-xs text-muted-foreground">
          © 2026 Shop. Все права защищены.
        </div>
      </div>
    </footer>
  )
}
