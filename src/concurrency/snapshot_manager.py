import os
import threading

from src.services.sistema_service import obtener_estado_cpu, obtener_estado_memoria, obtener_estado_disco, obtener_procesos_activos, obtener_usuarios_conectados, obtener_estado_red
from src.repositories.monitoreo_repository import crear_monitoreo

def _capturar_con_hilos() -> dict:
    """Lee CPU y memoria en paralelo usando threading, y el resto de forma secuencial."""
    resultados = {}

    def leer_cpu():
        resultados["cpu"] = obtener_estado_cpu()

    def leer_memoria():
        resultados["mem"] = obtener_estado_memoria()

    hilo_cpu = threading.Thread(target=leer_cpu)
    hilo_mem = threading.Thread(target=leer_memoria)

    hilo_cpu.start()
    hilo_mem.start()
    hilo_cpu.join()
    hilo_mem.join()

    resultados["disco"] = obtener_estado_disco()
    resultados["procesos"] = obtener_procesos_activos()
    resultados["usuarios"] = obtener_usuarios_conectados()
    resultados["red"] = obtener_estado_red()

    return resultados


def crear_snapshot_en_proceso_hijo(comentario: str = "", etiqueta: str = "") -> int | None:
    """
    Lanza un proceso hijo (os.fork) que captura el estado del sistema usando
    hilos (threading) y lo guarda en la base de datos.

    El proceso padre espera al hijo y retorna. La comunicación del id generado
    se hace mediante un pipe, ya que fork() no comparte memoria entre procesos.
    """
    lector, escritor = os.pipe()
    pid = os.fork()

    if pid == 0:
        # ---- Proceso hijo ----
        os.close(lector)
        datos = _capturar_con_hilos()

        nuevo_id = crear_monitoreo(
            cpu=datos["cpu"],
            mem=datos["mem"],
            disco=datos["disco"],
            procesos=datos["procesos"],
            usuarios=datos["usuarios"],
            interfaces=datos["red"],
            comentario=comentario,
            etiqueta=etiqueta,
        )

        os.write(escritor, str(nuevo_id).encode())
        os.close(escritor)
        os._exit(0)  # termina el hijo sin ejecutar código del padre

    else:
        # ---- Proceso padre ----
        os.close(escritor)
        _, status = os.waitpid(pid, 0)  # espera a que el hijo termine
        resultado = os.read(lector, 100).decode()
        os.close(lector)

        if resultado:
            return int(resultado)
        return None


if __name__ == "__main__":
    print("Creando snapshot en proceso hijo (fork)...")
    nuevo_id = crear_snapshot_en_proceso_hijo(comentario="Snapshot vía fork+threading", etiqueta="fork_test")
    print(f"Snapshot creado con id={nuevo_id} desde el proceso padre (PID={os.getpid()})")