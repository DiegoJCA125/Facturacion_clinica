
from pathlib import Path
import pandas as pd

# ==========================================
# CONFIGURACIÓN DEL PROYECTO
# ==========================================

# Ubicamos la carpeta principal del proyecto.
BASE_DIR = Path(__file__).resolve().parents[1]

# Archivo Excel con nuestros datos sintéticos.
RUTA_EXCEL = BASE_DIR / "data" / "raw" / "facturacion_clinica.xlsx"


# ==========================================
# EXTRACCIÓN DE DATOS
# ==========================================

def extraer_datos():
    """Lee las cinco hojas del archivo Excel."""

    if not RUTA_EXCEL.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {RUTA_EXCEL}"
        )

    tablas = {
        "FACTURAS": pd.read_excel(RUTA_EXCEL, sheet_name="FACTURAS"),
        "PLANES": pd.read_excel(RUTA_EXCEL, sheet_name="PLANES"),
        "FACTURAS_CUENTAS": pd.read_excel(
            RUTA_EXCEL, sheet_name="FACTURAS_CUENTAS"
        ),
        "CUENTAS_DETALLE": pd.read_excel(
            RUTA_EXCEL, sheet_name="CUENTAS_DETALLE"
        ),
        "DEPARTAMENTOS": pd.read_excel(
            RUTA_EXCEL, sheet_name="DEPARTAMENTOS"
        )
    }

    return tablas


# ==========================================
# VALIDACIÓN DE ESTRUCTURA
# ==========================================

def validar_estructura(tablas):

    columnas_esperadas = {
        "FACTURAS": [
            "factura_fiscal", "fecha_factura",
            "plan_id", "total_factura"
        ],
        "PLANES": ["plan_id", "nombre_plan", "tipo_plan"],
        "FACTURAS_CUENTAS": [
            "factura_fiscal", "numerodecuenta"
        ],
        "CUENTAS_DETALLE": [
            "numerodecuenta", "departamento_id", "valor_cargo"
        ],
        "DEPARTAMENTOS": [
            "departamento_id", "nombre_departamento"
        ]
    }

    for nombre_tabla, columnas in columnas_esperadas.items():

        columnas_faltantes = [
            columna for columna in columnas
            if columna not in tablas[nombre_tabla].columns
        ]

        if columnas_faltantes:
            raise ValueError(
                f"La tabla {nombre_tabla} no tiene estas columnas: "
                f"{columnas_faltantes}"
            )


# ==========================================
# VALIDACIONES DE CALIDAD
# ==========================================

def validar_calidad(tablas):
    """Revisa duplicados, relaciones y totales de facturación."""

    facturas = tablas["FACTURAS"]
    planes = tablas["PLANES"]
    relaciones = tablas["FACTURAS_CUENTAS"]
    detalles = tablas["CUENTAS_DETALLE"]
    departamentos = tablas["DEPARTAMENTOS"]

    # 1. Identificar facturas con identificadores duplicados.
    facturas_duplicadas = facturas[
        facturas.duplicated(
            subset=["factura_fiscal"], keep=False
        )
    ]

    # 2. Identificar cuentas asociadas más de una vez.
    cuentas_duplicadas = relaciones[
        relaciones.duplicated(
            subset=["numerodecuenta"], keep=False
        )
    ]

    # 3. Buscar facturas sin ninguna cuenta relacionada.
    facturas_con_cuenta = relaciones["factura_fiscal"].unique()

    facturas_sin_cuentas = facturas[
        ~facturas["factura_fiscal"].isin(facturas_con_cuenta)
    ]

    # 4. Buscar relaciones con facturas inexistentes.
    cuentas_sin_factura = relaciones[
        ~relaciones["factura_fiscal"].isin(
            facturas["factura_fiscal"]
        )
    ]

    # 5. Buscar detalles asociados a departamentos inexistentes.
    departamentos_invalidos = detalles[
        ~detalles["departamento_id"].isin(
            departamentos["departamento_id"]
        )
    ]

    # 6. Buscar facturas que usan planes inexistentes.
    planes_invalidos = facturas[
        ~facturas["plan_id"].isin(planes["plan_id"])
    ]

    # 7. Calcular los cargos por factura para compararlos
    # con el total almacenado en FACTURAS.
    detalle_completo = relaciones.merge(
        detalles,
        on="numerodecuenta",
        how="left"
    )

    suma_cargos = (
        detalle_completo
        .groupby("factura_fiscal")["valor_cargo"]
        .sum(min_count=1)
        .reset_index()
    )

    suma_cargos.rename(
        columns={"valor_cargo": "suma_cargos"},
        inplace=True
    )

    comparacion = facturas[
        ["factura_fiscal", "total_factura"]
    ].merge(
        suma_cargos,
        on="factura_fiscal",
        how="left"
    )

    # Una factura sin cargos o con diferencia también se reporta.
    facturas_con_diferencias = comparacion[
        comparacion["suma_cargos"].isna()
        | (
            comparacion["total_factura"]
            != comparacion["suma_cargos"]
        )
    ]

    # Mostramos los resultados de cada control.
    resultados = {
        "Facturas duplicadas (filas involucradas)": len(
            facturas_duplicadas
        ),
        "Cuentas duplicadas (filas involucradas)": len(
            cuentas_duplicadas
        ),
        "Facturas sin cuentas": len(facturas_sin_cuentas),
        "Relaciones con factura inexistente": len(cuentas_sin_factura),
        "Detalles con departamento inválido": len(departamentos_invalidos),
        "Facturas con plan inválido": len(planes_invalidos),
        "Facturas con diferencias en totales": len(
            facturas_con_diferencias
        )
    }

    print("\n====================================")
    print(" VALIDACIÓN DE CALIDAD DE DATOS")
    print("====================================")

    for nombre, cantidad in resultados.items():
        print(f"{nombre}: {cantidad}")

    # Devolvemos los resultados para utilizarlos después
    # en la limpieza y separación de registros.
    return resultados


