from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from argparse import ArgumentParser
import os

def main(doc_dir, db_dir, batch_size, run_test=False):

    #load md files
    loader = DirectoryLoader(doc_dir, glob="*.md", show_progress=True)
    docs = loader.load()
    print(f"Loaded {len(docs)} documents")

    #make embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={'device': 'cuda'}
    )

    #create vector db
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=db_dir)
    # vectorstore.save_local(db_dir)

    #run test

    if run_test:
        print("Running test query...")
        query = "What is the remote work policy?"
        results = vectorstore.similarity_search(query, k=3)
        print(f"Query: {query}")

        for i, doc in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(f"File: {doc.metadata['source']}")
            print(f"Content: {doc.page_content[:300]}...")

if __name__ == "__main__":
    parser = ArgumentParser(description='Create a vector database from markdown files.')
    parser.add_argument('input_dir', type=str, help='Directory containing input markdown files')
    parser.add_argument('output_dir', type=str, help='Directory to save the vector database')
    parser.add_argument('-bs', '--batch_size', type=int, default=256, help='Batch size for processing documents')
    parser.add_argument('--test', action='store_true', help='Run a test query after creating the database')
    args = parser.parse_args()

    main(doc_dir=args.input_dir, db_dir=args.output_dir, batch_size=args.batch_size, run_test=args.test)