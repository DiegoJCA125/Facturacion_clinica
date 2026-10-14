import pandas as pd
import random
from faker import Faker

# Faker permite generar datos ficticios
fake = Faker("es_CO")

# Semilla para que los datos generados sean reproducibles.
# Si ejecutamos nuevamente el programa, tendremos los mismos datos.
random.seed(42)
Faker.seed(42)

# 1. DEPARTAMENTOS DE LA CLINICA
departamentos = [
    {"departamento_id": 101, "nombre_departamento": "Urgencias"},
    {"departamento_id": 102, "nombre_departamento": "Hospitalización"},
    {"departamento_id": 103, "nombre_departamento": "Cirugía"},
    {"departamento_id": 104, "nombre_departamento": "Consulta Externa"},
    {"departamento_id": 105, "nombre_departamento": "Laboratorio"},
    {"departamento_id": 106, "nombre_departamento": "Imagenología"},
]

df_departamentos = pd.DataFrame(departamentos)

print("Departamentos creados:")
print(df_departamentos)

#2. PLANES DE MEDICINA
planes = [
    {"plan_id": 1, "nombre_plan": "Particular", "tipo_plan": "Particular"},
    {"plan_id": 2, "nombre_plan": "Salud Total", "tipo_plan": "EPS"},
    {"plan_id": 3, "nombre_plan": "SURA", "tipo_plan": "EPS"},
    {"plan_id": 4, "nombre_plan": "Nueva EPS", "tipo_plan": "EPS"},
    {"plan_id": 5, "nombre_plan": "Medicina Prepagada", "tipo_plan": "Prepagada"},
]

df_planes = pd.DataFrame(planes)

print("\n Planes Creados:")
print(df_planes)

# 3. FACTURAS 

cantidad_facturas = 100
facturas = []

for i in range(1, cantidad_facturas +1):
    factura_fiscal = f"FAC-{i:06d}"

    # SE ELIGE ALEATORIAMENTE UN PLAN DE MEDICINA
    plan_id = random.randint(1, 5)

    # FECHA FICTICA DEL 2026
    fecha_factura = fake.date_between(start_date ="-1y", end_date="today")

    facturas.append({
        "factura_fiscal": factura_fiscal,
        "fecha_factura": fecha_factura,
        "plan_id": plan_id
    })
df_facturas = pd.DataFrame(facturas)

print("\n Primeras facturas:")
print(df_facturas.head())

# 4. FACTURAS_CUENTAS Y CUENTAS_DETALLE

facturas_cuentas = []
cuentas_detalle = []

numero_cuenta = 1

for factura in facturas:
    factura_fiscal = factura["factura_fiscal"]
    #CADA FACTURA TENDRA ENTRE 1 Y 5 CUENTAS
    cantidad_cuentas = random.randint(1, 5)
    for _ in range(cantidad_cuentas):
        numerodecuenta = f"CTA-{numero_cuenta:06d}"
        #SELECIONA ALERATORIAMENTE UN DEPARTAMENTO
        departamento_id = random.choice(departamentos)["departamento_id"]

        #SE GENMERA EL VALOR DEL CARGO
        valor_cargo = random.randint(50000, 1500000)

        facturas_cuentas.append({
            "factura_fiscal": factura_fiscal,
            "numerodecuenta": numerodecuenta,
        })

        cuentas_detalle.append({
            "numerodecuenta": numerodecuenta,
            "departamento_id": departamento_id,
            "valor_cargo": valor_cargo
        })
        numero_cuenta += 1

df_facturas_cuentas = pd.DataFrame(facturas_cuentas)
# Validamos que las columnas esperadas existan.
columnas_esperadas = [
    "factura_fiscal",
    "numerodecuenta"
]

if not all(columna in df_facturas_cuentas.columns for columna in columnas_esperadas):
    raise ValueError(
        "ERROR: La tabla FACTURAS_CUENTAS no tiene las columnas esperadas."
    )
df_cuentas_detalle = pd.DataFrame(cuentas_detalle)

print("\nFacturas - Cuentas:")
print(df_facturas_cuentas.head())

print("\nDetalle de cuentas:")
print(df_cuentas_detalle.head())

#5 CALCULAR TOTAL DE LAS FACTURAS
#SE UNEN FACTURAS_CUENTAS CON CUENTAS_DETALLE, PARA SABER CUANTO DINERO CORRESPONDE A CADA FACTURA
detalle_facturas = df_facturas_cuentas.merge(
    df_cuentas_detalle, on="numerodecuenta", how="left"
)

#SE SUMA TODOS LSO CARGOS PERTENECIENTES A CADA FACTURA
totales_facturas = (
    detalle_facturas
    .groupby("factura_fiscal")["valor_cargo"]
    .sum()
    .reset_index()
)

