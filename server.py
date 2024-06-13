from flask import Flask, request, jsonify
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
import time
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from typing_extensions import TypedDict
from typing import List
from pprint import pprint
from langgraph.graph import END, StateGraph


embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
server_app = Flask(__name__)

# Commented out IPython magic to ensure Python compatibility.
# %pip3 install --upgrade --quiet  langchain-google-genai pillow
os.environ["GOOGLE_API_KEY"]="AIzaSyA7PN41FYdh86uuxvW4kKW5_YdvsHXb8ds"
llm = ChatGoogleGenerativeAI(model="gemini-pro")




os.environ['LANGCHAIN_TRACING-V2']='true'
os.environ['LANGCHAIN_ENDPOINT']='https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY']='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'
os.environ['ANTHROPIC_API_KEY']='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'

urls = [
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8060478/#:~:text=It%20has%20recorded%20its%20highest,at%20the%20end%20of%20lockdown."
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]
print(f"len of documents :{len(docs_list)}")

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=512, chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)
print(f"length of document chunks generated :{len(doc_splits)}")

vectorstore = Chroma.from_documents(documents=doc_splits,
                                    embedding=embed_model,
                                    collection_name="local-rag")

retriever = vectorstore.as_retriever(search_kwargs={"k":2})


prompt = PromptTemplate(
    template=""" You are an expert at routing a
    user question to a vectorstore or web search. Use the vectorstore if the question and the documents
    match each other . It doesnot need to be a stringent test . Otherwise, use web-search. Give a binary choice 'web_search'
    or 'vectorstore' based on it.The goal is to find whether the document is relevant to the questio or not . Return the a JSON with a single key 'datasource' and
    no premable or explaination. Question to route: {question} docmunet to look for{document} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question","document"],
)
start = time.time()
question_router = prompt | llm | JsonOutputParser()
# question = "covid 19 deaths in nepal"
# docs = retriever.invoke(question)
# print(question_router.invoke({"question": question,"document":docs}))
# end = time.time()
# print(f"The time required to generate response by Router Chain in seconds:{end - start}")

# docs[1].page_content

# generation
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.
    Use three sentences maximum and keep the answer concise <|eot_id|><|start_header_id|>user<|end_header_id|>
    Question: {question}
    Context: {context}
    Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "document"],
)

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain
start = time.time()
rag_chain = prompt | llm | StrOutputParser()
# question = "different types of human memory"
# docs = retriever.invoke(question)
# generation = rag_chain.invoke({"context":docs,"question": question})
# print(generation)
# end = time.time()
# print(f"The time required to generate response by Router Chain in seconds:{end - start}")

# docs

# retrieval grader
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing relevance
    of a retrieved document to a user question. If the document contains keywords related to the user question,
    grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explaination.
     <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["question", "document"],
)
start = time.time()
retrieval_grader = prompt | llm | JsonOutputParser()
# question = "how the human brain works?"
# docs = retriever.invoke(question)
# doc_txt = docs[1].page_content
# print(retrieval_grader.invoke({"question": question, "document": doc_txt}))
# end = time.time()
# print(f"The time required to generate response by the retrieval grader in seconds:{end - start}")

# hallucination grader
prompt = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether
    an answer is grounded in / supported by a set of facts. Give a binary 'yes' or 'no' score to indicate
    whether the answer is grounded in / supported by a set of facts. Provide the binary score as a JSON with a
    single key 'score' and no preamble or explanation. <|eot_id|><|start_header_id|>user<|end_header_id|>
    Here are the facts:
    \n ------- \n
    {documents}
    \n ------- \n
    Here is the answer: {generation}  <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "documents"],
)
start = time.time()
hallucination_grader = prompt | llm | JsonOutputParser()
# hallucination_grader_response = hallucination_grader.invoke({"documents": docs, "generation": generation})
# end = time.time()
# print(f"The time required to generate response by the generation chain in seconds:{end - start}")
# print(hallucination_grader_response)

# answer grader
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an
    answer is useful to resolve a question. Give a binary score 'yes' or 'no' to indicate whether the answer is
    useful to resolve a question. Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.
     <|eot_id|><|start_header_id|>user<|end_header_id|> Here is the answer:
    \n ------- \n
    {generation}
    \n ------- \n
    Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["generation", "question"],
)
start = time.time()
answer_grader = prompt | llm | JsonOutputParser()
# answer_grader_response = answer_grader.invoke({"question": question,"generation": generation})
# end = time.time()
# print(f"The time required to generate response by the answer grader in seconds:{end - start}")
# print(answer_grader_response)

# web search

os.environ['TAVILY_API_KEY'] = "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"
web_search_tool = TavilySearchResults(k=3)

### State

class GraphState(TypedDict):
    question : str
    generation : str
    web_search : str
    documents : List[str]

from langchain.schema import Document
def retrieve(state):
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}
#
def generate(state):

    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}
#
def grade_documents(state):

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    web_search = "No"
    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        grade = score['score']
        # Document relevant
        if grade.lower() == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        # Document not relevant
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            # We do not include the document in filtered_docs
            # We set a flag to indicate that we want to run web search
            web_search = "Yes"
            continue
    return {"documents": filtered_docs, "question": question, "web_search": web_search}
#
def web_search(state):

    print("---WEB SEARCH---")
    question = state["question"]
    documents = state["documents"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    if documents is not None:
        documents.append(web_results)
    else:
        documents = [web_results]
    return {"documents": documents, "question": question}

# conditional edges
def route_question(state):

    print("---ROUTE QUESTION---")
    question = state["question"]
    documents = retriever.invoke(question)
    print(question)
    source = question_router.invoke({"question": question,"document":documents})
    print(source)
    print(source['datasource'])
    if source['datasource'] == 'web_search':
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "websearch"
    elif source['datasource'] == 'vectorstore':
        print("---ROUTE QUESTION TO RAG---")
        return "vectorstore"

def decide_to_generate(state):

    print("---ASSESS GRADED DOCUMENTS---")
    question = state["question"]
    web_search = state["web_search"]
    filtered_documents = state["documents"]

    if web_search == "Yes":
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print("---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---")
        return "websearch"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"

def grade_generation_v_documents_and_question(state):

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke({"documents": documents, "generation": generation})
    grade = score['score']

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question,"generation": generation})
        grade = score['score']
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"

# adding notes
workflow = StateGraph(GraphState)

# Define the nodes
workflow.add_node("websearch", web_search) # web search
workflow.add_node("retrieve", retrieve) # retrieve
workflow.add_node("grade_documents", grade_documents) # grade documents
workflow.add_node("generate", generate) # generatae

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

app = workflow.compile()

@server_app.route('/query', methods=['POST'])
def query():
    data = request.json
    question = data['question']
    inputs = {"question": question}
    output = None
    for output in app.stream(inputs):
        for key, value in output.items():
            pprint(f"Finished running: {key}:")
    return jsonify({"generation": value["generation"]})
    
if __name__ == "__main__":
    server_app.run(debug=True)