# ==========================================
# REPORTE DE EXTRACCIÓN
# ==========================================

def mostrar_resumen(tablas):

    print("\n====================================")
    print(" RESUMEN DE EXTRACCIÓN ETL")
    print("====================================")

    for nombre_tabla, df in tablas.items():
        valores_vacios = int(df.isna().sum().sum())

        print(f"\nTabla: {nombre_tabla}")
        print(f"Cantidad de registros: {len(df)}")
        print(f"Valores vacíos: {valores_vacios}")


# ==========================================
# EJECUCIÓN DEL PIPELINE
# ==========================================
# SE COM,ENTA LINEA YA QUE ERA ANTIGUAMENTE COMO SE EJECUTABA EL PIPELINE SIMPLE
#def ejecutar_pipeline():
    #tablas = extraer_datos()
    #validar_estructura(tablas)
    #mostrar_resumen(tablas)
    #resultados = validar_calidad(tablas)
    #print("\nValidaciones finalizadas correctamente.")
    #return resultados

def ejecutar_pipeline():
    tablas = extraer_datos()
    validar_estructura(tablas)
    mostrar_resumen(tablas)

    
    # Creamos copias para probar errores sin modificar los datos originales.
    tablas_prueba = {
        nombre: df.copy()
        for nombre, df in tablas.items()
    }

    # PRUEBA 1: duplicamos la primera factura.
    tablas_prueba["FACTURAS"] = pd.concat(
        [
            tablas_prueba["FACTURAS"],
            tablas_prueba["FACTURAS"].iloc[[0]]
        ],
        ignore_index=True
    )

    # PRUEBA 2: agregamos una relación con una factura inexistente.
    nueva_relacion = pd.DataFrame([{
        "factura_fiscal": "FAC-999999",
        "numerodecuenta": "CTA-999999"
    }])

    tablas_prueba["FACTURAS_CUENTAS"] = pd.concat(
        [
            tablas_prueba["FACTURAS_CUENTAS"],
            nueva_relacion
        ],
        ignore_index=True
    )

    # PRUEBA 3: asignamos un departamento que no existe.
    tablas_prueba["CUENTAS_DETALLE"].loc[
        tablas_prueba["CUENTAS_DETALLE"].index[0],
        "departamento_id"
    ] = 999

    # PRUEBA 4: modificamos el total de la primera factura.
    tablas_prueba["FACTURAS"].loc[
        tablas_prueba["FACTURAS"].index[0],
        "total_factura"
    ] += 100000

    # Ejecutamos las validaciones sobre las copias modificadas.
    resultados = validar_calidad(tablas_prueba)

    print("\nPruebas de errores controlados finalizadas.")
    return resultados


if __name__ == "__main__":
    ejecutar_pipeline()
