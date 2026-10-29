from pathlib import Path
import shutil

import pyarrow as pa
import pyarrow.parquet as pq
from pyspark.sql import DataFrame


def write_parquet(df: DataFrame, path: Path, batch_size: int = 10000) -> None:
    """Write a Spark DataFrame as Parquet without requiring Hadoop on Windows."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    writer = None
    try:
        batch = []
        for row in df.toLocalIterator():
            batch.append(row.asDict(recursive=True))
            if len(batch) >= batch_size:
                table = pa.Table.from_pylist(batch)
                if writer is None:
                    writer = pq.ParquetWriter(path / "part-00000.parquet", table.schema)
                writer.write_table(table)
                batch.clear()
        if batch:
            table = pa.Table.from_pylist(batch)
            if writer is None:
                writer = pq.ParquetWriter(path / "part-00000.parquet", table.schema)
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
