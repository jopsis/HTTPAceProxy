# Configuración de Límites de Conexión

HTTPAceProxy permite configurar límites de conexión para controlar cuántos clientes pueden conectarse simultáneamente y cuántos canales diferentes pueden transmitirse al mismo tiempo.

## 📊 Conceptos Clave

### MAX_CONNECTIONS
**Qué es:** Número máximo total de conexiones de clientes simultáneas.

**Incluye:**
- Todos los clientes conectados
- Independientemente del canal que estén viendo
- Conexiones activas en tiempo real

**Ejemplo:**
- `MAX_CONNECTIONS=50` → Máximo 50 clientes conectados al mismo tiempo
- Puede ser 50 clientes viendo el mismo canal
- O 5 clientes en 10 canales diferentes (total 50)
- O cualquier combinación que no supere 50

### MAX_CONCURRENT_CHANNELS
**Qué es:** Número máximo de canales **diferentes** transmitiendo simultáneamente.

**Importante:**
- Múltiples clientes viendo el **mismo canal** solo cuentan como **1 canal**
- Cada canal diferente requiere una conexión independiente a AceStream
- Limita la cantidad de streams diferentes, no la cantidad de clientes

**Ejemplo:**
- `MAX_CONCURRENT_CHANNELS=5` → Máximo 5 canales diferentes al mismo tiempo
- ✅ 100 clientes viendo DAZN 1 → Usa 1 slot de canal
- ✅ 20 clientes en DAZN 1 + 30 en Eurosport → Usa 2 slots de canal
- ❌ 6 canales diferentes → Rechazado (límite alcanzado)

## 🔧 Configuración

### Opción 1: Variables de Entorno (Docker) - Recomendado

#### Con docker-compose.yml o docker-compose-aio.yml

Edita tu archivo `docker-compose-aio.yml`:

```yaml
services:
  httproxy:
    environment:
      - ACE_HOST=aceserve
      - ACE_API_PORT=62062
      - ACE_HTTP_PORT=6878
      - MAX_CONNECTIONS=50           # ← Cambia aquí
      - MAX_CONCURRENT_CHANNELS=10   # ← Cambia aquí
```

Luego reinicia:
```bash
docker-compose -f docker-compose-aio.yml restart
```

#### Con Docker run directo

```bash
docker run -d \
  --name httpaceproxy \
  -p 8888:8888 \
  -e ACESTREAM_HOST=127.0.0.1 \
  -e MAX_CONNECTIONS=50 \
  -e MAX_CONCURRENT_CHANNELS=10 \
  jopsis/httpaceproxy:latest
```

#### Con archivo .env

Crea o edita `.env`:
```bash
MAX_CONNECTIONS=50
MAX_CONCURRENT_CHANNELS=10
```

Asegúrate de que tu `docker-compose.yml` use las variables:
```yaml
environment:
  - MAX_CONNECTIONS=${MAX_CONNECTIONS:-10}
  - MAX_CONCURRENT_CHANNELS=${MAX_CONCURRENT_CHANNELS:-5}
```

### Opción 2: Archivo aceconfig.py (Sin Docker)

Edita `aceconfig.py`:

```python
class AceConfig(acedefconfig.AceDefConfig):
    # Connection limits
    maxconns = 50                   # Máximo de conexiones totales
    maxconcurrentchannels = 10      # Máximo de canales simultáneos
```

Reinicia el servidor:
```bash
# Si usas systemd
sudo systemctl restart httpaceproxy

# Si ejecutas manualmente
# Ctrl+C y luego:
python acehttp.py
```

## 📋 Guía de Configuración por Caso de Uso

### Uso Personal (1-5 usuarios)
**Escenario:** Tú y tu familia viendo canales ocasionalmente.

```yaml
environment:
  - MAX_CONNECTIONS=10
  - MAX_CONCURRENT_CHANNELS=3
```

