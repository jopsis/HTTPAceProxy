# Guía de Uso - HTTPAceProxy

HTTPAceProxy proporciona múltiples formas de acceder a contenido de Ace Stream.

## 🎯 Métodos de Acceso

### 1. Reproducción Directa por Content ID

Reproduce directamente cualquier hash de Ace Stream:

```
http://localhost:8888/content_id/HASH/stream.ts
http://localhost:8888/pid/HASH/stream.ts
```

**Ejemplo:**
```
http://localhost:8888/content_id/55ff9ee631af351f365f51cf3601695bf1fd20f3/stream.ts
http://localhost:8888/pid/55ff9ee631af351f365f51cf3601695bf1fd20f3/stream.ts
```

### 2. Reproducción por Infohash (Torrent)

Reproduce contenido desde un infohash de torrent:

```
http://localhost:8888/infohash/INFOHASH/video.ts
```

**Ejemplo:**
```
http://localhost:8888/infohash/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0/video.ts
```

### 3. Reproducción por URL de Torrent

Reproduce desde una URL de archivo torrent:

```
http://localhost:8888/url/URL_ENCODED/video.ts
```

**Ejemplo:**
```
# URL original: http://example.com/file.torrent
# URL encoded: http%3A%2F%2Fexample.com%2Ffile.torrent
http://localhost:8888/url/http%3A%2F%2Fexample.com%2Ffile.torrent/video.ts
```

### 4. Playlists de Plugins

Usa las playlists curadas de los plugins:

**NewEra (322 canales):**
```
http://localhost:8888/newera.m3u8
```

**Elcano (68 canales):**
```
http://localhost:8888/elcano.m3u8
```

### 5. Canales Individuales de Plugins

Reproduce canales específicos de las playlists:

**Formato:**
```
http://localhost:8888/PLUGIN/channel/NOMBRE_CANAL.EXTENSION
```

**Ejemplos:**
```
# NewEra
http://localhost:8888/newera/channel/DAZN%201%20FHD.m3u8
http://localhost:8888/newera.m3u8/channel/M+%20LaLiga.ts

# Elcano
http://localhost:8888/elcano/channel/Eurosport%201.m3u8
http://localhost:8888/elcano.m3u8/channel/M+%20Deportes.ts
```

## 📺 Extensiones Soportadas

Puedes usar cualquiera de estas extensiones en las URLs:

| Extensión | Descripción | Recomendado para |
|-----------|-------------|------------------|
| `.ts` | Transport Stream | Streaming general, más compatible |
| `.m3u8` | HLS Playlist | Apps IPTV, navegadores |
| `.mp4` | MP4 container | Descargas, algunos reproductores |
| `.mkv` | Matroska | Reproductores avanzados |
| `.avi` | AVI container | Reproductores antiguos |
| `.flv` | Flash Video | Streaming legacy |
| `.m2ts` | MPEG-2 TS | Blu-ray rips |
| `.mpegts` | MPEG Transport Stream | Streaming |
| `.mpg` | MPEG | Reproductores generales |
| `.wmv` | Windows Media | Windows Media Player |
| `.mov` | QuickTime | Reproductores Apple |

## 🎬 Uso en Reproductores

### VLC Media Player

**Método 1: Network Stream**
```
Media → Open Network Stream (Ctrl+N)
Pega la URL: http://localhost:8888/content_id/HASH/stream.ts
```

**Método 2: Playlist**
```
Media → Open Network Stream
Pega la URL: http://localhost:8888/newera.m3u8
```

**Método 3: Desde línea de comandos**
```bash
vlc http://localhost:8888/content_id/55ff9ee631af351f365f51cf3601695bf1fd20f3/stream.ts
vlc http://localhost:8888/newera.m3u8
```

### KODI

**Usando PVR IPTV Simple Client:**
```
1. Instalar "PVR IPTV Simple Client"
2. Configurar → Add-ons → My Add-ons → PVR clients
3. PVR IPTV Simple Client → Configure
4. General → Location: Remote Path
5. M3U Play List URL: http://localhost:8888/newera.m3u8
6. Guardar y habilitar
```

### Apps IPTV (Mobile/TV)

Usa cualquiera de estas URLs en tu app IPTV favorita:
```
http://SERVIDOR_IP:8888/newera.m3u8
http://SERVIDOR_IP:8888/elcano.m3u8
```

