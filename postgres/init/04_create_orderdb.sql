SELECT 'CREATE DATABASE orderdb'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'orderdb')\gexec