# SE CAMBIA EL NOMBRE PARA QUE COINCIDA CON LA TABLA DE FACTURAS
totales_facturas.rename(
    columns={"valor_cargo": "total_factura"},
    inplace=True
)

# SE AGREEGA EL TOTAL A LA TABLA DE FACTURAS
df_facturas = df_facturas.merge(
    totales_facturas, on="factura_fiscal", how="left"
)
print("\nFacturas con total:")
print(df_facturas.head())

#6. EXPORTAR A EXCEL
ruta_salida = "data/raw/facturacion_clinica.xlsx"

with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
    df_facturas.to_excel(writer, sheet_name="FACTURAS", index=False)
    df_planes.to_excel(writer, sheet_name="PLANES", index=False)
    df_facturas_cuentas.to_excel(writer, sheet_name="FACTURAS_CUENTAS", index=False)
    df_cuentas_detalle.to_excel(writer, sheet_name="CUENTAS_DETALLE", index=False)
    df_departamentos.to_excel(writer, sheet_name="DEPARTAMENTOS", index=False)


# ==========================================
#  VALIDACIONES DE CALIDAD DE LOS DATOS
# ==========================================

print("\n---------------------------------------")
print(" VALIDACIÓN DE CALIDAD DE LOS DATOS")
print("---------------------------------------")

# 1. Verificar si existen facturas duplicadas.
# Cada factura debe tener un identificador único.
facturas_duplicadas = df_facturas[
    df_facturas.duplicated(
        subset=["factura_fiscal"],
        keep=False
    )
]

print("\n1. Facturas duplicadas:")
print(len(facturas_duplicadas))

# 2. Verificar si existen cuentas duplicadas.
# Una cuenta no debe aparecer repetida en FACTURAS_CUENTAS.
cuentas_duplicadas = df_facturas_cuentas[
    df_facturas_cuentas.duplicated(
        subset=["numerodecuenta"],
        keep=False
    )
]

print("\n2. Cuentas duplicadas:")
print(len(cuentas_duplicadas))

# 3. Buscar facturas que no tengan ninguna cuenta asociada.
facturas_con_cuentas = df_facturas_cuentas[
    "factura_fiscal"
].unique()

facturas_sin_cuentas = df_facturas[
    ~df_facturas["factura_fiscal"].isin(facturas_con_cuentas)
]

print("\n3. Facturas sin cuentas asociadas:")
print(len(facturas_sin_cuentas))

# 4. Buscar cuentas que no estén asociadas a una factura existente.
cuentas_sin_factura = df_facturas_cuentas[
    ~df_facturas_cuentas["factura_fiscal"].isin(
        df_facturas["factura_fiscal"]
    )
]

print("\n4. Registros de cuentas sin factura válida:")
print(len(cuentas_sin_factura))

# 5. Buscar departamentos que no existan en DEPARTAMENTOS.
cuentas_con_departamento = df_cuentas_detalle[
    ~df_cuentas_detalle["departamento_id"].isin(
        df_departamentos["departamento_id"]
    )
]

print("\n5. Cuentas con departamento inválido:")
print(len(cuentas_con_departamento))

# 6. Comprobar que el total de cada factura
# coincida con la suma de los cargos de sus cuentas.
detalle_validacion = df_facturas_cuentas.merge(
    df_cuentas_detalle,
    on="numerodecuenta",
    how="left"
)

suma_cargos = (
    detalle_validacion
    .groupby("factura_fiscal")["valor_cargo"]
    .sum()
    .reset_index()
)

# Comparamos los cargos calculados con el total registrado.
comparacion_totales = df_facturas[
    ["factura_fiscal", "total_factura"]
].merge(
    suma_cargos,
    on="factura_fiscal",
    how="left"
)

# Una diferencia distinta de cero indica un posible error.
comparacion_totales["diferencia"] = (
    comparacion_totales["total_factura"]
    - comparacion_totales["valor_cargo"]
)

facturas_con_diferencias = comparacion_totales[
    comparacion_totales["diferencia"] != 0
]

print("\n6. Facturas con diferencias en los totales:")
print(len(facturas_con_diferencias))

# Resumen final para saber cuántos problemas encontramos.
total_problemas = (
    len(facturas_duplicadas)
    + len(cuentas_duplicadas)
    + len(facturas_sin_cuentas)
    + len(cuentas_sin_factura)
    + len(cuentas_con_departamento)
    + len(facturas_con_diferencias)
)

print("\n---------------------------------------")
print(f"Total de hallazgos: {total_problemas}")
print("---------------------------------------")


# ==========================================
#  COPIAS PARA PRUEBAS DE CALIDAD
# ==========================================

