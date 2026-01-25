# HTTPAceProxy

[![Docker Pulls](https://img.shields.io/docker/pulls/jopsis/httpaceproxy)](https://hub.docker.com/r/jopsis/httpaceproxy)
[![GitHub Release](https://img.shields.io/github/v/release/jopsis/HTTPAceProxy)](https://github.com/jopsis/HTTPAceProxy/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

HTTPAceProxy allows you to watch [Ace Stream](http://acestream.org/) live streams and torrent files over HTTP. Access Ace Stream content through a simple HTTP interface compatible with VLC, KODI, IPTV apps, and modern browsers.

## ✨ Features

- 🎯 **Direct Streaming** - Access Ace Stream content via HTTP URLs
- 📺 **Pre-configured Channels** - 1300+ channels ready to use (NewEra, Elcano & AcePL plugins)
- 👥 **Multi-Client & Multi-Channel** - Multiple users can watch different channels simultaneously
- 🔌 **Plugin System** - Extensible architecture for custom channel sources
- 📊 **Real-time Statistics** - Monitor connections, bandwidth, and system resources
- 🐳 **Docker Ready** - Multi-architecture support (AMD64, ARM64, ARM32)
- 🌐 **Reverse Proxy Compatible** - Works with Nginx, Nginx Proxy Manager, Caddy
- 🔄 **Auto-updates** - Playlists refresh automatically from IPFS and API sources

## 🚀 Quick Start

### Using Docker (Recommended)

#### 1. Standalone HTTPAceProxy (connect to external Ace Stream)

```bash
docker run -d \
  --name httpaceproxy \
  -p 8888:8888 \
  -e ACESTREAM_HOST=your_acestream_host \
  -e ACESTREAM_API_PORT=62062 \
  -e ACESTREAM_HTTP_PORT=6878 \
  -e MAX_CONNECTIONS=10 \
  -e MAX_CONCURRENT_CHANNELS=5 \
  jopsis/httpaceproxy:latest
```

#### 2. All-in-One (HTTPAceProxy + AceServe Engine)

Complete solution with HTTPAceProxy and AceServe (lightweight Ace Stream Engine):

```bash
# Download compose file
curl -O https://raw.githubusercontent.com/jopsis/HTTPAceProxy/master/docker-compose-aio.yml

# Start services (automatically selects x64, arm64, or arm32 image)
docker-compose -f docker-compose-aio.yml up -d
```

**AceServe Images:**
- `jopsis/aceserve:latest` - AMD64/Intel systems, ARM64 (Raspberry Pi 4, Apple Silicon), ARM32 (Raspberry Pi 3 and older)

**Features:**
- Built-in healthcheck - HTTPAceProxy waits for AceServe to be ready before starting
- Automatic dependency management with `depends_on: service_healthy`
- No manual configuration needed

### Access

Once running, access HTTPAceProxy at:
```
http://localhost:8888
```

**Dashboards:**
```
http://localhost:8888/stat          # Real-time statistics
http://localhost:8888/statplugin    # Channel browser with peer checking
```

**Playlists:**
```
http://localhost:8888/newera   (322 sports channels)
http://localhost:8888/elcano   (71 curated channels)
http://localhost:8888/acepl    (1000+ channels from Acestream API)
```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Installation and setup
- **[Usage Guide](USAGE.md)** - Complete usage examples (VLC, KODI, IPTV apps)
- **[Plugin Documentation](PLUGINS.md)** - NewEra, Elcano and AcePL plugin details
- **[Plugin Control](PLUGIN-CONTROL.md)** - Enable/disable plugins via environment variables
- **[Docker Setup](README.Docker.md)** - Advanced Docker configuration
- **[Ace Stream Setup](ACESTREAM-SETUP.md)** - Configure Ace Stream Engine
- **[Connection Limits](CONNECTION-LIMITS.md)** - Configure client and channel limits
- **[Nginx Proxy Manager Setup](NGINX-NPM-SETUP.md)** - Reverse proxy configuration

## 🎬 Usage Examples

### Direct Content ID Access

```
http://localhost:8888/content_id/HASH/stream.ts
http://localhost:8888/pid/HASH/stream.ts
```

### Individual Channel from Plugins

```
http://localhost:8888/newera/channel/DAZN%201%20FHD.m3u8
http://localhost:8888/elcano/channel/Eurosport%201.ts
```

### In VLC

```bash
# Open Network Stream (Ctrl+N)
vlc "http://localhost:8888/newera"

# Or command line
vlc "http://localhost:8888/content_id/HASH/stream.ts"
```

### In KODI

1. Install **PVR IPTV Simple Client**
2. Configure → Add-ons → My Add-ons → PVR clients
3. PVR IPTV Simple Client → Configure
4. M3U Play List URL: `http://localhost:8888/newera`

## 👥 Multi-Client & Multi-Channel Support

HTTPAceProxy supports **multiple simultaneous connections** with intelligent broadcast management:

### Multiple Clients, Same Channel
- ✅ Unlimited clients can watch the **same channel** simultaneously
- ✅ Efficient resource usage - one Ace Stream connection shared by all viewers
- ✅ Automatic broadcast management - starts when first client connects, stops when last disconnects

### Multiple Clients, Different Channels
- ✅ Up to **5 different channels** streaming concurrently (configurable)
- ✅ Each channel has its own dedicated Ace Stream connection
- ✅ Independent lifecycle management per channel
- ✅ Automatic cleanup when channels become inactive

### Architecture
```
Client A1, A2, A3 → Broadcast A (DAZN 1)     → AceStream Connection 1
Client B1         → Broadcast B (Eurosport)  → AceStream Connection 2
Client C1, C2     → Broadcast C (La Liga TV) → AceStream Connection 3
```

### Configuration

**Docker (Recommended):**
Configure via environment variables in `docker-compose.yml`:
```yaml
environment:
  - MAX_CONNECTIONS=10           # Maximum total client connections (default: 10)
  - MAX_CONCURRENT_CHANNELS=5    # Maximum different channels (default: 5)
```

**Direct Python:**
Edit `aceconfig.py`:
```python
maxconns = 10              # Maximum total client connections
maxconcurrentchannels = 5  # Maximum different channels simultaneously
```

**Example Scenarios:**
- 10 clients watching DAZN 1 → Uses 1 channel slot, 10 connections
- 3 clients on DAZN 1 + 2 clients on Eurosport 1 → Uses 2 channel slots, 5 connections
- 5 different channels with 1 client each → Uses all 5 slots (limit reached), 5 connections
- For 50 clients and 10 different channels: Set `MAX_CONNECTIONS=50` and `MAX_CONCURRENT_CHANNELS=10`

## 🔌 Active Plugins

| Plugin | Channels | Description | Source |
|--------|----------|-------------|--------|
| **NewEra** | 322 | Sports channels (La Liga, Champions, DAZN, NBA, F1, etc.) | IPFS |
| **Elcano** | 71 | Curated sports selection | IPFS |
| **AcePL** | 1000+ | Official Acestream API channels (Sports, Movies, Regional, etc.) | Acestream API |
| **Stat** | - | Real-time statistics and monitoring dashboard | Built-in |
| **StatPlugin** | - | Channel browser with availability & peer checking | Built-in |

## 🛠️ Requirements

- **Python:** 3.10+ (Python 3.11 recommended)
- **Dependencies:**
  - gevent >= 25.9.1
  - psutil >= 7.2.1
  - requests >= 2.32.0
- **Ace Stream Engine:** Required (local or remote)
  - **Recommended:** AceServe (lightweight Docker image by jopsis)
  - Alternative: Official Ace Stream Engine

## 🏗️ Installation Methods

### Method 1: Docker (Recommended)

See [Docker Setup Guide](README.Docker.md) for detailed instructions.

### Method 2: Direct Python

```bash
# Clone repository
git clone https://github.com/jopsis/HTTPAceProxy.git
cd HTTPAceProxy

# Install dependencies
pip install -r requirements.txt

# Configure (optional)
cp aceconfig.py.example aceconfig.py
# Edit aceconfig.py with your settings

# Run
python acehttp.py
```

### Method 3: Using Make

```bash
make install  # Install dependencies
make run      # Start server
make docker   # Build Docker image
```

See [Quick Start Guide](QUICKSTART.md) for more options.

## ⚙️ Configuration

### Environment Variables (Docker)

```bash
# Ace Stream Engine connection
ACESTREAM_HOST=127.0.0.1       # Ace Stream Engine host
ACESTREAM_API_PORT=62062       # Ace Stream API port
ACESTREAM_HTTP_PORT=6878       # Ace Stream HTTP port

# HTTPAceProxy settings
ACEPROXY_PORT=8888             # HTTPAceProxy port

# Connection limits (optional)
MAX_CONNECTIONS=10             # Maximum total client connections (default: 10)
MAX_CONCURRENT_CHANNELS=5      # Maximum different channels simultaneously (default: 5)

# Plugin control (optional)
ENABLED_PLUGINS=all            # Which plugins to enable (default: all)
                               # Options: 'all', 'newera,acepl,stat', 'stat,statplugin', etc.
                               # Available: newera, elcano, acepl, stat, statplugin

# Plugin playlist URLs (optional - uses defaults if not set)
NEWERA_PLAYLIST_URL=           # Custom NewEra playlist URL
ELCANO_PLAYLIST_URL=           # Custom Elcano playlist URL
```

### Configuration File

Edit `aceconfig.py` to customize:
- Ace Stream Engine connection
- HTTP server settings (host, port)
- Security settings (firewall, max connections)
- Multi-channel settings (concurrent channels, max clients)
- Plugin configurations

**Key Configuration Options:**
```python
# Via aceconfig.py (or environment variables in Docker):
maxconns = 10                  # Maximum total client connections (env: MAX_CONNECTIONS)
maxconcurrentchannels = 5      # Maximum different channels simultaneously (env: MAX_CONCURRENT_CHANNELS)
httpport = 8888                # HTTPAceProxy listening port
ace = {                        # Ace Stream Engine connection
    'aceHostIP': '127.0.0.1',  # env: ACESTREAM_HOST
    'aceAPIport': '62062',     # env: ACESTREAM_API_PORT
    'aceHTTPport': '6878'      # env: ACESTREAM_HTTP_PORT
}
```

See `acedefconfig.py` for all available options.

### Plugin Control

Control which plugins are loaded using the `ENABLED_PLUGINS` environment variable:

**Enable all plugins (default):**
```yaml
environment:
  - ENABLED_PLUGINS=all
```

**Enable specific plugins only:**
```yaml
# Only playlist plugins (no dashboards)
environment:
  - ENABLED_PLUGINS=newera,elcano,acepl

# Only dashboards (no playlists)
environment:
  - ENABLED_PLUGINS=stat,statplugin

# Only NewEra and Stats
environment:
  - ENABLED_PLUGINS=newera,stat,statplugin

# Only AcePL plugin
environment:
  - ENABLED_PLUGINS=acepl
```

**Disable all plugins:**
```yaml
environment:
  - ENABLED_PLUGINS=
```

**Available plugins:**
- `newera` - 322 sports channels (IPFS)
- `elcano` - 71 curated channels (IPFS)
- `acepl` - 1000+ channels (Acestream API)
- `stat` - Real-time statistics dashboard
- `statplugin` - Channel browser with peer checking

**Notes:**
- Plugin names are case-insensitive
- Use comma-separated list for multiple plugins
- Invalid plugin names will be logged as warnings and ignored
- The server will show enabled/disabled plugins in the logs on startup

### Custom Playlist URLs

Override the default playlist URLs for NewEra and Elcano plugins using environment variables:

**NewEra Plugin URL:**
```yaml
environment:
  - NEWERA_PLAYLIST_URL=https://your-custom-url/playlist.m3u
```

**Elcano Plugin URL:**
```yaml
environment:
  - ELCANO_PLAYLIST_URL=https://your-custom-url/playlist.m3u
```

**Example - Use custom URLs for both:**
```yaml
environment:
  - ENABLED_PLUGINS=newera,elcano,stat,statplugin
  - NEWERA_PLAYLIST_URL=https://my-server.com/newera.m3u
  - ELCANO_PLAYLIST_URL=https://<PROYECTO>-ids.vercel.app/hashes_acestream.m3u
```

**Default URLs:**
- NewEra: `https://ipfs.io/ipns/<IDIPFS>/data/listas/lista_fuera_iptv.m3u`
- Elcano: `https://<PROYECTO>-ids.vercel.app/hashes_acestream.m3u`

**Notes:**
- If not specified, plugins use their default URLs
- URLs can point to IPFS, HTTPS, or local files (`file:///path/to/playlist.m3u`)
- Changes require container restart to take effect
- Custom URLs will be shown in the startup logs

### Connection Limits Examples

Configure limits based on your use case:

**Personal Use (1-5 users):**
```yaml
environment:
  - MAX_CONNECTIONS=10
  - MAX_CONCURRENT_CHANNELS=3
```

**Family/Small Group (5-15 users):**
```yaml
environment:
  - MAX_CONNECTIONS=25
  - MAX_CONCURRENT_CHANNELS=5
```

**Shared Server (15-50 users):**
```yaml
environment:
  - MAX_CONNECTIONS=100
  - MAX_CONCURRENT_CHANNELS=15
```

**Important Notes:**
- Multiple clients watching the **same channel** only count as **1 channel slot**
- Each different channel requires **1 channel slot** and a dedicated AceStream connection
- Total connections includes all clients across all channels
- Adjust based on your server resources and bandwidth

## 🌐 Reverse Proxy Setup

HTTPAceProxy works behind reverse proxies. See detailed guides:

- **Nginx Proxy Manager** - [NGINX-NPM-SETUP.md](NGINX-NPM-SETUP.md)
- **Nginx Standalone** - [README.Docker.md](README.Docker.md#reverse-proxy)
- **Caddy** - [README.Docker.md](README.Docker.md#caddy-setup)

**Important:** Disable HTTP/2 and buffering for best streaming performance.

## 📊 Monitoring & Dashboards

HTTPAceProxy provides two modern web dashboards for monitoring:

### Statistics Dashboard (`/stat`)

```
http://localhost:8888/stat
```

Real-time system monitoring with:
- Active connections and client IPs
- System resources (CPU, RAM, disk)
- Download/upload speeds per client
- Connection duration and peer statistics
- Auto-refresh every 2 seconds

### Plugin Channels Dashboard (`/statplugin`)

```
http://localhost:8888/statplugin
```

Browse and check all available channels with:
- **Channel List**: All channels from all plugins
- **Availability Check**: Verify if content exists (fast check)
- **Peer Check**: Start stream briefly to count active peers (deep check)
- **Bulk Operations**: "Check All" and "Peers All" buttons per plugin
- **Filter**: Search channels by name
- **Cache**: Results cached for faster subsequent checks

**Features:**
- Check individual channels or entire plugins at once
- Visual indicators: Available (green), Unavailable (red), Unknown (gray)
- Peer count display: P2P peers + HTTP peers
- Progress bar for bulk operations

## 🔧 Troubleshooting

### Stream doesn't start

1. Verify Ace Stream Engine is running:
   ```bash
   curl http://ACESTREAM_HOST:62062/webui/api/service?method=get_version
   ```

2. Check HTTPAceProxy logs:
   ```bash
   docker logs httpaceproxy -f
   ```

3. Test direct access (without proxy):
   ```bash
   curl -I http://localhost:8888/stat
   ```

### High latency or buffering

1. Increase network cache in VLC (3000ms recommended)
2. Verify reverse proxy has buffering disabled
3. Check available bandwidth and peers

### Connection closes immediately

- If using reverse proxy: Disable HTTP/2, increase timeouts
- See [NGINX-NPM-SETUP.md](NGINX-NPM-SETUP.md) for configuration

## 🏗️ Building from Source

### Local Build

```bash
docker build -t httpaceproxy:local .
```

### Multi-architecture Build

```bash
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t httpaceproxy:multi .
```

### GitHub Actions

Automatic builds are configured for:
- Push to master/main → `latest` tag
- Release tags → version-specific tags
- Multi-arch: AMD64 + ARM64

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **Plugin Development** - Add new channel sources
- **Documentation** - Translations, examples
- **Testing** - Multi-platform testing
- **Features** - EPG integration, authentication, etc.

### Creating a Plugin

See `plugins/PluginInterface_example.py` for a template.

1. Create `plugins/yourplugin_plugin.py`
2. Define handlers (URL paths)
3. Implement `handle(connection)` method
4. Add configuration in `plugins/config/yourplugin.py`

## 📄 License

GPL-3.0 License - See [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

**Be careful with torrent/streaming content.** Depending on your country's copyright laws, you may face legal consequences for viewing or distributing copyrighted material without authorization.

This software is provided for legitimate uses only. The authors are not responsible for any misuse.

## 🔗 Links

- **GitHub Repository:** https://github.com/jopsis/HTTPAceProxy
- **Docker Hub:** https://hub.docker.com/r/jopsis/httpaceproxy
- **Ace Stream:** https://acestream.org
- **Issue Tracker:** https://github.com/jopsis/HTTPAceProxy/issues

## 📈 Project Statistics

- **Language:** Python 3.11
- **Lines of Code:** ~9,000+
- **Active Plugins:** 5 (NewEra, Elcano, AcePL, Stat, StatPlugin)
- **Available Channels:** 1390+ (322 NewEra + 71 Elcano + 1000+ AcePL)
- **Concurrent Channels:** Up to 5 different streams simultaneously (configurable)
- **Multi-Client:** Unlimited clients per channel
- **Supported Architectures:** AMD64, ARM64, ARM32 (armv7)
- **Docker Image Size:** ~200MB
- **Web Dashboards:** 2 (Statistics + Channel Browser)

---

**Latest Version:** Check [Releases](https://github.com/jopsis/HTTPAceProxy/releases) for the latest stable version.

**Need Help?** Open an [issue](https://github.com/jopsis/HTTPAceProxy/issues) or check the documentation links above.
