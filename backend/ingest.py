from app.ingestion import ingest_documents

def main():
    print("Starting ingestion...")
    ingest_documents()
    print("Ingestion completed!")

if __name__ == "__main__":
    main()
    