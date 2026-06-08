export type DisplayCategory = {
  uuid: string
  slug: string
  name: string
  icon: string
}

type ApiCategory = { id: string; name: string; slug: string; parent_id: string | null }

const slugIconMap: Record<string, string> = {
  laptops: "Laptop",
  smartphones: "Smartphone",
  audio: "Headphones",
  gaming: "Gamepad2",
  tablets: "Tablet",
  home: "House",
  photo: "Camera",
  wearables: "Watch",
}

export async function fetchCategories(): Promise<DisplayCategory[]> {
  try {
    const res = await fetch("/api/v1/categories", { cache: "no-store" })
    if (!res.ok) return []
    const data: ApiCategory[] = await res.json()
    return data.map((c) => ({
      uuid: c.id,
      slug: c.slug,
      name: c.name,
      icon: slugIconMap[c.slug] ?? "Package",
    }))
  } catch {
    return []
  }
}
