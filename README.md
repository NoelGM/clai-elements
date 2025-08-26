## Estructura general

```
back/
│
├── config/
├── src/
│   ├── api/
│   ├── config/
│   ├── domain/
│   ├── infrastructure/
│   └── logger/
├── test/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Archivos y carpetas principales

### 1. config
Contiene archivos de configuración en formato YAML, como:
- `logging_config.yaml`: Configuración de logs.
- `service_config.yaml`: Configuración de servicios, como credenciales de Neo4j y endpoints FHIR.

El proyecto utiliza dos herramientas principales para la configuración:

- **Dynaconf**: Para cargar y gestionar la configuración general de la aplicación (por ejemplo, credenciales, endpoints, parámetros de servicios).
- **Loguru**: Para configurar el sistema de logging (registro de eventos y errores) de forma flexible y centralizada.

#### a) Archivos de configuración YAML

En la carpeta config tienes archivos como:

- `service_config.yaml`: Aquí defines parámetros como la URL y credenciales de Neo4j, endpoints FHIR, y cualquier otro ajuste necesario para los servicios.
- `logging_config.yaml`: Aquí defines cómo y dónde se guardan los logs, el formato, los niveles de severidad, etc.

#### b) Carga de configuración con Dynaconf

En el código (por ejemplo, en config.py), se utiliza Dynaconf para leer estos archivos YAML y exponer sus valores como variables de configuración accesibles desde cualquier parte del proyecto. Así, puedes hacer algo como:

```python
from dynaconf import Dynaconf

settings = Dynaconf(settings_files=['config/service_config.yaml'])
db_url = settings.NEO4J_URL
```

Esto permite separar la configuración del código, facilitando cambios sin modificar el código fuente.

#### c) Configuración de logs con Loguru

En el archivo logger_config.py, se utiliza Loguru para leer `logging_config.yaml` y establecer cómo se registran los logs. Por ejemplo, puedes definir que los logs se guarden en un archivo, se muestren en consola, el formato de los mensajes, y el nivel de detalle (info, warning, error, etc.).

Esto permite tener un sistema de logs robusto y configurable, útil para depuración y monitoreo.

---

**Resumen:**  
La configuración centralizada con Dynaconf y Loguru permite que el comportamiento de la aplicación y el registro de eventos se puedan ajustar fácilmente desde archivos YAML, sin tocar el código. Esto es esencial para entornos profesionales y despliegues en diferentes ambientes (desarrollo, pruebas, producción).

---

### 2. src
Carpeta principal del código fuente.

#### a. api
Implementa la API web usando FastAPI. Aquí se definen:
- **Endpoints**: Rutas HTTP para interactuar con el sistema.
- **Modelos**: Esquemas de entrada/salida para los endpoints (usando Pydantic).
- **Chains**: Integración con LangChain para procesamiento de lenguaje.

Ejemplo:
- app.py: Instancia la aplicación FastAPI y registra los endpoints.
- endpoints: Subcarpeta con endpoints agrupados por dominio (ej. `data`, `conversion`, `examples`).
- model: Modelos de datos para validación de entradas.


## Estructura de `src/api`

```
src/api/
│
├── __init__.py
├── app.py
├── chains/
│   └── echo_chain.py
├── endpoints/
│   ├── __init__.py
│   ├── conversion/
│   │   ├── __init__.py
│   │   └── fhir2neo4j.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── fhir.py
│   │   └── neo4j.py
│   └── examples/
│       ├── __init__.py
│       └── say_hello.py
├── model/
│   ├── data/
│   │   ├── fhir.py
│   │   └── neo4j.py
│   └── examples/
│       └── say_hello.py
```

---

## Archivos principales

### `__init__.py`
Define respuestas estándar para la API: `RESP200`, `RESP202`, `RESP500`.

---

### `app.py`
- Crea la instancia principal de FastAPI.
- Añade rutas de LangChain (`/echo`).
- Incluye los routers/endpoints de ejemplos, FHIR, Neo4j y conversión FHIR→Neo4j.

---

### `chains/echo_chain.py`
- Define una cadena de LangChain que simplemente devuelve el input recibido (útil para pruebas).

---

## Subcarpeta `endpoints/`

Agrupa los endpoints por dominio:

- `__init__.py`: Define el prefijo base `/clai`.
- **conversion/**
  - `__init__.py`: Prefijo `/clai/conversion`.
  - `fhir2neo4j.py`: Endpoint POST para insertar un recurso FHIR en Neo4j.
- **data/**
  - `__init__.py`: Prefijo `/clai/data` y símbolos permitidos.
  - `fhir.py`: Endpoint GET para obtener pacientes FHIR desde un servidor externo.
  - `neo4j.py`: Endpoints GET/POST para extraer/inserir pacientes en Neo4j.
- **examples/**
  - `__init__.py`: Prefijo `/clai/examples`.
  - `say_hello.py`: Endpoints de ejemplo para saludar (sincrónico y asincrónico).

---

## Subcarpeta `model/`

Define modelos de datos (con Pydantic y Depends) para validar y estructurar los datos de entrada de los endpoints:

- **fhir.py**: Modelo para parámetros de paciente FHIR.
- **neo4j.py**: Modelos para operaciones de pull/push en Neo4j.
- **say_hello.py**: Modelo para parámetros del endpoint de saludo.

---

## Resumen del flujo

1. **El archivo `app.py`** inicializa la API y registra todos los endpoints.
2. **Los endpoints** están organizados por dominio y funcionalidad, y usan modelos para validar datos.
3. **Los modelos** aseguran que los datos recibidos sean correctos y facilitan la documentación automática.
4. **La integración con LangChain** permite procesamiento de lenguaje natural en rutas específicas.


---

#### b. config
Módulos para cargar y gestionar la configuración de la aplicación.
- `config.py`: Carga la configuración usando Dynaconf.
- `logger_config.py`: Configura el sistema de logging usando Loguru y YAML.


### config.py

- Utiliza la librería **Dynaconf** para cargar la configuración desde archivos YAML.
- Lee la ruta del archivo de configuración y el entorno desde variables de entorno (`CONFIG_FILE` y `ENVIRONMENT`).
- Expone el objeto config, que se usa en todo el proyecto para acceder a parámetros como credenciales de bases de datos, endpoints, etc.

**Ejemplo de uso:**
```python
from src.config.config import config
uri = config.database.neo4j.uri
```

---

### logger_config.py

- Utiliza **Loguru** y **PyYAML** para configurar el sistema de logs a partir del archivo `logging_config.yaml`.
- Lee la configuración de logs (niveles, formatos, archivos, rotación, filtros, etc.) y crea los sinks de Loguru dinámicamente.
- Redirige los logs estándar de Python (`logging`) hacia Loguru para unificar el registro.
- Aplica filtros personalizados según la configuración YAML (por nombre, nivel o categoría).
- Ajusta el nivel de logging para librerías externas como Neo4j.

**Resultado:**  
Todos los logs del proyecto se gestionan de forma centralizada y configurable, con soporte para múltiples archivos y filtros.

---

### __init__.py

- Archivo vacío o de inicialización para tratar la carpeta como un paquete Python.

---

**Resumen:**  
La carpeta `src/config` permite que toda la configuración (parámetros de servicios y logging) sea externa, centralizada y fácilmente modificable, facilitando la gestión de entornos y el mantenimiento del proyecto.


---

#### c. domain
Define la lógica de negocio y los contratos (puertos) de la aplicación.
- `ports/`: Interfaces abstractas para acceso a datos (ej. `data_stream.py`).
- `services/`: Servicios de negocio, tanto síncronos como asíncronos, y ejemplos de servicios (ej. `SayHelloSync`, `PullSync`, `PushSync`, etc.).
- `model/`: Modelos de dominio (no se muestra contenido, pero suelen estar aquí).

---

## Estructura de `src/domain`

```
src/domain/
│
├── __init__.py
├── model/
├── ports/
│   └── dao/
│       └── data_stream.py
└── services/
    ├── __init__.py
    ├── async_service.py
    ├── service.py
    ├── sync_service.py
    ├── data/
    │   ├── get_patien_sync.py
    │   ├── pull_sync.py
    │   ├── push_sync.py
    │   └── fhir/
    │       ├── get_fhir_patients.py
    │       └── get_fhir_resources.py
    └── examples/
        ├── say_hello_async.py
        └── say_hello_sync.py
