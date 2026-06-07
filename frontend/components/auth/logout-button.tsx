"use client"

import { useState } from "react"
import { LogOut, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { apiLogout } from "@/lib/api/auth"
import { useAuth } from "@/components/auth-provider"

export function LogoutButton() {
  const { setUser } = useAuth()
  const [loading, setLoading] = useState(false)

  async function handleLogout() {
    setLoading(true)
    await apiLogout()
    setUser(null)
    window.location.replace("/")
  }

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full rounded-xl border-destructive/30 text-destructive hover:bg-destructive/5 hover:text-destructive"
      onClick={handleLogout}
      disabled={loading}
    >
      {loading ? (
        <Loader2 className="mr-2 size-4 animate-spin" />
      ) : (
        <LogOut className="mr-2 size-4" />
      )}
      Выйти из аккаунта
    </Button>
  )
}
