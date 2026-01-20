# HTTPAceProxy - Quick Start Guide

## ⚡ Inicio Más Rápido (Recomendado)

**Todo incluido con AceServe** (no necesitas instalar Ace Stream):

```bash
# Descargar docker-compose all-in-one
curl -O https://raw.githubusercontent.com/jopsis/HTTPAceProxy/master/docker-compose-aio.yml

# Iniciar (incluye HTTPAceProxy + AceServe)
docker-compose -f docker-compose-aio.yml up -d

# Acceder
# http://localhost:8888/newera.m3u8
# http://localhost:8888/stat
```

**Listo!** Ya tienes todo funcionando. Salta a la sección [URLs de acceso](#urls-de-acceso).

**💡 Personalizar límites de conexión (opcional):**
Si necesitas más clientes o canales simultáneos, edita `docker-compose-aio.yml` antes de iniciar:
```yaml
environment:
  - MAX_CONNECTIONS=50           # Aumentar clientes totales
  - MAX_CONCURRENT_CHANNELS=10   # Permitir más canales diferentes
```

---

## 🔧 Alternativa: Usar tu propio Ace Stream

Si ya tienes Ace Stream instalado o prefieres usar el motor oficial:

### ¿Tienes Ace Stream instalado?

Si NO, descárgalo primero desde: http://acestream.org/

### Configurar la conexión a Ace Stream

**En Mac (lo más común):**
```bash
# Edita el archivo .env (ya está configurado por defecto)
# No necesitas cambiar nada si Ace Stream está en tu Mac
```

**En Linux:**
```bash
# Edita .env y cambia:
ACESTREAM_HOST=172.17.0.1
```

**En otra máquina:**
```bash
# Edita .env y cambia:
ACESTREAM_HOST=192.168.1.XXX  # IP de la máquina con Ace Stream
```

Ver [ACESTREAM-SETUP.md](ACESTREAM-SETUP.md) para más detalles.

## Inicio rápido (1 comando)

```bash
./start.sh
```

Eso es todo! El servidor estará disponible en: `http://localhost:8888/newera.m3u8`

## Inicio manual

### Opción 1: Docker Compose (Recomendado)

```bash
# Construir e iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Opción 2: Make

```bash
# Ver comandos disponibles
make help

# Iniciar
make up

# Ver logs
make logs

# Detener
make down
```

### Opción 3: Docker directo

```bash
# Construir
docker build -t httpaceproxy .

# Ejecutar
docker run -d -p 8888:8888 --name httpaceproxy httpaceproxy
```

## URLs de acceso

**Playlists:**
- NewEra (322 canales): http://localhost:8888/newera.m3u8
- Elcano (71 canales): http://localhost:8888/elcano.m3u8
- Canal individual: http://localhost:8888/newera/channel/NOMBRE_CANAL.m3u8

**Dashboards:**
- Estadísticas en tiempo real: http://localhost:8888/stat
- Navegador de canales + verificación de peers: http://localhost:8888/statplugin

## Uso en apps

### VLC
```
Media → Open Network Stream
URL: http://localhost:8888/newera.m3u8
```

### KODI
```
Add-ons → PVR IPTV Simple Client
M3U Play List URL: http://localhost:8888/newera.m3u8
```

### Navegador
Simplemente abre: http://localhost:8888/newera.m3u8

## Configuración

### Configuración básica (Docker)

Edita el archivo `docker-compose-aio.yml` o `docker-compose.yml` para cambiar las variables de entorno:

```yaml
environment:
  # Límites de conexión (opcional)
  - MAX_CONNECTIONS=20              # Aumentar conexiones totales (default: 10)
  - MAX_CONCURRENT_CHANNELS=10      # Permitir más canales simultáneos (default: 5)

  # Conexión a Ace Stream
  - ACESTREAM_HOST=aceserve
  - ACESTREAM_API_PORT=62062
  - ACESTREAM_HTTP_PORT=6878
```

**Ejemplos de uso:**
- Para 50 clientes y 10 canales diferentes: `MAX_CONNECTIONS=50` y `MAX_CONCURRENT_CHANNELS=10`
- Para uso personal (pocos clientes): Usar valores por defecto
- Para servidor compartido: Aumentar según necesidad

📖 **Para más detalles sobre límites de conexión, consulta:** [CONNECTION-LIMITS.md](CONNECTION-LIMITS.md)

### Configuración avanzada (Archivo)

Edita `aceconfig.py` para cambiar:
- Puerto del servidor
- Configuración de Ace Stream
- Firewall y seguridad

Edita `plugins/config/newera.py` para cambiar:
- URL de la playlist
- Frecuencia de actualización
- EPG (guía de TV)

Después de cambios, reinicia:
```bash
docker-compose restart
```

## Solución de problemas

### Ver logs en tiempo real
```bash
docker-compose logs -f
```

### Verificar que el contenedor está corriendo
```bash
docker-compose ps
```

### Entrar al contenedor
```bash
docker-compose exec httpaceproxy /bin/bash
```

### Reconstruir desde cero
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Documentación completa

Ver [README.Docker.md](README.Docker.md) para documentación detallada.
