"""
01 - DATA EXTRACTION
Extract monthly revenue data from AdventureWorks2025 SQL Server database."""


import math

import pandas as pd
from pathlib import Path
import pyodbc

DATA_DIR = Path(__file__).resolve().parent/ "data" / "raw"

# Valores de control de revenue (ver NOTAS_PROYECTO.md): (mes, canal) -> ingreso
CONTROL_VALUES = {
    ("2022-06-01", "reseller"): 1538408.31,
    ("2022-06-01", "online"): 462870.65,
}

QUERY = """SELECT
        DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1) AS month_start,
        CASE
            WHEN soh.OnlineOrderFlag = 1 THEN 'online'
            ELSE 'reseller'
            END AS channel,
        COUNT(DISTINCT soh.SalesOrderID) AS orders,
        SUM(sod.LineTotal) AS revenue,
        SUM(sod.OrderQty) as units,
        COUNT(DISTINCT soh.CustomerID) as customers,
        count( distinct CAST(soh.OrderDate AS date)) as active_days,
        min(soh.OrderDate) as first_order_date,
        max(soh.OrderDate) as last_order_date
    FROM Sales.SalesOrderHeader AS soh
        JOIN Sales.SalesOrderDetail AS sod
        ON soh.SalesOrderID = sod.SalesOrderID
    GROUP BY
        DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1),
        soh.OnlineOrderFlag
    ORDER BY
        month_start,
        channel """

def get_connection() -> pyodbc.Connection:
    """Establish a connection to the AdventureWorks2025 SQL Server database."""

    return pyodbc.connect('Driver={SQL Server};'
                              'Server=.;'
                              'Database=AdventureWorks2025;'
                              'Trusted_Connection=yes')



def extract_revenue_features(cnn: pyodbc.Connection) -> pd.DataFrame:
    """Extract monthly revenue features from the AdventureWorks2025 database."""

    return pd.read_sql(QUERY, cnn)


def validate_extraction(df: pd.DataFrame) -> None:
    """Comprueba que df no esté vacío y que coincida con los valores de control."""
    if df.empty:
        raise ValueError("La extracción devolvió un DataFrame vacío")

    # pyodbc devuelve Decimal y fecha como date: se convierten antes de comparar
    fechas = pd.to_datetime(df["month_start"])
    revenue = df["revenue"].astype(float)

    for (fecha, channel), esperado in CONTROL_VALUES.items():
        mask = (fechas == pd.Timestamp(fecha)) & (df["channel"] == channel)
        if not mask.any():
            raise ValueError(f"Falta la fila de control: {fecha}, {channel}")

        obtenido = revenue[mask].iloc[0]
        if not math.isclose(obtenido, esperado, abs_tol=0.01):
            raise ValueError(
                f"Control fallido en {fecha}, {channel}: "
                f"esperado {esperado:,.2f}, obtenido {obtenido:,.2f}"
            )


def main() -> None:
    print("Connecting to AdventureWorks2025 database...")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    cnn = None
    try:
        cnn = get_connection()
        
        print("Connected successfully!")

        print("Extracting revenue features...")
        df = extract_revenue_features(cnn)
        print(f"Extracted {len(df)} revenue records")

        validate_extraction(df)
        print("Validation passed")

        output_path = DATA_DIR / "raw_revenue_features.csv"
        df.to_csv(output_path, index=False)
        print(f"Data save to {output_path}")

    except Exception as error:
        print(f"Error: {error}")
        raise

    finally:
        if cnn is not None:
            cnn.close()
            print("Data base connection closed")



if __name__ == "__main__":
    main()