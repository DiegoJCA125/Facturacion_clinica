from pathlib import Path
import pandas as pd


RUTA_SALIDA = Path("data/raw/facturacion_clinica.xlsx")


def generar_datos():
    # planes ficticios.
    planes = pd.DataFrame([
        {"plan_id": 1, "nombre_plan": "Particular", "tipo_plan": "Particular"},
        {"plan_id": 2, "nombre_plan": "Salud Total (EPS)", "tipo_plan": "EPS"},
        {"plan_id": 3, "nombre_plan": "SURA (EPS)", "tipo_plan": "EPS"},
        {"plan_id": 4, "nombre_plan": "Nueva EPS", "tipo_plan": "EPS"},
        {"plan_id": 5, "nombre_plan": "Medicina Prepagada", "tipo_plan": "Prepagada"},
    ])

    # departamentos ficticios.
    departamentos = pd.DataFrame([
        {"departamento_id": 101, "nombre_departamento": "Urgencias"},
        {"departamento_id": 102, "nombre_departamento": "Hospitalizacion"},
        {"departamento_id": 103, "nombre_departamento": "Cirugia"},
        {"departamento_id": 104, "nombre_departamento": "Consulta Externa"},
        {"departamento_id": 105, "nombre_departamento": "Laboratorio"},
        {"departamento_id": 106, "nombre_departamento": "Imagenologia"},
    ])

    facturas = []
    facturas_cuentas = []
    cuentas_detalle = []

    numero_cuenta = 1001

    for i in range(1, 101):
        factura_fiscal = f"FC-{i:05d}"
        plan_id = ((i - 1) % 5) + 1
        fecha = pd.Timestamp("2026-01-01") + pd.Timedelta(days=(i * 3) % 270)

        # 84 facturas tendran 3 cuentas y 16 tendran 2.
        # Asi obtenemos exactamente 284 relaciones.
        cantidad_cuentas = 3 if i <= 84 else 2
        total_factura = 0

        cuentas_de_esta_factura = []

        for j in range(cantidad_cuentas):
            valor_cargo = 15000 + ((i * 7919 + j * 3571) % 150000)
            departamento_id = 101 + ((i + j) % 6)

            cuentas_de_esta_factura.append({
                "factura_fiscal": factura_fiscal,
                "numerodecuenta": numero_cuenta,
            })

            cuentas_detalle.append({
                "numerodecuenta": numero_cuenta,
                "departamento_id": departamento_id,
                "valor_cargo": valor_cargo,
            })

            total_factura += valor_cargo
            numero_cuenta += 1

        facturas_cuentas.extend(cuentas_de_esta_factura)

        facturas.append({
            "factura_fiscal": factura_fiscal,
            "fecha_factura": fecha.date().isoformat(),
            "plan_id": plan_id,
            "total_factura": total_factura,
        })

    # Crear el directorio si todavia no existe.
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)

    # Guardar las cinco hojas que consume el pipeline.
    with pd.ExcelWriter(RUTA_SALIDA, engine="openpyxl") as writer:
        pd.DataFrame(facturas).to_excel(
            writer, sheet_name="FACTURAS", index=False
        )
        planes.to_excel(writer, sheet_name="PLANES", index=False)
        pd.DataFrame(facturas_cuentas).to_excel(
            writer, sheet_name="FACTURAS_CUENTAS", index=False
        )
        pd.DataFrame(cuentas_detalle).to_excel(
            writer, sheet_name="CUENTAS_DETALLE", index=False
        )
        departamentos.to_excel(
            writer, sheet_name="DEPARTAMENTOS", index=False
        )

    print(f"Archivo generado: {RUTA_SALIDA}")
    print(f"Facturas: {len(facturas)}")
    print(f"Relaciones factura-cuenta: {len(facturas_cuentas)}")
    print(f"Detalles de cargos: {len(cuentas_detalle)}")


if __name__ == "__main__":
    generar_datos()
