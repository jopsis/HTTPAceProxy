# HTTPAceProxy - Docker Setup

Configuración Docker para HTTPAceProxy con el plugin NewEra.

## Requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+ (opcional, pero recomendado)

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
curl http://localhost:8001/newera.m3u8

# Ver estadísticas
curl http://localhost:8001/stat
```

## Opción 2: Usando Docker directamente

### Construir la imagen

```bash
docker build -t httpaceproxy:latest .
```

### Ejecutar el contenedor

```bash
docker run -d \
  --name httpaceproxy \
  --restart unless-stopped \
  -p 8001:8001 \
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

- **Playlist principal**: `http://localhost:8001/newera.m3u8`
- **Playlist alternativa**: `http://localhost:8001/newera`
- **Panel de estadísticas**: `http://localhost:8001/stat`
- **Canal individual**: `http://localhost:8001/newera/channel/NOMBRE_CANAL.m3u8`

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
  - ACEPROXY_HOST=0.0.0.0
  - ACEPROXY_PORT=8001
```

## Volúmenes

El contenedor monta los siguientes volúmenes:

- `./logs:/app/logs` - Logs persistentes
- `./aceconfig.py:/app/aceconfig.py:ro` - Configuración (solo lectura)
- `./plugins/config/newera.py:/app/plugins/config/newera.py:ro` - Config del plugin (solo lectura)

## Health Check

El contenedor incluye un health check que verifica cada 30 segundos que el servidor está respondiendo:

```bash
# Ver el estado de salud
docker inspect --format='{{.State.Health.Status}}' httpaceproxy
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

### Verificar que AceStream está accesible

El contenedor necesita acceso a un motor de Ace Stream. Por defecto busca en `127.0.0.1:62062`.

Si tu Ace Stream Engine está en otro host:

1. Edita `aceconfig.py`
2. Cambia la configuración `ace = {'aceHostIP': 'IP_DE_ACESTREAM', ...}`
3. Reinicia el contenedor

### El contenedor no arranca

```bash
# Ver el error
docker-compose logs httpaceproxy

# Verificar que el puerto 8001 no está ocupado
lsof -i :8001

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
- Solo se expone el puerto necesario (8001)
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
URL: http://IP_DEL_SERVIDOR:8001/newera.m3u8
```

### En Kodi

```
Add-ons → PVR IPTV Simple Client
M3U Play List URL: http://IP_DEL_SERVIDOR:8001/newera.m3u8
```

### En cualquier app IPTV

Simplemente usa la URL: `http://IP_DEL_SERVIDOR:8001/newera.m3u8`
