"use client"

import Link from "next/link"
import { Sparkles } from "lucide-react"

export function SiteFooter() {
  return (
    <footer className="border-t bg-card">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
          <span className="flex size-6 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Sparkles className="size-3.5" />
          </span>
          <span className="text-sm font-medium">Shop</span>
        </Link>

        <p className="text-xs text-muted-foreground">© 2026 Shop. Все права защищены.</p>

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span className="cursor-pointer hover:text-foreground transition-colors">Конфиденциальность</span>
          <span className="cursor-pointer hover:text-foreground transition-colors">Условия</span>
        </div>
      </div>
    </footer>
  )
}
