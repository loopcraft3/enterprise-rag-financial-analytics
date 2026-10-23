from app.embeddings import get_embedding_model
from app.vectorstore import load_vector_store
from app.chat import generate_answer


def main():

    embedding_model = get_embedding_model()

    vector_store = load_vector_store(
        embedding_model=embedding_model
    )

    print("RAG Chat Test")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ")

        if question.lower() == "exit":
            break

        response = generate_answer(
            question=question,
            vector_store=vector_store,
        )

        print("\nAssistant:")
        print(response["answer"])

        print("\nSources:")
        for source in response["sources"]:
            print(source)

        print("-" * 50)


if __name__ == "__main__":
    main()