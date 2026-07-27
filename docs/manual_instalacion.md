# Manual de instalación

Estos pasos se ejecutan **dentro de la máquina virtual Linux**, ya sea directamente o mediante una conexión remota (SSH / VS Code Remote-SSH). Antes de comenzar, revisa los [Requisitos previos](../README.md#requisitos-previos) en el README.

## 1. Clonar el repositorio

```bash
git clone https://github.com/saraycanarteg/Mini-Monitor.git
cd Mini-Monitor
```

## 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

## 4. Inicializar la base de datos

Si el archivo `db/monitor.db` no existe aún, crearlo a partir del esquema:

```bash
sqlite3 db/monitor.db < db/schema.sql
```

Verifica que las tablas se hayan creado correctamente:

```bash
sqlite3 db/monitor.db ".tables"
```

Deberías ver: `interfaces_red`, `monitoreos`, `procesos`, `usuarios_conectados`.
