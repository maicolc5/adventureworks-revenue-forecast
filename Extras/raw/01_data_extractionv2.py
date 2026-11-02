"""
01 - DATA EXTRACTION
Extract customer purchase data from AdventureWorks2025 SQL Server database."""


import pandas as pd
from pathlib import Path
import os
import pyodbc


# Rutas: el script esta en la raiz; si lo mueves a src/, usa parents[1]
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = RAW_DATA_DIR / "monthly_revenue.csv"

# Servidor y base de datos configurables por variables de entorno
SQL_SERVER = os.getenv("SQL_SERVER", ".")
SQL_DATABASE = os.getenv("SQL_DATABASE", "AdventureWorks2025")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")

EXPECTED_COLUMNS = [
    "month_start",
    "month",
    "channel",
    "orders",
    "revenue",
    "unit_qty",
    "customers",
    "active_days",
    "first_order_date",
    "last_order_date",
]

# Valores de control (junio 2022) para validar la consulta
CONTROL_MONTH = pd.Timestamp("2022-06-01")
CONTROL_VALUES = {"reseller": 1538408.31, "online": 462870.65}

QUERY = """
SELECT
    DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1) AS month_start,
    MONTH(soh.OrderDate) AS [month],
    CASE
        WHEN soh.OnlineOrderFlag = 1 THEN 'online'
        ELSE 'reseller'
    END AS channel,
    COUNT(DISTINCT soh.SalesOrderID) AS orders,
    SUM(sod.LineTotal) AS revenue,
    SUM(sod.OrderQty) AS unit_qty,
    COUNT(DISTINCT soh.CustomerID) AS customers,
    COUNT(DISTINCT CAST(soh.OrderDate AS date)) AS active_days,
    MIN(soh.OrderDate) AS first_order_date,
    MAX(soh.OrderDate) AS last_order_date
FROM Sales.SalesOrderHeader AS soh
JOIN Sales.SalesOrderDetail AS sod
    ON soh.SalesOrderID = sod.SalesOrderID
GROUP BY
    DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1),
    MONTH(soh.OrderDate),
    soh.OnlineOrderFlag
ORDER BY
    month_start,
    channel
"""

def get_connection() -> pyodbc.Connection:
    """Abre la conexion a SQL Server con autenticacion de Windows."""
    connection_string = (
        f"Driver={{{SQL_DRIVER}}};"
        f"Server={SQL_SERVER};"
        f"Database={SQL_DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    return pyodbc.connect(connection_string)


def extract_monthly_revenue(connection: pyodbc.Connection) -> pd.DataFrame:
    """Ejecuta la consulta y devuelve una fila por mes y canal."""
    return pd.read_sql(QUERY, connection)


def validate_data(df: pd.DataFrame) -> None:
    """Valida columnas, que no este vacio y los valores de control."""
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Columnas inesperadas: {list(df.columns)}")
    if df.empty:
        raise ValueError("La consulta no devolvio filas")

    control = df[pd.to_datetime(df["month_start"]) == CONTROL_MONTH]
    for channel, expected in CONTROL_VALUES.items():
        value = control.loc[control["channel"] == channel, "revenue"]
        if value.empty or abs(float(value.iloc[0]) - expected) > 0.01:
            raise ValueError(f"Valor de control no coincide para {channel}")



def main():
    print("Connecting to AdventureWorks2025 database...")

    cnn = None
    try:
        cnn = get_connection()
        if cnn is None:
            raise Exception("No database conection available")
        print("Connected successfully!")

        print("Extracting revenue features...")
        df = extract_revenue_features(cnn)
        print(f"Extracted {len(df)} revenue records")

        output_path = DATA_DIR / "raw_revenue_features.csv"
        df.to_csv(output_path, index=False)
        print(f"Data save to {output_path}")

    except Exception as error:
        print(f"Error: {error}")

    finally:
        if cnn is not None:
            cnn.close()
            print("Data base connection closed")



if __name__ == "__main__":
    main()