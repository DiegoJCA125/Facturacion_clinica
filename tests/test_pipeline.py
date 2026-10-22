import pandas as pd

from etl.pipeline import validar_datos
from etl.transformaciones import (
    unir_facturas_planes,
    unir_facturas_cargos,
    unir_facturas_departamentos,
)


def crear_datos_prueba():
    # Se realiza test con datos pequeños para el etl.
    facturas = pd.DataFrame([{
        "factura_fiscal": "FC-001",
        "fecha_factura": "2026-01-01",
        "plan_id": 1,
        "total_factura": 100000,
    }])

    planes = pd.DataFrame([{
        "plan_id": 1,
        "nombre_plan": "Particular",
        "tipo_plan": "Particular",
    }])

    facturas_cuentas = pd.DataFrame([{
        "factura_fiscal": "FC-001",
        "numerodecuenta": 1001,
    }])

    cuentas_detalle = pd.DataFrame([{
        "numerodecuenta": 1001,
        "departamento_id": 101,
        "valor_cargo": 100000,
    }])

    departamentos = pd.DataFrame([{
        "departamento_id": 101,
        "nombre_departamento": "Urgencias",
    }])

    return (
        facturas, planes, facturas_cuentas,
        cuentas_detalle, departamentos
    )


def test_validaciones_sin_errores():
    datos = crear_datos_prueba()

    resultados = validar_datos(*datos)

    # Todas las validaciones deben dar cero.
    assert all(valor == 0 for valor in resultados.values())


def test_transformacion_conserva_datos():
    facturas, planes, relaciones, detalles, departamentos = (
        crear_datos_prueba()
    )

    df = unir_facturas_planes(facturas, planes)
    df = unir_facturas_cargos(df, relaciones, detalles)
    df = unir_facturas_departamentos(df, departamentos)

    assert len(df) == 1
    assert df.loc[0, "factura_fiscal"] == "FC-001"
    assert df.loc[0, "nombre_plan"] == "Particular"
    assert df.loc[0, "nombre_departamento"] == "Urgencias"
    assert df.loc[0, "valor_cargo"] == 100000