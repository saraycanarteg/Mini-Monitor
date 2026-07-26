_ultima_muestra_cpu: tuple[int, int] | None = None  # (jiffies_ocupados, jiffies_totales) de la lectura anterior


def _leer_jiffies_cpu() -> tuple[int, int]:
    """Lee la línea agregada 'cpu' de /proc/stat y devuelve (jiffies_ocupados, jiffies_totales)."""
    with open("/proc/stat", "r") as f:
        campos = f.readline().split()[1:]  # descarta la etiqueta "cpu"

    valores = [int(v) for v in campos]
    ocioso = valores[3] + valores[4]  # idle + iowait
    total = sum(valores)
    return total - ocioso, total


def get_cpu_info() -> dict:
    """Lee /proc/cpuinfo, /proc/loadavg y /proc/stat para núcleos, frecuencia, carga y % de uso real."""
    global _ultima_muestra_cpu

    nucleos = 0
    frecuencia = 0.0

    with open("/proc/cpuinfo", "r") as f:
        for linea in f:
            if linea.startswith("processor"):
                nucleos += 1
            if linea.startswith("cpu MHz") and frecuencia == 0.0:
                frecuencia = float(linea.split(":")[1].strip())

    with open("/proc/loadavg", "r") as f:
        carga_1min = float(f.read().split()[0])

    # % de uso real: delta de jiffies ocupados vs. totales entre esta lectura y la anterior.
    # Al ser una medición incremental (no bloqueante) requiere al menos dos llamadas para
    # dar un valor distinto de 0; esto evita frenar la interfaz con un time.sleep().
    ocupado, total = _leer_jiffies_cpu()
    uso_porcentaje = 0.0
    if _ultima_muestra_cpu is not None:
        ocupado_prev, total_prev = _ultima_muestra_cpu
        delta_total = total - total_prev
        if delta_total > 0:
            uso_porcentaje = max(0.0, min(100.0, (ocupado - ocupado_prev) / delta_total * 100))
    _ultima_muestra_cpu = (ocupado, total)

    return {
        "nucleos": nucleos,
        "frecuencia_mhz": frecuencia,
        "carga_1min": carga_1min,
        "uso_porcentaje": round(uso_porcentaje, 1),
    }


def get_memory_info() -> dict:
    """Lee /proc/meminfo para obtener memoria total, libre y swap."""
    datos = {}
    with open("/proc/meminfo", "r") as f:
        for linea in f:
            clave, valor = linea.split(":")
            datos[clave.strip()] = int(valor.strip().split()[0])  # en KB

    return {
        "mem_total_kb": datos.get("MemTotal", 0),
        "mem_libre_kb": datos.get("MemFree", 0),
        "mem_usada_kb": datos.get("MemTotal", 0) - datos.get("MemAvailable", 0),
        "swap_total_kb": datos.get("SwapTotal", 0),
        "swap_libre_kb": datos.get("SwapFree", 0),
    }


def get_network_info() -> list[dict]:
    """Lee /proc/net/dev para obtener estadísticas de tráfico por interfaz."""
    interfaces = []
    with open("/proc/net/dev", "r") as f:
        lineas = f.readlines()[2:]  # las primeras 2 líneas son encabezados

    for linea in lineas:
        nombre, datos = linea.split(":")
        campos = datos.split()
        interfaces.append({
            "nombre_interfaz": nombre.strip(),
            "bytes_recibidos": int(campos[0]),
            "paquetes_recibidos": int(campos[1]),
            "bytes_enviados": int(campos[8]),
            "paquetes_enviados": int(campos[9]),
        })

    return interfaces


if __name__ == "__main__":
    print("CPU:", get_cpu_info())
    print("Memoria:", get_memory_info())
    print("Red:", get_network_info())