
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. UNIR FACTURAS CON PLANES
# --------------------------------------------------

def unir_facturas_planes(tablas):
    facturas = tablas["FACTURAS"].copy()
    planes = tablas["PLANES"].copy()

    # Agregamos el nombre y tipo del plan a cada factura.
    facturas_con_planes = facturas.merge(
        planes[["plan_id", "nombre_plan", "tipo_plan"]],
        on="plan_id",
        how="left",
        validate="many_to_one"
    )

    return facturas_con_planes


# --------------------------------------------------
# 2. UNIR FACTURAS CON CUENTAS Y CARGOS
# --------------------------------------------------

def unir_facturas_cargos(tablas):
    # Primero incorporamos la información de los planes.
    facturas_con_planes = unir_facturas_planes(tablas)

    relaciones = tablas["FACTURAS_CUENTAS"].copy()
    detalles = tablas["CUENTAS_DETALLE"].copy()

    # Relacionamos cada factura con sus cuentas.
    facturas_con_cuentas = facturas_con_planes.merge(
        relaciones,
        on="factura_fiscal",
        how="left",
        validate="one_to_many"
    )

    # Incorporamos los cargos registrados en cada cuenta.
    facturas_con_cargos = facturas_con_cuentas.merge(
        detalles,
        on="numerodecuenta",
        how="left",
        validate="many_to_many"
    )

    return facturas_con_cargos


# --------------------------------------------------
# 3. AGREGAR LOS NOMBRES DE LOS DEPARTAMENTOS
# --------------------------------------------------

def unir_facturas_departamentos(tablas):
    facturas_con_cargos = unir_facturas_cargos(tablas)
    departamentos = tablas["DEPARTAMENTOS"].copy()

    # Incorporamos el nombre del departamento de cada cargo.
    facturas_con_departamentos = facturas_con_cargos.merge(
        departamentos[
            ["departamento_id", "nombre_departamento"]
        ],
        on="departamento_id",
        how="left",
        validate="many_to_one"
    )

    return facturas_con_departamentos


# --------------------------------------------------
# 4. GUARDAR LA TABLA CONSOLIDADA
# --------------------------------------------------

def guardar_datos_procesados(tabla_consolidada):
    # Localizamos la raíz del proyecto, sin depender
    # de la carpeta desde la que se ejecute el comando.
    base_dir = Path(__file__).resolve().parents[1]

    # Creamos la carpeta de salida si no existe.
    carpeta_salida = base_dir / "data" / "processed"
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    # Definimos la ruta del archivo final.
    ruta_csv = carpeta_salida / "facturacion_consolidada.csv"

    # Exportamos sin el índice de pandas.
    tabla_consolidada.to_csv(
        ruta_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nArchivo procesado guardado en: {ruta_csv}")

    return ruta_csv
