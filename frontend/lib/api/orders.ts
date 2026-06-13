export type ApiOrderStatus =
  | "created"
  | "pending_payment"
  | "paid"
  | "processing"
  | "shipped"
  | "delivered"
  | "cancelled"

export type FrontendOrderItem = {
  id: string
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
}

export type FrontendOrder = {
  id: string
  status: ApiOrderStatus
  total_amount: number
  delivery_address: string
  payment_method: string
  created_at: string
  items: FrontendOrderItem[]
}

type ApiOrderItem = {
  id: string
  order_id: string
  product_id: string
  product_name: string
  quantity: number
  unit_price: string
  total_price: string
}

type ApiOrder = {
  id: string
  user_id: string
  status: string
  total_amount: string
  delivery_address: string
  payment_method: string
  items: ApiOrderItem[]
  created_at: string
  updated_at: string
}

function adaptOrder(o: ApiOrder): FrontendOrder {
  return {
    id: o.id,
    status: o.status as ApiOrderStatus,
    total_amount: parseFloat(o.total_amount),
    delivery_address: o.delivery_address,
    payment_method: o.payment_method,
    created_at: o.created_at,
    items: o.items.map((i) => ({
      id: i.id,
      product_id: i.product_id,
      product_name: i.product_name,
      quantity: i.quantity,
      unit_price: parseFloat(i.unit_price),
      total_price: parseFloat(i.total_price),
    })),
  }
}

async function apiFetch<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(path, { cache: "no-store", credentials: "include" })
    if (!res.ok) return null
    return res.json() as Promise<T>
  } catch {
    return null
  }
}

export async function fetchOrders(): Promise<FrontendOrder[]> {
  const data = await apiFetch<ApiOrder[]>("/api/v1/orders")
  if (!data) return []
  return data.map(adaptOrder)
}

export async function fetchOrderById(id: string): Promise<FrontendOrder | null> {
  const data = await apiFetch<ApiOrder>(`/api/v1/orders/${id}`)
  if (!data) return null
  return adaptOrder(data)
}

export async function createOrder(
  deliveryAddress: string,
  paymentMethod: string,
): Promise<FrontendOrder | null> {
  try {
    const res = await fetch("/api/v1/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        delivery_address: deliveryAddress,
        payment_method: paymentMethod,
      }),
    })
    if (!res.ok) return null
    const data: ApiOrder = await res.json()
    return adaptOrder(data)
  } catch {
    return null
  }
}

export async function cancelOrder(id: string): Promise<FrontendOrder | null> {
  try {
    const res = await fetch(`/api/v1/orders/${id}/cancel`, {
      method: "PATCH",
      credentials: "include",
    })
    if (!res.ok) return null
    const data: ApiOrder = await res.json()
    return adaptOrder(data)
  } catch {
    return null
  }
}

const STATUS_STEPS: ApiOrderStatus[] = [
  "created",
  "pending_payment",
  "paid",
  "processing",
  "shipped",
  "delivered",
]

const STEP_LABELS: Record<string, string> = {
  created: "Заказ оформлен",
  paid: "Оплата подтверждена",
  processing: "В обработке",
  shipped: "Передан в доставку",
  delivered: "Доставлен",
}

export function buildTimeline(status: ApiOrderStatus): { label: string; done: boolean }[] {
  if (status === "cancelled") {
    return [
      { label: "Заказ оформлен", done: true },
      { label: "Отменён", done: true },
    ]
  }
  const currentIdx = STATUS_STEPS.indexOf(status)
  const visibleSteps: ApiOrderStatus[] = ["created", "paid", "processing", "shipped", "delivered"]
  return visibleSteps.map((step) => ({
    label: STEP_LABELS[step],
    done: STATUS_STEPS.indexOf(step) <= currentIdx,
  }))
}

export function formatOrderDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ru-RU", {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}
