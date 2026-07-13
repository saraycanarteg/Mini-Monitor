import subprocess


def get_disk_info() -> dict:
    """Ejecuta 'df' para obtener espacio total, usado y libre del disco raíz."""
    resultado = subprocess.run(
        ["df", "-k", "/"], capture_output=True, text=True
    )
    lineas = resultado.stdout.strip().split("\n")
    campos = lineas[1].split()  # segunda línea = datos del filesystem raíz

    return {
        "disco_total_kb": int(campos[1]),
        "disco_usado_kb": int(campos[2]),
        "disco_libre_kb": int(campos[3]),
    }


def get_processes() -> list[dict]:
    """Ejecuta 'ps' para listar procesos con PID, nombre, estado y usuario."""
    resultado = subprocess.run(
        ["ps", "-eo", "pid,comm,stat,user", "--no-headers"],
        capture_output=True, text=True
    )
    procesos = []
    for linea in resultado.stdout.strip().split("\n"):
        campos = linea.split(maxsplit=3)
        if len(campos) == 4:
            procesos.append({
                "pid": int(campos[0]),
                "nombre": campos[1],
                "estado": campos[2],
                "usuario": campos[3],
            })
    return procesos


def get_connected_users() -> list[dict]:
    """Ejecuta 'who' para listar usuarios conectados y su tiempo de conexión."""
    resultado = subprocess.run(["who"], capture_output=True, text=True)
    usuarios = []
    for linea in resultado.stdout.strip().split("\n"):
        if not linea:
            continue
        campos = linea.split()
        usuarios.append({
            "usuario": campos[0],
            "tiempo_conexion": " ".join(campos[2:4]) if len(campos) >= 4 else "N/A",
        })
    return usuarios


if __name__ == "__main__":
    print("Disco:", get_disk_info())
    print("Procesos (primeros 5):", get_processes()[:5])
    print("Usuarios conectados:", get_connected_users())