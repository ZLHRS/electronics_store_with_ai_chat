SELECT 'CREATE DATABASE productdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'productdb')\gexec
