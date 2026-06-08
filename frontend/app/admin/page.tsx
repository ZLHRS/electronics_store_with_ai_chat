"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import {
  Package,
  Tag,
  Layers,
  Plus,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Search,
  ShieldCheck,
  Loader2,
  X,
  Check,
  Pencil,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuth } from "@/components/auth-provider"
import { formatPrice } from "@/lib/data"
import {
  adminListAllProducts,
  adminListCategories,
  adminListBrands,
  adminCreateProduct,
  adminUpdateProduct,
  adminDeleteProduct,
  adminCreateCategory,
  adminUpdateCategory,
  adminDeleteCategory,
  adminCreateBrand,
  adminUpdateBrand,
  adminDeleteBrand,
  type AdminProduct,
  type AdminCategory,
  type AdminBrand,
  type CreateProductPayload,
} from "@/lib/api/admin"

const STATUS_LABELS: Record<string, string> = {
  active: "Активен",
  draft: "Черновик",
  archived: "Архив",
}

function StatusBadge({ status }: { status: string }) {
  return (
    <Badge
      variant={status === "active" ? "default" : "secondary"}
      className="capitalize"
    >
      {STATUS_LABELS[status] ?? status}
    </Badge>
  )
}

function ProductForm({
  categories,
  brands,
  onSubmit,
  loading,
}: {
  categories: AdminCategory[]
  brands: AdminBrand[]
  onSubmit: (data: CreateProductPayload) => void
  loading: boolean
}) {
  const [name, setName] = useState("")
  const [price, setPrice] = useState("")
  const [description, setDescription] = useState("")
  const [categoryId, setCategoryId] = useState<string>("none")
  const [brandId, setBrandId] = useState<string>("none")
  const [status, setStatus] = useState("active")
  const [imageUrl, setImageUrl] = useState("")

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onSubmit({
      name: name.trim(),
      price: parseFloat(price),
      description: description.trim() || undefined,
      category_id: categoryId === "none" ? null : categoryId,
      brand_id: brandId === "none" ? null : brandId,
      status,
      images: imageUrl.trim() ? [{ image_url: imageUrl.trim(), sort_order: 0 }] : [],
      attributes: [],
    })
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2 flex flex-col gap-1.5">
          <label className="text-sm font-medium">Название *</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Ноутбук Aurora Pro" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">Цена (₸) *</label>
          <Input value={price} onChange={(e) => setPrice(e.target.value)} type="number" required min="0" placeholder="99990" />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">Статус</label>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="active">Активен</SelectItem>
              <SelectItem value="draft">Черновик</SelectItem>
              <SelectItem value="archived">Архив</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">Категория</label>
          <select
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus:border-ring dark:bg-input/30"
          >
            <option value="none">Без категории</option>
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-sm font-medium">Бренд</label>
          <select
            value={brandId}
            onChange={(e) => setBrandId(e.target.value)}
            className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus:border-ring dark:bg-input/30"
          >
            <option value="none">Без бренда</option>
            {brands.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
        <div className="col-span-2 flex flex-col gap-1.5">
          <label className="text-sm font-medium">URL изображения</label>
          <Input value={imageUrl} onChange={(e) => setImageUrl(e.target.value)} placeholder="https://..." />
        </div>
        <div className="col-span-2 flex flex-col gap-1.5">
          <label className="text-sm font-medium">Описание</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            placeholder="Краткое описание товара..."
            className="w-full rounded-xl border bg-background px-3 py-2 text-sm outline-none focus:border-ring resize-none"
          />
        </div>
      </div>
      <Button type="submit" disabled={loading || !name || !price} className="rounded-xl">
        {loading ? <Loader2 className="size-4 animate-spin" /> : "Создать товар"}
      </Button>
    </form>
  )
}

function SimpleCreateForm({
  label,
  placeholder,
  onSubmit,
  loading,
}: {
  label: string
  placeholder: string
  onSubmit: (name: string) => void
  loading: boolean
}) {
  const [value, setValue] = useState("")
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (value.trim()) onSubmit(value.trim())
      }}
      className="flex gap-2"
    >
      <Input value={value} onChange={(e) => setValue(e.target.value)} placeholder={placeholder} className="flex-1" />
      <Button type="submit" disabled={loading || !value.trim()} className="rounded-xl">
        {loading ? <Loader2 className="size-4 animate-spin" /> : <Plus className="size-4" />}
      </Button>
    </form>
  )
}

