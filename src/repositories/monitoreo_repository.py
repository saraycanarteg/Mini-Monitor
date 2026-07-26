import sqlite3
from datetime import datetime

DB_PATH = "db/monitor.db"


def _conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # necesario para que ON DELETE CASCADE funcione
    conn.row_factory = sqlite3.Row
    return conn


def crear_monitoreo(cpu: dict, mem: dict, disco: dict, procesos: list, usuarios: list, interfaces: list,
                     comentario: str = "", etiqueta: str = "") -> int:
    """Inserta una captura completa del sistema y devuelve el id generado."""
    conn = _conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO monitoreos (
            fecha_hora, cpu_nucleos, cpu_frecuencia_mhz, cpu_uso_porcentaje,
            mem_total_kb, mem_usada_kb, mem_libre_kb, swap_total_kb, swap_usada_kb,
            disco_total_kb, disco_usado_kb, disco_libre_kb, comentario, etiqueta
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        cpu["nucleos"], cpu["frecuencia_mhz"], cpu.get("uso_porcentaje", 0.0),
        mem["mem_total_kb"], mem["mem_usada_kb"], mem["mem_libre_kb"],
        mem.get("swap_total_kb", 0), mem.get("swap_total_kb", 0) - mem.get("swap_libre_kb", 0),
        disco["disco_total_kb"], disco["disco_usado_kb"], disco["disco_libre_kb"],
        comentario, etiqueta
    ))
    monitoreo_id = cur.lastrowid

    for p in procesos:
        cur.execute("""
            INSERT INTO procesos (monitoreo_id, pid, nombre, estado, usuario)
            VALUES (?, ?, ?, ?, ?)
        """, (monitoreo_id, p["pid"], p["nombre"], p["estado"], p["usuario"]))

    for u in usuarios:
        cur.execute("""
            INSERT INTO usuarios_conectados (monitoreo_id, usuario, tiempo_conexion)
            VALUES (?, ?, ?)
        """, (monitoreo_id, u["usuario"], u["tiempo_conexion"]))

    for i in interfaces:
        cur.execute("""
            INSERT INTO interfaces_red (monitoreo_id, nombre_interfaz, direccion_ip, bytes_recibidos,
                                         bytes_enviados, paquetes_recibidos, paquetes_enviados)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (monitoreo_id, i["nombre_interfaz"], i.get("direccion_ip", "N/A"), i["bytes_recibidos"],
              i["bytes_enviados"], i["paquetes_recibidos"], i["paquetes_enviados"]))

    conn.commit()
    conn.close()
    return monitoreo_id


def listar_monitoreos() -> list[dict]:
    """Devuelve todas las capturas guardadas, más recientes primero."""
    conn = _conectar()
    filas = conn.execute("SELECT * FROM monitoreos ORDER BY fecha_hora DESC").fetchall()
    conn.close()
    return [dict(f) for f in filas]


def obtener_monitoreo(monitoreo_id: int) -> dict | None:
    """Devuelve el detalle completo de una captura, incluyendo procesos/usuarios/red asociados."""
    conn = _conectar()
    fila = conn.execute("SELECT * FROM monitoreos WHERE id = ?", (monitoreo_id,)).fetchone()
    if fila is None:
        conn.close()
        return None

    resultado = dict(fila)
    resultado["procesos"] = [dict(r) for r in conn.execute(
        "SELECT * FROM procesos WHERE monitoreo_id = ?", (monitoreo_id,)).fetchall()]
    resultado["usuarios"] = [dict(r) for r in conn.execute(
        "SELECT * FROM usuarios_conectados WHERE monitoreo_id = ?", (monitoreo_id,)).fetchall()]
    resultado["interfaces"] = [dict(r) for r in conn.execute(
        "SELECT * FROM interfaces_red WHERE monitoreo_id = ?", (monitoreo_id,)).fetchall()]

    conn.close()
    return resultado


def actualizar_comentario_etiqueta(monitoreo_id: int, comentario: str = None, etiqueta: str = None) -> bool:
    """Actualiza comentario y/o etiqueta de una captura existente."""
    conn = _conectar()
    cur = conn.cursor()

    if comentario is not None:
        cur.execute("UPDATE monitoreos SET comentario = ? WHERE id = ?", (comentario, monitoreo_id))
    if etiqueta is not None:
        cur.execute("UPDATE monitoreos SET etiqueta = ? WHERE id = ?", (etiqueta, monitoreo_id))

    afectadas = cur.rowcount
    conn.commit()
    conn.close()
    return afectadas > 0


def eliminar_monitoreo(monitoreo_id: int) -> bool:
    """Elimina una captura y (por CASCADE) sus procesos/usuarios/red asociados."""
    conn = _conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM monitoreos WHERE id = ?", (monitoreo_id,))
    afectadas = cur.rowcount
    conn.commit()
    conn.close()
    return afectadas > 0


if __name__ == "__main__":
    from src.system.procfs_reader import get_cpu_info, get_memory_info, get_network_info
    from src.system.shell_executor import get_disk_info, get_processes, get_connected_users

    print("Creando un monitoreo de prueba...")
    nuevo_id = crear_monitoreo(
        cpu=get_cpu_info(),
        mem=get_memory_info(),
        disco=get_disk_info(),
        procesos=get_processes(),
        usuarios=get_connected_users(),
        interfaces=get_network_info(),
        comentario="Prueba inicial del repositorio",
        etiqueta="test"
    )
    print(f"Creado con id={nuevo_id}")

    print("\nListando monitoreos:")
    for m in listar_monitoreos():
        print(m)

    print(f"\nDetalle del monitoreo {nuevo_id}:")
    detalle = obtener_monitoreo(nuevo_id)
    print("Procesos guardados:", len(detalle["procesos"]))
    print("Usuarios guardados:", len(detalle["usuarios"]))
    print("Interfaces guardadas:", len(detalle["interfaces"]))

    print("\nActualizando comentario...")
    actualizar_comentario_etiqueta(nuevo_id, comentario="Comentario editado", etiqueta="editado")
    print(obtener_monitoreo(nuevo_id)["comentario"])

    print("\nEliminando monitoreo de prueba...")
    print("Eliminado:", eliminar_monitoreo(nuevo_id))
    print("Queda algo?", listar_monitoreos())