"""
Ingest SPY 1-minute OHLCV data from CSV into TimescaleDB.

Usage:
    python -m server.ingest

The CSV file is expected at the project root:
    spy_1min_2008_2021_cleaned.csv

Columns: date, open, high, low, close, volume, barCount, average
We map: date -> ts, keep OHLCV, ignore barCount/average.
Symbol = SPY, exchange = NYSE, market_type = etf.

Uses psycopg2 COPY for fast bulk insertion (~2M rows in under a minute).
Duplicate rows are handled via ON CONFLICT DO NOTHING.
"""

from __future__ import annotations

import csv
import io
import os
import sys
import time

import psycopg2


# Config
CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "spy_1min_2008_2021_cleaned.csv",
)
SYMBOL = "SPY"
EXCHANGE = "NYSE"
MARKET_TYPE = "etf"
BATCH_SIZE = 100_000

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://backtest:backtest@localhost:5434/backtest",
)


def ingest():
    """Bulk-load the SPY CSV into TimescaleDB."""
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV not found at {CSV_PATH}")
        print("Make sure spy_1min_2008_2021_cleaned.csv is in the project root.")
        sys.exit(1)

    # Count total lines for progress
    print(f"Counting rows in {os.path.basename(CSV_PATH)}...")
    with open(CSV_PATH, "r") as f:
        total_rows = sum(1 for _ in f) - 1  # subtract header
    print(f"Total rows: {total_rows:,}")

    # Check existing data
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM ohlcv WHERE symbol = %s AND exchange = %s",
        (SYMBOL, EXCHANGE),
    )
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"Found {existing:,} existing rows for {SYMBOL}/{EXCHANGE}")
        if existing >= total_rows * 0.99:
            print("Data appears complete. Skipping ingestion.")
            conn.close()
            return
        print("Resuming ingestion (ON CONFLICT DO NOTHING)...")

    # Create temp table for bulk COPY, then merge
    cur.execute("""
        CREATE TEMP TABLE _ingest_tmp (
            ts          TIMESTAMPTZ,
            open        DOUBLE PRECISION,
            high        DOUBLE PRECISION,
            low         DOUBLE PRECISION,
            close       DOUBLE PRECISION,
            volume      DOUBLE PRECISION
        ) ON COMMIT DROP
    """)

    print(f"\nIngesting {SYMBOL} data...")
    start_time = time.time()
    rows_loaded = 0

    with open(CSV_PATH, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        batch_buf = io.StringIO()
        batch_count = 0

        for row in reader:
            # Write TSV line: ts, open, high, low, close, volume
            batch_buf.write(
                f"{row['date']}\t{row['open']}\t{row['high']}\t"
                f"{row['low']}\t{row['close']}\t{row['volume']}\n"
            )
            batch_count += 1

            if batch_count >= BATCH_SIZE:
                _flush_batch(cur, batch_buf, batch_count)
                rows_loaded += batch_count
                elapsed = time.time() - start_time
                pct = rows_loaded / total_rows * 100
                rate = rows_loaded / elapsed if elapsed > 0 else 0
                print(
                    f"\r  {pct:5.1f}%  |  {rows_loaded:>10,} / {total_rows:,}  |  "
                    f"{rate:,.0f} rows/s",
                    end="", flush=True,
                )
                batch_buf = io.StringIO()
                batch_count = 0

        # Flush remaining
        if batch_count > 0:
            _flush_batch(cur, batch_buf, batch_count)
            rows_loaded += batch_count

    # Merge from temp to ohlcv
    print(f"\n\nMerging into ohlcv table (ON CONFLICT DO NOTHING)...")
    cur.execute(f"""
        INSERT INTO ohlcv (symbol, exchange, market_type, ts, open, high, low, close, volume)
        SELECT '{SYMBOL}', '{EXCHANGE}', '{MARKET_TYPE}', ts, open, high, low, close, volume
        FROM _ingest_tmp
        ON CONFLICT (symbol, exchange, market_type, ts) DO NOTHING
    """)
    inserted = cur.rowcount
    conn.commit()

    elapsed = time.time() - start_time
    print(f"  Inserted: {inserted:,} new rows")
    print(f"  Total time: {elapsed:.1f}s")

    # Verify
    cur.execute(
        "SELECT COUNT(*), MIN(ts), MAX(ts) FROM ohlcv WHERE symbol = %s AND exchange = %s",
        (SYMBOL, EXCHANGE),
    )
    count, min_ts, max_ts = cur.fetchone()
    print(f"\n  {SYMBOL}/{EXCHANGE}: {count:,} rows  ({min_ts} -> {max_ts})")

    cur.close()
    conn.close()
    print("Done!")


def _flush_batch(cur, buf: io.StringIO, count: int):
    """COPY a batch from StringIO into the temp table."""
    buf.seek(0)
    cur.copy_expert(
        "COPY _ingest_tmp (ts, open, high, low, close, volume) FROM STDIN",
        buf,
    )


if __name__ == "__main__":
    ingest()
