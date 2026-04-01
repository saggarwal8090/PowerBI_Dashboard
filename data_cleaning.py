"""
===============================================================================
 DATA CLEANING PIPELINE — Power BI Dashboard Project
 ─────────────────────────────────────────────────────
 Uses pandas to:
   1. Load the raw sales CSV
   2. Handle null / missing values
   3. Remove duplicates
   4. Standardise date formats → YYYY-MM-DD
   5. Fix categorical inconsistencies (casing, whitespace)
   6. Remove invalid rows (negative quantities)
   7. Derive useful columns (Year, Month, Quarter, Day-of-Week)
   8. Export a clean CSV ready for Power BI import
===============================================================================
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# ── PATHS ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw_sales_data.csv")
CLEAN_PATH = os.path.join(BASE_DIR, "data", "cleaned_sales_data.csv")
REPORT_PATH = os.path.join(BASE_DIR, "data", "cleaning_report.txt")


def separator(title: str) -> str:
    return f"\n{'─' * 60}\n  {title}\n{'─' * 60}"


def load_data(path: str) -> pd.DataFrame:
    """Load the raw CSV file."""
    print(separator("1 · LOADING RAW DATA"))
    df = pd.read_csv(path)
    print(f"   Loaded {len(df):,} rows × {df.shape[1]} columns from:\n   {path}")
    return df


def inspect(df: pd.DataFrame, label: str = ""):
    """Quick inspection helper."""
    print(f"\n   [{label}]  Shape: {df.shape}  |  Nulls: {df.isnull().sum().sum()}  |  Dupes: {df.duplicated().sum()}")


def handle_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values with domain-appropriate strategies."""
    print(separator("2 · HANDLING NULL VALUES"))
    null_before = df.isnull().sum()
    print("   Null counts before cleaning:")
    for col, cnt in null_before[null_before > 0].items():
        print(f"     • {col}: {cnt}")

    # Customer Name → fill with 'Unknown Customer'
    df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")

    # Sales / Profit → fill with column median (robust to outliers)
    for col in ["Sales", "Profit"]:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"   ✓ {col} nulls filled with median ({median_val:.2f})")

    # Region / Category → fill with mode
    for col in ["Region", "Category"]:
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
        print(f"   ✓ {col} nulls filled with mode ('{mode_val}')")

    # Any remaining nulls → drop rows
    remaining = df.isnull().sum().sum()
    if remaining > 0:
        df = df.dropna()
        print(f"   ✓ Dropped {remaining} rows with remaining nulls")

    inspect(df, "After null handling")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    print(separator("3 · REMOVING DUPLICATES"))
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    print(f"   ✓ Removed {removed:,} duplicate rows")
    inspect(df, "After dedup")
    return df


def standardise_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert all date columns to a uniform YYYY-MM-DD format."""
    print(separator("4 · STANDARDISING DATE FORMATS"))

    for col in ["Order Date", "Ship Date"]:
        df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
        invalid = df[col].isnull().sum()
        if invalid:
            print(f"   ⚠  {invalid} unparseable dates in '{col}' — dropping those rows")
            df = df.dropna(subset=[col])
        df[col] = df[col].dt.strftime("%Y-%m-%d")
        print(f"   ✓ '{col}' converted to YYYY-MM-DD")

    inspect(df, "After date standardisation")
    return df


def fix_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Fix whitespace, casing, and common typos in categorical columns."""
    print(separator("5 · FIXING CATEGORICAL INCONSISTENCIES"))

    cat_columns = ["Region", "Category", "Sub-Category", "Ship Mode", "Segment"]

    for col in cat_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            unique_before = df[col].nunique()
            print(f"   ✓ '{col}' cleaned → {unique_before} unique values")

    # Manual corrections for known issues
    region_map = {"West": "West", "East": "East", "Central": "Central", "South": "South"}
    df["Region"] = df["Region"].map(lambda x: region_map.get(x, x))

    inspect(df, "After categorical fixes")
    return df


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with invalid data (e.g. negative quantities)."""
    print(separator("6 · REMOVING INVALID ROWS"))

    before = len(df)
    df = df[df["Quantity"] > 0]
    removed = before - len(df)
    print(f"   ✓ Removed {removed} rows with non-positive Quantity")

    # Sales should be positive
    before = len(df)
    df = df[df["Sales"] > 0]
    removed = before - len(df)
    print(f"   ✓ Removed {removed} rows with non-positive Sales")

    inspect(df, "After invalid-row removal")
    return df


def derive_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create useful derived columns for Power BI analysis."""
    print(separator("7 · DERIVING NEW COLUMNS"))

    order_dt = pd.to_datetime(df["Order Date"])

    df["Year"] = order_dt.dt.year
    df["Month"] = order_dt.dt.month
    df["Month Name"] = order_dt.dt.strftime("%B")
    df["Quarter"] = order_dt.dt.quarter.map(lambda q: f"Q{q}")
    df["Day of Week"] = order_dt.dt.day_name()
    df["Profit Margin (%)"] = ((df["Profit"] / df["Sales"]) * 100).round(2)

    print("   ✓ Added: Year, Month, Month Name, Quarter, Day of Week, Profit Margin (%)")
    inspect(df, "After derived columns")
    return df


