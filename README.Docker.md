# HTTPAceProxy - Docker Setup

Configuración Docker para HTTPAceProxy con el plugin NewEra.

## Requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+ (opcional, pero recomendado)

## Opción 0: All-in-One con AceServe (Más Fácil)

La forma más sencilla es usar `docker-compose-aio.yml` que incluye HTTPAceProxy + AceServe (motor Ace Stream ligero):

```bash
# Descargar el archivo compose
curl -O https://raw.githubusercontent.com/jopsis/HTTPAceProxy/master/docker-compose-aio.yml


# Iniciar ambos servicios
docker-compose -f docker-compose-aio.yml up -d

# Ver logs
docker-compose -f docker-compose-aio.yml logs -f

# Acceder
# http://localhost:8888/stat
# http://localhost:8888/statplugin
```

**Ventajas:**
- Todo incluido (proxy + motor)
- No necesitas Ace Stream Engine instalado separadamente
- Optimizado y más ligero que el motor oficial
- Soporta x64, ARM64 y ARM32
- Healthcheck integrado: HTTPAceProxy espera a que AceServe esté completamente listo

## Opción 1: Usando Docker Compose (Recomendado)

### Construcción e inicio rápido

```bash
# Construir y arrancar el contenedor
docker-compose up -d

# Ver los logs
docker-compose logs -f

# Detener el contenedor
docker-compose down

# Reiniciar el contenedor
docker-compose restart
```

### Verificar que funciona

```bash
# Verificar estado del contenedor
docker-compose ps

# Acceder a la playlist
curl http://localhost:8888/newera

# Ver estadísticas
curl http://localhost:8888/stat
```

## Opción 2: Usando Docker directamente

### Construir la imagen

```bash
docker build -t httpaceproxy:latest .
```

### Ejecutar el contenedor

**Ejecución básica:**
```bash
docker run -d \
  --name httpaceproxy \
  --restart unless-stopped \
  -p 8888:8888 \
  -v $(pwd)/logs:/app/logs \
  httpaceproxy:latest
```

**Con configuración personalizada:**
```bash
docker run -d \
  --name httpaceproxy \
  --restart unless-stopped \
  -p 8888:8888 \
  -e ACESTREAM_HOST=127.0.0.1 \
  -e ACESTREAM_API_PORT=62062 \
  -e ACESTREAM_HTTP_PORT=6878 \
  -e MAX_CONNECTIONS=50 \
  -e MAX_CONCURRENT_CHANNELS=10 \
  -v $(pwd)/logs:/app/logs \
  httpaceproxy:latest
```

### Ver logs

```bash
docker logs -f httpaceproxy
```

### Detener y eliminar

```bash
docker stop httpaceproxy
docker rm httpaceproxy
```

## Acceso a la aplicación

Una vez iniciado el contenedor, la aplicación estará disponible en:

- **Playlist**: `http://localhost:8888/newera`
- **Panel de estadísticas**: `http://localhost:8888/stat`
- **Canal individual**: `http://localhost:8888/newera/channel/NOMBRE_CANAL.m3u8`

## Configuración

### Modificar la configuración

Edita el archivo `aceconfig.py` y reinicia el contenedor:

```bash
# Si usas docker-compose
docker-compose restart

# Si usas docker directamente
docker restart httpaceproxy
```

### Modificar el plugin NewEra

Edita el archivo `plugins/config/newera.py` y reinicia el contenedor.

### Variables de entorno

Puedes configurar las siguientes variables de entorno en `docker-compose.yml`:

```yaml
environment:
  # Conexión a Ace Stream Engine
  - ACESTREAM_HOST=aceserve          # Host del motor Ace Stream
  - ACESTREAM_API_PORT=62062         # Puerto API (default: 62062)
  - ACESTREAM_HTTP_PORT=6878         # Puerto HTTP (default: 6878)

  # Servidor HTTPAceProxy
  - ACEPROXY_HOST=0.0.0.0            # Interfaz de escucha
  - ACEPROXY_PORT=8888               # Puerto del servidor

  # Límites de conexión (opcional)
  - MAX_CONNECTIONS=10               # Máximo de conexiones totales (default: 10)
  - MAX_CONCURRENT_CHANNELS=5        # Máximo de canales simultáneos (default: 5)

  # Control de plugins (opcional)
  - ENABLED_PLUGINS=all              # Plugins habilitados (default: all)
                                     # Opciones: 'all', 'newera,acepl,stat', etc.
```

### Control de plugins

Puedes habilitar solo los plugins que necesites:

**Todos los plugins (por defecto):**
```yaml
environment:
  - ENABLED_PLUGINS=all
```

**Solo algunos plugins:**
```yaml
# Solo NewEra y AcePL
environment:
  - ENABLED_PLUGINS=newera,acepl,stat,statplugin

# Solo dashboards (sin listas de canales)
environment:
  - ENABLED_PLUGINS=stat,statplugin

# Solo un plugin
environment:
  - ENABLED_PLUGINS=acepl
```

**Plugins disponibles:**
- `newera` - 322 canales deportivos
- `elcano` - 71 canales curados
- `acepl` - 1000+ canales de API Acestream
- `stat` - Dashboard de estadísticas
- `statplugin` - Navegador de canales

### Ejemplos de configuración de límites

**Uso personal (1-5 usuarios):**
```yaml
environment:
  - MAX_CONNECTIONS=10
  - MAX_CONCURRENT_CHANNELS=3
```

**Uso familiar (5-15 usuarios):**
```yaml
environment:
  - MAX_CONNECTIONS=25
  - MAX_CONCURRENT_CHANNELS=5
```

