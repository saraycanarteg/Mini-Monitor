# Mini Monitor de Recursos para Linux

Aplicación de monitoreo de recursos del sistema operativo Linux, desarrollada en Python con interfaz TUI (Text User Interface). Permite visualizar en tiempo real el estado de CPU, memoria, disco, procesos, usuarios conectados e interfaces de red, además de gestionar un historial de capturas (snapshots) mediante operaciones CRUD sobre una base de datos SQLite.

Proyecto Integrador — Sistemas Operativos — Carrera de Ingeniería de Software.

## Integrantes

- Saray Adriana Cañarte Galarza — sacanarte@espe.edu.ec
- Doménica Nicole Villagómez Freire — dnvillagomez@espe.edu.ec
- Danny Mateo Ayuquina Navas — dmayuquina@espe.edu.ec

## Características

- **Módulo CPU**: núcleos, frecuencia y carga del sistema, leídos desde `/proc/cpuinfo` y `/proc/loadavg`.
- **Módulo Memoria**: memoria total, usada, libre y swap, leídos desde `/proc/meminfo`.
- **Módulo Disco**: espacio total, usado y libre, obtenido mediante el comando `df`.
- **Módulo Procesos**: PID, nombre, estado y usuario propietario, obtenido mediante el comando `ps`.
- **Módulo Usuarios**: usuarios conectados y tiempo de conexión, obtenido mediante el comando `who`.
- **Módulo Red**: estadísticas de tráfico por interfaz, leídas desde `/proc/net/dev`.
- **Historial (CRUD)**: creación, consulta, edición y eliminación de capturas del sistema, almacenadas en SQLite.
- **Concurrencia**: cada captura se ejecuta en un proceso hijo (`os.fork()`), que a su vez utiliza hilos (`threading.Thread`) para leer CPU y memoria en paralelo.

## Arquitectura

El proyecto está organizado en capas:

```
src/
├── main.py                  # Capa de Presentación (interfaz TUI con textual)
├── main.tcss                # Estilos de la interfaz
├── services/                 # Capa de Aplicación / Servicios
│   └── sistema_service.py   # Agrupa y expone los datos del sistema listos para negocio
├── concurrency/              # Capa de Concurrencia
│   └── snapshot_manager.py  # Orquesta fork() + threading para capturar el sistema
├── repositories/              # Capa de Acceso a Datos
│   └── monitoreo_repository.py  # Operaciones CRUD contra SQLite
└── system/                  # Capa del Sistema Operativo
    ├── procfs_reader.py     # Lectura de /proc (cpuinfo, meminfo, net/dev, loadavg)
    └── shell_executor.py    # Ejecución de comandos (ps, who, df)

db/
└── schema.sql                # Definición de tablas (monitoreos, procesos, usuarios_conectados, interfaces_red)
```

Diagrama de arquitectura completo (PlantUML) disponible en `docs/arquitectura.puml`.

## Requisitos previos

- Máquina virtual con Linux (Ubuntu Desktop).
- Python 3.10 o superior.
- `sqlite3` (cliente de línea de comandos, opcional pero recomendado para inspección manual).
- Acceso a los comandos estándar de Linux: `ps`, `who`, `df`.

## Manual de instalación

Estos pasos se ejecutan **dentro de la máquina virtual Linux**, ya sea directamente o mediante una conexión remota (SSH / VS Code Remote-SSH).

### 1. Clonar el repositorio

```bash
git clone https://github.com/saraycanarteg/Mini-Monitor.git
cd Mini-Monitor
```

### 2. Crear y activar el entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Inicializar la base de datos

Si el archivo `db/monitor.db` no existe aún, crearlo a partir del esquema:

```bash
sqlite3 db/monitor.db < db/schema.sql
```

Verifica que las tablas se hayan creado correctamente:

```bash
sqlite3 db/monitor.db ".tables"
```

Deberías ver: `interfaces_red`, `monitoreos`, `procesos`, `usuarios_conectados`.

## Manual de ejecución

**Cada vez que se vaya a ejecutar la aplicación**, se deben seguir estos dos pasos, en este orden, desde la raíz del proyecto (`Mini-Monitor/`):

```bash
source venv/bin/activate
python3 -m src.main
```

> **Importante:** la aplicación debe ejecutarse siempre con `python3 -m src.main` desde la carpeta raíz del proyecto, y no con `python3 src/main.py` ni desde dentro de la carpeta `src/`, ya que los módulos internos usan rutas de importación absolutas (`from src.system...`, `from src.repositories...`).

Para salir del entorno virtual al terminar:

```bash
deactivate
```

## Uso de la aplicación

Una vez dentro de la interfaz, se navega entre pestañas (Resumen, Procesos, Usuarios, Red, Historial) con las flechas del teclado o el mouse.

| Tecla | Acción |
|---|---|
| `←` / `→` | Cambiar de pestaña |
| `↑` / `↓` | Moverse entre filas de una tabla |
| `r` | Refrescar manualmente los datos en pantalla |
| `c` | Crear una nueva captura del sistema (pestaña Historial) |
| `e` | Editar comentario/etiqueta de la captura seleccionada (pestaña Historial) |
| `d` | Eliminar la captura seleccionada (pestaña Historial) |
| `q` | Salir de la aplicación |

Las pestañas Resumen, Procesos, Usuarios y Red se actualizan automáticamente cada 2 segundos. La pestaña Historial muestra las capturas guardadas en la base de datos y se actualiza tras cada operación de Crear, Editar o Eliminar.

## Estructura de la base de datos

| Tabla | Descripción |
|---|---|
| `monitoreos` | Captura principal: fecha, métricas de CPU/memoria/disco, comentario y etiqueta |
| `procesos` | Procesos activos asociados a una captura |
| `usuarios_conectados` | Usuarios conectados asociados a una captura |
| `interfaces_red` | Estadísticas de red asociadas a una captura |

Las tablas hijas (`procesos`, `usuarios_conectados`, `interfaces_red`) se eliminan automáticamente al borrar una captura (`ON DELETE CASCADE`).

## Solución de problemas

**`ModuleNotFoundError: No module named 'textual'`**
El entorno virtual no está activado. Ejecuta `source venv/bin/activate` antes de correr la aplicación.

**`ModuleNotFoundError: No module named 'src'` o `'system'`**
La aplicación se está ejecutando desde una carpeta distinta a la raíz del proyecto, o con el comando incorrecto. Usa siempre `python3 -m src.main` desde `Mini-Monitor/`.

**La base de datos no tiene tablas**
Ejecuta `sqlite3 db/monitor.db < db/schema.sql` desde la raíz del proyecto.

## Tecnologías utilizadas

- Python 3
- [Textual](https://textual.textualize.io/) — framework para interfaces TUI
- SQLite 3
- Sistema de archivos virtual `/proc` (Linux)
- `os.fork()` y `threading` (concurrencia)
- `subprocess` (ejecución de comandos del sistema)

## Licencia

Proyecto académico desarrollado para la asignatura de Sistemas Operativos.