# Creamos copias para simular errores sin modificar
# los DataFrames originales del proyecto.
df_facturas_prueba = df_facturas.copy()
df_facturas_cuentas_prueba = df_facturas_cuentas.copy()
df_cuentas_detalle_prueba = df_cuentas_detalle.copy()
df_departamentos_prueba = df_departamentos.copy()

print("\n==================================")
print("COPIAS DE PRUEBA CREADAS")
print("====================================")

print("Facturas:", len(df_facturas_prueba))
print("Relaciones factura-cuenta:", len(df_facturas_cuentas_prueba))
print("Detalles de cuentas:", len(df_cuentas_detalle_prueba))
print("Departamentos:", len(df_departamentos_prueba))


# ==========================================
#  SIMULACIÓN DE ERRORES CONTROLADOS
# ==========================================

# ERROR 1: Duplicar una factura.
# Copiamos la primera fila y la agregamos nuevamente.
factura_duplicada = df_facturas_prueba.iloc[[0]].copy()

df_facturas_prueba = pd.concat(
    [df_facturas_prueba, factura_duplicada],
    ignore_index=True
)

# ERROR 2: Crear una relación con una factura inexistente.
# Usamos una factura ficticia que no está en FACTURAS.
cuenta_sin_factura = pd.DataFrame([{
    "factura_fiscal": "FAC-999999",
    "numerodecuenta": "CTA-999999"
}])

df_facturas_cuentas_prueba = pd.concat(
    [df_facturas_cuentas_prueba, cuenta_sin_factura],
    ignore_index=True
)

# ==========================================
#  COMPROBAR SI DETECTAMOS LOS ERRORES
# ==========================================

# Buscamos las facturas duplicadas.
duplicados_detectados = df_facturas_prueba[
    df_facturas_prueba.duplicated(
        subset=["factura_fiscal"],
        keep=False
    )
]

# Buscamos relaciones cuya factura no existe.
cuentas_sin_factura_detectadas = df_facturas_cuentas_prueba[
    ~df_facturas_cuentas_prueba["factura_fiscal"].isin(
        df_facturas_prueba["factura_fiscal"]
    )
]

print("\n====================================")
print("RESULTADO DE LAS PRUEBAS")
print("====================================")

print(
    "Filas involucradas en facturas duplicadas:",
    len(duplicados_detectados)
)

print(
    "Relaciones con factura inexistente:",
    len(cuentas_sin_factura_detectadas)
)


# ==========================================
#  SIMULAR OTROS DOS ERRORES
# ==========================================

# ERROR 3: Asignar una cuenta a un departamento inexistente.
# Copiamos el primer detalle y cambiamos su departamento por 999.
df_cuentas_detalle_prueba.loc[
    df_cuentas_detalle_prueba.index[0],
    "departamento_id"
] = 999

# ERROR 4: Alterar el total de una factura.
# Aumentamos en $100.000 el total de la primera factura.
df_facturas_prueba.loc[
    df_facturas_prueba.index[0],
    "total_factura"
] += 100000

# ==========================================
#  DETECTAR LOS ERRORES
# ==========================================

# Buscamos departamentos que no existen en la tabla maestra.
departamentos_invalidos = df_cuentas_detalle_prueba[
    ~df_cuentas_detalle_prueba["departamento_id"].isin(
        df_departamentos_prueba["departamento_id"]
    )
]

# Unimos las relaciones con el detalle de las cuentas.
detalle_prueba = df_facturas_cuentas_prueba.merge(
    df_cuentas_detalle_prueba,
    on="numerodecuenta",
    how="left"
)

# Sumamos los cargos asociados a cada factura.
suma_cargos_prueba = (
    detalle_prueba
    .groupby("factura_fiscal")["valor_cargo"]
    .sum()
    .reset_index()
)

# Comparamos el total registrado contra la suma de los cargos.
comparacion_prueba = df_facturas_prueba[
    ["factura_fiscal", "total_factura"]
].merge(
    suma_cargos_prueba,
    on="factura_fiscal",
    how="left"
)

# Calculamos la diferencia entre ambos valores.
comparacion_prueba["diferencia"] = (
    comparacion_prueba["total_factura"]
    - comparacion_prueba["valor_cargo"]
)

# Identificamos las facturas con diferencias.
totales_incorrectos = comparacion_prueba[
    comparacion_prueba["diferencia"] != 0
]

print("\n====================================")
print("RESULTADO DE LAS NUEVAS PRUEBAS")
print("====================================")

print(
    "Cuentas con departamento inválido:",
    len(departamentos_invalidos)
)

print(
    "Facturas con diferencias en sus totales:",
    len(totales_incorrectos)
)

# Mostramos el detalle de las facturas con diferencias.
if not totales_incorrectos.empty:
    print("\nDetalle de las diferencias:")
    print(
        totales_incorrectos[
            ["factura_fiscal", "total_factura",
             "valor_cargo", "diferencia"]
        ]
    )
