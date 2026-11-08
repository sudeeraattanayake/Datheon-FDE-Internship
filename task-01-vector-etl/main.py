from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from src.pipeline import EnterpriseETLPipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enterprise Vector ETL Pipeline"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to PDF, CSV, or Markdown document",
    )
    parser.add_argument("--department", required=True)
    parser.add_argument("--access-tier", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--batch-size", type=int, default=32)

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    pipeline = EnterpriseETLPipeline()

    result = pipeline.ingest(
        path=args.file,
        metadata={
            "department": args.department,
            "access_tier": args.access_tier,
            "date": args.date,
        },
        batch_size=args.batch_size,
    )

    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
