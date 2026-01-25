# Plugins de HTTPAceProxy

HTTPAceProxy incluye tres plugins personalizados para listas de canales de Ace Stream.

## 📺 Plugin NewEra

Plugin que proporciona acceso a una lista extensa de canales deportivos.

### Características:
- **322 canales** de deportes
- Actualización automática cada 30 minutos
- Múltiples categorías: La Liga, Champions, DAZN, NBA, UFC, F1, etc.
- Soporte para guía de TV (EPG)

### URLs de acceso:

**Playlist completa:**
```
http://localhost:8888/newera
```

**Canal individual:**
```
http://localhost:8888/newera/channel/DAZN%201%20FHD%20--%3E%20NEW%20ERA.m3u8
http://localhost:8888/newera/channel/DAZN%201%20FHD%20--%3E%20NEW%20ERA.ts
```

### Configuración:

**Opción 1: Variable de entorno (Docker - Recomendado):**

```yaml
environment:
  - NEWERA_PLAYLIST_URL=https://tu-url-personalizada/playlist.m3u
```

**Opción 2: Archivo de configuración:**

Edita `plugins/config/newera.py` para cambiar:
- URL de la playlist (o usa la variable de entorno `NEWERA_PLAYLIST_URL`)
- Frecuencia de actualización (updateevery)
- URL de la guía de TV (tvgurl)

**URL por defecto:**
```
https://ipfs.io/ipns/<IDIPFS>/data/listas/lista_fuera_iptv.m3u
```

### Categorías disponibles:
- 1RFEF - Primera Federación
- BUNDESLIGA - Liga alemana
- DAZN - Canales DAZN
- DEPORTES - Deportes generales
- EUROSPORT - Canales Eurosport
- EVENTOS - Eventos especiales
- FORMULA 1 - Fórmula 1
- FUTBOL INT - Fútbol internacional
- HYPERMOTION - Segunda división
- LA LIGA - Primera división española
- LIGA DE CAMPEONES - Champions League
- LIGA ENDESA - Baloncesto español
- MOTOR - Deportes de motor
- MOVISTAR - Canales Movistar
- MOVISTAR DEPORTES
- NBA - Baloncesto americano
- OTROS
- SPORT TV - Sport TV Portugal
- TDT - Canales TDT
- TENNIS - Tenis
- UFC - Artes marciales mixtas

---

## 🚢 Plugin Elcano

Plugin alternativo con una lista curada de canales deportivos.

### Características:
- **68 canales** de deportes seleccionados
- Actualización automática cada 30 minutos
- Categorías principales de deportes
- Soporte para guía de TV (EPG)

### URLs de acceso:

**Playlist completa:**
```
http://localhost:8888/elcano
```

**Canal individual:**
```
http://localhost:8888/elcano/channel/Eurosport%201.m3u8
http://localhost:8888/elcano/channel/M+%20LaLiga.ts
```

### Configuración:

**Opción 1: Variable de entorno (Docker - Recomendado):**

```yaml
environment:
  - ELCANO_PLAYLIST_URL=https://tu-url-personalizada/playlist.m3u
```

**Opción 2: Archivo de configuración:**

Edita `plugins/config/elcano.py` para cambiar:
- URL de la playlist (o usa la variable de entorno `ELCANO_PLAYLIST_URL`)
- Frecuencia de actualización (updateevery)
- URL de la guía de TV (tvgurl)

**URL por defecto:**
```
https://acestream-ids.vercel.app/hashes_acestream.m3u
```

**URL anterior (guardada como backup en el código):**
```
https://ipfs.io/ipns/<IDIPFS>/hashes_acestream.m3u
```

### Categorías disponibles:
- EUROSPORT
- DEPORTES
- MOVISTAR DEPORTES
- FORMULA 1
- LA LIGA
- LIGA DE CAMPEONES
- DAZN
- LIGA ENDESA
- Y más...

---

## 🌐 Plugin AcePL

Plugin que obtiene canales directamente desde la API oficial de Acestream.

### Características:
- **1000+ canales** de múltiples categorías
- Actualización automática cada 30 minutos desde la API de Acestream
- Categorías: Sport, Movies, Regional, y más
- Filtrado por disponibilidad (availability)
- Filtrado por categorías
- Datos en tiempo real desde Acestream API

### URLs de acceso:

**Playlist completa:**
```
http://localhost:8888/acepl
```

**Canal individual:**
```
http://localhost:8888/acepl/channel/M.%20Liga%20de%20Campeones.m3u8
http://localhost:8888/acepl/channel/DAZN%201%20Bar%20HD%20%5BDE%5D.ts
```

### Configuración:

Edita `plugins/config/acepl.py` para cambiar:

