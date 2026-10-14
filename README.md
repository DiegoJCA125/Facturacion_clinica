# Proyecto de Facturación Clínica — ETL

## Descripción

Proyecto de práctica de Ingeniería de Datos orientado al procesamiento y análisis de información de facturación clínica mediante datos sintéticos.

El objetivo es construir un proceso ETL que permita extraer, validar, transformar y preparar los datos para su posterior almacenamiento en una base de datos y análisis mediante herramientas de inteligencia de negocios.

## Tecnologías utilizadas

- **Python:** generación y procesamiento de datos.
- **Pandas:** manipulación y validación de tablas.
- **Faker:** generación de datos ficticios.
- **OpenPyXL:** creación de archivos Excel.
- **Git y GitHub:** control de versiones.

## Modelo de datos

El conjunto de datos está organizado en cinco tablas:

1. **FACTURAS:** identificador, fecha, plan y total facturado.
2. **PLANES:** nombre y tipo de plan.
3. **FACTURAS_CUENTAS:** relación entre facturas y cuentas.
4. **CUENTAS_DETALLE:** departamento y valor de cada cargo.
5. **DEPARTAMENTOS:** catálogo de departamentos.

## Validaciones de calidad

El proyecto contempla controles para detectar:

- Facturas duplicadas.
- Cuentas duplicadas.
- Facturas sin cuentas asociadas.
- Relaciones con facturas inexistentes.
- Departamentos inválidos.
- Diferencias entre el total de una factura y la suma de sus cargos.

También se realizan pruebas con errores controlados para comprobar el funcionamiento de las validaciones.

## Estructura del proyecto

```text
ETL_Facturacion_Clinica/
├── data/
│   ├── raw/
│   ├── processed/
│   └── output/
├── etl/
├── sql/
├── .gitignore
├── README.md
└── generar_datos.py
```

## Estado actual

- [x] Generación de datos sintéticos.
- [x] Creación del archivo Excel con cinco tablas.
- [x] Validaciones iniciales de calidad de datos.
- [x] Pruebas controladas de errores.
- [ ] Construcción del proceso ETL de limpieza.
- [ ] Separación de registros válidos y rechazados.
- [ ] Almacenamiento en PostgreSQL.
- [ ] Consultas SQL para análisis.
- [ ] Creación de un tablero en Power BI.

## Consideraciones

Todos los datos utilizados en este proyecto son sintéticos y se destinan exclusivamente a fines educativos y de portafolio. No se deben utilizar ni publicar datos personales o información confidencial de pacientes.

## Autor

Diego Carmona

Proyecto de aprendizaje y portafolio en Ingeniería de Datos.
