#!/bin/bash
# Initialize Trillian database schema
# Using $mysql_flags provided by SCLORG container scripts
echo "==> Initializing Trillian database schema..."
echo "==> APP_DATA=${APP_DATA}"
echo "==> MYSQL_DATABASE=${MYSQL_DATABASE}"
echo "==> Loading SQL from: ${APP_DATA}/mysql-init/initdb.sql"

if [ -f "${APP_DATA}/mysql-init/initdb.sql" ]; then
    mysql $mysql_flags $MYSQL_DATABASE < ${APP_DATA}/mysql-init/initdb.sql
    echo "==> Trillian database schema initialized successfully"
else
    echo "==> ERROR: SQL file not found at ${APP_DATA}/mysql-init/initdb.sql"
    ls -la ${APP_DATA}/mysql-init/ || echo "==> Cannot list directory"
    exit 1
fi
