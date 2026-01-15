# Configuración de Nginx Proxy Manager para HTTPAceProxy

Esta guía explica cómo configurar **Nginx Proxy Manager (NPM)** para funcionar correctamente con HTTPAceProxy y permitir streaming de larga duración.

## 🔴 Problema Original

Al acceder a HTTPAceProxy a través de NPM, el streaming se detenía inmediatamente:

```
[10:26:32] Streaming started
[10:26:32] >>> STOP  ← Se detiene inmediatamente
[10:26:32] Streaming finished
[10:26:32] Disconnected
```

**Causa:** NPM estaba cerrando las conexiones prematuramente con `Connection: close` y usando configuraciones incompatibles con streaming de larga duración (HTTP/2, timeouts cortos, buffering activado).

---

## ✅ Solución: Configuración NPM

### 1. Pestaña "Details"

**Domain Names:**
```
your-domain.com
```

**Scheme:**
```
http
```

**Forward Hostname / IP:**
```
HTTPACEPROXY_SERVER_IP  (la IP interna donde corre HTTPAceProxy)
```

**Forward Port:**
```
8888
```

**Access List:**
```
Publicly Accessible
```

**Options:**
- ❌ Cache Assets: **DESACTIVADO**
- ❌ Block Common Exploits: **DESACTIVADO**
- ❌ Websockets Support: **DESACTIVADO** ⚠️ (Causa problemas con streaming)

---

### 2. Pestaña "SSL"

**SSL Certificate:**
```
your-domain.com (tu certificado Let's Encrypt)
```

**Opciones SSL:**
- ✅ **Force SSL: ACTIVADO** (redirige HTTP → HTTPS)
- ❌ **HTTP/2 Support: DESACTIVADO** ⚠️ (Incompatible con streaming largo)
- ❌ **HSTS Enabled: DESACTIVADO**
- ❌ **HSTS Sub-domains: DESACTIVADO**

> **Importante:** HTTP/2 usa multiplexing que puede interferir con streams de larga duración. HTTP/1.1 es más confiable para este caso.

---

### 3. Pestaña "Custom Nginx Configuration" (⚙️)

Añade esta configuración en el campo **"Custom Nginx Configuration"**:

```nginx
# CRÍTICO: Usar HTTP/1.1 y mantener conexiones vivas
proxy_http_version 1.1;

# NO forzar Connection: close - dejar que el cliente controle
proxy_set_header Connection "";
proxy_set_header Upgrade $http_upgrade;

# Timeouts LARGOS para streaming (1 hora)
proxy_connect_timeout 3600s;
proxy_send_timeout 3600s;
proxy_read_timeout 3600s;
send_timeout 3600s;

# CRÍTICO: Deshabilitar COMPLETAMENTE el buffering
proxy_buffering off;
proxy_request_buffering off;
proxy_max_temp_file_size 0;

# Headers necesarios
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

# No limitar tamaño del cuerpo
client_max_body_size 0;
client_body_timeout 3600s;

# Mantener la conexión activa
keepalive_timeout 3600s;

# No comprimir video
gzip off;
```

---

## 📝 Explicación Técnica

### ¿Por qué funciona esta configuración?

| Directiva | Valor | Razón |
|-----------|-------|-------|
| `proxy_http_version 1.1` | HTTP/1.1 | HTTP/2 multiplexing causa problemas con streams largos |
| `proxy_set_header Connection ""` | Vacío | NO forzar `Connection: close`, dejar que el cliente controle |
| `proxy_buffering off` | OFF | Sin buffering = latencia baja, streaming en tiempo real |
| `proxy_read_timeout 3600s` | 1 hora | Permitir streams largos sin desconexión |
| `keepalive_timeout 3600s` | 1 hora | Mantener conexión TCP abierta durante el stream |
| `gzip off` | OFF | No comprimir video (ya está comprimido) |
| `client_max_body_size 0` | Sin límite | Permitir transferencias grandes |

### Configuraciones problemáticas

❌ **NO activar:**
- **Websockets Support**: Interfiere con el streaming HTTP normal
- **HTTP/2 Support**: Multiplexing incompatible con streams de larga duración
- **HSTS Enabled**: No necesario y puede causar problemas de cache
- **Cache Assets**: Nunca cachear streams en vivo
- **Block Common Exploits**: Puede bloquear peticiones legítimas de streaming

---

## 🧪 Verificación

### 1. Verificar que funciona localmente

Desde el servidor donde corre HTTPAceProxy:

```bash
curl -I http://localhost:8888/stat
```

