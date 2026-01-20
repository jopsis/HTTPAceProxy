#!/bin/bash
set -e

echo "================================================"
echo "HTTPAceProxy with NewEra Plugin"
echo "================================================"
echo ""

# Function to print colored output
print_status() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Check if Python is available
print_status "Checking Python installation..."
python --version

# Check if required Python packages are installed
print_status "Checking Python dependencies..."
python -c "import gevent; print('  ✓ gevent', gevent.__version__)" || { echo "  ✗ gevent not found"; exit 1; }
python -c "import psutil; print('  ✓ psutil', psutil.__version__)" || { echo "  ✗ psutil not found"; exit 1; }
python -c "import requests; print('  ✓ requests', requests.__version__)" || { echo "  ✗ requests not found"; exit 1; }

# Check if required files exist
print_status "Checking application files..."
[ -f "acehttp.py" ] && echo "  ✓ acehttp.py" || { echo "  ✗ acehttp.py not found"; exit 1; }
[ -f "aceconfig.py" ] && echo "  ✓ aceconfig.py" || { echo "  ✗ aceconfig.py not found"; exit 1; }
[ -f "acedefconfig.py" ] && echo "  ✓ acedefconfig.py" || { echo "  ✗ acedefconfig.py not found"; exit 1; }
[ -d "plugins" ] && echo "  ✓ plugins directory" || { echo "  ✗ plugins directory not found"; exit 1; }

# Check if NewEra plugin exists
print_status "Checking NewEra plugin..."
[ -f "plugins/newera_plugin.py" ] && echo "  ✓ newera_plugin.py" || { echo "  ✗ newera_plugin.py not found"; exit 1; }
[ -f "plugins/config/newera.py" ] && echo "  ✓ newera config" || { echo "  ✗ newera config not found"; exit 1; }

# Create logs directory if it doesn't exist
if [ ! -d "/app/logs" ]; then
    print_status "Creating logs directory..."
    mkdir -p /app/logs
fi

# Map ACE_* to ACESTREAM_* for backward compatibility
export ACESTREAM_HOST="${ACE_HOST:-${ACESTREAM_HOST:-127.0.0.1}}"
export ACESTREAM_API_PORT="${ACE_API_PORT:-${ACESTREAM_API_PORT:-62062}}"
export ACESTREAM_HTTP_PORT="${ACE_HTTP_PORT:-${ACESTREAM_HTTP_PORT:-6878}}"

# Display configuration
print_status "Configuration:"
echo "  HTTPAceProxy:"
echo "    Host: ${ACEPROXY_HOST:-0.0.0.0}"
echo "    Port: ${ACEPROXY_PORT:-8888}"
echo "  Ace Stream Engine:"
echo "    Host: ${ACESTREAM_HOST}"
echo "    API Port: ${ACESTREAM_API_PORT}"
echo "    HTTP Port: ${ACESTREAM_HTTP_PORT}"
echo "  Connection Limits:"
echo "    Max Connections: ${MAX_CONNECTIONS:-10}"
echo "    Max Concurrent Channels: ${MAX_CONCURRENT_CHANNELS:-5}"

echo ""
print_status "Starting HTTPAceProxy..."
echo "================================================"
echo ""

# Execute the main application
exec python -u acehttp.py "$@"
