# Manual de ejecución

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
