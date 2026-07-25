"""
Capa de Servicios (Aplicación).

Actúa como intermediario entre la Capa del Sistema Operativo (procfs_reader,
shell_executor) y las capas superiores (Presentación, Concurrencia). Expone
funciones de negocio ya listas para usar, sin que quien las consuma necesite
saber si el dato viene de /proc o de un comando de shell.
"""

from src.system.procfs_reader import get_cpu_info, get_memory_info, get_network_info
from src.system.shell_executor import get_disk_info, get_processes, get_connected_users


def obtener_estado_cpu() -> dict:
    """Servicio de CPU: núcleos, frecuencia y carga del sistema."""
    return get_cpu_info()


def obtener_estado_memoria() -> dict:
    """Servicio de Memoria: total, usada, libre y swap."""
    return get_memory_info()


def obtener_estado_disco() -> dict:
    """Servicio de Disco: espacio total, usado y libre."""
    return get_disk_info()


def obtener_procesos_activos() -> list[dict]:
    """Servicio de Procesos: PID, nombre, estado y usuario."""
    return get_processes()


def obtener_usuarios_conectados() -> list[dict]:
    """Servicio de Usuarios: usuario y tiempo de conexión."""
    return get_connected_users()


def obtener_estado_red() -> list[dict]:
    """Servicio de Red: estadísticas de tráfico por interfaz."""
    return get_network_info()


def obtener_estado_completo_sistema() -> dict:
    """
    Servicio agregador: combina todos los servicios individuales en un solo
    diccionario. Usado por el SnapshotManager para construir una captura completa.
    """
    return {
        "cpu": obtener_estado_cpu(),
        "mem": obtener_estado_memoria(),
        "disco": obtener_estado_disco(),
        "procesos": obtener_procesos_activos(),
        "usuarios": obtener_usuarios_conectados(),
        "red": obtener_estado_red(),
    }