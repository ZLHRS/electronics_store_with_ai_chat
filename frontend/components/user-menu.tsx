"use client"

import { useRouter } from "next/navigation"
import { User, LogOut, Package, ChevronDown, Loader2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { apiLogout } from "@/lib/api/auth"
import { useAuth } from "@/components/auth-provider"
import Link from "next/link"

export function UserMenu() {
  const router = useRouter()
  const { user, loading, setUser } = useAuth()

  async function handleLogout() {
    await apiLogout()
    setUser(null)
    window.location.replace("/")
  }

  if (loading) {
    return (
      <div className="flex size-9 items-center justify-center rounded-full">
        <Loader2 className="size-4 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center gap-1">
        <Link
          href="/auth/login"
          className="hidden h-7 items-center rounded-full px-2.5 text-[0.8rem] font-medium hover:bg-muted hover:text-foreground sm:inline-flex"
        >
          Войти
        </Link>
        <Link
          href="/auth/register"
          className="inline-flex h-7 items-center rounded-full bg-primary px-2.5 text-[0.8rem] font-medium text-primary-foreground hover:bg-primary/80"
        >
          Регистрация
        </Link>
      </div>
    )
  }

  const initials = user.email.slice(0, 2).toUpperCase()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="flex items-center gap-1.5 rounded-full pr-1 transition-colors hover:bg-accent">
        <span className="flex size-9 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
          {initials}
        </span>
        <ChevronDown className="size-3.5 text-muted-foreground" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-52">
        <div className="px-1.5 py-1.5 flex flex-col gap-0.5">
          <span className="truncate text-sm font-medium">{user.email}</span>
          <span className="text-xs text-muted-foreground capitalize">
            {user.roles.includes("admin") ? "Администратор" : "Покупатель"}
          </span>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => router.push("/profile")}
        >
          <User className="size-4" />
          Профиль
        </DropdownMenuItem>
        <DropdownMenuItem
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => router.push("/orders")}
        >
          <Package className="size-4" />
          Мои заказы
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="flex items-center gap-2 text-destructive focus:text-destructive cursor-pointer"
          onClick={handleLogout}
        >
          <LogOut className="size-4" />
          Выйти
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
