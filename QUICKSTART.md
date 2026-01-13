# HTTPAceProxy - Quick Start Guide

## ⚠️ Antes de empezar

**IMPORTANTE**: Necesitas tener **Ace Stream Engine** corriendo en tu máquina o en tu red.

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

Eso es todo! El servidor estará disponible en: `http://localhost:8001/newera.m3u8`

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
docker run -d -p 8001:8001 --name httpaceproxy httpaceproxy
```

## URLs de acceso

- **Playlist M3U8**: http://localhost:8001/newera.m3u8
- **Playlist M3U**: http://localhost:8001/newera
- **Estadísticas**: http://localhost:8001/stat
- **Canal individual**: http://localhost:8001/newera/channel/NOMBRE_CANAL.m3u8

## Uso en apps

### VLC
```
Media → Open Network Stream
URL: http://localhost:8001/newera.m3u8
```

### KODI
```
Add-ons → PVR IPTV Simple Client
M3U Play List URL: http://localhost:8001/newera.m3u8
```

### Navegador
Simplemente abre: http://localhost:8001/newera.m3u8

## Configuración

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