Apps compatibles:
- **Android:** IPTV Smarters, TiviMate, GSE Smart IPTV
- **iOS:** GSE Smart IPTV, IPTV Smarters
- **Smart TV:** IPTV Smarters, SS IPTV
- **Fire TV:** IPTV Smarters Pro

### MPV

```bash
mpv http://localhost:8888/content_id/55ff9ee631af351f365f51cf3601695bf1fd20f3/stream.ts
```

### ffplay

```bash
ffplay http://localhost:8888/pid/55ff9ee631af351f365f51cf3601695bf1fd20f3/stream.ts
```

## 🌐 Acceso Remoto

Para acceder desde otros dispositivos en tu red:

1. **Encuentra tu IP local:**
```bash
# En Mac/Linux
ifconfig | grep "inet "
hostname -I

# En Windows
ipconfig
```

2. **Usa la IP en lugar de localhost:**
```
# Si tu IP es 192.168.1.100
http://192.168.1.100:8888/newera.m3u8
http://192.168.1.100:8888/content_id/HASH/stream.ts
```

3. **Verifica que el firewall permite conexiones en el puerto 8888**

## 🔗 Parámetros de URL

### Extensión personalizada

Usa el parámetro `?ext=EXTENSION`:

```
http://localhost:8888/newera?ext=m3u8
http://localhost:8888/content_id/HASH/stream.ts?ext=mp4
```

### Otros parámetros

Los canales de plugins soportan parámetros adicionales que se pasan a Ace Stream.

## 📊 Panel de Estadísticas

Monitorea las conexiones activas:

```
http://localhost:8888/stat
```

Muestra:
- Canales en reproducción
- IPs conectadas
- Velocidad de transferencia
- Peers conectados
- Duración de la conexión

## 🎯 Ejemplos Prácticos

### Reproducir La Liga en VLC:
```bash
vlc "http://localhost:8888/newera/channel/M%2B%20LaLiga%20FHD.m3u8"
```

### Reproducir Champions en navegador:
```
http://localhost:8888/newera/channel/M%2B%20Liga%20de%20Campeones.m3u8
```

### Reproducir un hash directo:
```bash
vlc "http://localhost:8888/pid/4955867fad3bc92e5b4c36045699fc277800fb18/stream.ts"
```

### Cargar playlist en IPTV Smarters:
```
1. Abrir IPTV Smarters
2. Add New User → Load your playlist
3. Playlist URL: http://192.168.1.100:8888/newera.m3u8
4. Playlist Name: NewEra
5. Add
```

## ⚙️ Tips y Trucos

### 1. Buffer de red en VLC

Para mejorar el streaming en VLC:
```
Herramientas → Preferencias → Mostrar configuración: Todos
Input / Codecs → Network → Network caching: 3000 ms
```

### 2. Codificar nombres de canales

Los nombres con espacios o caracteres especiales deben codificarse:
```python
import urllib.parse
nombre = "M+ LaLiga FHD"
encoded = urllib.parse.quote(nombre)
print(encoded)  # M%2B%20LaLiga%20FHD
```

O usa una herramienta online: https://www.urlencoder.org/

### 3. Verificar conectividad

```bash
# Verificar que el servidor responde
curl -I http://localhost:8888/stat

# Verificar que una playlist se descarga
curl http://localhost:8888/newera.m3u8 | head -10

# Verificar un content_id específico
curl -I "http://localhost:8888/content_id/55ff9ee631af351f365f51cf3601695bf1fd20f3/stream.ts"
```

## 🐛 Troubleshooting

### Error: "No valid video extension"
Asegúrate de terminar la URL con una extensión válida (`.ts`, `.m3u8`, etc.)

### Error: "Maximum client connections reached"
Aumenta `maxconns` en `aceconfig.py` o espera a que otras conexiones terminen.

### Stream no inicia
1. Verifica que Ace Stream Engine está corriendo
2. Comprueba los logs: `docker logs -f httpaceproxy`
3. Prueba el hash directamente en Ace Stream

### Calidad baja o buffering
1. Aumenta el cache de red en tu reproductor
2. Verifica tu conexión a internet
3. Espera a que más peers se conecten

## 📚 Referencias

- [Documentación de Plugins](PLUGINS.md)
- [Configuración de Docker](README.Docker.md)
- [Setup de Ace Stream](ACESTREAM-SETUP.md)
- [Inicio Rápido](QUICKSTART.md)