**URL de la API:**
```python
url = 'https://api.acestream.me/all?api_version=1.0&api_key=test_api_key'
```

**Frecuencia de actualización:**
```python
updateevery = 30  # minutos (0 = solo al inicio)
```

**Filtrado por disponibilidad mínima:**
```python
# Solo incluir canales con al menos 70% de disponibilidad
min_availability = 0.7  # 0.0 a 1.0 (0.0 = todos los canales)
```

**Filtrado por categorías:**
```python
# Opción 1: Todos los canales (por defecto)
categories_filter = []

# Opción 2: Solo canales de deportes
categories_filter = ['sport']

# Opción 3: Deportes y películas
categories_filter = ['sport', 'movies']
```

### Categorías disponibles:
- **sport** - Canales deportivos (fútbol, baloncesto, etc.)
- **movies** - Películas y series
- **regional** - Canales regionales de diferentes países
- **Y más categorías...**

### Datos del canal:

Cada canal incluye:
- **name**: Nombre del canal
- **infohash**: Hash único de Acestream
- **availability**: Disponibilidad del canal (0.0 a 1.0)
- **categories**: Categorías del canal
- **availability_updated_at**: Timestamp de última actualización

### Ejemplos de uso:

**1. Solo canales deportivos con alta disponibilidad:**
```python
# En plugins/config/acepl.py
min_availability = 0.8
categories_filter = ['sport']
```

**2. Todos los canales con disponibilidad mínima:**
```python
min_availability = 0.5
categories_filter = []
```

**3. Películas y series de alta calidad:**
```python
min_availability = 0.9
categories_filter = ['movies']
```

---

## 🔧 Uso general

### En VLC:
```
Media → Open Network Stream
URL: http://localhost:8888/newera
URL: http://localhost:8888/elcano
URL: http://localhost:8888/acepl
```

### En KODI:
```
Add-ons → PVR IPTV Simple Client
M3U Play List URL: http://localhost:8888/newera
M3U Play List URL: http://localhost:8888/elcano
M3U Play List URL: http://localhost:8888/acepl
```

### En cualquier app IPTV:
Usa las URLs directamente en tu aplicación favorita.

### Desde navegador:
Simplemente abre las URLs en tu navegador:
- http://localhost:8888/newera
- http://localhost:8888/elcano
- http://localhost:8888/acepl

---

## 📊 Comparación

| Característica | NewEra | Elcano | AcePL |
|----------------|--------|--------|-------|
| Canales | 322 | 68 | 1000+ |
| Categorías | 23 | 15 | Múltiples |
| Actualización | 30 min | 30 min | 30 min |
| EPG | ✅ | ✅ | ❌ |
| M3U8 | ✅ | ✅ | ✅ |
| Fuente | IPFS | IPFS | Acestream API |
| Filtrado | ❌ | ❌ | ✅ (availability + categorías) |
| Enfoque | Deportes España | Deportes curados | Global (todos los idiomas) |

---

## 🔄 Actualización de playlists

Los tres plugins actualizan automáticamente las listas cada 30 minutos. Puedes cambiar esta frecuencia editando los archivos de configuración:

```python
# En plugins/config/newera.py, plugins/config/elcano.py o plugins/config/acepl.py
updateevery = 30  # minutos (0 = solo al inicio)
```

---

## 🐛 Troubleshooting

### El plugin no carga:
```bash
# Ver logs
docker logs -f httpaceproxy

# Verificar que el plugin está activo
docker logs httpaceproxy | grep "Plugin loaded"
```

### Los canales no reproducen:
1. Verifica que Ace Stream Engine está corriendo
2. Comprueba la conexión en los logs
3. Prueba accediendo directamente al ID de Ace Stream

### Error 404 en canal específico:
- Verifica que el nombre del canal es correcto
- Los nombres deben estar URL-encoded
- Ejemplo: `M+ LaLiga` → `M%2B%20LaLiga`

---

## 📝 Notas

- **NewEra** y **Elcano** descargan las listas desde IPFS
- **AcePL** obtiene los canales desde la API oficial de Acestream
- Las listas se actualizan automáticamente
- Los tres plugins pueden coexistir sin problemas
- Soportan tanto formato .ts como .m3u8
- Incluyen compresión gzip automática
- Compatible con todas las apps IPTV estándar
- **AcePL** permite filtrado avanzado por disponibilidad y categorías

---

## 🔗 URLs de las fuentes originales

**NewEra (IPFS):**
```
https://ipfs.io/ipns/<IDIPFS>/data/listas/lista_fuera_iptv.m3u
```

**Elcano (IPFS):**
```
https://ipfs.io/ipns/<IDIPFS>/hashes_acestream.m3u
```

**AcePL (API):**
```
https://api.acestream.me/all?api_version=1.0&api_key=test_api_key
```
