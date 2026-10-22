from pathlib import Path
import pandas as pd


def unir_facturas_planes(df_facturas, df_planes):
    # CAMBIO: usamos LEFT JOIN para conservar las facturas
    # aunque algun plan no tenga coincidencia.
    return df_facturas.merge(
        df_planes,
        on="plan_id",
        how="left",
        validate="many_to_one"
    )


def unir_facturas_cargos(df_facturas, df_facturas_cuentas, df_cuentas_detalle):
    # Paso 1: relacionar las facturas con sus cuentas.
    facturas_cuentas = df_facturas.merge(
        df_facturas_cuentas,
        on="factura_fiscal",
        how="left",
        validate="one_to_many"
    )

    # Paso 2: incorporar el valor de cada cargo.
    facturas_cargos = facturas_cuentas.merge(
        df_cuentas_detalle,
        on="numerodecuenta",
        how="left",
        validate="many_to_one"
    )

    return facturas_cargos


def unir_facturas_departamentos(df_facturas_cargos, df_departamentos):
    # CAMBIO: el nombre del departamento se incorpora mediante
    # departamento_id, sin eliminar cargos sin coincidencia.
    return df_facturas_cargos.merge(
        df_departamentos,
        on="departamento_id",
        how="left",
        validate="many_to_one"
    )


def guardar_datos_procesados(df, ruta_salida):
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")

    print(f"Archivo guardado correctamente: {ruta_salida}")
    print(f"Filas guardadas: {len(df)}")
    print(f"Columnas guardadas: {len(df.columns)}")

    return ruta_salida
