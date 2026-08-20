#!/bin/bash
# ContainerGuard Cloud Server Setup Script
# Run once on a fresh amla-agent-test / cloud server
# Usage: bash setup.sh

set -e

echo "=== ContainerGuard Cloud Setup ==="

# 1. Install PostgreSQL
echo "[1/6] Installing PostgreSQL..."
sudo dnf install -y postgresql-server postgresql

# 2. Initialize and start PostgreSQL
echo "[2/6] Initializing PostgreSQL..."
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql

# 3. Fix pg_hba.conf to use md5 (password) auth
echo "[3/6] Configuring pg_hba.conf for password auth..."
sudo sed -i 's/^local\s\+all\s\+all\s\+peer/local   all             all                                     md5/' /var/lib/pgsql/data/pg_hba.conf
sudo sed -i 's/^host\s\+all\s\+all\s\+127.0.0.1\/32\s\+ident/host    all             all             127.0.0.1\/32            md5/' /var/lib/pgsql/data/pg_hba.conf
sudo sed -i 's/::1\/128                 ident/::1\/128                 md5/' /var/lib/pgsql/data/pg_hba.conf
sudo systemctl restart postgresql

# 4. Create DB user and database
echo "[4/6] Creating database and user..."
sudo -u postgres createuser containerguard --no-superuser --no-createdb --no-createrole 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER containerguard WITH PASSWORD 'dev-password';" 2>/dev/null || true
sudo -u postgres createdb containerguard --owner=containerguard 2>/dev/null || true

# 5. Open firewall ports
echo "[5/6] Opening firewall ports..."
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=5173/tcp
sudo firewall-cmd --reload

# 6. Install Python dependencies
echo "[6/6] Installing cloud API dependencies..."
pip3 install -r ~/containerguard-v2/cloud/requirements.txt --user

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next: Register agent in DB (replace values as needed):"
echo "  psql -U containerguard -h localhost -d containerguard -c \\"
echo "    \"INSERT INTO agents (id, name, location, status, api_key) VALUES ('docker-worker', 'Docker Worker', 'docker-worker host', 'active', '<your-api-key>') ON CONFLICT (id) DO NOTHING;\""
echo "  psql -U containerguard -h localhost -d containerguard -c \\"
echo "    \"INSERT INTO api_keys (key, agent_id) VALUES ('<your-api-key>', 'docker-worker') ON CONFLICT (key) DO NOTHING;\""
echo ""
echo "Start cloud API:"
echo "  cd ~/containerguard-v2/cloud && nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 &"
echo ""
echo "Start frontend:"
echo "  cd ~/containerguard-v2/frontend && npm install && npm run dev -- --host"
