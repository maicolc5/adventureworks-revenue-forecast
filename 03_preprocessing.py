"""Preprocesamiento de ingresos mensuales por canal (AdventureWorks2025)."""
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_PATH = BASE_DIR / "data" / "raw" / "raw_revenue_features.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Periodos de modelado por canal (inicio, fin) inclusive
PERIODS: dict[str, tuple[str, str]] = {
    "reseller": ("2022-06-01", "2025-04-01"),
    "online": ("2022-06-01", "2025-05-01"),
}
EXPECTED_ROWS: dict[str, int] = {"reseller": 35, "online": 36}
REGIME_BREAK = "2024-06-01"  # confirmar con el EDA

EXPECTED_COLUMNS = [
    "month_start",
    "channel",
    "orders",
    "revenue",
    "units",
    "customers",
    "active_days",
    "first_order_date",
    "last_order_date",
]
# Fechas de pedidos: no se usan (se descarta el efecto calendario)
DROP_COLUMNS = ["first_order_date", "last_order_date"]


def load_raw(path: Path) -> pd.DataFrame:
    """Lee el CSV crudo, parsea 'month_start' y valida columnas y duplicados."""
    df = pd.read_csv(
        path, parse_dates=["month_start", "first_order_date", "last_order_date"]
    )

    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en {path}: {sorted(missing)}")
    if df.duplicated(subset=["month_start", "channel"]).any():
        raise ValueError(f"Hay claves (month_start, channel) duplicadas en {path}")
    return df


def select_channel(df: pd.DataFrame, channel: str) -> pd.DataFrame:
    """Filtra el canal, recorta con PERIODS, pone 'month_start' de índice (MS)."""
    start, end = PERIODS[channel]
    mask = (
        (df["channel"] == channel)
        & (df["month_start"] >= start)
        & (df["month_start"] <= end)
    )
    out = df.loc[mask].drop(columns=DROP_COLUMNS).set_index("month_start")
    # asfreq rellena con NaN los meses ausentes; validate_series los detecta
    return out.sort_index().asfreq("MS").copy()


def validate_series(df: pd.DataFrame, channel: str) -> None:
    """Comprueba huecos, nº de filas, nulos y revenue > 0.
    Lanza ValueError si algo falla."""
    start, end = PERIODS[channel]
    expected_index = pd.date_range(start, end, freq="MS")
    if not df.index.equals(expected_index):
        raise ValueError(f"El canal {channel} tiene huecos o fechas fuera de rango")

    expected_rows = EXPECTED_ROWS[channel]
    if len(df) != expected_rows:
        raise ValueError(
            f"El canal {channel} tiene {len(df)} filas, se esperaban {expected_rows}"
        )
    if df.isna().any().any():
        raise ValueError(f"El canal {channel} tiene valores nulos")
    if (df["revenue"] <= 0).any():
        raise ValueError(f"El canal {channel} tiene revenue <= 0")


def add_online_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """Añade log_revenue y el indicador 'regime' (0/1 según REGIME_BREAK)."""
    df = df.copy()
    df["log_revenue"] = np.log(df["revenue"])
    df["regime"] = (df.index >= pd.Timestamp(REGIME_BREAK)).astype(int)
    return df


def save(df: pd.DataFrame, channel: str) -> None:
    """Crea data/processed si no existe y guarda <channel>_monthly.csv."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / f"{channel}_monthly.csv")


def main() -> None:
    raw = load_raw(RAW_PATH)
    for channel in PERIODS:
        df = select_channel(raw, channel)
        validate_series(df, channel)
        if channel == "online":
            df = add_online_transforms(df)
        save(df, channel)
        print(f"{channel}: {len(df)} filas guardadas")


if __name__ == "__main__":
    main()
