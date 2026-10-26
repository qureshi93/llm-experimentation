import sys

from src.ingestion.baseline import ingest_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python -m src.ingestion.ingest_baseline FILE [FILE...]")
    for p in sys.argv[1:]:
        ok, skipped = ingest_file(p)
        print(f"{p}: upserted={ok} skipped={skipped}")
