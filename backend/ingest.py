import sys

from app.ingestion import ingest_documents


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <session-uuid>")
        print("Documents are stored per session, so give the session id they should belong to.")
        return

    print("Starting ingestion...")
    ingest_documents(session_id=sys.argv[1])
    print("Ingestion completed!")


if __name__ == "__main__":
    main()
