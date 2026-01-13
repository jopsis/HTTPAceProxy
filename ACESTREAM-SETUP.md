# Configurar conexión a Ace Stream Engine

HTTPAceProxy necesita conectarse a un Ace Stream Engine. Aquí te explico cómo configurarlo según dónde esté corriendo tu Ace Stream Engine.

## 🔍 ¿Dónde está tu Ace Stream Engine?

### Opción 1: En la misma máquina (Docker Desktop - Mac/Windows)

Si tienes Ace Stream corriendo en tu Mac o Windows con Docker Desktop:

**Edita el archivo `.env`:**
```bash
ACESTREAM_HOST=host.docker.internal
ACESTREAM_API_PORT=62062
ACESTREAM_HTTP_PORT=6878
```

Esto es lo que viene por defecto y debería funcionar automáticamente.

### Opción 2: En la misma máquina (Linux)

En Linux, Docker no soporta `host.docker.internal`. Necesitas usar la IP del bridge de Docker:

**Opción A - Usar el gateway de Docker:**
```bash
ACESTREAM_HOST=172.17.0.1
ACESTREAM_API_PORT=62062
ACESTREAM_HTTP_PORT=6878
```

**Opción B - Usar modo host (más fácil en Linux):**

Edita `docker-compose.yml` y cambia:
```yaml
services:
  httpaceproxy:
    network_mode: host
    # Comenta o elimina la sección ports: cuando uses network_mode: host
    # También comenta la sección networks:
```

Luego en `.env`:
```bash
ACESTREAM_HOST=127.0.0.1
ACESTREAM_API_PORT=62062
ACESTREAM_HTTP_PORT=6878
```

### Opción 3: En otra máquina de tu red

Si Ace Stream está en otra máquina (ej: 192.168.1.50):

**Edita el archivo `.env`:**
```bash
ACESTREAM_HOST=192.168.1.50
ACESTREAM_API_PORT=62062
ACESTREAM_HTTP_PORT=6878
```

## 📝 Guía paso a paso

### 1. Averiguar la IP de Ace Stream

**En Mac:**
```bash
# Ace Stream en tu Mac, usa:
ACESTREAM_HOST=host.docker.internal
```

**En Linux:**
```bash
# Averiguar IP del gateway de Docker
docker network inspect bridge | grep Gateway

# O si Ace Stream está en el host, usa:
hostname -I | awk '{print $1}'
```

**En Windows:**
```bash
# Ace Stream en tu Windows, usa:
ACESTREAM_HOST=host.docker.internal
```

### 2. Verificar que Ace Stream está corriendo

**Verificar desde tu máquina host:**
```bash
# Verificar puerto API
curl http://localhost:62062/webui/api/service?method=get_version

# Debería devolver algo como: {"result": {"version": "3.2.13"}}
```

**Verificar desde dentro del contenedor Docker:**
```bash
# Primero, inicia el contenedor
docker-compose up -d

# Entra al contenedor
docker-compose exec httpaceproxy /bin/bash

# Dentro del contenedor, verifica la conexión
curl http://$ACESTREAM_HOST:$ACESTREAM_API_PORT/webui/api/service?method=get_version

# Salir del contenedor
exit
```

### 3. Editar el archivo .env

```bash
# Copia el ejemplo si no existe
cp .env.example .env

# Edita según tu caso
nano .env
# o
vi .env
```

### 4. Reiniciar el contenedor

```bash
# Si ya estaba corriendo
docker-compose restart

# O detener y volver a iniciar
docker-compose down
docker-compose up -d
```

### 5. Verificar en los logs

```bash
# Ver los logs
docker-compose logs -f

# Deberías ver algo como:
# "Remote AceStream engine ver.3.2.13 will be used on <IP>:62062"
```

## 🐛 Solución de problemas

### Error: "AceStream not found!"

Significa que HTTPAceProxy no puede conectarse a Ace Stream.

**Verifica:**

1. **¿Ace Stream está corriendo?**
   ```bash
   # En tu máquina host
   curl http://localhost:62062/webui/api/service?method=get_version
   ```

2. **¿La IP es correcta?**
   - En Mac/Windows con Docker Desktop: usa `host.docker.internal`
   - En Linux: usa `172.17.0.1` o la IP de tu host
   - En otra máquina: usa la IP de esa máquina

3. **¿El firewall bloquea la conexión?**
   ```bash
   # En Mac, permitir conexiones a Ace Stream
   # System Preferences → Security & Privacy → Firewall

   # En Linux, verificar iptables
   sudo iptables -L
   ```

4. **¿Los puertos son correctos?**
   - Puerto API: 62062 (por defecto)
   - Puerto HTTP: 6878 (por defecto)

### Error: "Connection refused"

**En Mac/Windows:**
```bash
# Verifica que host.docker.internal funciona
docker run --rm alpine ping -c 1 host.docker.internal
```

**En Linux:**
```bash
# Intenta con la IP del gateway
docker network inspect bridge | grep Gateway

# O usa network_mode: host en docker-compose.yml
```

### Verificar conectividad desde el contenedor

```bash
# Entrar al contenedor
docker-compose exec httpaceproxy /bin/bash

# Probar conexión
ping $ACESTREAM_HOST
curl http://$ACESTREAM_HOST:$ACESTREAM_API_PORT/webui/api/service?method=get_version

# Verificar variables de entorno
echo $ACESTREAM_HOST
echo $ACESTREAM_API_PORT
```

## 📋 Resumen de configuraciones comunes

### Mac con Docker Desktop
```bash
ACESTREAM_HOST=host.docker.internal
```

### Windows con Docker Desktop
```bash
ACESTREAM_HOST=host.docker.internal
```

### Linux - Opción 1 (bridge)
```bash
ACESTREAM_HOST=172.17.0.1
```

### Linux - Opción 2 (host mode)
En docker-compose.yml:
```yaml
network_mode: host
```
En .env:
```bash
ACESTREAM_HOST=127.0.0.1
```

### Ace Stream en otra máquina
```bash
ACESTREAM_HOST=192.168.1.50  # IP de la máquina con Ace Stream
```

## 🔗 Links útiles

- [Docker networking docs](https://docs.docker.com/network/)
- [host.docker.internal](https://docs.docker.com/desktop/networking/#i-want-to-connect-from-a-container-to-a-service-on-the-host)
- [Ace Stream documentation](http://acestream.org/)