```

---

## Explicación de cada parte

### `ports/dao/data_stream.py`
Define la **interfaz abstracta** `DataStream` para los adaptadores de acceso a datos.  
- Métodos abstractos: `pull`, `push`, `update`.
- Permite desacoplar la lógica de negocio de la infraestructura concreta (por ejemplo, Neo4j).

---

### `services/`
Contiene los **servicios de dominio** que encapsulan la lógica de negocio.  
- service.py: Clase base abstracta `Service` con gestión de estado, logging y método abstracto `run`.
- sync_service.py: Servicio síncrono que hereda de `Service`.
- async_service.py: Servicio asíncrono que ejecuta la lógica en un hilo separado.
- __init__.py: Define constantes de estado (`STATUS_IDLE`, `STATUS_RUNNING`, etc.).

#### Subcarpeta `data/`
Servicios relacionados con la gestión de datos:
- get_patien_sync.py: Servicio para obtener pacientes desde un puerto de datos.
- pull_sync.py: Servicio para extraer datos de una fuente.
- push_sync.py: Servicio para insertar datos en una fuente.
- get_fhir_patients.py: Servicio para obtener pacientes FHIR desde un endpoint externo.
- get_fhir_resources.py: Servicio base para obtener recursos FHIR.

#### Subcarpeta `examples/`
Servicios de ejemplo:
- say_hello_sync.py: Servicio síncrono que retorna un saludo.
- say_hello_async.py: Servicio asíncrono que retorna un saludo.

---

### `model/`
Aquí normalmente se definen los **modelos de dominio** (no se muestra contenido, pero suelen estar aquí).

---

## Resumen del flujo

1. **Los servicios** (`Service`, `SyncService`, `AsyncService`) encapsulan la lógica de negocio y gestionan el ciclo de vida de las operaciones.
2. **Los puertos** (`DataStream`) definen contratos para el acceso a datos, permitiendo cambiar la infraestructura sin modificar la lógica de negocio.
3. **Los servicios concretos** (por ejemplo, `PullSync`, `PushSync`, `GetFHIRPatients`) implementan operaciones específicas usando los puertos.
4. **Los modelos de dominio** (en `model/`) representan las entidades centrales del negocio.





#### d. infrastructure
Implementaciones concretas de los puertos definidos en `domain/ports`.
- `adapters/`: Adaptadores para interactuar con bases de datos (ej. Neo4j) y para conversión de datos (ej. FHIR a string o a grafo).
  - `dao/`: Adaptadores DAO, como `neo4j_stream.py`.
  - `conversion/`: Conversores de datos FHIR a otros formatos.
- `logger/`: Configuración adicional de logging.


## Estructura de `src/infrastructure`

```
src/infrastructure/
│
├── __init__.py
├── adapters/
│   ├── dao/
│   │   └── neo4j_stream.py
│   └── conversion/
│       └── fhir/
│           ├── FHIR_flattener.py
│           ├── FHIR_to_graph.py
│           └── FHIR_to_string.py
```

---

## Explicación de cada parte

### 1. `adapters/dao/neo4j_stream.py`
Implementa el puerto `DataStream` para la base de datos Neo4j:
- Permite **pull** (consultar datos), **push** (insertar datos) y **update** (actualizar datos) en Neo4j usando Cypher.
- Usa el driver oficial de Neo4j y valida los símbolos permitidos antes de ejecutar las consultas.
- Devuelve los resultados como `pandas.DataFrame`.

---

### 2. `adapters/conversion/fhir/`
Contiene utilidades para convertir datos FHIR a otros formatos:

- `FHIR_flattener.py`:  
  Funciones para "aplanar" (flatten) estructuras FHIR complejas a diccionarios planos y extraer información relevante de bundles FHIR.

- `FHIR_to_string.py`:  
  Convierte recursos FHIR en descripciones de texto legibles, útiles para procesamiento de lenguaje natural o generación de resúmenes.

- `FHIR_to_graph.py`:  
  Convierte recursos FHIR en nodos y relaciones de grafo (Cypher) para Neo4j. Incluye lógica para extraer identificadores, fechas y relaciones entre recursos.

---

## Resumen

- **neo4j_stream.py**: Adaptador para operar con Neo4j desde la lógica de negocio.
- **adapters/conversion/fhir/**: Herramientas para transformar datos FHIR a texto o grafos, facilitando su almacenamiento o análisis.

Esta carpeta es clave para desacoplar la lógica de negocio de la infraestructura concreta, permitiendo cambiar la tecnología subyacente sin modificar el dominio.


---

#### e. main.py
Punto de entrada principal. Lanza el servidor Uvicorn para servir la API FastAPI.

---

### 3. test
Contiene pruebas unitarias y de integración, organizadas por dominio e infraestructura. Ejemplo: ne04j_stream_test.py.

---

### 4. requirements.txt
Lista de dependencias del proyecto.

---

### 5. README.md
Descripción básica del proyecto.

---

## Flujo general del proyecto

1. **Configuración**: Se cargan las configuraciones de servicios y logging desde YAML usando Dynaconf y Loguru.
2. **API**: Se expone una API REST con FastAPI, con endpoints para:
   - Ejemplos (`/clai/examples`)
   - Datos FHIR (`/clai/data/fhir`)
   - Datos Neo4j (`/clai/data/neo4j`)
   - Conversión FHIR a Neo4j (`/clai/conversion/fhir2neo4j`)
3. **Servicios de dominio**: Los endpoints llaman a servicios de dominio que encapsulan la lógica de negocio (por ejemplo, obtener pacientes, insertar datos, etc.).
4. **Infraestructura**: Los servicios de dominio usan adaptadores de infraestructura para interactuar con bases de datos (Neo4j) o para convertir datos (FHIR a string/grafo).
5. **Logging**: Todo el sistema está instrumentado con logs configurables por YAML.

---

## Ejemplo de flujo: Insertar un recurso FHIR en Neo4j

1. El endpoint `/clai/conversion/fhir2neo4j/resource` recibe un recurso FHIR.
2. Se convierte el recurso a un nodo de grafo usando `resource_to_node`.
3. Se crea un adaptador `Neo4jStream` con las credenciales de la configuración.
4. Se llama al servicio `PushSync` para insertar el nodo en Neo4j.
5. Se retorna la respuesta al cliente.

---

## Resumen de tecnologías usadas

- **FastAPI**: Framework web para la API.
- **Dynaconf**: Gestión de configuración.
- **Loguru**: Logging avanzado.
- **Neo4j**: Base de datos de grafos.
- **Pandas**: Manipulación de datos tabulares.
- **LangChain**: Procesamiento de lenguaje natural.
- **Pydantic**: Validación de datos.
- **Uvicorn**: Servidor ASGI para Python.



