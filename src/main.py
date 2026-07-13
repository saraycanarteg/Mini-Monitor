from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Container

from system.procfs_reader import get_cpu_info, get_memory_info


class MiniMonitorApp(App):
    """Aplicación TUI para el Mini Monitor de Recursos."""

    CSS_PATH = "main.tcss"
    BINDINGS = [("q", "quit", "Salir"), ("r", "refresh_data", "Refrescar")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Mini Monitor de Recursos — Linux", id="titulo")
        yield Container(
            DataTable(id="tabla_resumen"),
        )
        yield Footer()

    def on_mount(self) -> None:
        tabla = self.query_one("#tabla_resumen", DataTable)
        tabla.add_columns("Recurso", "Valor")
        tabla.add_row("CPU - Núcleos", "-", key="cpu_nucleos")
        tabla.add_row("CPU - Frecuencia (MHz)", "-", key="cpu_freq")
        tabla.add_row("CPU - Carga (1 min)", "-", key="cpu_carga")
        tabla.add_row("Memoria Total (KB)", "-", key="mem_total")
        tabla.add_row("Memoria Usada (KB)", "-", key="mem_usada")
        tabla.add_row("Memoria Libre (KB)", "-", key="mem_libre")

        self.actualizar_datos()
        # Refresca automáticamente cada 2 segundos
        self.set_interval(2, self.actualizar_datos)

    def actualizar_datos(self) -> None:
        tabla = self.query_one("#tabla_resumen", DataTable)

        cpu = get_cpu_info()
        mem = get_memory_info()

        # column_index=1 -> segunda columna ("Valor")
        tabla.update_cell("cpu_nucleos", tabla.ordered_columns[1].key, str(cpu["nucleos"]))
        tabla.update_cell("cpu_freq", tabla.ordered_columns[1].key, f"{cpu['frecuencia_mhz']:.1f}")
        tabla.update_cell("cpu_carga", tabla.ordered_columns[1].key, str(cpu["carga_1min"]))
        tabla.update_cell("mem_total", tabla.ordered_columns[1].key, str(mem["mem_total_kb"]))
        tabla.update_cell("mem_usada", tabla.ordered_columns[1].key, str(mem["mem_usada_kb"]))
        tabla.update_cell("mem_libre", tabla.ordered_columns[1].key, str(mem["mem_libre_kb"]))

    def action_refresh_data(self) -> None:
        self.actualizar_datos()


if __name__ == "__main__":
    app = MiniMonitorApp()
    app.run()