**Servidor compartido (15-50 usuarios):**
```yaml
environment:
  - MAX_CONNECTIONS=100
  - MAX_CONCURRENT_CHANNELS=15
```

**Notas importantes:**
- Múltiples clientes viendo el **mismo canal** solo usan **1 slot de canal**
- Cada canal diferente requiere **1 slot de canal** y una conexión dedicada a AceStream
- El total de conexiones incluye todos los clientes en todos los canales
- Ajusta según los recursos de tu servidor y ancho de banda disponible

📖 **Para una guía completa sobre límites de conexión, consulta:** [CONNECTION-LIMITS.md](CONNECTION-LIMITS.md)

## Volúmenes

El contenedor monta los siguientes volúmenes:

- `./logs:/app/logs` - Logs persistentes
- `./aceconfig.py:/app/aceconfig.py:ro` - Configuración (solo lectura)
- `./plugins/config/newera.py:/app/plugins/config/newera.py:ro` - Config del plugin (solo lectura)

## Health Check

### HTTPAceProxy Health Check

El contenedor HTTPAceProxy incluye un health check que verifica cada 30 segundos que el servidor está respondiendo:

```bash
# Ver el estado de salud
docker inspect --format='{{.State.Health.Status}}' httpaceproxy
```

### AceServe Health Check (docker-compose-aio.yml)

En la configuración all-in-one, el servicio AceServe tiene un health check que verifica:
- **Puerto HTTP (6878)**: Comprueba que el puerto de streaming está abierto
- **Puerto API (62062)**: Comprueba que la API de AceStream está disponible
- **Frecuencia**: Cada 10 segundos
- **Tiempo de inicio**: 30 segundos de gracia para que el motor arranque
- **Reintentos**: 5 intentos antes de marcar como unhealthy

El servicio HTTPAceProxy **espera automáticamente** a que AceServe esté saludable antes de iniciar, gracias a:

```yaml
depends_on:
  aceserve:
    condition: service_healthy   # Espera a que aceserve esté listo
```

**Verificar el estado de salud:**
```bash
# Ver estado de ambos servicios
docker-compose ps

# Ver estado específico de AceServe
docker inspect --format='{{.State.Health.Status}}' aceserve-engine

# Ver logs del healthcheck
docker inspect aceserve-engine | jq '.[0].State.Health'
```

**Estados posibles:**
- `starting` - El contenedor acaba de iniciar, esperando el primer check
- `healthy` - Todos los checks pasaron correctamente
- `unhealthy` - Falló después de varios reintentos

**Qué verifica el healthcheck:**
```bash
nc -z 127.0.0.1 6878 && nc -z 127.0.0.1 62062
```

Este comando verifica que ambos puertos (HTTP 6878 y API 62062) están escuchando y disponibles.

**Nota:** Usamos `127.0.0.1` en lugar de `localhost` porque algunos contenedores no resuelven correctamente localhost.

**Verificación manual:**
```bash
# Verificar puerto HTTP
curl -I http://localhost:6878

# Verificar puerto API
curl http://localhost:62062/webui/api/service?method=get_version
```

## Troubleshooting

### Ver logs en tiempo real

```bash
docker-compose logs -f httpaceproxy
```

### Entrar al contenedor

```bash
docker-compose exec httpaceproxy /bin/bash
```

### Verificar que AceServe/AceStream está accesible

El contenedor necesita acceso a un motor de Ace Stream (AceServe o Ace Stream Engine). Por defecto busca en `127.0.0.1:62062`.

**Opción recomendada:** Usar AceServe con docker-compose-aio.yml (incluye motor y proxy).

Si tu motor está en otro host:

1. Edita `aceconfig.py`
2. Cambia la configuración `ace = {'aceHostIP': 'IP_DEL_MOTOR', ...}`
3. Reinicia el contenedor

### El contenedor no arranca

```bash
# Ver el error
docker-compose logs httpaceproxy

# Verificar que el puerto 8888 no está ocupado
lsof -i :8888

# Reconstruir la imagen
docker-compose build --no-cache
docker-compose up -d
```

## Actualización

Para actualizar el contenedor con cambios en el código:

```bash
# Detener el contenedor actual
docker-compose down

# Reconstruir la imagen
docker-compose build

# Iniciar nuevamente
docker-compose up -d
```

## Red

El contenedor usa una red bridge personalizada llamada `aceproxy-network`. Esto permite:

- Aislamiento de red
- Comunicación con otros contenedores
- DNS interno entre contenedores

## Seguridad

- Los archivos de configuración se montan como solo lectura (`:ro`)
- El contenedor se ejecuta con usuario no privilegiado
- Solo se expone el puerto necesario (8888)
- El health check verifica que el servicio está funcionando correctamente

## Producción

Para producción, considera:

1. **Usar un proxy reverso** (Nginx, Traefik) delante del contenedor
2. **Habilitar HTTPS** con certificados SSL
3. **Configurar límites de recursos**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 512M
   ```
4. **Configurar logging** adecuado
5. **Monitorear** el health check

## Ejemplo de uso con apps IPTV

### En VLC

```
Media → Open Network Stream
URL: http://IP_DEL_SERVIDOR:8888/newera
```

### En Kodi

```
Add-ons → PVR IPTV Simple Client
M3U Play List URL: http://IP_DEL_SERVIDOR:8888/newera
```

### En cualquier app IPTV

Simplemente usa la URL: `http://IP_DEL_SERVIDOR:8888/newera`