def generate_report(df_raw: pd.DataFrame, df_clean: pd.DataFrame, path: str):
    """Generate a text-based cleaning report."""
    lines = [
        "=" * 60,
        "  DATA CLEANING REPORT",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        f"  Raw rows         : {len(df_raw):>8,}",
        f"  Clean rows        : {len(df_clean):>8,}",
        f"  Rows removed      : {len(df_raw) - len(df_clean):>8,}",
        f"  Raw columns       : {df_raw.shape[1]:>8}",
        f"  Clean columns     : {df_clean.shape[1]:>8}",
        f"  Remaining nulls   : {df_clean.isnull().sum().sum():>8}",
        f"  Remaining dupes   : {df_clean.duplicated().sum():>8}",
        "",
        "  COLUMN SUMMARY (cleaned):",
        "  " + "-" * 50,
    ]
    for col in df_clean.columns:
        dtype = str(df_clean[col].dtype)
        nunique = df_clean[col].nunique()
        lines.append(f"  {col:<25} {dtype:<12} {nunique:>6} unique")

    lines += [
        "",
        "  SALES STATISTICS:",
        "  " + "-" * 50,
        f"  Total Sales      : ${df_clean['Sales'].sum():>15,.2f}",
        f"  Total Profit     : ${df_clean['Profit'].sum():>15,.2f}",
        f"  Total Orders     : {len(df_clean):>15,}",
        f"  Avg Order Value  : ${df_clean['Sales'].mean():>15,.2f}",
        f"  Avg Profit Margin: {df_clean['Profit Margin (%)'].mean():>14.2f}%",
        "",
        "=" * 60,
    ]

    report = "\n".join(lines)
    with open(path, "w") as f:
        f.write(report)
    print(f"\n📊  Cleaning report saved → {path}")


def main():
    print("\n" + "=" * 60)
    print("  POWER BI DASHBOARD — DATA CLEANING PIPELINE")
    print("=" * 60)

    # Check raw file exists
    if not os.path.exists(RAW_PATH):
        print(f"\n❌  Raw data not found at: {RAW_PATH}")
        print("   Run `python generate_dataset.py` first to create the dataset.")
        sys.exit(1)

    # Pipeline
    df_raw = load_data(RAW_PATH)
    df = df_raw.copy()

    df = handle_nulls(df)
    df = remove_duplicates(df)
    df = standardise_dates(df)
    df = fix_categoricals(df)
    df = remove_invalid_rows(df)
    df = derive_columns(df)

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned data
    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)

    print(separator("8 · EXPORT"))
    print(f"   ✅  Cleaned dataset saved → {CLEAN_PATH}")
    print(f"   Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns\n")

    # Generate cleaning report
    generate_report(df_raw, df, REPORT_PATH)

    # Quick summary
    print(separator("SUMMARY"))
    print(f"   Raw   → {len(df_raw):>6,} rows")
    print(f"   Clean → {len(df):>6,} rows")
    print(f"   Δ     → {len(df_raw) - len(df):>6,} rows removed")
    print(f"   Nulls → {df.isnull().sum().sum()}")
    print(f"   Dupes → {df.duplicated().sum()}")
    print()


if __name__ == "__main__":
    main()
