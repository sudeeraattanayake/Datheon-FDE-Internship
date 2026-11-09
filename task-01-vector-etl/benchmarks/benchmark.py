from __future__ import annotations

import csv
import json
import logging
import statistics
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from src.pipeline import EnterpriseETLPipeline

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "benchmarks" / "results"
DATA_DIR = ROOT / "data" / "raw"

BATCH_SIZES = (8, 16, 32, 64)
REPEATS = 3
DOCUMENT_COUNT = 100


def create_dataset() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "benchmark_synthetic.csv"

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["record_id", "title", "content"])

        for index in range(DOCUMENT_COUNT):
            writer.writerow([
                index,
                f"Policy Record {index}",
                (
                    f"Policy record {index} describes employee "
                    "leave approval, document handling, and "
                    "internal compliance requirements."
                ),
            ])

    return path


def run_benchmark() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    dataset = create_dataset()

    metadata = {
        "department": "HR",
        "access_tier": "internal",
        "date": "2026-11-09",
    }

    results = []

    # Warm up model loading before measuring ingestion.
    from src.embeddings import generate_embeddings
    generate_embeddings(["Benchmark warmup sentence."])

    for batch_size in BATCH_SIZES:
        elapsed_values = []
        throughput_values = []
        peak_memory_values = []

        for repeat in range(REPEATS):
            database = RESULTS_DIR / (
                f"chroma_batch_{batch_size}_run_{repeat}"
            )

            pipeline = EnterpriseETLPipeline(
                persist_directory=database
            )

            tracemalloc.start()
            started = time.perf_counter()

            result = pipeline.ingest(
                dataset,
                metadata,
                batch_size=batch_size,
            )

            elapsed = time.perf_counter() - started
            _, peak_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            throughput = result.chunks_created / elapsed

            elapsed_values.append(elapsed)
            throughput_values.append(throughput)
            peak_memory_values.append(
                peak_memory / (1024 * 1024)
            )

            print(
                f"Batch={batch_size} "
                f"Run={repeat + 1} "
                f"Chunks={result.chunks_created} "
                f"Time={elapsed:.3f}s "
                f"Throughput={throughput:.2f} chunks/s"
            )

        results.append({
            "batch_size": batch_size,
            "repeats": REPEATS,
            "mean_seconds": round(
                statistics.mean(elapsed_values), 4
            ),
            "mean_chunks_per_second": round(
                statistics.mean(throughput_values), 4
            ),
            "mean_peak_python_memory_mb": round(
                statistics.mean(peak_memory_values), 4
            ),
        })

    report = {
        "timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "document_count": DOCUMENT_COUNT,
        "results": results,
    }

    json_path = RESULTS_DIR / "benchmark_report.json"
    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    csv_path = RESULTS_DIR / "benchmark_report.csv"

    with csv_path.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print("\nBenchmark completed!")
    print(f"JSON report: {json_path}")
    print(f"CSV report: {csv_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    run_benchmark()
