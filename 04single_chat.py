from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

DB_DIR = "/home/kuba/projects/usc-policy-knowledge-base/db/chroma" #path to vector database markdown files
CHAT_MODEL_TYPE = "gpt-3.5-turbo" #model to use for chat

def query_vector_store(vector_store, query, k=3):
    res = vector_store.similarity_search_with_score(query, k=k)
    return res

def filter_results_by_score(results, threshold=0.3):
    filtered = []
    for doc, score in results:
        if score > threshold:
            print(f"SKIPPING: Document: {doc.metadata} Score: {score}")
        else:
            filtered.append(doc)

    return filtered

def do_rag(vector_store, query, k=3, score_threshold=0.3):
    results = query_vector_store(vector_store, query, k=k)
    filtered_results = filter_results_by_score(results, threshold=score_threshold)
    return filtered_results



#load model 
def main():
    #load db
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={'device': 'cuda'}
    )

    load_vector_store = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings)

    llm = OllamaLLM(
        model="gemma3:1b",
        temperature=0.0,
    )

    chats = [
        SystemMessage(content="You work in HR at a univeristy. You are helful but have a bit of an attitude. " \
        "You answer questions based on the provided context from the university policy documents. " \
        "If you don't know the answer, you say you don't know and suggest contacting HR directly."),
    ]


    while True:
        #query user for message
        raw_query = input("You: ")

        #send mesg to vec db
        context_docs = do_rag(load_vector_store, raw_query, k=3, score_threshold=0.75)
        # make context out of docs
        if context_docs:
            context = "".join([doc.page_content for doc in context_docs])
        else:
            context = "No relevant documents found for your query."

        #append context to mesg
        query = f"context: {context}\n\n Users actual question: {raw_query}\n\n" 

        #send to model
        res = llm.invoke(chats + [HumanMessage(content=query)])
        #print response
        print(f"\n\nAssistant: {res}\n")

        #add all to chat history
        chats.append(HumanMessage(content=query))
        chats.append(AIMessage(content=res))

if __name__ == "__main__":
    main()
