from flask import Flask, request, jsonify
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import time
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from typing import List
from langgraph.graph import StateGraph, END
from langchain.schema import Document

embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

os.environ["GOOGLE_API_KEY"] = "your_google_api_key_here"
llm = ChatGoogleGenerativeAI(model="gemini-pro")

os.environ['LANGCHAIN_TRACING-V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = 'your_langchain_api_key_here'
os.environ['ANTHROPIC_API_KEY'] = 'your_anthropic_api_key_here'

urls = [
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8060478/#:~:text=It%20has%20recorded%20its%20highest,at%20the%20end%20of%20lockdown."
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=512, chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)

vectorstore = Chroma.from_documents(documents=doc_splits,
                                    embedding=embed_model,
                                    collection_name="local-rag")

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

prompt = PromptTemplate(
    template=""" You are an expert at routing a
    user question to a vectorstore or web search. Use the vectorstore if the question and the documents
    match each other . It doesnot need to be a stringent test . Otherwise, use web-search. Give a binary choice 'web_search'
    or 'vectorstore' based on it.The goal is to find whether the document is relevant to the questio or not . Return the a JSON with a single key 'datasource' and
    no premable or explaination. Question to route: {question} docmunet to look for{document} assistant""",
    input_variables=["question", "document"],
)

question_router = prompt | llm | JsonOutputParser()

# Define the Flask app
server_app = Flask(__name__)

class GraphState(TypedDict):
    question: str
    generation: str
    web_search: str
    documents: List[str]

# Define the workflow
workflow = StateGraph(GraphState)

def retrieve(state):
    question = state["question"]
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def generate(state):
    question = state["question"]
    documents = state["documents"]
    rag_chain = PromptTemplate(
        template="""system You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
        Use three sentences maximum and keep the answer concise user
        Question: {question}
        Context: {context}
        Answer: assistant""",
        input_variables=["question", "context"],
    ) | llm | StrOutputParser()
    generation = rag_chain.invoke({"context": format_docs(documents), "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def grade_documents(state):
    question = state["question"]
    documents = state["documents"]
    filtered_docs = []
    web_search = "No"
    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        grade = score['score']
        if grade.lower() == "yes":
            filtered_docs.append(d)
        else:
            web_search = "Yes"
    return {"documents": filtered_docs, "question": question, "web_search": web_search}

def web_search(state):
    question = state["question"]
    documents = state["documents"]
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
    return {"documents": documents, "question": question}

def route_question(state):
    question = state["question"]
    documents = retriever.invoke(question)
    source = question_router.invoke({"question": question, "document": documents})
    if source['datasource'] == 'web_search':
        return "websearch"
    elif source['datasource'] == 'vectorstore':
        return "retrieve"

def decide_to_generate(state):
    web_search = state["web_search"]
    if web_search == "Yes":
        return "websearch"
    else:
        return "generate"

def grade_generation_v_documents_and_question(state):
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    score = hallucination_grader.invoke({"documents": documents, "generation": generation})
    grade = score['score']
    if grade == "yes":
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score['score']
        if grade == "yes":
            return "useful"
        else:
            return "not useful"
    else:
        return "not supported"

workflow.add_node("websearch", web_search)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)

workflow.set_conditional_entry_point(
    route_question,
    {
        "websearch": "websearch",
        "vectorstore": "retrieve",
    },
)

workflow.add_edge("retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "websearch": "websearch",
        "generate": "generate",
    },
)
workflow.add_edge("websearch", "generate")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "websearch",
    },
)

app_workflow = workflow.compile()

@server_app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data['question']
    inputs = {"question": question}
    output = None
    for output in app_workflow.stream(inputs):
        pass
    if output and "generation" in output:
        return jsonify({"generation": output["generation"]})
    else:
        return jsonify({"error": "Failed to generate response"}), 500

if __name__ == "__main__":
    server_app.run(debug=True)
