from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, TabbedContent, TabPane, Input, Label, Button
from textual.containers import Vertical
from textual.screen import ModalScreen

from src.services.sistema_service import (
    obtener_estado_cpu, obtener_estado_memoria, obtener_estado_disco,
    obtener_procesos_activos, obtener_usuarios_conectados, obtener_estado_red
)
from src.repositories.monitoreo_repository import (
    listar_monitoreos, actualizar_comentario_etiqueta, eliminar_monitoreo
)
from src.concurrency.snapshot_manager import crear_snapshot_en_proceso_hijo


class ModalCrear(ModalScreen):
    """Pide comentario y etiqueta antes de crear una captura."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Nueva captura del sistema"),
            Label("Comentario:"),
            Input(placeholder="Ej. Revisión de carga alta", id="input_comentario"),
            Label("Etiqueta:"),
            Input(placeholder="Ej. incidente", id="input_etiqueta"),
            Button("Guardar", id="btn_guardar", variant="success"),
            Button("Cancelar", id="btn_cancelar", variant="error"),
            id="modal_crear_box",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_guardar":
            comentario = self.query_one("#input_comentario", Input).value
            etiqueta = self.query_one("#input_etiqueta", Input).value
            self.dismiss((comentario, etiqueta))
        else:
            self.dismiss(None)


class ModalEditar(ModalScreen):
    """Pide nuevo comentario y etiqueta para actualizar una captura existente."""

    def __init__(self, monitoreo_id: int, comentario_actual: str, etiqueta_actual: str):
        super().__init__()
        self.monitoreo_id = monitoreo_id
        self.comentario_actual = comentario_actual
        self.etiqueta_actual = etiqueta_actual

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label(f"Editar captura #{self.monitoreo_id}"),
            Label("Comentario:"),
            Input(value=self.comentario_actual or "", id="input_comentario"),
            Label("Etiqueta:"),
            Input(value=self.etiqueta_actual or "", id="input_etiqueta"),
            Button("Guardar", id="btn_guardar", variant="success"),
            Button("Cancelar", id="btn_cancelar", variant="error"),
            id="modal_editar_box",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_guardar":
            comentario = self.query_one("#input_comentario", Input).value
            etiqueta = self.query_one("#input_etiqueta", Input).value
            self.dismiss((comentario, etiqueta))
        else:
            self.dismiss(None)


class MiniMonitorApp(App):
    """Aplicación TUI para el Mini Monitor de Recursos."""

    CSS_PATH = "main.tcss"
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("r", "refresh_data", "Refrescar"),
        ("c", "crear_captura", "Crear captura"),
        ("e", "editar_captura", "Editar"),
        ("d", "eliminar_captura", "Eliminar"),
    ]

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
            with TabPane("Historial", id="historial"):
                yield DataTable(id="tabla_historial")
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "rose-pine-dawn"
        tabla = self.query_one("#tabla_resumen", DataTable)
        tabla.add_columns("Recurso", "Valor")
        tabla.add_row("CPU - Núcleos", "-", key="cpu_nucleos")
        tabla.add_row("CPU - Frecuencia (MHz)", "-", key="cpu_freq")
        tabla.add_row("CPU - Uso (%)", "-", key="cpu_uso")
        tabla.add_row("CPU - Carga (1 min)", "-", key="cpu_carga")
        tabla.add_row("Memoria Total (KB)", "-", key="mem_total")
        tabla.add_row("Memoria Usada (KB)", "-", key="mem_usada")
        tabla.add_row("Memoria Libre (KB)", "-", key="mem_libre")
        tabla.add_row("Disco Total (KB)", "-", key="disco_total")
        tabla.add_row("Disco Usado (KB)", "-", key="disco_usado")
        tabla.add_row("Disco Libre (KB)", "-", key="disco_libre")

        self.query_one("#tabla_procesos", DataTable).add_columns("PID", "Nombre", "Estado", "Usuario")
        self.query_one("#tabla_usuarios", DataTable).add_columns("Usuario", "Tiempo de conexión")
        self.query_one("#tabla_red", DataTable).add_columns("Interfaz", "IP", "Bytes Recibidos", "Bytes Enviados")

        tabla_h = self.query_one("#tabla_historial", DataTable)
        tabla_h.add_columns("ID", "Fecha", "CPU %", "Mem Usada KB", "Comentario", "Etiqueta")
        tabla_h.cursor_type = "row"

        self.actualizar_datos()
        self.set_interval(2, self.actualizar_datos)

    def actualizar_datos(self) -> None:
        self.actualizar_resumen()
        self.actualizar_procesos()
        self.actualizar_usuarios()
        self.actualizar_red()
        self.actualizar_historial()

    def actualizar_resumen(self) -> None:
        tabla = self.query_one("#tabla_resumen", DataTable)
        columna_valor = tabla.ordered_columns[1].key

        cpu = obtener_estado_cpu()
        mem = obtener_estado_memoria()
        disco = obtener_estado_disco()

        tabla.update_cell("cpu_nucleos", columna_valor, str(cpu["nucleos"]))
        tabla.update_cell("cpu_freq", columna_valor, f"{cpu['frecuencia_mhz']:.1f}")
        tabla.update_cell("cpu_uso", columna_valor, f"{cpu['uso_porcentaje']:.1f}")
        tabla.update_cell("cpu_carga", columna_valor, str(cpu["carga_1min"]))
        tabla.update_cell("mem_total", columna_valor, str(mem["mem_total_kb"]))
        tabla.update_cell("mem_usada", columna_valor, str(mem["mem_usada_kb"]))
        tabla.update_cell("mem_libre", columna_valor, str(mem["mem_libre_kb"]))
        tabla.update_cell("disco_total", columna_valor, str(disco["disco_total_kb"]))
        tabla.update_cell("disco_usado", columna_valor, str(disco["disco_usado_kb"]))
        tabla.update_cell("disco_libre", columna_valor, str(disco["disco_libre_kb"]))

    def actualizar_procesos(self) -> None:
        tabla = self.query_one("#tabla_procesos", DataTable)
        tabla.clear()
        for p in obtener_procesos_activos():
            tabla.add_row(str(p["pid"]), p["nombre"], p["estado"], p["usuario"])

    def actualizar_usuarios(self) -> None:
        tabla = self.query_one("#tabla_usuarios", DataTable)
        tabla.clear()
        for u in obtener_usuarios_conectados():
            tabla.add_row(u["usuario"], u["tiempo_conexion"])

    def actualizar_red(self) -> None:
        tabla = self.query_one("#tabla_red", DataTable)
        tabla.clear()
        for iface in obtener_estado_red():
            tabla.add_row(
                iface["nombre_interfaz"], iface["direccion_ip"],
                str(iface["bytes_recibidos"]), str(iface["bytes_enviados"])
            )

    def actualizar_historial(self) -> None:
        tabla = self.query_one("#tabla_historial", DataTable)
        tabla.clear()
        for m in listar_monitoreos():
            tabla.add_row(
                str(m["id"]), m["fecha_hora"], f"{m['cpu_uso_porcentaje']:.1f}",
                str(m["mem_usada_kb"]), m["comentario"] or "-", m["etiqueta"] or "-",
                key=str(m["id"])
            )

    def action_refresh_data(self) -> None:
        self.actualizar_datos()

    def action_crear_captura(self) -> None:
        def al_cerrar(resultado):
            if resultado is not None:
                comentario, etiqueta = resultado
                crear_snapshot_en_proceso_hijo(comentario=comentario, etiqueta=etiqueta)
                self.actualizar_historial()
                self.notify("Captura guardada correctamente.")

        self.push_screen(ModalCrear(), al_cerrar)

    def action_editar_captura(self) -> None:
        tabla = self.query_one("#tabla_historial", DataTable)
        if tabla.cursor_row is None or tabla.row_count == 0:
            self.notify("Selecciona una captura en Historial primero.", severity="warning")
            return

        fila_key, _ = tabla.coordinate_to_cell_key(tabla.cursor_coordinate)
        monitoreo_id = int(fila_key.value)
        fila = tabla.get_row(fila_key)
        comentario_actual, etiqueta_actual = fila[4], fila[5]

        def al_cerrar(resultado):
            if resultado is not None:
                comentario, etiqueta = resultado
                actualizar_comentario_etiqueta(monitoreo_id, comentario=comentario, etiqueta=etiqueta)
                self.actualizar_historial()
                self.notify(f"Captura #{monitoreo_id} actualizada.")

        self.push_screen(ModalEditar(monitoreo_id, comentario_actual, etiqueta_actual), al_cerrar)

    def action_eliminar_captura(self) -> None:
        tabla = self.query_one("#tabla_historial", DataTable)
        if tabla.cursor_row is None or tabla.row_count == 0:
            self.notify("Selecciona una captura en Historial primero.", severity="warning")
            return

        fila_key, _ = tabla.coordinate_to_cell_key(tabla.cursor_coordinate)
        monitoreo_id = int(fila_key.value)
        eliminar_monitoreo(monitoreo_id)
        self.actualizar_historial()
        self.notify(f"Captura #{monitoreo_id} eliminada.")


if __name__ == "__main__":
    app = MiniMonitorApp()
    app.run()