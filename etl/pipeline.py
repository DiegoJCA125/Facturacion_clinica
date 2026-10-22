from pathlib import Path
import pandas as pd

# Permite ejecutar el archivo  directamente desde etl/.
try:
    from .transformaciones import (
        unir_facturas_planes,
        unir_facturas_cargos,
        unir_facturas_departamentos,
        guardar_datos_procesados,
    )
except ImportError:
    from transformaciones import (
        unir_facturas_planes,
        unir_facturas_cargos,
        unir_facturas_departamentos,
        guardar_datos_procesados,
    )


# Rutas basadas en la ubicacion del proyecto
RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_EXCEL = RAIZ_PROYECTO / "data" / "raw" / "facturacion_clinica.xlsx"
RUTA_CSV = RAIZ_PROYECTO / "data" / "processed" / "facturacion_consolidada.csv"


def validar_datos(facturas, planes, facturas_cuentas,
                  cuentas_detalle, departamentos):
    # VALIDACIoN 1: buscara facturas duplicadas.
    duplicados_facturas = int(
        facturas["factura_fiscal"].duplicated().sum()
    )

    # VALIDACIoN 2: buscara cuentas duplicadas en el detalle.
    duplicados_cuentas = int(
        cuentas_detalle["numerodecuenta"].duplicated().sum()
    )

    # VALIDACIoN 3: buscara facturas que no tienen ninguna cuenta relacionada.
    facturas_con_cuenta = set(
        facturas_cuentas["factura_fiscal"].dropna()
    )
    facturas_sin_cuenta = int(
        (~facturas["factura_fiscal"].isin(facturas_con_cuenta)).sum()
    )

    # VALIDACIoN 4: buscararelaciones que apuntan a facturas inexistentes.
    ids_facturas = set(facturas["factura_fiscal"].dropna())
    relaciones_sin_factura = int(
        (~facturas_cuentas["factura_fiscal"].isin(ids_facturas)).sum()
    )

    # VALIDACIoN 5: buscara cargos con departamentos inexistentes.
    ids_departamentos = set(departamentos["departamento_id"].dropna())
    departamentos_invalidos = int(
        (~cuentas_detalle["departamento_id"].isin(ids_departamentos)).sum()
    )

    # VALIDACIoN 6: buscarafacturas con planes inexistentes.
    ids_planes = set(planes["plan_id"].dropna())
    planes_invalidos = int(
        (~facturas["plan_id"].isin(ids_planes)).sum()
    )

    # VALIDACIoN 7: diferencias entre el total de la factura y la suma de sus cargos. Solo se comparan facturas sin duplicados y con relaciones identificables para no falsear el resultado.
    facturas_unicas = facturas.drop_duplicates(
        subset="factura_fiscal", keep=False
    )
    relaciones_validas = facturas_cuentas[
        facturas_cuentas["factura_fiscal"].isin(ids_facturas)
    ]
    cargos_validos = cuentas_detalle[
        cuentas_detalle["numerodecuenta"].isin(
            set(relaciones_validas["numerodecuenta"].dropna())
        )
    ]

    cargos_por_factura = (
        relaciones_validas
        .merge(cargos_validos, on="numerodecuenta", how="inner")
        .groupby("factura_fiscal")["valor_cargo"]
        .sum()
    )

    comparacion = facturas_unicas.set_index("factura_fiscal")[
        "total_factura"
    ].to_frame().join(cargos_por_factura.rename("total_cargos"))

    comparacion = comparacion.dropna(subset=["total_cargos"])
    diferencias_totales = int(
        (comparacion["total_factura"] != comparacion["total_cargos"]).sum()
    )

    resultados = {
        "Facturas duplicadas": duplicados_facturas,
        "Cuentas duplicadas": duplicados_cuentas,
        "Facturas sin cuentas": facturas_sin_cuenta,
        "Relaciones sin factura": relaciones_sin_factura,
        "Departamentos invalidos": departamentos_invalidos,
        "Planes invalidos": planes_invalidos,
        "Diferencias en totales": diferencias_totales,
    }

    print("\nVALIDACIONES DE CALIDAD")
    for nombre, cantidad in resultados.items():
        estado = "OK" if cantidad == 0 else "ERROR"
        print(f"[{estado}] {nombre}: {cantidad}")

    return resultados


