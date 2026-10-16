
from pathlib import Path
import pandas as pd

# IMPORTACIÓN COMPATIBLE CON LAS DOS FORMAS DE EJECUTAR EL PIPELINE.
# Si se ejecuta como módulo, usamos la importación relativa.
# Si se ejecuta directamente como archivo, usamos la alternativa.
try:
    from .transformaciones import (
        unir_facturas_departamentos,
        guardar_datos_procesados
    )
except ImportError:
    from transformaciones import (
        unir_facturas_departamentos,
        guardar_datos_procesados
    )


# --------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# --------------------------------------------------

# Localizamos la raíz del proyecto.
BASE_DIR = Path(__file__).resolve().parents[1]

# Ruta del Excel con los datos de entrada.
RUTA_EXCEL = (
    BASE_DIR / "data" / "raw" / "facturacion_clinica.xlsx"
)


# --------------------------------------------------
# 1. EXTRACCIÓN
# --------------------------------------------------

def extraer_datos():
    # Confirmamos que exista el archivo antes de leerlo.
    if not RUTA_EXCEL.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo Excel: {RUTA_EXCEL}"
        )

    # Leemos las cinco hojas del archivo de Excel.
    tablas = {
        "FACTURAS": pd.read_excel(
            RUTA_EXCEL, sheet_name="FACTURAS"
        ),
        "PLANES": pd.read_excel(
            RUTA_EXCEL, sheet_name="PLANES"
        ),
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

    print("Extracción completada: cinco tablas cargadas.")

    return tablas


# --------------------------------------------------
# 2. VALIDACIÓN DE ESTRUCTURA
# --------------------------------------------------

def validar_estructura(tablas):
    # Columnas obligatorias para cada tabla.
    columnas_esperadas = {
        "FACTURAS": [
            "factura_fiscal", "fecha_factura",
            "plan_id", "total_factura"
        ],
        "PLANES": [
            "plan_id", "nombre_plan", "tipo_plan"
        ],
        "FACTURAS_CUENTAS": [
            "factura_fiscal", "numerodecuenta"
        ],
        "CUENTAS_DETALLE": [
            "numerodecuenta", "departamento_id",
            "valor_cargo"
        ],
        "DEPARTAMENTOS": [
            "departamento_id", "nombre_departamento"
        ]
    }

    # Revisamos que cada tabla tenga sus columnas requeridas.
    for nombre_tabla, columnas in columnas_esperadas.items():
        if nombre_tabla not in tablas:
            raise ValueError(
                f"No se encontró la tabla requerida: {nombre_tabla}"
            )

        columnas_faltantes = [
            columna
            for columna in columnas
            if columna not in tablas[nombre_tabla].columns
        ]

        if columnas_faltantes:
            raise ValueError(
                f"La tabla {nombre_tabla} no tiene estas columnas: "
                f"{columnas_faltantes}"
            )

    print("La estructura de las cinco tablas es correcta.")


# --------------------------------------------------
# 3. VALIDACIÓN DE CALIDAD DE LOS DATOS
# --------------------------------------------------

def validar_calidad(tablas):
    facturas = tablas["FACTURAS"]
    planes = tablas["PLANES"]
    relaciones = tablas["FACTURAS_CUENTAS"]
    detalles = tablas["CUENTAS_DETALLE"]
    departamentos = tablas["DEPARTAMENTOS"]

    # 1. Detectamos todas las filas que tienen una factura duplicada.
    facturas_duplicadas = facturas[
        facturas.duplicated(
            subset=["factura_fiscal"], keep=False
        )
    ]

    # 2. Detectamos cuentas repetidas en la tabla de relaciones.
    cuentas_duplicadas = relaciones[
        relaciones.duplicated(
            subset=["numerodecuenta"], keep=False
        )
    ]

    # 3. Detectamos facturas que no tienen una cuenta asociada.
    facturas_con_cuenta = relaciones["factura_fiscal"].unique()

    facturas_sin_cuentas = facturas[
        ~facturas["factura_fiscal"].isin(facturas_con_cuenta)
    ]

    # 4. Detectamos relaciones que apuntan a facturas inexistentes.
    cuentas_sin_factura = relaciones[
        ~relaciones["factura_fiscal"].isin(
            facturas["factura_fiscal"]
        )
    ]

    # 5. Detectamos cargos que usan departamentos inexistentes.
    departamentos_invalidos = detalles[
        ~detalles["departamento_id"].isin(
            departamentos["departamento_id"]
        )
    ]

    # 6. Detectamos facturas que tienen un plan inexistente.
    planes_invalidos = facturas[
        ~facturas["plan_id"].isin(planes["plan_id"])
    ]

    # 7. Sumamos los cargos por factura para compararlos
    # con el total registrado en la tabla FACTURAS.
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
        .rename(columns={"valor_cargo": "suma_cargos"})
    )

    comparacion = facturas[
        ["factura_fiscal", "total_factura"]
    ].merge(
        suma_cargos,
        on="factura_fiscal",
        how="left"
    )

    facturas_con_diferencias = comparacion[
        comparacion["suma_cargos"].isna()
        | (
            comparacion["total_factura"]
            != comparacion["suma_cargos"]
        )
    ]

    # Consolidamos los resultados de las siete validaciones.
    resultados = {
        "Facturas duplicadas (filas involucradas)":
            len(facturas_duplicadas),
        "Cuentas duplicadas (filas involucradas)":
            len(cuentas_duplicadas),
        "Facturas sin cuentas":
            len(facturas_sin_cuentas),
        "Relaciones con factura inexistente":
            len(cuentas_sin_factura),
        "Detalles con departamento inválido":
            len(departamentos_invalidos),
        "Facturas con plan inválido":
            len(planes_invalidos),
        "Facturas con diferencias en totales":
            len(facturas_con_diferencias)
    }

    # Mostramos las validaciones una sola vez.
    print("\n========================================")
    print("     VALIDACIÓN DE CALIDAD DE DATOS")
    print("========================================")

    for nombre, cantidad in resultados.items():
        print(f"{nombre}: {cantidad}")

    return resultados


