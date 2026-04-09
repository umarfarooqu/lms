#!/bin/bash
# Run this on your Ubuntu 22.04 server as root
# Usage: bash server-setup.sh

set -e

echo "=== Installing Coolify on Ubuntu 22.04 ==="
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

echo ""
echo "=== Coolify installed! ==="
echo ""
echo "Open your browser: http://$(curl -s ifconfig.me):8000"
echo "Create your admin account there."
