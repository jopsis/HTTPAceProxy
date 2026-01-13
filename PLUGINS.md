# Plugins de HTTPAceProxy

HTTPAceProxy incluye dos plugins personalizados para listas de canales de Ace Stream.

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
http://localhost:8888/newera.m3u8
```

**Canal individual:**
```
http://localhost:8888/newera/channel/DAZN%201%20FHD%20--%3E%20NEW%20ERA.m3u8
http://localhost:8888/newera.m3u8/channel/DAZN%201%20FHD%20--%3E%20NEW%20ERA.ts
```

### Configuración:

Edita `plugins/config/newera.py` para cambiar:
- URL de la playlist
- Frecuencia de actualización (updateevery)
- URL de la guía de TV (tvgurl)

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
http://localhost:8888/elcano.m3u8
```

**Canal individual:**
```
http://localhost:8888/elcano/channel/Eurosport%201.m3u8
http://localhost:8888/elcano.m3u8/channel/M+%20LaLiga.ts
```

### Configuración:

Edita `plugins/config/elcano.py` para cambiar:
- URL de la playlist
- Frecuencia de actualización (updateevery)
- URL de la guía de TV (tvgurl)

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

## 🔧 Uso general

### En VLC:
```
Media → Open Network Stream
URL: http://localhost:8888/newera.m3u8
URL: http://localhost:8888/elcano.m3u8
```

### En KODI:
```
Add-ons → PVR IPTV Simple Client
M3U Play List URL: http://localhost:8888/newera.m3u8
M3U Play List URL: http://localhost:8888/elcano.m3u8
```

### En cualquier app IPTV:
Usa las URLs directamente en tu aplicación favorita.

### Desde navegador:
Simplemente abre las URLs en tu navegador:
- http://localhost:8888/newera.m3u8
- http://localhost:8888/elcano.m3u8

---

## 📊 Comparación

| Característica | NewEra | Elcano |
|----------------|--------|--------|
| Canales | 322 | 68 |
| Categorías | 23 | 15 |
| Actualización | 30 min | 30 min |
| EPG | ✅ | ✅ |
| M3U8 | ✅ | ✅ |

---

## 🔄 Actualización de playlists

Ambos plugins actualizan automáticamente las listas cada 30 minutos. Puedes cambiar esta frecuencia editando los archivos de configuración:

```python
# En plugins/config/newera.py o plugins/config/elcano.py
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

- Los plugins descargan las listas desde IPFS
- Las listas se actualizan automáticamente
- Ambos plugins pueden coexistir sin problemas
- Soportan tanto formato .ts como .m3u8
- Incluyen compresión gzip automática
- Compatible con todas las apps IPTV estándar

---

## 🔗 URLs de las listas originales

**NewEra:**
```
https://ipfs.io/ipns/k2k4r8oqlcjxsritt5mczkcn4mmvcmymbqw7113fz2flkrerfwfps004/data/listas/lista_fuera_iptv.m3u
```

**Elcano:**
```
https://ipfs.io/ipns/k51qzi5uqu5di462t7j4vu4akwfhvtjhy88qbupktvoacqfqe9uforjvhyi4wr/hashes_acestream.m3u
```