# --------------------------------------------------
# 4. EJECUCIÓN COMPLETA DEL PIPELINE
# --------------------------------------------------

def ejecutar_pipeline():
    print("\nINICIANDO PIPELINE DE FACTURACIÓN")
    print("----------------------------------------")

    # ETAPA 1: extraemos los datos del Excel.
    tablas = extraer_datos()

    # ETAPA 2: verificamos que las tablas estén completas.
    validar_estructura(tablas)

    # ETAPA 3: ejecutamos las siete validaciones de calidad.
    resultados = validar_calidad(tablas)

    # Si una validación encuentra problemas, detenemos el proceso.
    if any(cantidad > 0 for cantidad in resultados.values()):
        print(
            "\nPipeline detenido: se encontraron problemas "
            "de calidad. Revisa los datos antes de continuar."
        )
        return resultados

    print("\nLos datos superaron las siete validaciones.")

    # ETAPA 4: unimos facturas, planes, cuentas, cargos
    # y departamentos.
    tabla_consolidada = unir_facturas_departamentos(tablas)

    # Verificamos que cada cargo tenga un departamento asociado.
    cargos_sin_departamento = (
        tabla_consolidada["nombre_departamento"].isna().sum()
    )

    print("\n========================================")
    print("       RESULTADO DE LA TRANSFORMACIÓN")
    print("========================================")
    print("Filas consolidadas:", len(tabla_consolidada))
    print("Columnas consolidadas:", len(tabla_consolidada.columns))
    print("Cargos sin nombre de departamento:", cargos_sin_departamento)

    # Si hay departamentos sin identificar, no guardamos el CSV.
    if cargos_sin_departamento > 0:
        raise ValueError(
            "Hay cargos sin nombre de departamento. "
            "Revisa las relaciones antes de continuar."
        )

    # ETAPA 5: guardamos la tabla consolidada.
    ruta_csv = guardar_datos_procesados(tabla_consolidada)

    # ETAPA 6: volvemos a leer el CSV para comprobar el resultado.
    datos_guardados = pd.read_csv(ruta_csv)

    print("\n========================================")
    print("       COMPROBACIÓN DEL CSV GUARDADO")
    print("========================================")
    print("Filas de la tabla consolidada:", len(tabla_consolidada))
    print("Filas leídas desde el CSV:", len(datos_guardados))
    print("Columnas guardadas:", len(datos_guardados.columns))

    # Confirmamos que coincidan las cantidades de filas y columnas.
    if (
        len(tabla_consolidada) != len(datos_guardados)
        or len(tabla_consolidada.columns) != len(datos_guardados.columns)
    ):
        raise ValueError(
            "El CSV guardado no coincide en cantidad de filas "
            "o columnas con la tabla consolidada."
        )

    print("El CSV conserva la cantidad de filas y columnas.")
    print("\nPIPELINE FINALIZADO CORRECTAMENTE.")

    return resultados


# Ejecutamos el proceso solo si este archivo se ejecuta directamente.
if __name__ == "__main__":
    ejecutar_pipeline()
