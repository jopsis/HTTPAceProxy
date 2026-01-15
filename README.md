# HTTPAceProxy

[![Docker Pulls](https://img.shields.io/docker/pulls/jopsis/httpaceproxy)](https://hub.docker.com/r/jopsis/httpaceproxy)
[![GitHub Release](https://img.shields.io/github/v/release/jopsis/HTTPAceProxy)](https://github.com/jopsis/HTTPAceProxy/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

HTTPAceProxy allows you to watch [Ace Stream](http://acestream.org/) live streams and torrent files over HTTP. Access Ace Stream content through a simple HTTP interface compatible with VLC, KODI, IPTV apps, and modern browsers.

## ✨ Features

- 🎯 **Direct Streaming** - Access Ace Stream content via HTTP URLs
- 📺 **Pre-configured Channels** - 300+ sports channels ready to use (NewEra & Elcano plugins)
- 🔌 **Plugin System** - Extensible architecture for custom channel sources
- 📊 **Real-time Statistics** - Monitor connections, bandwidth, and system resources
- 🐳 **Docker Ready** - Multi-architecture support (AMD64, ARM64)
- 🌐 **Reverse Proxy Compatible** - Works with Nginx, Nginx Proxy Manager, Caddy
- 🔄 **Auto-updates** - Playlists refresh automatically from IPFS sources

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
  jopsis/httpaceproxy:latest
```

#### 2. All-in-One (HTTPAceProxy + Ace Stream Engine)

```bash
# Download compose file
curl -O https://raw.githubusercontent.com/jopsis/HTTPAceProxy/master/docker-compose-aio.yml

# Start services
docker-compose -f docker-compose-aio.yml up -d
```

### Access

Once running, access HTTPAceProxy at:
```
http://localhost:8888
```

**Statistics Dashboard:**
```
http://localhost:8888/stat
```

**Playlists:**
```
http://localhost:8888/newera.m3u8   (322 sports channels)
http://localhost:8888/elcano.m3u8   (68 curated channels)
```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Installation and setup
- **[Usage Guide](USAGE.md)** - Complete usage examples (VLC, KODI, IPTV apps)
- **[Plugin Documentation](PLUGINS.md)** - NewEra and Elcano plugin details
- **[Docker Setup](README.Docker.md)** - Advanced Docker configuration
- **[Ace Stream Setup](ACESTREAM-SETUP.md)** - Configure Ace Stream Engine
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
vlc "http://localhost:8888/newera.m3u8"

# Or command line
vlc "http://localhost:8888/content_id/HASH/stream.ts"
```

### In KODI

1. Install **PVR IPTV Simple Client**
2. Configure → Add-ons → My Add-ons → PVR clients
3. PVR IPTV Simple Client → Configure
4. M3U Play List URL: `http://localhost:8888/newera.m3u8`

## 🔌 Active Plugins

| Plugin | Channels | Description | Source |
|--------|----------|-------------|--------|
| **NewEra** | 322 | Sports channels (La Liga, Champions, DAZN, NBA, F1, etc.) | IPFS |
| **Elcano** | 68 | Curated sports selection | IPFS |
| **Stat** | - | Real-time statistics and monitoring dashboard | Built-in |

## 🛠️ Requirements

- **Python:** 3.10+ (Python 3.11 recommended)
- **Dependencies:**
  - gevent >= 25.9.1
  - psutil >= 7.2.1
  - requests >= 2.32.0
- **Ace Stream Engine:** Required (local or remote)

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
ACESTREAM_HOST=127.0.0.1       # Ace Stream Engine host
ACESTREAM_API_PORT=62062       # Ace Stream API port
ACESTREAM_HTTP_PORT=6878       # Ace Stream HTTP port
ACEPROXY_PORT=8888             # HTTPAceProxy port
```

### Configuration File

Edit `aceconfig.py` to customize:
- Ace Stream Engine connection
- HTTP server settings (host, port)
- Security settings (firewall, max connections)
- Plugin configurations

See `acedefconfig.py` for all available options.

## 🌐 Reverse Proxy Setup

HTTPAceProxy works behind reverse proxies. See detailed guides:

- **Nginx Proxy Manager** - [NGINX-NPM-SETUP.md](NGINX-NPM-SETUP.md)
- **Nginx Standalone** - [README.Docker.md](README.Docker.md#reverse-proxy)
- **Caddy** - [README.Docker.md](README.Docker.md#caddy-setup)

**Important:** Disable HTTP/2 and buffering for best streaming performance.

## 📊 Monitoring

Access real-time statistics at `/stat`:

```
http://localhost:8888/stat
```

**Displays:**
- Active connections and client IPs
- System resources (CPU, RAM, disk)
- Download/upload speeds per client
- Connection duration
- Peer statistics

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
docker buildx build --platform linux/amd64,linux/arm64 -t httpaceproxy:multi .
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
- **Lines of Code:** ~8,200
- **Active Plugins:** 3 (NewEra, Elcano, Stat)
- **Supported Architectures:** AMD64, ARM64
- **Docker Image Size:** ~200MB

---

**Latest Version:** Check [Releases](https://github.com/jopsis/HTTPAceProxy/releases) for the latest stable version.

**Need Help?** Open an [issue](https://github.com/jopsis/HTTPAceProxy/issues) or check the documentation links above.