function InlineEditRow({
  value,
  linkedCount,
  onSave,
  onDelete,
  saving,
  deleting,
}: {
  value: string
  linkedCount: number
  onSave: (name: string) => void
  onDelete: () => void
  saving: boolean
  deleting: boolean
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)

  function handleSave() {
    if (draft.trim() && draft.trim() !== value) {
      onSave(draft.trim())
    }
    setEditing(false)
  }

  return editing ? (
    <div className="flex items-center gap-2">
      <input
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSave()
          if (e.key === "Escape") { setDraft(value); setEditing(false) }
        }}
        className="h-7 flex-1 rounded-lg border border-ring bg-background px-2 text-sm outline-none"
      />
      <Button size="icon" variant="ghost" className="size-7 rounded-lg text-green-600 hover:bg-green-50" onClick={handleSave} disabled={saving}>
        {saving ? <Loader2 className="size-3.5 animate-spin" /> : <Check className="size-3.5" />}
      </Button>
      <Button size="icon" variant="ghost" className="size-7 rounded-lg" onClick={() => { setDraft(value); setEditing(false) }}>
        <X className="size-3.5" />
      </Button>
    </div>
  ) : (
    <div className="flex items-center justify-between gap-2 group">
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-sm font-medium">{value}</span>
        {linkedCount > 0 && (
          <span className="shrink-0 rounded-full bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground">
            {linkedCount} товаров
          </span>
        )}
      </div>
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
        <Button size="icon" variant="ghost" className="size-7 rounded-lg" onClick={() => setEditing(true)}>
          <Pencil className="size-3.5" />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          className="size-7 rounded-lg text-destructive hover:bg-destructive/10"
          disabled={deleting}
          onClick={onDelete}
        >
          {deleting ? <Loader2 className="size-3.5 animate-spin" /> : <Trash2 className="size-3.5" />}
        </Button>
      </div>
    </div>
  )
}

