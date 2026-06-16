import json
import urllib.request
import urllib.parse
import http.cookiejar

BASE = "http://localhost"

CATEGORIES = [
    {"name": "Ноутбуки", "slug": "laptops"},
    {"name": "Смартфоны", "slug": "smartphones"},
    {"name": "Аудио", "slug": "audio"},
    {"name": "Игры", "slug": "gaming"},
    {"name": "Планшеты", "slug": "tablets"},
    {"name": "Для дома", "slug": "home"},
    {"name": "Фото", "slug": "photo"},
    {"name": "Гаджеты", "slug": "wearables"},
]

BRANDS = [
    {"name": "Aurora", "slug": "aurora"},
    {"name": "Nova", "slug": "nova"},
    {"name": "SoundWave", "slug": "soundwave"},
    {"name": "Titan", "slug": "titan"},
    {"name": "Pulse", "slug": "pulse"},
    {"name": "Slate", "slug": "slate"},
    {"name": "PlayBox", "slug": "playbox"},
    {"name": "CleanBot", "slug": "cleanbot"},
    {"name": "Click", "slug": "click"},
    {"name": "FramePro", "slug": "framepro"},
    {"name": "BoomBox", "slug": "boombox"},
]

PRODUCTS = [
    {"name":"Ноутбук Aurora Air 13 M3 256GB","slug":"macbook-air-m3","price":"389990.00","description":"Ультратонкий ноутбук с чипом M3, безвентиляторным дизайном и временем работы до 18 часов.","category_slug":"laptops","brand_slug":"aurora","status":"active","images":[{"image_url":"/products/laptop.png","sort_order":0}],"attributes":[{"name":"Процессор","value":"Aurora M3, 8 ядер"},{"name":"Память","value":"16 ГБ"},{"name":"Накопитель","value":"256 ГБ SSD"},{"name":"Экран","value":"13.6\" Liquid Retina"},{"name":"Автономность","value":"до 18 часов"}]},
    {"name":"Смартфон Nova Pro Max 256GB","slug":"phone-pro-max","price":"549990.00","description":"Флагманский смартфон с титановым корпусом, тройной камерой 48 Мп.","category_slug":"smartphones","brand_slug":"nova","status":"active","images":[{"image_url":"/products/smartphone.png","sort_order":0}],"attributes":[{"name":"Экран","value":"6.7\" OLED 120 Гц"},{"name":"Процессор","value":"Nova A18 Pro"},{"name":"Камера","value":"48 + 12 + 12 Мп"},{"name":"Защита","value":"IP68"}]},
    {"name":"Наушники SoundWave Max ANC","slug":"headphones-max","price":"179990.00","description":"Беспроводные наушники с активным шумоподавлением и автономностью до 40 часов.","category_slug":"audio","brand_slug":"soundwave","status":"active","images":[{"image_url":"/products/headphones.png","sort_order":0}],"attributes":[{"name":"Шумоподавление","value":"Активное (ANC)"},{"name":"Автономность","value":"до 40 часов"},{"name":"Подключение","value":"Bluetooth 5.3"}]},
    {"name":"Игровой ПК Titan RTX 4070 32GB","slug":"gaming-pc-rtx","price":"899990.00","description":"Мощный игровой компьютер для 2K и 4K игр. Видеокарта RTX 4070, 32 ГБ памяти.","category_slug":"gaming","brand_slug":"titan","status":"active","images":[{"image_url":"/products/gaming-pc.png","sort_order":0}],"attributes":[{"name":"Видеокарта","value":"RTX 4070 12 ГБ"},{"name":"Память","value":"32 ГБ DDR5"},{"name":"Накопитель","value":"1 ТБ NVMe SSD"}]},
    {"name":"Часы Pulse Watch Ultra 49mm","slug":"smartwatch-ultra","price":"299990.00","description":"Защищённые смарт-часы с GPS, мониторингом здоровья и автономностью до 36 часов.","category_slug":"wearables","brand_slug":"pulse","status":"active","images":[{"image_url":"/products/smartwatch.png","sort_order":0}],"attributes":[{"name":"Корпус","value":"49 мм, титан"},{"name":"Защита","value":"10 ATM, MIL-STD"},{"name":"Датчики","value":"ЭКГ, SpO2, GPS"}]},
    {"name":"Планшет Slate Pro 11 128GB","slug":"tablet-pro","price":"329990.00","description":"Универсальный планшет с поддержкой стилуса и производительностью настольного уровня.","category_slug":"tablets","brand_slug":"slate","status":"active","images":[{"image_url":"/products/tablet.png","sort_order":0}],"attributes":[{"name":"Экран","value":"11\" Liquid Retina 120 Гц"},{"name":"Память","value":"128 ГБ"},{"name":"Стилус","value":"Slate Pencil"}]},
    {"name":"Игровая консоль PlayBox X 1TB","slug":"console-x","price":"269990.00","description":"Игровая консоль нового поколения с поддержкой 4K 120 fps и быстрым SSD.","category_slug":"gaming","brand_slug":"playbox","status":"active","images":[{"image_url":"/products/console.png","sort_order":0}],"attributes":[{"name":"Накопитель","value":"1 ТБ SSD"},{"name":"Разрешение","value":"до 4K 120 fps"},{"name":"Поддержка","value":"Ray Tracing"}]},
    {"name":"Робот-пылесос CleanBot Z10","slug":"robot-vacuum","price":"159990.00","description":"Умный робот-пылесос с лазерной навигацией, влажной уборкой и станцией самоочистки.","category_slug":"home","brand_slug":"cleanbot","status":"active","images":[{"image_url":"/products/vacuum.png","sort_order":0}],"attributes":[{"name":"Навигация","value":"Лазерный LiDAR"},{"name":"Мощность","value":"5000 Па"},{"name":"Уборка","value":"Сухая + влажная"}]},
    {"name":"Клавиатура Click TKL RGB","slug":"keyboard-mech","price":"49990.00","description":"Механическая игровая клавиатура с горячей заменой переключателей.","category_slug":"gaming","brand_slug":"click","status":"active","images":[{"image_url":"/products/keyboard.png","sort_order":0}],"attributes":[{"name":"Форм-фактор","value":"TKL (87 клавиш)"},{"name":"Подсветка","value":"RGB по клавишам"},{"name":"Подключение","value":"USB-C, Bluetooth"}]},
    {"name":"Камера FramePro X 24Mp","slug":"camera-mirrorless","price":"749990.00","description":"Беззеркальная камера для профессионалов с матрицей 24 Мп и съёмкой 4K.","category_slug":"photo","brand_slug":"framepro","status":"archived","images":[{"image_url":"/products/camera.png","sort_order":0}],"attributes":[{"name":"Матрица","value":"24 Мп, полный кадр"},{"name":"Видео","value":"4K 60 fps"},{"name":"Автофокус","value":"759 точек"}]},
    {"name":"Колонка BoomBox Go","slug":"speaker-portable","price":"64990.00","description":"Портативная влагозащищённая колонка с глубоким басом и автономностью до 24 часов.","category_slug":"audio","brand_slug":"boombox","status":"active","images":[{"image_url":"/products/speaker.png","sort_order":0}],"attributes":[{"name":"Мощность","value":"30 Вт"},{"name":"Защита","value":"IP67"},{"name":"Подключение","value":"Bluetooth 5.3"}]},
    {"name":"Ноутбук Aurora Pro 16 M3 Max","slug":"laptop-pro-16","price":"1299990.00","description":"Профессиональный ноутбук с чипом M3 Max для монтажа, 3D и разработки.","category_slug":"laptops","brand_slug":"aurora","status":"active","images":[{"image_url":"/products/laptop.png","sort_order":0}],"attributes":[{"name":"Процессор","value":"Aurora M3 Max, 16 ядер"},{"name":"Память","value":"48 ГБ"},{"name":"Накопитель","value":"1 ТБ SSD"}]},
]


