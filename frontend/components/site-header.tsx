"use client"

import Link from "next/link"
import { useState, useEffect } from "react"
import { useTheme } from "next-themes"
import {
  Search,
  ShoppingCart,
  Heart,
  Menu,
  Sun,
  Moon,
  Package,
  Sparkles,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { fetchCategories, type DisplayCategory } from "@/lib/api/categories"
import { useCart } from "@/components/cart-provider"
import { useAuth } from "@/components/auth-provider"
import { useFavorites } from "@/components/favorites-provider"
import { UserMenu } from "@/components/user-menu"

function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Переключить тему"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      className="rounded-full"
    >
      <Sun className="hidden dark:block" />
      <Moon className="block dark:hidden" />
    </Button>
  )
}

export function SiteHeader() {
  const { count, setOpen } = useCart()
  const { user } = useAuth()
  const { count: favCount } = useFavorites()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [categories, setCategories] = useState<DisplayCategory[]>([])

  useEffect(() => {
    fetchCategories().then(setCategories)
  }, [])

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/70 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4 sm:px-6 lg:px-8">
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetTrigger
            render={
              <Button variant="ghost" size="icon" className="rounded-full lg:hidden" aria-label="Меню">
                <Menu />
              </Button>
            }
          />
          <SheetContent side="left" className="w-80 p-0">
            <SheetHeader className="border-b">
              <SheetTitle className="flex items-center gap-2">
                <Logo />
              </SheetTitle>
            </SheetHeader>
            <nav className="flex flex-col gap-1 p-4">
              {categories.map((c) => (
                <Link
                  key={c.uuid}
                  href={`/?category=${c.slug}`}
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-accent"
                >
                  {c.name}
                </Link>
              ))}
              <div className="my-2 h-px bg-border" />
              <Link
                href="/"
                onClick={() => setMobileOpen(false)}
                className="rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-accent"
              >
                Главная
              </Link>
              {user && (
                <>
                  <Link
                    href="/orders"
                    onClick={() => setMobileOpen(false)}
                    className="rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-accent"
                  >
                    Заказы
                  </Link>
                  <Link
                    href="/favorites"
                    onClick={() => setMobileOpen(false)}
                    className="rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-accent"
                  >
                    Избранное
                  </Link>
                  <Link
                    href="/profile"
                    onClick={() => setMobileOpen(false)}
                    className="rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-accent"
                  >
                    Профиль
                  </Link>
                </>
              )}
              {!user && (
                <Link
                  href="/auth/login"
                  onClick={() => setMobileOpen(false)}
                  className="rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-accent"
                >
                  Войти
                </Link>
              )}
            </nav>
          </SheetContent>
        </Sheet>

        <Link href="/" className="flex items-center gap-2">
          <Logo />
        </Link>

        <div className="relative ml-2 hidden flex-1 md:block">
          <Search className="absolute left-3.5 top-1/2 size-4.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Искать товары, бренды и категории..."
            className="h-11 rounded-full border-transparent bg-muted pl-11 focus-visible:border-ring focus-visible:bg-background"
          />
        </div>

        <div className="ml-auto flex items-center gap-1">
          {user && (
            <>
              <Button
                variant="ghost"
                className="hidden rounded-full text-muted-foreground lg:inline-flex"
                render={<Link href="/orders" />}
              >
                <Package data-icon="inline-start" />
                Заказы
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="relative rounded-full"
                aria-label="Избранное"
                render={<Link href="/favorites" />}
              >
                <Heart />
                {favCount > 0 && (
                  <Badge className="absolute -right-0.5 -top-0.5 size-5 justify-center rounded-full p-0 text-[10px] tabular-nums">
                    {favCount}
                  </Badge>
                )}
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="relative rounded-full"
                aria-label="Корзина"
                onClick={() => setOpen(true)}
              >
                <ShoppingCart />
                {count > 0 && (
                  <Badge className="absolute -right-0.5 -top-0.5 size-5 justify-center rounded-full p-0 text-[10px] tabular-nums">
                    {count}
                  </Badge>
                )}
              </Button>
            </>
          )}
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>

    </header>
  )
}

function Logo() {
  return (
    <span className="flex items-center gap-2">
      <span className="flex size-8 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <Sparkles className="size-4.5" />
      </span>
      <span className="text-lg font-semibold tracking-tight">Shop</span>
    </span>
  )
}