**Capacidad:**
- Hasta 10 dispositivos conectados simultáneamente
- Hasta 3 canales diferentes al mismo tiempo
- Ejemplo: Sala (DAZN 1), Habitación 1 (Eurosport), Habitación 2 (La Liga TV)

---

### Uso Familiar/Grupo Pequeño (5-15 usuarios)
**Escenario:** Grupo de amigos o familia extendida compartiendo el servicio.

```yaml
environment:
  - MAX_CONNECTIONS=25
  - MAX_CONCURRENT_CHANNELS=5
```

**Capacidad:**
- Hasta 25 dispositivos conectados
- Hasta 5 canales diferentes simultáneos
- Ejemplo: 5 partidos diferentes con 5 espectadores cada uno

---

### Servidor Compartido (15-50 usuarios)
**Escenario:** Comunidad de usuarios o servidor semi-público.

```yaml
environment:
  - MAX_CONNECTIONS=100
  - MAX_CONCURRENT_CHANNELS=15
```

**Capacidad:**
- Hasta 100 clientes conectados
- Hasta 15 canales diferentes simultáneos
- Recomendado: Servidor con al menos 4GB RAM y 50Mbps de ancho de banda

---

### Servidor Público (50+ usuarios)
**Escenario:** Servicio público o comercial con muchos usuarios.

```yaml
environment:
  - MAX_CONNECTIONS=200
  - MAX_CONCURRENT_CHANNELS=20
```

**Capacidad:**
- Hasta 200 clientes conectados
- Hasta 20 canales diferentes simultáneos
- Recomendado: Servidor dedicado con 8GB+ RAM y 100Mbps+ de ancho de banda

## 📊 Ejemplos de Escenarios

### Escenario 1: Evento Deportivo Popular
**Situación:** 100 usuarios viendo el mismo partido (DAZN 1)

```yaml
environment:
  - MAX_CONNECTIONS=100
  - MAX_CONCURRENT_CHANNELS=5
```

**Resultado:**
- ✅ Usa 1 canal (todos ven lo mismo)
- ✅ 100 conexiones activas
- ✅ Recursos: Solo 1 conexión a AceStream necesaria
- ✅ Quedan 4 slots de canal disponibles para otros canales

---

### Escenario 2: Múltiples Partidos Simultáneos
**Situación:** 10 partidos diferentes, 5 usuarios viendo cada uno

```yaml
environment:
  - MAX_CONNECTIONS=50
  - MAX_CONCURRENT_CHANNELS=10
```

**Resultado:**
- ✅ Usa 10 canales (todos los partidos)
- ✅ 50 conexiones activas
- ✅ Recursos: 10 conexiones a AceStream necesarias
- ✅ Límite de canales alcanzado, no se pueden abrir más canales

---

### Escenario 3: Límite de Conexiones Alcanzado
**Situación:** 51º cliente intenta conectarse con MAX_CONNECTIONS=50

```yaml
environment:
  - MAX_CONNECTIONS=50
  - MAX_CONCURRENT_CHANNELS=10
```

**Resultado:**
- ❌ Cliente 51 es rechazado
- ℹ️ Mensaje: "Maximum connections reached"
- ✅ Los 50 clientes existentes continúan sin problemas

---

### Escenario 4: Límite de Canales Alcanzado
**Situación:** Intento de abrir el canal 11 con MAX_CONCURRENT_CHANNELS=10

```yaml
environment:
  - MAX_CONNECTIONS=100
  - MAX_CONCURRENT_CHANNELS=10
```

**Resultado:**
- ❌ El nuevo canal es rechazado
- ℹ️ Debe esperar a que se cierre un canal existente
- ✅ Los 10 canales activos continúan normalmente

## 🔍 Verificación

### Ver configuración actual

**Desde logs del contenedor:**
```bash
docker-compose logs httpaceproxy | grep "Connection Limits"
```

