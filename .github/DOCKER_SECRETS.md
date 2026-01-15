# Configuración de Secrets para Docker Hub

Para que GitHub Actions pueda publicar imágenes en Docker Hub, necesitas configurar los siguientes secrets en tu repositorio:

## 1. Crear un Access Token en Docker Hub

1. Ve a https://hub.docker.com/settings/security
2. Click en "New Access Token"
3. Nombre: `github-actions-httpaceproxy`
4. Permisos: **Read, Write, Delete**
5. Copia el token generado (solo se muestra una vez)

## 2. Configurar Secrets en GitHub

1. Ve a tu repositorio: https://github.com/jopsis/HTTPAceProxy
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**

### Secrets necesarios:

**Secret 1: DOCKERHUB_USERNAME**
- Name: `DOCKERHUB_USERNAME`
- Value: `jopsis`

**Secret 2: DOCKERHUB_TOKEN**
- Name: `DOCKERHUB_TOKEN`
- Value: `[el token que copiaste de Docker Hub]`

## 3. Verificar configuración

Una vez configurados los secrets, el workflow se ejecutará automáticamente cuando:
- Hagas push a las ramas `master` o `main`
- Crees un tag con formato `v*` (ej: v1.0.0)
- Lo ejecutes manualmente desde la pestaña Actions

## 4. Ejecución manual (opcional)

Para ejecutar el workflow manualmente:
1. Ve a **Actions** en tu repositorio
2. Selecciona "Build and Push Docker Images"
3. Click en "Run workflow"
4. Selecciona la rama
5. Click en "Run workflow"

## Resultado

Las imágenes se publicarán en:
- https://hub.docker.com/r/jopsis/httpaceproxy

Con las siguientes arquitecturas:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM 64-bit, Apple Silicon, Raspberry Pi 4/5)

Tags generados:
- `latest` (última versión de la rama principal)
- `master` o `main` (según la rama)
- `v1.0.0` (si creas tags de versión)
- SHA del commit (para trazabilidad)