def ejecutar_pipeline():
    print("=" * 55)
    print("INICIANDO PIPELINE DE FACTURACIoN CLiNICA")
    print("=" * 55)

    if not RUTA_EXCEL.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo: {RUTA_EXCEL}\n"
            "Verifica que exista o genera los datos sinteticos."
        )

    # Lectura de las cinco hojas del archivo Excel.
    hojas = pd.read_excel(RUTA_EXCEL, sheet_name=None)

    hojas_requeridas = [
        "FACTURAS",
        "PLANES",
        "FACTURAS_CUENTAS",
        "CUENTAS_DETALLE",
        "DEPARTAMENTOS",
    ]

    for hoja in hojas_requeridas:
        if hoja not in hojas:
            raise ValueError(f"Falta la hoja requerida: {hoja}")

    facturas = hojas["FACTURAS"]
    planes = hojas["PLANES"]
    facturas_cuentas = hojas["FACTURAS_CUENTAS"]
    cuentas_detalle = hojas["CUENTAS_DETALLE"]
    departamentos = hojas["DEPARTAMENTOS"]

    # Verificara las columnas necesarias antes de transformar.
    columnas_requeridas = {
        "FACTURAS": [
            "factura_fiscal", "fecha_factura", "plan_id", "total_factura"
        ],
        "PLANES": ["plan_id", "nombre_plan", "tipo_plan"],
        "FACTURAS_CUENTAS": ["factura_fiscal", "numerodecuenta"],
        "CUENTAS_DETALLE": [
            "numerodecuenta", "departamento_id", "valor_cargo"
        ],
        "DEPARTAMENTOS": ["departamento_id", "nombre_departamento"],
    }

    for nombre, columnas in columnas_requeridas.items():
        faltantes = set(columnas) - set(hojas[nombre].columns)
        if faltantes:
            raise ValueError(
                f"En {nombre} faltan estas columnas: {sorted(faltantes)}"
            )

    resultados = validar_datos(
        facturas, planes, facturas_cuentas,
        cuentas_detalle, departamentos
    )

    # No producira el CSV final si las validaciones detectan problemas.
    errores = {nombre: cantidad for nombre, cantidad in resultados.items()
               if cantidad > 0}

    if errores:
        raise ValueError(
            "El pipeline se detuvo porque hay errores de calidad. "
            "Revisa el detalle anterior antes de generar el resultado final."
        )

    # Uniones sucesivas para conservar las funciones del proyecto.
    df = unir_facturas_planes(facturas, planes)

    df = unir_facturas_cargos(
        df, facturas_cuentas, cuentas_detalle
    )

    df = unir_facturas_departamentos(df, departamentos)

    # Mantener el formato consolidado de 10 columnas.
    columnas_salida = [
        "factura_fiscal",
        "fecha_factura",
        "plan_id",
        "nombre_plan",
        "tipo_plan",
        "total_factura",
        "numerodecuenta",
        "departamento_id",
        "nombre_departamento",
        "valor_cargo",
    ]

    df = df[columnas_salida]

    if df["nombre_departamento"].isna().any():
        raise ValueError(
            "Hay cargos sin nombre de departamento. "
            "No se generara el CSV final."
        )

    guardar_datos_procesados(df, RUTA_CSV)

    print("\nPIPELINE FINALIZADO CORRECTAMENTE")
    print(f"Filas consolidadas: {len(df)}")
    print(f"Archivo de salida: {RUTA_CSV}")

    return df


if __name__ == "__main__":
    ejecutar_pipeline()
