# Gestion de Plugins

HTTPAceProxyCPP carga plugins en el arranque. La seleccion se controla con variables de entorno y no requiere editar codigo ni archivos Python.

## Plugins Disponibles

| Plugin | Tipo | Endpoint | Notas |
|--------|------|----------|-------|
| `newera` | Playlist | `/newera` | Lista M3U deportiva desde IPFS. |
| `elcano` | Playlist | `/elcano` | Lista M3U deportiva curada desde IPFS. |
| `acepl` | Playlist | `/acepl` | Catalogo desde la API publica de AceStream. |
| `af1c1onados` | Playlist | `/af1c1onados` | Lista JSON organizada por grupos; usa fallback por catalogo GitHub. |
| `aio` | Playlist agregada | `/aio` | Combina canales de los plugins activos. |
| `stat` | UI/API | `/stat` | Dashboard de estado, clientes y recursos. |
| `statplugin` | UI/API | `/statplugin` | Navegador de canales y comprobaciones. |

Los recuentos de canales son dinamicos porque dependen de fuentes externas.

## ENABLED_PLUGINS

Controla que plugins se cargan:

```env
ENABLED_PLUGINS=all
```

Valores:

- `all`: carga todos los plugins disponibles.
- Lista separada por comas: carga solo esos plugins.
- Valor vacio: no carga plugins. El proxy basico sigue funcionando para rutas directas como `/content_id/HASH/stream.ts`.

Ejemplos:

```env
ENABLED_PLUGINS=newera,elcano,acepl,stat,statplugin
ENABLED_PLUGINS=af1c1onados,aio,stat,statplugin
ENABLED_PLUGINS=stat,statplugin
ENABLED_PLUGINS=
```

Los nombres no distinguen mayusculas/minusculas y se ignoran espacios alrededor de las comas.

## AIO_PLUGINS

Controla que plugins entran en la lista agregada `/aio`.

```env
AIO_PLUGINS=all
AIO_PLUGINS=newera,elcano,acepl,af1c1onados
```

Notas:

- `aio` solo puede agregar plugins que tambien esten cargados en `ENABLED_PLUGINS`.
- `stat`, `statplugin` y `aio` no se agregan a si mismos.
- Si `AIO_PLUGINS` esta vacio o vale `all`, incluye todos los plugins de playlist cargados.

## URLs Personalizadas

NewEra y Elcano permiten reemplazar la URL de fuente:

```env
NEWERA_PLAYLIST_URL=https://example.net/newera.m3u
ELCANO_PLAYLIST_URL=https://example.net/elcano.m3u
```

Usa estas variables para probar mirrors, fuentes internas o copias propias. Los cambios requieren reiniciar el contenedor.

## User-Agent de los Plugins

Las descargas de los plugins usan por defecto el User-Agent `curl/8.5.0`.

```env
PLUGIN_USER_AGENT=curl/8.5.0
```

Notas:

- Cloudflare (por ejemplo en `ipfs.io`) responde `403 Forbidden` a clientes que dicen ser un navegador pero cuya huella TLS/HTTP no lo es. Por eso el valor por defecto no simula un navegador.
- Si una fuente exige otro valor, defínelo con `PLUGIN_USER_AGENT` (también se acepta `HTTP_USER_AGENT`).
- El cambio requiere reiniciar el contenedor.

## Ejemplos Docker Compose

Solo dashboards:

```yaml
services:
  httpaceproxy:
    environment:
      - ENABLED_PLUGINS=stat,statplugin
```

Listas principales y dashboards:

```yaml
services:
  httpaceproxy:
    environment:
      - ENABLED_PLUGINS=newera,elcano,acepl,af1c1onados,aio,stat,statplugin
      - AIO_PLUGINS=newera,elcano,acepl,af1c1onados
```

Todos los plugins:

```yaml
services:
  httpaceproxy:
    environment:
      - ENABLED_PLUGINS=all
      - AIO_PLUGINS=all
```

## Endpoints por Plugin

Playlist completa:

```text
http://localhost:8888/newera
http://localhost:8888/elcano
http://localhost:8888/acepl
http://localhost:8888/af1c1onados
http://localhost:8888/aio
```

Canal individual:

```text
http://localhost:8888/newera/channel/NOMBRE_CANAL.m3u8
http://localhost:8888/elcano/channel/NOMBRE_CANAL.ts
```

El nombre del canal debe ir URL-encoded si contiene espacios, simbolos o acentos.

## StatPlugin y Comprobaciones

`/statplugin` tiene dos tipos de comprobacion:

- Comprobacion ligera: consulta metadata del contenido contra el engine AceStream.
- Comprobacion de peers: inicia brevemente el stream con `START`, lee estado y hace `STOP`.

La comprobacion de peers puede generar trafico P2P en el engine configurado. Si usas un engine remoto, ese trafico sale desde la maquina remota.

## Troubleshooting

Ver plugins cargados:

```bash
docker logs httpaceproxy
```

Probar una playlist:

```bash
curl -I http://localhost:8888/newera
curl http://localhost:8888/aio | head
```

Si un plugin externo carga cero canales o falla:

- Revisa los logs del contenedor.
- Verifica que la fuente remota responde desde el contenedor.
- Prueba deshabilitar temporalmente el plugin problematico con `ENABLED_PLUGINS`.