Deberías ver:
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
```

### 2. Verificar acceso directo (sin NPM)

```bash
curl -I http://IP_DEL_SERVIDOR:8888/stat
```

Si esto funciona pero a través de NPM no, el problema está en la configuración del proxy.

### 3. Verificar a través de NPM

```bash
curl -I https://your-domain.com/stat
```

Deberías ver una redirección a HTTPS y luego:
```
HTTP/2 200
content-type: text/html; charset=utf-8
```

### 4. Probar streaming

En VLC:
```
Media → Open Network Stream
URL: https://your-domain.com/content_id/HASH/stream.ts
```

Verifica en los logs de HTTPAceProxy:
```bash
docker logs httpaceproxy -f
```

Deberías ver:
```
[IP]: Streaming started
STATUS main:dl;...  ← Estado de descarga activo
STATUS main:dl;...  ← Continúa descargando
```

**NO debería aparecer:**
```
>>> STOP  ← Esto indica desconexión prematura
Streaming finished (inmediatamente después de started)
```

---

## 🐛 Troubleshooting

### Problema: Streaming se detiene inmediatamente

**Síntomas:**
```
[10:26:32] Streaming started
[10:26:32] >>> STOP
[10:26:32] Streaming finished
```

**Soluciones:**
1. ✅ Verificar que HTTP/2 Support está **DESACTIVADO**
2. ✅ Verificar que Websockets Support está **DESACTIVADO**
3. ✅ Verificar que la configuración custom está aplicada
4. 🔄 Reiniciar NPM: `docker restart nginxproxymanager`
5. 🧪 Probar acceso directo para descartar problemas del proxy

### Problema: Error "Connection: close" en headers

**Causa:** NPM está forzando `Connection: close` en lugar de mantener la conexión abierta.

**Solución:** Verificar que la configuración custom incluye:
```nginx
proxy_set_header Connection "";
```

### Problema: Timeout después de 60 segundos

**Causa:** Timeouts por defecto de nginx son muy cortos (60s).

**Solución:** Aumentar todos los timeouts a 3600s (1 hora):
```nginx
proxy_connect_timeout 3600s;
proxy_send_timeout 3600s;
proxy_read_timeout 3600s;
```

### Problema: Buffering causa latencia alta

**Causa:** Nginx está bufferizando el stream antes de enviarlo al cliente.

**Solución:** Deshabilitar completamente el buffering:
```nginx
proxy_buffering off;
proxy_request_buffering off;
proxy_max_temp_file_size 0;
```

---

## 🔗 URLs de Ejemplo

Una vez configurado correctamente, puedes acceder a:

**Estadísticas:**
```
https://your-domain.com/stat
```

**Playlist NewEra (322 canales):**
```
https://your-domain.com/newera.m3u8
```

**Playlist Elcano (68 canales):**
```
https://your-domain.com/elcano.m3u8
```

**Canal individual:**
```
https://your-domain.com/newera/channel/DAZN%201%20FHD.m3u8
```

**Content ID directo:**
```
https://your-domain.com/content_id/24f940fef7e270b6b3ae5d9dc713a80c8345cfba/stream.ts
```

---

## ⚙️ Configuración Completa de Referencia

### Proxy Host en NPM

```yaml
Domain Names: your-domain.com
Scheme: http
Forward Hostname: YOUR_SERVER_IP
Forward Port: 8888
Access List: Publicly Accessible

Options:
  Cache Assets: OFF
  Block Common Exploits: OFF
  Websockets Support: OFF

SSL:
  Force SSL: ON
  HTTP/2 Support: OFF
  HSTS Enabled: OFF
  HSTS Sub-domains: OFF
```

### Custom Nginx Configuration (completa)

```nginx
# HTTP/1.1 con keepalive
proxy_http_version 1.1;
proxy_set_header Connection "";
proxy_set_header Upgrade $http_upgrade;

# Timeouts largos (1 hora)
proxy_connect_timeout 3600s;
proxy_send_timeout 3600s;
proxy_read_timeout 3600s;
send_timeout 3600s;

# Sin buffering
proxy_buffering off;
proxy_request_buffering off;
proxy_max_temp_file_size 0;

# Headers
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;

# Sin límites
client_max_body_size 0;
client_body_timeout 3600s;
keepalive_timeout 3600s;

# Sin compresión
gzip off;
```

---

## 📚 Referencias

- [Configuración de Plugins](PLUGINS.md)
- [Guía de Uso](USAGE.md)
- [Setup de Ace Stream](ACESTREAM-SETUP.md)
- [Inicio Rápido](QUICKSTART.md)

---

## 💡 Alternativa: Nginx Standalone

Si NPM sigue dando problemas, puedes usar nginx standalone con esta configuración:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://YOUR_SERVER_IP:8888;
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        proxy_buffering off;
        proxy_request_buffering off;

        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_read_timeout 3600s;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        client_max_body_size 0;
        gzip off;
    }
}
```

O usar **Caddy** (configuración más simple):

```caddy
your-domain.com {
    reverse_proxy YOUR_SERVER_IP:8888 {
        flush_interval -1
        transport http {
            read_timeout 3600s
            write_timeout 3600s
        }
    }
}
```

---

**Última actualización:** 2026-01-15
**Versión HTTPAceProxy:** Compatible con todas las versiones
**Versión NPM:** 2.x+
