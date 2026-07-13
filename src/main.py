from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, TabbedContent, TabPane
from textual.containers import Container

from src.system.procfs_reader import get_cpu_info, get_memory_info, get_network_info
from src.system.shell_executor import get_disk_info, get_processes, get_connected_users


class MiniMonitorApp(App):
    """Aplicación TUI para el Mini Monitor de Recursos."""

    CSS_PATH = "main.tcss"
    BINDINGS = [("q", "quit", "Salir"), ("r", "refresh_data", "Refrescar")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Mini Monitor de Recursos — Linux", id="titulo")
        with TabbedContent(initial="resumen"):
            with TabPane("Resumen", id="resumen"):
                yield DataTable(id="tabla_resumen")
            with TabPane("Procesos", id="procesos"):
                yield DataTable(id="tabla_procesos")
            with TabPane("Usuarios", id="usuarios"):
                yield DataTable(id="tabla_usuarios")
            with TabPane("Red", id="red"):
                yield DataTable(id="tabla_red")
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "rose-pine-dawn"
        # --- Tabla Resumen ---
        tabla = self.query_one("#tabla_resumen", DataTable)
        tabla.add_columns("Recurso", "Valor")
        tabla.add_row("CPU - Núcleos", "-", key="cpu_nucleos")
        tabla.add_row("CPU - Frecuencia (MHz)", "-", key="cpu_freq")
        tabla.add_row("CPU - Carga (1 min)", "-", key="cpu_carga")
        tabla.add_row("Memoria Total (KB)", "-", key="mem_total")
        tabla.add_row("Memoria Usada (KB)", "-", key="mem_usada")
        tabla.add_row("Memoria Libre (KB)", "-", key="mem_libre")
        tabla.add_row("Disco Total (KB)", "-", key="disco_total")
        tabla.add_row("Disco Usado (KB)", "-", key="disco_usado")
        tabla.add_row("Disco Libre (KB)", "-", key="disco_libre")

        # --- Tabla Procesos ---
        tabla_p = self.query_one("#tabla_procesos", DataTable)
        tabla_p.add_columns("PID", "Nombre", "Estado", "Usuario")

        # --- Tabla Usuarios ---
        tabla_u = self.query_one("#tabla_usuarios", DataTable)
        tabla_u.add_columns("Usuario", "Tiempo de conexión")

        # --- Tabla Red ---
        tabla_r = self.query_one("#tabla_red", DataTable)
        tabla_r.add_columns("Interfaz", "Bytes Recibidos", "Bytes Enviados")

        self.actualizar_datos()
        self.set_interval(2, self.actualizar_datos)

    def actualizar_datos(self) -> None:
        self.actualizar_resumen()
        self.actualizar_procesos()
        self.actualizar_usuarios()
        self.actualizar_red()

    def actualizar_resumen(self) -> None:
        tabla = self.query_one("#tabla_resumen", DataTable)
        columna_valor = tabla.ordered_columns[1].key

        cpu = get_cpu_info()
        mem = get_memory_info()
        disco = get_disk_info()

        tabla.update_cell("cpu_nucleos", columna_valor, str(cpu["nucleos"]))
        tabla.update_cell("cpu_freq", columna_valor, f"{cpu['frecuencia_mhz']:.1f}")
        tabla.update_cell("cpu_carga", columna_valor, str(cpu["carga_1min"]))
        tabla.update_cell("mem_total", columna_valor, str(mem["mem_total_kb"]))
        tabla.update_cell("mem_usada", columna_valor, str(mem["mem_usada_kb"]))
        tabla.update_cell("mem_libre", columna_valor, str(mem["mem_libre_kb"]))
        tabla.update_cell("disco_total", columna_valor, str(disco["disco_total_kb"]))
        tabla.update_cell("disco_usado", columna_valor, str(disco["disco_usado_kb"]))
        tabla.update_cell("disco_libre", columna_valor, str(disco["disco_libre_kb"]))

    def actualizar_procesos(self) -> None:
        tabla = self.query_one("#tabla_procesos", DataTable)
        fila_actual = tabla.cursor_row  # conserva posición del cursor al refrescar
        tabla.clear()
        for p in get_processes():
            tabla.add_row(str(p["pid"]), p["nombre"], p["estado"], p["usuario"])

    def actualizar_usuarios(self) -> None:
        tabla = self.query_one("#tabla_usuarios", DataTable)
        tabla.clear()
        for u in get_connected_users():
            tabla.add_row(u["usuario"], u["tiempo_conexion"])

    def actualizar_red(self) -> None:
        tabla = self.query_one("#tabla_red", DataTable)
        tabla.clear()
        for iface in get_network_info():
            tabla.add_row(
                iface["nombre_interfaz"],
                str(iface["bytes_recibidos"]),
                str(iface["bytes_enviados"]),
            )

    def action_refresh_data(self) -> None:
        self.actualizar_datos()


if __name__ == "__main__":
    app = MiniMonitorApp()
    app.run()