# ?? ETL de Facturación Clínica | Python · SQL · Power BI

## Descripción del proyecto

Proyecto de Ingeniería de Datos enfocado en la construcción de un proceso ETL (Extract, Transform, Load) para procesar y consolidar información de facturación de una institución de salud.

Se utilizaron datos sintéticos que simulan operaciones de facturación clínica, permitiendo trabajar con información similar a la de un entorno real sin exponer datos sensibles.

El objetivo es transformar datos de diferentes fuentes en información confiable, aplicando controles de calidad y generando indicadores para apoyar la toma de decisiones.

## ?? Objetivos

- Construir un pipeline ETL utilizando Python.
- Consolidar información de facturas, cuentas, cargos, departamentos y planes de salud.
- Implementar validaciones de calidad de datos.
- Detectar inconsistencias y relaciones incorrectas.
- Generar un archivo consolidado para análisis.
- Visualizar los resultados mediante Power BI.

## ??? Tecnologías utilizadas

| Tecnología | Aplicación |

| Python | Desarrollo del pipeline ETL |
| Pandas | Manipulación y transformación de datos |
| SQL | Fundamentos de consulta y estructuración de datos |
| Pytest | Pruebas automatizadas |
| Power BI | Análisis y visualización |
| Git y GitHub | Control de versiones |

## ?? Proceso ETL

### 1. Extract ? Extracción
Lectura de archivos con información sintética de:
- Facturas.
- Planes de salud.
- Relación de facturas y cuentas.
- Detalle de cargos.
- Departamentos.

### 2. Transform ? Transformación
- Limpieza y preparación de datos.
- Integración de las diferentes fuentes.
- Consolidación de información mediante sus relaciones.
- Validación de integridad y consistencia.

### 3. Load ? Carga
Generación del archivo consolidado:

data/processed/facturacion_consolidada.csv`

Este archivo sirve como fuente para el análisis en Power BI.

## ?? Validaciones de calidad de datos

El pipeline implementa controles para identificar:

- Facturas duplicadas.
- Cuentas duplicadas.
- Facturas sin cuentas asociadas.
- Relaciones con facturas inexistentes.
- Departamentos inválidos.
- Planes de salud inválidos.
- Diferencias entre los totales de facturación y sus cargos.

## ?? Resultados obtenidos

En la última ejecución exitosa del pipeline se obtuvieron los siguientes resultados:

| Indicador | Resultado |

| Facturas procesadas | 100 |
| Filas consolidadas | 284 |
| Columnas generadas | 10 |
| Facturas duplicadas | 0 |
| Cuentas duplicadas | 0 |
| Relaciones sin factura | 0 |
| Departamentos inválidos | 0 |
| Planes inválidos | 0 |
| Diferencias en totales | 0 |

## ?? Dashboard en Power BI

El informe permite analizar:

- Total de facturas.
- Total facturado.
- Totalidad de cargos.
- Distribución de cargos por departamento.
- Evolución mensual de la facturación.
- Filtros por plan de salud y departamento.

## ??? Estructura del proyecto

```text
Facturacion_clinica/
?
??? data/
?   ??? raw/
?   ??? processed/
?
??? etl/
?   ??? __init__.py
?   ??? pipeline.py
?   ??? transformaciones.py
?   ??? generar_datos.py
?
??? tests/
?
??? .gitignore
??? requirements.txt
??? README.md
```

## ?? Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/DiegoJCA125/Facturacion_clinica.git
cd Facturacion_clinica
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

### 3. Activar entorno virtual (Windows)

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar el pipeline

```bash
python -m etl.pipeline
```

### 6. Ejecutar pruebas automatizadas

```bash
python -m pytest tests/ -v
```

## ?? Aprendizajes

Este proyecto permitió fortalecer conocimientos en:

- Desarrollo de procesos ETL.
- Manipulación de datos con Python y Pandas.
- Integración de fuentes relacionadas.
- Validación de calidad e integridad de datos.
- Pruebas automatizadas con Pytest.
- Preparación de datos para herramientas de BI.
- Control de versiones con Git y GitHub.

## ?? Consideraciones sobre los datos

Todos los datos utilizados en este proyecto son sintéticos y fueron generados con fines educativos y de demostración. No se utilizan registros reales de pacientes ni información confidencial de instituciones de salud.

## ????? Autor

**Juan Diego Carmona**

Ingeniero de Sistemas | En formación en Ingeniería de Datos.

GitHub: https://github.com/DiegoJCA125

LinkedIn: https://www.linkedin.com/in/diegojca125