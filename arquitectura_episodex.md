# Episodex (Media Tracker) - Arquitectura

## Stack
- **UI**: PyQt6
- **Lógica**: Python puro
- **Base de datos**: SQLite (`sqlite3` built-in, sin dependencias extra)
- **Distribución**: PyInstaller (genera ejecutable único para Linux y Windows)

## Patrón: MVC simplificado

| Capa | Responsabilidad |
|------|----------------|
| **View** | Widgets PyQt6 — lo que el usuario ve |
| **Controller** | Señales/slots de Qt — conecta UI con lógica |
| **Model** | Dataclasses Python + `MediaManager` que habla con SQLite |

## Estructura de carpetas

```
episodex/
├── arquitectura_episodex.md
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
└── tracker/
    ├── main.py
    ├── db/
    │   ├── database.py        # conexión, creación de tablas, migraciones
    │   └── tracker.db         # archivo SQLite (generado en runtime)
    ├── models/
    │   └── title.py           # dataclass: Title
    ├── services/
    │   ├── media_manager.py   # CRUD de títulos y catálogos
    │   └── exporter.py        # exportar a CSV / JSON
    └── ui/
        ├── main_window.py     # ventana principal: lista + filtros + acciones
        ├── form_dialog.py     # diálogo agregar / editar título
        ├── detail_view.py     # vista de detalle y notas
        └── catalog_dialog.py  # diálogo CRUD genérico para catálogos
```

## Modelo de datos

### Tabla principal: `titles`

| Campo        | Tipo   | Notas                                      |
|--------------|--------|--------------------------------------------|
| `id`         | INT    | Primary key, autoincrement                 |
| `title`      | TEXT   | Nombre del título                          |
| `type`       | TEXT   | Valor del catálogo `types`                 |
| `season`     | INT?   | Nullable. Siempre editable independiente del tipo |
| `episode`    | INT?   | Nullable. Siempre editable independiente del tipo |
| `status`     | TEXT   | Valor del catálogo `statuses`              |
| `rating`     | INT?   | 1–10, nullable                             |
| `platform`   | TEXT?  | Valor del catálogo `platforms`. Nullable   |
| `notes`      | TEXT?  | Notas libres. Nullable                     |
| `watched_at` | TEXT?  | Fecha ISO 8601 (`YYYY-MM-DD`). Nullable    |

### Catálogos (tablas auxiliares)

Los tres catálogos tienen la misma estructura y son completamente editables por el usuario via la UI:

| Tabla       | Valores iniciales                                              |
|-------------|----------------------------------------------------------------|
| `types`     | Serie, Película                                                |
| `statuses`  | Pendiente, Viendo, Completado                                  |
| `platforms` | Netflix, HBO Max, Disney+, Amazon Prime, Apple TV+, Crunchyroll, Paramount+, YouTube, Otra |

> Los campos `type`, `status` y `platform` en `titles` almacenan el **nombre como texto**, no un ID. No hay FK real — es una decisión intencional para simplificar el esquema dado que la app no escala a miles de usuarios. Si se elimina un catálogo en uso, los títulos conservan el valor viejo.

## Capas en detalle

### `db/database.py`
- Abre/crea la conexión SQLite
- Ejecuta `CREATE TABLE IF NOT EXISTS` para `titles`, `types`, `statuses` y `platforms` al iniciar
- Inserta los valores iniciales de cada catálogo con `INSERT OR IGNORE`
- Migra datos existentes al renombrar valores internos a nombres de display (ej: `"series"` → `"Serie"`)

### `models/title.py`
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Title:
    id: Optional[int]
    title: str
    type: str       # valor libre del catálogo types
    status: str     # valor libre del catálogo statuses
    season: Optional[int] = None
    episode: Optional[int] = None
    rating: Optional[int] = None
    platform: Optional[str] = None
    notes: Optional[str] = None
    watched_at: Optional[str] = None
