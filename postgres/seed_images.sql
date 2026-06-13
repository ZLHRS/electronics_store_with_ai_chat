
INSERT INTO product_images (id, product_id, image_url, sort_order)
SELECT gen_random_uuid(), p.id, v.image_url, 0
FROM products p
JOIN (VALUES
  ('edgepro-ultrabook-15',    '/products/laptop.png'),
  ('aurora-pro-16-m4',        '/products/laptop.png'),
  ('edgepro-creator-14',      '/products/laptop.png'),
  ('aurora-air-15',           '/products/laptop.png'),

  ('nova-lite-5g',            '/products/smartphone.png'),
  ('nova-ultra-5g',           '/products/smartphone.png'),
  ('nova-s30',                '/products/smartphone.png'),
  ('nova-fold-3',             '/products/smartphone.png'),

  ('vizor-pro-27-4k',         '/products/monitor.png'),
  ('vizor-game-32-165hz',     '/products/monitor.png'),
  ('edgepro-view-24',         '/products/monitor.png'),
  ('vizor-ultra-34-curved',   '/products/monitor.png'),
  ('vizor-studio-27-2k',      '/products/monitor.png'),

  ('vizor-smart-55-4k',       '/products/tv.png'),
  ('vizor-oled-65',           '/products/tv.png'),
  ('vizor-smart-43',          '/products/tv.png'),
  ('edgepro-tv-50-neo',       '/products/tv.png'),
  ('vizor-neo-75-8k',         '/products/tv.png'),

  ('lensmark-x100',           '/products/camera.png'),
  ('lensmark-vlog-4k',        '/products/camera.png'),
  ('orbcam-drone-4k',         '/products/camera.png'),
  ('lensmark-action-360',     '/products/camera.png'),
  ('orbcam-studio-kit',       '/products/camera.png'),

  ('keymaster-pro-mech-60',   '/products/keyboard.png'),
  ('keymaster-glidex-pro',    '/products/keyboard.png'),
  ('click-streamdeck-xl',     '/products/keyboard.png'),
  ('keymaster-ergomouse',     '/products/keyboard.png'),
  ('keymaster-pad-xxl',       '/products/keyboard.png'),
  ('click-webcam-4k',         '/products/keyboard.png'),

  ('voxair-pro-anc',          '/products/headphones.png'),
  ('soundwave-bar-51',        '/products/speaker.png'),
  ('voxair-buds-pro-2',       '/products/headphones.png'),
  ('boombox-outdoor-xl',      '/products/speaker.png'),
  ('voxair-studio-monitor',   '/products/speaker.png'),

  ('pulse-band-6-pro',        '/products/smartwatch.png'),
  ('pulse-air-watch-ultra-2', '/products/smartwatch.png'),
  ('swiftfit-ring',           '/products/smartwatch.png'),
  ('pulse-earfit-sport-2',    '/products/smartwatch.png'),

  ('aquacool-air-purifier',   '/products/vacuum.png'),
  ('cleanbot-ultra-z20',      '/products/vacuum.png'),
  ('aquacool-humidifier-5l',  '/products/vacuum.png'),
  ('aquacool-water-purifier', '/products/vacuum.png'),

  ('novasmart-hub-pro',       '/products/smart-home.png'),
  ('novasmart-cam-4k',        '/products/smart-home.png'),
  ('novasmart-doorbell',      '/products/smart-home.png'),
  ('novasmart-sensor-pack',   '/products/smart-home.png'),
  ('novasmart-light-strip',   '/products/smart-home.png'),

  ('slate-pro-13',            '/products/tablet.png'),
  ('slate-mini-8',            '/products/tablet.png'),
  ('framepro-tab-artist',     '/products/tablet.png'),

  ('playbox-titan-2',         '/products/console.png'),
  ('playbox-portable',        '/products/console.png'),
  ('keymaster-racing-wheel',  '/products/keyboard.png'),
  ('click-vr-headset-pro-2',  '/products/gaming-pc.png')
) AS v(slug, image_url) ON v.slug = p.slug
ON CONFLICT DO NOTHING;

SELECT COUNT(*) AS images_inserted FROM product_images;
