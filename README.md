# Episodex

Media tracker de escritorio para registrar manualmente el progreso de series, películas y cualquier otro contenido audiovisual.

## Requisitos

- Python 3.10+
- Sistema operativo: Linux, Windows o macOS

## Uso rápido

```bash
# 1. Clonar o descargar el proyecto
cd episodex

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
cd tracker
python3 main.py
```

## Funcionalidades

### Títulos
- **Agregar** un título con: nombre, tipo, temporada, episodio, estado, valoración (1–10), plataforma, notas y fecha de visionado
- **Editar** cualquier campo de un título existente
- **Ver detalle** en una vista de solo lectura
- **Eliminar** con confirmación

### Búsqueda y filtros
- Búsqueda por nombre (con debounce — no dispara en cada tecla)
- Filtros combinables por tipo, estado y plataforma
- Botón para limpiar todos los filtros

### Catálogos (Tipos, Estados, Plataformas)
Los tres catálogos son completamente editables desde la barra de acciones:
- **Agregar** nuevos valores
- **Renombrar** existentes
- **Eliminar** — si el valor está en uso, muestra cuántos títulos lo usan y permite forzar la eliminación

Valores iniciales:

| Catálogo   | Valores |
|------------|---------|
| Tipos      | Serie, Película |
| Estados    | Pendiente, Viendo, Completado |
| Plataformas | Netflix, HBO Max, Disney+, Amazon Prime, Apple TV+, Crunchyroll, Paramount+, YouTube, Otra |

### Exportación e importación

**Exportar** — guarda toda la biblioteca en **CSV** o **JSON** desde el botón "Exportar".

**Importar** — carga títulos desde un archivo CSV o JSON con el botón "Importar". Los títulos cuyo nombre ya exista en la biblioteca se omiten automáticamente. Los valores de tipo, estado y plataforma que no existan en los catálogos se agregan automáticamente.

### Migración / Backup

Hay dos formas de mover o respaldar los datos:

| Método | Qué incluye | Cuándo usarlo |
|--------|-------------|---------------|
| Copiar `tracker/db/tracker.db` | Todo: títulos y catálogos personalizados (tipos, estados, plataformas) | Migrar toda la biblioteca a otro equipo o hacer backup completo |
| Importar CSV / JSON | Solo títulos | Mezclar datos de distintas fuentes o restaurar un export parcial |

> Al importar desde CSV/JSON, los valores de tipo, estado y plataforma que no existan en el catálogo de destino se agregan automáticamente antes de insertar los títulos.

---

## Desarrollo

### Instalar dependencias de desarrollo

```bash
pip install -r requirements-dev.txt
```

### Estructura del proyecto

```
episodex/
├── tracker/
│   ├── main.py                 # punto de entrada
│   ├── db/database.py          # conexión SQLite y migraciones
│   ├── models/title.py         # dataclass Title
│   ├── services/
│   │   ├── media_manager.py    # CRUD de títulos y catálogos
│   │   └── exporter.py         # exportación e importación CSV / JSON
│   └── ui/
│       ├── main_window.py      # ventana principal
│       ├── form_dialog.py      # formulario agregar / editar
│       ├── detail_view.py      # vista de detalle
│       └── catalog_dialog.py   # diálogo CRUD de catálogos
├── requirements.txt
├── requirements-dev.txt
└── .gitignore
```

### Generar ejecutable (PyInstaller)

```bash
cd tracker
pyinstaller --onefile --windowed --name Episodex main.py
```

El ejecutable se genera en `tracker/dist/Episodex`. La base de datos se crea automáticamente junto al ejecutable la primera vez que se abre.