export default function AdminPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()

  const [products, setProducts] = useState<AdminProduct[]>([])
  const [categories, setCategories] = useState<AdminCategory[]>([])
  const [brands, setBrands] = useState<AdminBrand[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "draft" | "archived">("all")

  const [createProductOpen, setCreateProductOpen] = useState(false)
  const [createLoading, setCreateLoading] = useState(false)

  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [togglingId, setTogglingId] = useState<string | null>(null)

  const [savingCatId, setSavingCatId] = useState<string | null>(null)
  const [deletingCatId, setDeletingCatId] = useState<string | null>(null)
  const [savingBrandId, setSavingBrandId] = useState<string | null>(null)
  const [deletingBrandId, setDeletingBrandId] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    setDataLoading(true)
    const [prods, cats, brnds] = await Promise.all([
      adminListAllProducts(),
      adminListCategories(),
      adminListBrands(),
    ])
    setProducts(prods)
    setCategories(cats)
    setBrands(brnds)
    setDataLoading(false)
  }, [])

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/auth/login")
      return
    }
    if (!authLoading && user && !user.roles.includes("admin")) {
      router.replace("/")
      return
    }
    if (!authLoading && user) {
      loadData()
    }
  }, [authLoading, user, router, loadData])

  const catMap = Object.fromEntries(categories.map((c) => [c.id, c.name]))
  const brandMap = Object.fromEntries(brands.map((b) => [b.id, b.name]))

  const filteredProducts = products.filter((p) => {
    if (statusFilter !== "all" && p.status !== statusFilter) return false
    if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  async function handleCreateProduct(data: CreateProductPayload) {
    setCreateLoading(true)
    try {
      const created = await adminCreateProduct(data)
      setProducts((prev) => [created, ...prev])
      setCreateProductOpen(false)
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setCreateLoading(false)
    }
  }

  async function handleDeleteProduct(id: string) {
    if (!confirm("Удалить товар? Это действие необратимо.")) return
    setDeletingId(id)
    try {
      await adminDeleteProduct(id)
      setProducts((prev) => prev.filter((p) => p.id !== id))
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setDeletingId(null)
    }
  }

  async function handleToggleStatus(product: AdminProduct) {
    setTogglingId(product.id)
    try {
      const newStatus = product.status === "active" ? "archived" : "active"
      const updated = await adminUpdateProduct(product.id, { status: newStatus })
      setProducts((prev) => prev.map((p) => (p.id === product.id ? updated : p)))
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setTogglingId(null)
    }
  }

  async function handleCreateCategory(name: string) {
    try {
      const created = await adminCreateCategory({ name })
      setCategories((prev) => [...prev, created])
    } catch (e) {
      alert((e as Error).message)
    }
  }

  async function handleUpdateCategory(id: string, name: string) {
    setSavingCatId(id)
    try {
      const updated = await adminUpdateCategory(id, { name })
      setCategories((prev) => prev.map((c) => (c.id === id ? updated : c)))
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setSavingCatId(null)
    }
  }

  async function handleDeleteCategory(id: string, name: string) {
    const count = products.filter((p) => p.category_id === id).length
    const msg = count > 0
      ? `Удалить категорию «${name}»?\n\n${count} ${count === 1 ? "товар потеряет" : count < 5 ? "товара потеряют" : "товаров потеряют"} категорию — они останутся в каталоге, но без привязки к категории.`
      : `Удалить категорию «${name}»?`
    if (!confirm(msg)) return
    setDeletingCatId(id)
    try {
      await adminDeleteCategory(id)
      setCategories((prev) => prev.filter((c) => c.id !== id))
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setDeletingCatId(null)
    }
  }

  async function handleCreateBrand(name: string) {
    try {
      const created = await adminCreateBrand({ name })
      setBrands((prev) => [...prev, created])
    } catch (e) {
      alert((e as Error).message)
    }
  }

  async function handleUpdateBrand(id: string, name: string) {
    setSavingBrandId(id)
    try {
      const updated = await adminUpdateBrand(id, { name })
      setBrands((prev) => prev.map((b) => (b.id === id ? updated : b)))
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setSavingBrandId(null)
    }
  }

  async function handleDeleteBrand(id: string, name: string) {
    const count = products.filter((p) => p.brand_id === id).length
    const msg = count > 0
      ? `Удалить бренд «${name}»?\n\n${count} ${count === 1 ? "товар потеряет" : count < 5 ? "товара потеряют" : "товаров потеряют"} бренд — они останутся в каталоге, но без привязки к бренду.`
      : `Удалить бренд «${name}»?`
    if (!confirm(msg)) return
    setDeletingBrandId(id)
    try {
      await adminDeleteBrand(id)
      setBrands((prev) => prev.filter((b) => b.id !== id))
    } catch (e) {
      alert((e as Error).message)
    } finally {
      setDeletingBrandId(null)
    }
  }

  if (authLoading || dataLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!user || !user.roles.includes("admin")) return null

  const activeCount = products.filter((p) => p.status === "active").length
  const inactiveCount = products.filter((p) => p.status !== "active").length

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <ShieldCheck className="size-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Панель администратора</h1>
          <p className="text-sm text-muted-foreground">{user.email}</p>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Всего товаров", value: products.length, icon: Package, color: "text-primary" },
          { label: "Активных", value: activeCount, icon: Check, color: "text-green-600" },
          { label: "Черновиков/Архив", value: inactiveCount, icon: X, color: "text-muted-foreground" },
          { label: "Категорий", value: categories.length, icon: Layers, color: "text-primary" },
        ].map((s) => (
          <div key={s.label} className="rounded-2xl border bg-card p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">{s.label}</p>
              <s.icon className={`size-4 ${s.color}`} />
            </div>
            <p className="mt-2 text-3xl font-bold">{s.value}</p>
          </div>
        ))}
      </div>

      <Tabs defaultValue="products">
        <TabsList className="mb-6">
          <TabsTrigger value="products" className="gap-2">
            <Package className="size-4" />
            Товары
          </TabsTrigger>
          <TabsTrigger value="categories" className="gap-2">
            <Layers className="size-4" />
            Категории
          </TabsTrigger>
          <TabsTrigger value="brands" className="gap-2">
            <Tag className="size-4" />
            Бренды
          </TabsTrigger>
        </TabsList>

        <TabsContent value="products">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-1 gap-2">
              <div className="relative flex-1 max-w-sm">
                <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Поиск по названию..."
                  className="pl-9 rounded-xl"
                />
              </div>
              <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as typeof statusFilter)}>
                <SelectTrigger className="w-36 rounded-xl"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все</SelectItem>
                  <SelectItem value="active">Активные</SelectItem>
                  <SelectItem value="draft">Черновики</SelectItem>
                  <SelectItem value="archived">Архив</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={() => setCreateProductOpen(true)} className="rounded-xl gap-1.5">
              <Plus className="size-4" />
              Добавить товар
            </Button>
          </div>

          <div className="rounded-2xl border bg-card overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12"></TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead className="hidden md:table-cell">Категория</TableHead>
                  <TableHead className="hidden sm:table-cell">Бренд</TableHead>
                  <TableHead>Цена</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead className="w-20 text-right">Действия</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="py-16 text-center text-muted-foreground">
                      {search ? "Ничего не найдено" : "Товаров пока нет"}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredProducts.map((product) => (
                    <TableRow key={product.id}>
                      <TableCell>
                        <div className="relative size-10 overflow-hidden rounded-lg bg-muted/50">
                          {product.images[0] ? (
                            <Image
                              src={product.images[0].image_url}
                              alt={product.name}
                              fill
                              sizes="40px"
                              className="object-contain p-1"
                            />
                          ) : (
                            <div className="flex size-full items-center justify-center">
                              <Package className="size-4 text-muted-foreground/40" />
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <p className="font-medium line-clamp-1">{product.name}</p>
                        <p className="text-xs text-muted-foreground">{product.id.slice(0, 8)}…</p>
                      </TableCell>
                      <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                        {product.category_id ? (catMap[product.category_id] ?? "—") : "—"}
                      </TableCell>
                      <TableCell className="hidden sm:table-cell text-sm text-muted-foreground">
                        {product.brand_id ? (brandMap[product.brand_id] ?? "—") : "—"}
                      </TableCell>
                      <TableCell className="font-medium">
                        {formatPrice(parseFloat(product.price))}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={product.status} />
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8 rounded-lg"
                            title={product.status === "active" ? "В архив" : "Активировать"}
                            disabled={togglingId === product.id}
                            onClick={() => handleToggleStatus(product)}
                          >
                            {togglingId === product.id ? (
                              <Loader2 className="size-4 animate-spin" />
                            ) : product.status === "active" ? (
                              <ToggleRight className="size-4 text-green-600" />
                            ) : (
                              <ToggleLeft className="size-4 text-muted-foreground" />
                            )}
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8 rounded-lg text-destructive hover:bg-destructive/10"
                            disabled={deletingId === product.id}
                            onClick={() => handleDeleteProduct(product.id)}
                          >
                            {deletingId === product.id ? (
                              <Loader2 className="size-4 animate-spin" />
                            ) : (
                              <Trash2 className="size-4" />
                            )}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {filteredProducts.length > 0 && (
            <p className="mt-3 text-sm text-muted-foreground">
              Показано {filteredProducts.length} из {products.length} товаров
            </p>
          )}
        </TabsContent>

        <TabsContent value="categories">
          <div className="mb-6 max-w-md">
            <p className="mb-2 text-sm font-medium">Добавить категорию</p>
            <SimpleCreateForm
              label="Название"
              placeholder="Например: Телевизоры"
              onSubmit={handleCreateCategory}
              loading={false}
            />
          </div>
          <div className="rounded-2xl border bg-card overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Название</TableHead>
                  <TableHead className="hidden sm:table-cell">Slug</TableHead>
                  <TableHead className="hidden md:table-cell">ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {categories.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="py-10 text-center text-muted-foreground">Категорий нет</TableCell>
                  </TableRow>
                ) : (
                  categories.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>
                        <InlineEditRow
                          value={c.name}
                          linkedCount={products.filter((p) => p.category_id === c.id).length}
                          onSave={(name) => handleUpdateCategory(c.id, name)}
                          onDelete={() => handleDeleteCategory(c.id, c.name)}
                          saving={savingCatId === c.id}
                          deleting={deletingCatId === c.id}
                        />
                      </TableCell>
                      <TableCell className="hidden sm:table-cell font-mono text-sm text-muted-foreground">{c.slug}</TableCell>
                      <TableCell className="hidden md:table-cell font-mono text-xs text-muted-foreground">{c.id.slice(0, 8)}…</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        <TabsContent value="brands">
          <div className="mb-6 max-w-md">
            <p className="mb-2 text-sm font-medium">Добавить бренд</p>
            <SimpleCreateForm
              label="Название"
              placeholder="Например: Samsung"
              onSubmit={handleCreateBrand}
              loading={false}
            />
          </div>
          <div className="rounded-2xl border bg-card overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Название</TableHead>
                  <TableHead className="hidden sm:table-cell">Slug</TableHead>
                  <TableHead className="hidden md:table-cell">ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {brands.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="py-10 text-center text-muted-foreground">Брендов нет</TableCell>
                  </TableRow>
                ) : (
                  brands.map((b) => (
                    <TableRow key={b.id}>
                      <TableCell>
                        <InlineEditRow
                          value={b.name}
                          linkedCount={products.filter((p) => p.brand_id === b.id).length}
                          onSave={(name) => handleUpdateBrand(b.id, name)}
                          onDelete={() => handleDeleteBrand(b.id, b.name)}
                          saving={savingBrandId === b.id}
                          deleting={deletingBrandId === b.id}
                        />
                      </TableCell>
                      <TableCell className="hidden sm:table-cell font-mono text-sm text-muted-foreground">{b.slug}</TableCell>
                      <TableCell className="hidden md:table-cell font-mono text-xs text-muted-foreground">{b.id.slice(0, 8)}…</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>

      <Dialog open={createProductOpen} onOpenChange={setCreateProductOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Новый товар</DialogTitle>
          </DialogHeader>
          <ProductForm
            categories={categories}
            brands={brands}
            onSubmit={handleCreateProduct}
            loading={createLoading}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
