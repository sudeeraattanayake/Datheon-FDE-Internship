import json
from src.pipeline import EnterpriseETLPipeline


def main() -> None:
    pipeline = EnterpriseETLPipeline()

    results = pipeline.search(
        query="How do employees request annual leave?",
        department="HR",
        access_tier="internal",
        n_results=3,
    )

    print(f"\nTotal results: {len(results)}")

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
