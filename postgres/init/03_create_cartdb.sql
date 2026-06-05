SELECT 'CREATE DATABASE cartdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'cartdb')\gexec