Deberías ver:
```
Connection Limits:
  Max Connections: 50
  Max Concurrent Channels: 10
```

**Desde el dashboard:**
Accede a `http://localhost:8888/stat` y verás:
- Conexiones activas vs máximo
- Canales activos vs máximo

### Monitorear uso en tiempo real

```bash
# Ver logs en tiempo real
docker-compose logs -f httpaceproxy

# Ver estadísticas
curl http://localhost:8888/stat
```

## ⚠️ Consideraciones Importantes

### Recursos del Servidor

**RAM requerida (aproximadamente):**
- Por canal: ~100-200MB
- Por cliente: ~5-10MB
- Sistema base: ~200MB

**Ejemplo:** Para 10 canales y 50 clientes:
```
RAM = 200MB (base) + (10 * 150MB) + (50 * 7.5MB)
RAM = 200 + 1500 + 375 = ~2GB
```

**Recomendación:** Servidor con al menos el doble de RAM calculada.

### Ancho de Banda

**Por canal AceStream:**
- Calidad HD: 3-5 Mbps
- Calidad FHD: 6-10 Mbps
- Calidad 4K: 15-25 Mbps

**Por cliente:** Similar al canal (depende de la calidad del stream)

**Ejemplo:** 5 canales FHD con 20 clientes cada uno:
```
Upstream: 5 canales * 8 Mbps = 40 Mbps (desde AceStream)
Downstream: 100 clientes * 8 Mbps = 800 Mbps (hacia clientes)
```

**Nota:** Si todos los clientes están en la misma red local, el downstream no afecta tu conexión a Internet.

### Límites del Motor AceStream

El motor AceStream (AceServe) también tiene sus propios límites:
- Típicamente puede manejar 5-10 canales simultáneos
- Depende de los recursos del servidor
- Monitorea el uso de CPU y RAM del contenedor `aceserve`

## 🆘 Troubleshooting

### Problema: "Maximum connections reached"

**Causa:** Se alcanzó el límite de `MAX_CONNECTIONS`

**Solución:**
1. Aumenta el valor:
   ```yaml
   - MAX_CONNECTIONS=100
   ```
2. Verifica que tienes suficientes recursos (RAM, CPU)
3. Reinicia el contenedor

### Problema: "Cannot start broadcast - channel limit reached"

**Causa:** Se alcanzó el límite de `MAX_CONCURRENT_CHANNELS`

**Solución:**
1. Aumenta el valor:
   ```yaml
   - MAX_CONCURRENT_CHANNELS=15
   ```
2. O espera a que se cierre un canal inactivo (timeout automático)
3. Verifica recursos del servidor AceStream

### Problema: Alto uso de RAM

**Causa:** Demasiados canales o clientes para los recursos disponibles

**Solución:**
1. Reduce los límites:
   ```yaml
   - MAX_CONNECTIONS=50
   - MAX_CONCURRENT_CHANNELS=5
   ```
2. Actualiza el servidor (más RAM)
3. Monitorea el uso con `docker stats`

### Problema: Streams se cortan o buffering constante

**Causa:** Insuficiente ancho de banda o CPU

**Solución:**
1. Reduce el número de canales simultáneos
2. Verifica el ancho de banda disponible
3. Monitorea el uso de CPU del contenedor aceserve

## 📚 Referencias

- **Configuración general:** [README.md](README.md)
- **Setup de Docker:** [README.Docker.md](README.Docker.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Variables de entorno:** [.env.example](.env.example)

## 💡 Consejos

1. **Empieza conservador:** Usa valores bajos y aumenta gradualmente según necesidad
2. **Monitorea recursos:** Usa `docker stats` para ver uso de RAM y CPU
3. **Prueba con carga:** Simula tu caso de uso antes de ir a producción
4. **Documenta tu configuración:** Guarda los valores que funcionan para tu caso
5. **Backups:** Si usas volúmenes, haz backups de tu configuración
