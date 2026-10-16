"""
01 - DATA EXTRACTION
Extract customer purchase data from AdventureWorks2025 SQL Server database."""


import pandas as pd
from pathlib import Path

try:
    import pyodbc
    HAS_PYODBC = True
except ImportError:
    HAS_PYODBC = False
    print("pyodbc not installed")


DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def get_connection():
    """Establish a connection to the AdventureWorks2025 SQL Server database."""
    if not HAS_PYODBC:
        raise ImportError("pyodbc not installed")
    else: 
        return pyodbc.connect('Driver={SQL Server};'
                              'Server=.;'
                              'Database=AdventureWorks2025;'
                              'Trusted_Connection=yes')



def extract_revenue_features(cnn):
    """Extract customer features from the AdventureWorks2025 database."""

    query = """SELECT
        DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1) AS fecha,
        MONTH(soh.OrderDate) as [month], 
        CASE
            WHEN soh.OnlineOrderFlag = 1 THEN 'online'
            ELSE 'reseller'
            END AS channel,
        COUNT(DISTINCT soh.SalesOrderID) AS orders,
        SUM(sod.LineTotal) AS revenue,
        SUM(sod.OrderQty) as unit_qty,
        COUNT(DISTINCT soh.CustomerID) as customers,
        count( distinct( OrderDate)) as active_days,
        min(OrderDate) as first_order_date,
        max(OrderDate) as last_order_date
    FROM Sales.SalesOrderHeader AS soh
        JOIN Sales.SalesOrderDetail AS sod
        ON soh.SalesOrderID = sod.SalesOrderID
    GROUP BY
        DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1),
        soh.OnlineOrderFlag,  MONTH(soh.OrderDate)
    ORDER BY
        fecha,
        channel """
        
    return pd.read_sql(query, cnn)


def main():
    print("Connecting to AdventureWorks2025 database...")


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