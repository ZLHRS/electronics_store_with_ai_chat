import Link from "next/link"
import { Sparkles } from "lucide-react"

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/40 px-4 py-12">
      <Link href="/" className="mb-8 flex items-center gap-2">
        <span className="flex size-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Sparkles className="size-5" />
        </span>
        <span className="text-xl font-semibold tracking-tight">Kvant</span>
      </Link>
      {children}
    </div>
  )
}
