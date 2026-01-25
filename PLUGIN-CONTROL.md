# Control de Plugins

HTTPAceProxy permite habilitar o deshabilitar plugins mediante la variable de entorno `ENABLED_PLUGINS`.

## 🎯 Variable de Entorno

### ENABLED_PLUGINS

Controla qué plugins se cargan al iniciar el servidor.

**Formato:**
```
ENABLED_PLUGINS=plugin1,plugin2,plugin3
```

**Valores posibles:**
- `all` - Habilitar todos los plugins (por defecto)
- `plugin1,plugin2` - Lista separada por comas de plugins específicos
- `""` (vacío) - Deshabilitar todos los plugins

**Nombres de plugins disponibles:**
- `newera` - 322 canales deportivos desde IPFS
- `elcano` - 71 canales curados desde IPFS
- `acepl` - 1000+ canales desde la API de Acestream
- `stat` - Dashboard de estadísticas en tiempo real
- `statplugin` - Navegador de canales con verificación de peers

### NEWERA_PLAYLIST_URL

Permite personalizar la URL de la playlist de NewEra.

**Formato:**
```
NEWERA_PLAYLIST_URL=https://tu-url-personalizada/playlist.m3u
```

**Valor por defecto:**
```
https://ipfs.io/ipns/<IPFSID>/data/listas/lista_fuera_iptv.m3u
```

### ELCANO_PLAYLIST_URL

Permite personalizar la URL de la playlist de Elcano.

**Formato:**
```
ELCANO_PLAYLIST_URL=https://tu-url-personalizada/playlist.m3u
```

**Valor por defecto:**
```
https://<proyecto>-ids.vercel.app/hashes_acestream.m3u
```

**Tipos de URL soportados:**
- URLs HTTPS: `https://ejemplo.com/playlist.m3u`
- URLs IPFS: `https://ipfs.io/ipns/...` o `https://ipfs.io/ipfs/...`
- Archivos locales: `file:///path/to/playlist.m3u`

**Ejemplo combinado:**
```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=newera,elcano,stat,statplugin
      - NEWERA_PLAYLIST_URL=https://mi-servidor.com/newera.m3u
      - ELCANO_PLAYLIST_URL=https://otra-url.com/elcano.m3u
```

**Notas:**
- Si no se especifica, se usa la URL por defecto
- Las URLs personalizadas se muestran en los logs de inicio
- Los cambios requieren reiniciar el contenedor
- Si la URL es inválida o no responde, el plugin no se cargará

## 📋 Ejemplos de Uso

### Configuración en Docker Compose

#### Todos los plugins (default)

```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=all
```

#### Solo plugins de playlists

```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=newera,elcano,acepl
```

#### Solo dashboards (sin playlists)

```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=stat,statplugin
```

#### Solo NewEra y Stats

```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=newera,stat,statplugin
```

#### Solo AcePL (API oficial de Acestream)

```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=acepl,stat,statplugin
```

#### Sin plugins

```yaml
services:
  httproxy:
    environment:
      - ENABLED_PLUGINS=
```

### Configuración con archivo .env

Crea o edita el archivo `.env`:

```bash
# Copiar el ejemplo
cp .env.example .env

# Editar
nano .env
```

Añade o modifica la línea:

```bash
# Todos los plugins
ENABLED_PLUGINS=all

# Solo algunos
ENABLED_PLUGINS=newera,acepl,stat

# Solo stats
ENABLED_PLUGINS=stat,statplugin
```

### Configuración en línea de comandos

```bash
# Al iniciar con docker-compose
ENABLED_PLUGINS=newera,stat docker-compose up -d

# Con docker run
docker run -d \
  -p 8888:8888 \
  -e ENABLED_PLUGINS=newera,acepl,stat \
  jopsis/httpaceproxy:latest
```

## 🔍 Verificación

### Ver plugins habilitados en los logs

Al iniciar el servidor, verás en los logs:

**Si todos están habilitados:**
```
[INFO] All plugins enabled: acepl, elcano, newera, stat, statplugin
```

**Si solo algunos están habilitados:**
```
[INFO] Enabled plugins: acepl, newera, stat
[INFO] Disabled plugins: elcano, statplugin
```

**Si especificas un plugin inválido:**
```
[WARNING] Invalid plugin names in ENABLED_PLUGINS (will be ignored): foo, bar
[WARNING] Available plugins: acepl, elcano, newera, stat, statplugin
[INFO] Enabled plugins: newera
```

### Verificar desde docker-entrypoint

Al iniciar el contenedor, se mostrará la configuración:

```
Configuration:
  HTTPAceProxy:
    Host: 0.0.0.0
    Port: 8888
  Ace Stream Engine:
    Host: aceserve
    API Port: 62062
    HTTP Port: 6878
  Connection Limits:
    Max Connections: 10
    Max Concurrent Channels: 5
  Plugins:
    Enabled: newera,acepl,stat
```

### Verificar logs en tiempo real

