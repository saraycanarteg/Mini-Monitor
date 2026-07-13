def get_cpu_info() -> dict:
    """Lee /proc/cpuinfo y /proc/loadavg para obtener núcleos, frecuencia y uso."""
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

    return {
        "nucleos": nucleos,
        "frecuencia_mhz": frecuencia,
        "carga_1min": carga_1min
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