```

### `services/media_manager.py`
Métodos de títulos:
- `add(title: Title) -> int`
- `update(title: Title) -> None`
- `delete(id: int) -> None`
- `get_all(filters: dict) -> list[Title]`
- `get_by_id(id: int) -> Title`
- `search(query: str) -> list[Title]`

Métodos de catálogos (mismo patrón para `types`, `statuses` y `platforms`):
- `get_types() -> list[str]`
- `get_types_full() -> list[dict]`  — incluye `id` para operaciones CRUD
- `add_type(name: str) -> int`
- `rename_type(id: int, name: str) -> None`
- `count_titles_with_type(name: str) -> int`
- `delete_type(id: int) -> None`
- *(ídem para `statuses` y `platforms`)*

### `services/exporter.py`
Exportación:
- `to_csv(titles: list[Title], path: str) -> None`
- `to_json(titles: list[Title], path: str) -> None`

Importación:
- `from_csv(path: str) -> list[Title]`
- `from_json(path: str) -> list[Title]`

Ambos métodos de importación devuelven `Title` con `id=None` — el ID lo asigna la DB al insertar. Los valores nulos del archivo (`None`, `""`, `"None"`) se normalizan correctamente.

La sincronización de catálogos ocurre en `MainWindow._import_dialog`: antes de insertar títulos, compara los valores de `type`, `status` y `platform` de cada candidato contra los catálogos existentes y llama a `add_type` / `add_status` / `add_platform` por cada valor nuevo. Si hubo cambios, refresca los filtros correspondientes con `blockSignals`.

### `ui/main_window.py`
- `QMainWindow` con `QTableWidget`
- Barra de filtros: tipo, estado, plataforma (cargados desde DB)
- Barra de búsqueda con debounce de 300 ms
- Botones de acción sobre títulos: Agregar, Editar, Ver detalle, Eliminar, Exportar, Importar
- Botones de gestión de catálogos: Tipos, Estados, Plataformas
- Al cerrar cualquier diálogo de catálogo, refresca el filtro correspondiente con `blockSignals`

### `ui/form_dialog.py`
- `QDialog` para agregar y editar títulos
- Tipos y estados se cargan desde DB (no hardcodeados)
- Temporada y episodio siempre visibles e independientes del tipo

### `ui/detail_view.py`
- Vista de solo lectura con todos los campos del título
- Emite señal `edit_requested(int)` al presionar "Editar" — no acopla la vista con `MainWindow`

### `ui/catalog_dialog.py`
- `QDialog` genérico y reutilizable para gestionar cualquier catálogo
- Recibe callables del `MediaManager` en el constructor — no conoce qué catálogo está editando
- Acciones: Agregar (con validación de duplicados), Renombrar, Eliminar
- Al eliminar un elemento en uso: muestra un aviso con el número de títulos afectados y ofrece forzar la eliminación

## Dependencias

```txt
# requirements.txt
PyQt6

# requirements-dev.txt
PyInstaller   # solo para generar el ejecutable
```

`sqlite3` viene incluido en Python — no necesita instalarse.

## Migración y backup

Dos mecanismos con propósitos distintos:

| Método | Qué incluye | Uso |
|--------|-------------|-----|
| Copiar `tracker.db` | Títulos + catálogos personalizados | Migración completa entre equipos, backup total |
| Exportar/Importar CSV o JSON | Solo títulos | Mezcla de datos, backup parcial, interoperabilidad |

Al importar desde CSV/JSON, los valores de `type`, `status` y `platform` que no existan en los catálogos de la DB de destino se agregan automáticamente antes de insertar los títulos. Los filtros se refrescan si hubo cambios en algún catálogo.

## Notas de implementación

- El archivo `tracker.db` vive en `db/tracker.db` relativo al ejecutable, nunca una ruta absoluta. En modo PyInstaller usa `os.path.dirname(sys.executable)`
- Escalabilidad: SQLite soporta millones de registros; para este caso (cientos de títulos) nunca será un cuello de botella
