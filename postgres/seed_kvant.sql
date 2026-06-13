
INSERT INTO products (id, name, slug, description, price, category_id, brand_id, status, created_at, updated_at)
SELECT gen_random_uuid(), p.name, p.slug, p.description, p.price,
       c.id AS category_id, b.id AS brand_id,
       'active', NOW(), NOW()
FROM (VALUES

  -- НОУТБУКИ
  ('EdgePro UltraBook 15 i7',    'edgepro-ultrabook-15',    'Тонкий алюминиевый ноутбук с Intel Core i7-13700H, 16 ГБ DDR5, 512 ГБ NVMe SSD. Дисплей 15,6" IPS FHD 144 Гц. Автономность до 14 ч.',                 649990.00::numeric, 'laptops',  'EdgePro'),
  ('Aurora Pro 16 M4 Pro',       'aurora-pro-16-m4',        'Профессиональный ноутбук на чипе Apple M4 Pro с 12-ядерным CPU. 16" Liquid Retina XDR, 24 ГБ RAM, 1 ТБ SSD. Идеален для разработки и монтажа.', 1499990.00::numeric, 'laptops',  'Aurora'),
  ('EdgePro Creator 14 OLED',    'edgepro-creator-14',      'Ноутбук для творческих задач: OLED 2.8K 120 Гц, Intel i7, 32 ГБ RAM, RTX 4060. Охватывает 100% DCI-P3.',                                           899990.00::numeric, 'laptops',  'EdgePro'),
  ('Aurora Air 15 M3 512GB',     'aurora-air-15',           'Лёгкий ноутбук весом 1,5 кг с M3, 18 ГБ памяти, 512 ГБ SSD. Матрица 15,3" 2880x1864. Автономность до 22 ч.',                                      549990.00::numeric, 'laptops',  'Aurora'),

  -- СМАРТФОНЫ
  ('Nova Lite 5G 128GB',         'nova-lite-5g',            'Доступный смартфон с 5G, Snapdragon 6s, 6,6" AMOLED 90 Гц, тройной камерой 50 Мп. Батарея 5000 мАч.',                                              199990.00::numeric, 'smartphones', 'Nova'),
  ('Nova Ultra 5G 512GB',        'nova-ultra-5g',           'Флагман Snapdragon 8 Gen 3, 12 ГБ RAM. Экран 6,8" LTPO AMOLED 120 Гц. Камера 200 Мп с оптикой.',                                                  799990.00::numeric, 'smartphones', 'Nova'),
  ('Nova S30 256GB',             'nova-s30',                'Смартфон среднего класса: Dimensity 9200, 8 ГБ RAM, 6,7" Super AMOLED. Быстрая зарядка 67 Вт. Камера 108 Мп.',                                     349990.00::numeric, 'smartphones', 'Nova'),
  ('Nova Fold 3 256GB',          'nova-fold-3',             'Складной смартфон с гибким AMOLED 7,6" внутри и 6,2" снаружи. Snapdragon 8 Gen 3, 12 ГБ RAM, IPX8.',                                             1099990.00::numeric, 'smartphones', 'Nova'),

  -- МОНИТОРЫ
  ('Vizor Pro 27 4K IPS',        'vizor-pro-27-4k',         'Профессиональный монитор 27", 3840x2160, IPS, 144 Гц, HDR600. Охватывает 99% Adobe RGB. USB-C 90 Вт, KVM.',                                        249990.00::numeric, 'monitors', 'Vizor'),
  ('Vizor Game 32 165Hz',        'vizor-game-32-165hz',     'Игровой монитор 32", VA 2K QHD, 165 Гц, 1 мс MPRT. AMD FreeSync Premium. Изогнутость 1500R. HDMI 2.1.',                                           199990.00::numeric, 'monitors', 'Vizor'),
  ('EdgePro View 24 IPS',        'edgepro-view-24',         'Бюджетный IPS монитор 24", FHD 1080p, 75 Гц. Без бликов, синий фильтр, регулировка высоты. USB-C хаб.',                                           129990.00::numeric, 'monitors', 'EdgePro'),
  ('Vizor Ultra 34 Curved',      'vizor-ultra-34-curved',   'Ультраширокий изогнутый монитор 34", UWQHD 3440x1440, IPS 160 Гц, HDR400. KVM, 2 x USB-C 96 Вт.',                                                 349990.00::numeric, 'monitors', 'Vizor'),
  ('Vizor Studio 27 2K',         'vizor-studio-27-2k',      'Монитор для дизайнеров 27", QHD 2560x1440, IPS 75 Гц. Заводская калибровка deltaE < 2. Высота и наклон регулируются.',                            179990.00::numeric, 'monitors', 'Vizor'),

  -- ТЕЛЕВИЗОРЫ
  ('Vizor Smart TV 55 4K',       'vizor-smart-55-4k',       '55" QLED 4K Smart TV на Android TV. 120 Гц, Dolby Vision, HDR10+, 4 x HDMI 2.1. Голосовое управление.',                                           299990.00::numeric, 'tvs', 'Vizor'),
  ('Vizor OLED 65 4K',           'vizor-oled-65',           'Флагманский 65" OLED 4K 120 Гц. Pixel Dimming, Dolby Atmos, 4 x HDMI 2.1. Бесконечный контраст.',                                                  699990.00::numeric, 'tvs', 'Vizor'),
  ('Vizor Smart TV 43',          'vizor-smart-43',          'Компактный 43" 4K Smart TV. Wi-Fi 6, Bluetooth 5.2, ARC, три HDMI. Встроенный Google TV.',                                                          169990.00::numeric, 'tvs', 'Vizor'),
  ('EdgePro TV 50 Neo QLED',     'edgepro-tv-50-neo',       '50" Neo QLED 4K 144 Гц. Mini-LED, 2000 зон диминга. Quantum HDR 2000. Gaming TV с ALLM и VRR.',                                                    399990.00::numeric, 'tvs', 'EdgePro'),
  ('Vizor Neo 75 8K',            'vizor-neo-75-8k',         'Флагманский 75" 8K QLED Smart TV. AI Upscaling, 144 Гц, 60 Вт аудио. Тонкий One Connect Box.',                                                   1299990.00::numeric, 'tvs', 'Vizor'),

  -- ФОТО И ВИДЕО
  ('LensMark X100 Mirrorless',   'lensmark-x100',           'Беззеркальная камера APS-C 40 Мп, объектив 23mm f/2. Запись 4K 60fps, IBIS, электронный затвор. Wi-Fi, Bluetooth.',                                 599990.00::numeric, 'photo', 'LensMark'),
  ('LensMark Vlog 4K Pro',       'lensmark-vlog-4k',        'Влог-камера 4K 120fps, сенсор 1", OIS, откидной экран 3". Три микрофона, ND-фильтры, Log-запись.',                                                  249990.00::numeric, 'photo', 'LensMark'),
  ('OrbCam Drone 4K Mini',       'orbcam-drone-4k',         'Компактный дрон 4K с 3-осевым гимбалом, дальностью 12 км, временем полёта 46 мин. Автоматические треки.',                                           399990.00::numeric, 'photo', 'OrbCam'),
  ('LensMark Action Pro 360',    'lensmark-action-360',     'Экшн-камера 5K с 360-режимом, водозащита до 18 м. HorizonSteady, голосовое управление, магнитное крепление.',                                       149990.00::numeric, 'photo', 'LensMark'),
  ('OrbCam Studio Kit',          'orbcam-studio-kit',       'Набор для съёмки: камера 24 Мп + кольцевая LED лампа 48 см + штатив 2 м. Для блогеров и стримеров.',                                               189990.00::numeric, 'photo', 'OrbCam'),

  -- ПЕРИФЕРИЯ
  ('KeyMaster Pro Mech 60',      'keymaster-pro-mech-60',   'Механическая клавиатура 60% с Red переключателями, RGB подсветка, алюминиевый корпус. Hot-swap. Кабель USB-C.',                                       89990.00::numeric, 'peripherals', 'KeyMaster'),
  ('KeyMaster GlideX Pro Mouse', 'keymaster-glidex-pro',    'Игровая мышь 26000 DPI, PAW3395 сенсор. Беспроводная 2.4 ГГц + Bluetooth. Вес 58 г. Зарядная станция.',                                             49990.00::numeric, 'peripherals', 'KeyMaster'),
  ('Click StreamDeck XL',        'click-streamdeck-xl',     '32 программируемых LCD-клавиши для стримов. USB-C, совместим с OBS, YouTube, Spotify. Регулируемая подставка.',                                       79990.00::numeric, 'peripherals', 'Click'),
  ('KeyMaster ErgoMouse Pro',    'keymaster-ergomouse',     'Вертикальная эргономичная мышь, регулируемый DPI до 16000, бесшумные клики. Беспроводная, 70 ч работы.',                                              59990.00::numeric, 'peripherals', 'KeyMaster'),
  ('KeyMaster Pad XXL Desk',     'keymaster-pad-xxl',       'Коврик для стола 900x400x4 мм с RGB окантовкой. Тканевая поверхность Speed. Нескользящая основа.',                                                    29990.00::numeric, 'peripherals', 'KeyMaster'),
  ('Click WebCam 4K Studio',     'click-webcam-4k',         'Веб-камера 4K 30fps, автофокус, встроенный микрофон с шумоподавлением. HDR, поле зрения 90 градусов.',                                               69990.00::numeric, 'peripherals', 'Click'),

  -- АУДИО
  ('VoxAir Pro ANC',             'voxair-pro-anc',          'Накладные наушники с гибридным ANC, Hi-Res Audio, 30 ч автономности. LDAC, aptX HD. Складная конструкция, кейс.',                                    129990.00::numeric, 'audio', 'VoxAir'),
  ('SoundWave Bar 5.1',          'soundwave-bar-51',        'Саундбар 5.1 с беспроводным сабвуфером и тыловыми колонками. Dolby Atmos, DTS:X. 500 Вт, HDMI ARC, Wi-Fi.',                                         299990.00::numeric, 'audio', 'SoundWave'),
  ('VoxAir Buds Pro 2',          'voxair-buds-pro-2',       'TWS наушники с ANC -42 дБ, 6 ч + 30 ч от кейса. Spatial Audio, IP54, быстрая зарядка 5 мин = 1 ч.',                                                 79990.00::numeric, 'audio', 'VoxAir'),
  ('BoomBox Outdoor XL',         'boombox-outdoor-xl',      'Портативная колонка 80 Вт, IPX5, Bluetooth 5.3. Стереозвук 360 градусов, LED-подсветка, 24 ч работы. Карабин.',                                     149990.00::numeric, 'audio', 'BoomBox'),
  ('VoxAir Studio Monitor 5',    'voxair-studio-monitor',   'Студийные мониторы 5" ближнего поля. 70 Вт/пара, АЧХ 45 Гц - 35 кГц. Балансный XLR/TRS вход. USB подключение.',                                   199990.00::numeric, 'audio', 'VoxAir'),

  -- ГАДЖЕТЫ/WEARABLES
  ('Pulse Band 6 Pro',           'pulse-band-6-pro',        'Фитнес-браслет с AMOLED дисплеем, GPS, ЭКГ, SpO2 и ЧСС. 14 дней без подзарядки. 100+ режимов тренировок.',                                          89990.00::numeric, 'wearables', 'Pulse'),
  ('Pulse Air Watch Ultra 2',    'pulse-air-watch-ultra-2', 'Умные часы titanium корпус, Always-On OLED, GPS + GLONASS. Карты оплаты, ЭКГ, термометр. Автономность 3 суток.',                                   199990.00::numeric, 'wearables', 'Pulse'),
  ('SwiftFit Ring Sensor',       'swiftfit-ring',           'Умное кольцо: отслеживает сон, пульс, SpO2 и температуру тела. Размеры 6-13. IP68, 7 дней работы. Titanium.',                                        99990.00::numeric, 'wearables', 'SwiftFit'),
  ('Pulse EarFit Sport 2',       'pulse-earfit-sport-2',    'Спортивные TWS наушники со встроенным пульсометром. IP55, 8 ч + 24 ч от кейса. BT 5.3.',                                                             69990.00::numeric, 'wearables', 'Pulse'),

  -- ДЛЯ ДОМА
  ('AquaCool Air Purifier Pro',  'aquacool-air-purifier',   'Очиститель воздуха HEPA H13 + угольный фильтр. Площадь 50 м2, PM2.5 датчик, тихий режим 24 дБ, управление со смартфона.',                           129990.00::numeric, 'home', 'AquaCool'),
  ('CleanBot Ultra Z20',         'cleanbot-ultra-z20',      'Робот-пылесос 7500 Па с лазерным лидаром, мойкой пола, станцией самоочистки. Работает 180 мин, площадь 300 м2.',                                     249990.00::numeric, 'home', 'CleanBot'),
  ('AquaCool Humidifier 5L',     'aquacool-humidifier-5l',  'Ультразвуковой увлажнитель 5 л, ультратихий, ионизация, авторежим по влажности. Подходит для комнаты 45 м2.',                                         89990.00::numeric, 'home', 'AquaCool'),
  ('AquaCool Water Purifier',    'aquacool-water-purifier', 'Обратноосмотический фильтр 6 ступеней с минерализацией. 400 л/сутки. Встроенный насос, Wi-Fi модуль.',                                               169990.00::numeric, 'home', 'AquaCool'),

  -- УМНЫЙ ДОМ
  ('NovaSmart Hub Pro',          'novasmart-hub-pro',       'Центр умного дома: Matter, Zigbee, Z-Wave, Wi-Fi 6, Bluetooth 5. Совместим с Алисой, Google Home, HomeKit.',                                          99990.00::numeric, 'smart-home', 'NovaSmart'),
  ('NovaSmart Camera 4K',        'novasmart-cam-4k',        'Уличная камера 4K с ИИ-детекцией людей, авто-прожектором, двусторонним звуком. IP66, работает при -40 градусах.',                                     79990.00::numeric, 'smart-home', 'NovaSmart'),
  ('NovaSmart Video Doorbell',   'novasmart-doorbell',      'Умный звонок 2K, обнаружение пакетов и лиц. Встроенная батарея. Мгновенные push-уведомления. IPX4.',                                                  69990.00::numeric, 'smart-home', 'NovaSmart'),
  ('NovaSmart Sensor Pack 5in1', 'novasmart-sensor-pack',   'Набор 5 датчиков: движение, открытие двери, дым, CO, утечка воды. Zigbee 3.0, работает 2 года от батарейки.',                                         49990.00::numeric, 'smart-home', 'NovaSmart'),
  ('NovaSmart Light Strip 5m',   'novasmart-light-strip',   'Умная RGB лента 5 м, 2500+ цветов, 2700-6500K. Музыкальный режим, сценарии, голосовое управление.',                                                   29990.00::numeric, 'smart-home', 'NovaSmart'),

  -- ПЛАНШЕТЫ
  ('Slate Pro 13 256GB',         'slate-pro-13',            'Планшет 13" OLED 2K 120 Гц, Snapdragon 8s Gen 3, 12 ГБ RAM, 256 ГБ. Стилус Slate Pen 2 в комплекте. DeX-режим.',                                   449990.00::numeric, 'tablets', 'Slate'),
  ('Slate Mini 8 128GB',         'slate-mini-8',            'Компактный планшет 8,4" AMOLED, Snapdragon 6 Gen 1, 6 ГБ RAM. Тонкий 5,5 мм, вес 262 г.',                                                          199990.00::numeric, 'tablets', 'Slate'),
  ('FramePro Tab Artist 12',     'framepro-tab-artist',     'Планшет для художников 12" 2K, 8192 уровней чувствительности пера, 144 Гц. 99% sRGB, 16 ГБ RAM.',                                                   349990.00::numeric, 'tablets', 'FramePro'),

  -- ИГРЫ
  ('PlayBox Titan 2 Console',    'playbox-titan-2',         'Игровая консоль 4K 120fps, SSD 2 ТБ, трассировка лучей. Обратная совместимость. Геймпад с адаптивными триггерами.',                                  399990.00::numeric, 'gaming', 'PlayBox'),
  ('PlayBox Portable Mini',      'playbox-portable',        'Портативная консоль 7" OLED 120 Гц, 256 ГБ, 8 ч игры. Съёмные контроллеры, режим TV через USB-C. Wi-Fi 6.',                                         199990.00::numeric, 'gaming', 'PlayBox'),
  ('KeyMaster Racing Wheel Pro', 'keymaster-racing-wheel',  'Руль 900 градусов вращения, силовая обратная связь 8 Нм, педали с нагрузкой. ПК + консоли. Металлический каркас.',                                   149990.00::numeric, 'gaming', 'KeyMaster'),
  ('Click VR Headset Pro 2',     'click-vr-headset-pro-2',  'Автономная VR-гарнитура 4K pancake линзы, 120 Гц, отслеживание рук без контроллеров. 128 ГБ, Wi-Fi 6E.',                                            299990.00::numeric, 'gaming', 'Click')

) AS p(name, slug, description, price, cat_slug, brand_name)
JOIN categories c ON c.slug = p.cat_slug
JOIN brands b ON b.name = p.brand_name
ON CONFLICT (slug) DO NOTHING;

SELECT COUNT(*) AS total_products FROM products;