```bash
# Docker Compose
docker-compose logs -f httpaceproxy | grep -i plugin

# Docker directo
docker logs -f httpaceproxy | grep -i plugin
```

Deberías ver líneas como:
```
[Newera        ]: Plugin loaded
[Acepl         ]: Plugin loaded
[Stat          ]: Plugin loaded
```

## 📊 Casos de Uso

### Caso 1: Solo quiero estadísticas, sin playlists

**Configuración:**
```yaml
environment:
  - ENABLED_PLUGINS=stat,statplugin
```

**Resultado:**
- ✅ Acceso a `http://localhost:8888/stat`
- ✅ Acceso a `http://localhost:8888/statplugin`
- ❌ No disponible `http://localhost:8888/newera`
- ❌ No disponible `http://localhost:8888/acepl`

### Caso 2: Solo quiero la API oficial (AcePL)

**Configuración:**
```yaml
environment:
  - ENABLED_PLUGINS=acepl,stat,statplugin
```

**Resultado:**
- ✅ Acceso a `http://localhost:8888/acepl` (1000+ canales)
- ✅ Acceso a dashboards
- ❌ No disponible NewEra ni Elcano

### Caso 3: Solo canales españoles (NewEra + Elcano)

**Configuración:**
```yaml
environment:
  - ENABLED_PLUGINS=newera,elcano,stat,statplugin
```

**Resultado:**
- ✅ Acceso a `http://localhost:8888/newera` (322 canales)
- ✅ Acceso a `http://localhost:8888/elcano` (71 canales)
- ✅ Acceso a dashboards
- ❌ No disponible AcePL

### Caso 4: Todos los canales + dashboards

**Configuración:**
```yaml
environment:
  - ENABLED_PLUGINS=all
```

**Resultado:**
- ✅ Todo disponible (configuración por defecto)

### Caso 5: Servidor mínimo (sin plugins)

**Configuración:**
```yaml
environment:
  - ENABLED_PLUGINS=
```

**Resultado:**
- ❌ No hay plugins cargados
- ✅ Solo funcionalidad básica de proxy
- ⚠️ No hay playlists ni dashboards

## 💡 Consejos

### Optimización de recursos

Si solo usas algunos plugins, deshabilita los que no necesitas para:
- **Reducir uso de RAM** - Cada plugin carga canales en memoria
- **Reducir tiempo de inicio** - Menos plugins = inicio más rápido
- **Reducir tráfico de red** - No descarga playlists innecesarias

### Ejemplo de optimización

Si solo usas AcePL:
```yaml
environment:
  - ENABLED_PLUGINS=acepl,stat,statplugin
```

Ahorro estimado:
- RAM: ~50-100MB menos
- Startup: ~5-10 segundos más rápido
- Red: No descarga playlists de IPFS

### Debugging

Para depurar problemas con plugins:

1. **Habilita solo el plugin problemático:**
   ```yaml
   - ENABLED_PLUGINS=newera,stat
   ```

2. **Verifica los logs:**
   ```bash
   docker-compose logs -f | grep Newera
   ```

3. **Prueba uno a uno:**
   ```yaml
   # Prueba 1
   - ENABLED_PLUGINS=newera

   # Prueba 2
   - ENABLED_PLUGINS=acepl
   ```

## ❗ Notas Importantes

### Mayúsculas/minúsculas

Los nombres de plugins **no distinguen mayúsculas/minúsculas**:

```yaml
# Todas estas son equivalentes:
- ENABLED_PLUGINS=newera,acepl
- ENABLED_PLUGINS=NewEra,AcePL
- ENABLED_PLUGINS=NEWERA,ACEPL
```

### Espacios

Los espacios alrededor de comas se ignoran:

```yaml
# Todas estas son equivalentes:
- ENABLED_PLUGINS=newera,acepl,stat
- ENABLED_PLUGINS=newera, acepl, stat
- ENABLED_PLUGINS=newera , acepl , stat
```

### Plugins inválidos

Si especificas un plugin que no existe:

```yaml
- ENABLED_PLUGINS=newera,foobar,acepl
```

Resultado:
```
[WARNING] Invalid plugin names in ENABLED_PLUGINS (will be ignored): foobar
[WARNING] Available plugins: acepl, elcano, newera, stat, statplugin
[INFO] Enabled plugins: acepl, newera
```

El servidor continúa funcionando con los plugins válidos.

### Sin plugins

Si deshabilitas todos los plugins (`ENABLED_PLUGINS=`):

⚠️ **Advertencia:** El servidor funcionará pero no habrá:
- Playlists M3U8
- Dashboards de estadísticas
- Navegador de canales

Solo funcionará el proxy básico para URLs directas tipo:
```
http://localhost:8888/content_id/HASH/stream.ts
```

## 🔗 Referencias

- **Documentación de plugins:** [PLUGINS.md](PLUGINS.md)
- **Configuración general:** [README.md](README.md)
- **Variables de entorno:** [.env.example](.env.example)
- **Setup de Docker:** [README.Docker.md](README.Docker.md)