def api(opener, method, path, data=None):
    url = BASE + path
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

status, data = api(opener, "POST", "/api/v1/login", {"email": "admin@shop.kz", "password": "Admin123456"})
print(f"Login: {status}")

cat_map = {}
print("\n--- Categories ---")
for cat in CATEGORIES:
    s, d = api(opener, "POST", "/api/v1/categories", cat)
    if s in (200, 201):
        cat_map[cat["slug"]] = d["id"]
        print(f"  ✓ {cat['name']}")
    elif s == 409:
        s2, d2 = api(opener, "GET", "/api/v1/categories")
        for c in d2:
            if c["slug"] == cat["slug"]:
                cat_map[cat["slug"]] = c["id"]
        print(f"  ~ {cat['name']} exists")
    else:
        print(f"  ✗ {cat['name']}: {s} {d}")

brand_map = {}
print("\n--- Brands ---")
for brand in BRANDS:
    s, d = api(opener, "POST", "/api/v1/brands", brand)
    if s in (200, 201):
        brand_map[brand["slug"]] = d["id"]
        print(f"  ✓ {brand['name']}")
    elif s == 409:
        s2, d2 = api(opener, "GET", "/api/v1/brands")
        for b in d2:
            if b["slug"] == brand["slug"]:
                brand_map[brand["slug"]] = b["id"]
        print(f"  ~ {brand['name']} exists")
    else:
        print(f"  ✗ {brand['name']}: {s} {d}")

print("\n--- Products ---")
for p in PRODUCTS:
    payload = {
        "name": p["name"],
        "slug": p["slug"],
        "price": p["price"],
        "description": p["description"],
        "category_id": cat_map.get(p["category_slug"]),
        "brand_id": brand_map.get(p["brand_slug"]),
        "status": p["status"],
        "images": p["images"],
        "attributes": p["attributes"],
    }
    s, d = api(opener, "POST", "/api/v1/products", payload)
    if s in (200, 201):
        print(f"  ✓ {p['name']}")
    elif s == 409:
        print(f"  ~ {p['name']} exists")
    else:
        print(f"  ✗ {p['name']}: {s} {str(d)[:150]}")

print("\nDone!")
