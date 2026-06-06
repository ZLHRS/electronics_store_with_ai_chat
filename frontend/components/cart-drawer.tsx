"use client"

import Link from "next/link"
import Image from "next/image"
import { Minus, Plus, Trash2, ShoppingBag, ArrowRight } from "lucide-react"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetFooter,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Empty, EmptyHeader, EmptyMedia, EmptyTitle, EmptyDescription, EmptyContent } from "@/components/ui/empty"
import { useCart } from "@/components/cart-provider"
import { formatPrice } from "@/lib/data"

export function CartDrawer() {
  const { items, isOpen, setOpen, subtotal, setQty, remove, count } = useCart()
  const delivery = subtotal > 0 && subtotal < 300000 ? 2990 : 0

  return (
    <Sheet open={isOpen} onOpenChange={setOpen}>
      <SheetContent side="right" className="flex w-full flex-col gap-0 p-0 sm:max-w-md">
        <SheetHeader className="border-b">
          <SheetTitle className="flex items-center gap-2">
            <ShoppingBag className="size-5 text-primary" />
            Корзина
            {count > 0 && <span className="text-muted-foreground">· {count}</span>}
          </SheetTitle>
        </SheetHeader>

        {items.length === 0 ? (
          <Empty className="flex-1">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <ShoppingBag />
              </EmptyMedia>
              <EmptyTitle>Корзина пуста</EmptyTitle>
              <EmptyDescription>
                Добавьте товары или спросите AI-ассистента, что выбрать.
              </EmptyDescription>
            </EmptyHeader>
            <EmptyContent>
              <Button onClick={() => setOpen(false)} render={<Link href="/" />}>
                Перейти к покупкам
              </Button>
            </EmptyContent>
          </Empty>
        ) : (
          <>
            <ScrollArea className="flex-1">
              <div className="flex flex-col gap-4 p-4">
                {items.map((item) => (
                  <div key={item.product.id} className="flex gap-3">
                    <Link
                      href={`/product/${item.product.id}`}
                      onClick={() => setOpen(false)}
                      className="relative size-20 shrink-0 overflow-hidden rounded-xl bg-muted"
                    >
                      <Image
                        src={item.product.image || "/placeholder.svg"}
                        alt={item.product.name}
                        fill
                        sizes="80px"
                        className="object-contain p-2"
                      />
                    </Link>
                    <div className="flex flex-1 flex-col">
                      <p className="line-clamp-2 text-sm font-medium leading-snug">{item.product.name}</p>
                      <p className="mt-0.5 text-sm font-semibold">{formatPrice(item.product.price)}</p>
                      <div className="mt-auto flex items-center justify-between pt-2">
                        <div className="flex items-center rounded-full border">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8 rounded-full"
                            aria-label="Уменьшить"
                            onClick={() => setQty(item.product.id, item.qty - 1)}
                          >
                            <Minus className="size-3.5" />
                          </Button>
                          <span className="w-7 text-center text-sm tabular-nums">{item.qty}</span>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8 rounded-full"
                            aria-label="Увеличить"
                            onClick={() => setQty(item.product.id, item.qty + 1)}
                          >
                            <Plus className="size-3.5" />
                          </Button>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8 text-muted-foreground hover:text-destructive"
                          aria-label="Удалить"
                          onClick={() => remove(item.product.id)}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            <SheetFooter className="border-t">
              <div className="flex flex-col gap-2 text-sm">
                <div className="flex justify-between text-muted-foreground">
                  <span>Товары</span>
                  <span className="text-foreground">{formatPrice(subtotal)}</span>
                </div>
                <div className="flex justify-between text-muted-foreground">
                  <span>Доставка</span>
                  <span className="text-foreground">{delivery === 0 ? "Бесплатно" : formatPrice(delivery)}</span>
                </div>
                <Separator className="my-1" />
                <div className="flex justify-between text-base font-semibold">
                  <span>Итого</span>
                  <span>{formatPrice(subtotal + delivery)}</span>
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <Button size="lg" className="rounded-xl" onClick={() => setOpen(false)} render={<Link href="/checkout" />}>
                  Оформить заказ
                  <ArrowRight data-icon="inline-end" />
                </Button>
                <Button variant="outline" size="lg" className="rounded-xl" onClick={() => setOpen(false)} render={<Link href="/cart" />}>
                  Перейти в корзину
                </Button>
              </div>
            </SheetFooter>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
