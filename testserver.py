from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os
from dotenv import load_dotenv 

from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import END, StateGraph

from llama_index.llms.groq import Groq
from llama_index.core import Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
import qdrant_client

from typing_extensions import TypedDict
from typing import List
from pprint import pprint
import nest_asyncio

# pip install
# ! pip install -U langchain-nomic langchain_community tiktoken langchainhub langchain langgraph tavily-python llama-index llama-parse llama-index-llms-groq llama-index-embeddings-fastembed fastembed  llama-index-vector-stores-qdrant

# pdf data
# !wget "https://lawcommission.gov.np/en/wp-content/uploads/2021/01/Constitution-of-Nepal.pdf"
# !wget "https://www.lawcommission.gov.np/en/wp-content/uploads/2021/01/Nepal-Citizenship-Act-2063-2006.pdf"

load_dotenv()
embed_model = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
server_app = Flask(__name__)
CORS(server_app) 


nest_asyncio.apply()
os.environ['LLAMA_PARSE_API_KEY']="xxxxxxxxxxx"

from llama_parse import LlamaParse
llama_parse_documents = LlamaParse(api_key="xxxxxxxxx", result_type="markdown").load_data("downloaded filespaths as list.pdf")

os.environ["GROQ_API_KEY"]='xxxxxxxxxx'
llm1 = Groq(model="mixtral-8x7b-32768", api_key="xxxxxxxxxx")

Settings.llm=llm1
Settings.embed_model=embed_model

client = qdrant_client.QdrantClient(
    "qdrant_storage_link",
    api_key="xxxxxxxxx",
)

vector_store = QdrantVectorStore(client=client, collection_name="legal_documents")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index =VectorStoreIndex.from_documents(documents=llama_parse_documents,storage_context=storage_context,show_progress=True)

retriever = index.as_retriever(search_kwargs={"k":3})

os.environ['LANGCHAIN_TRACING-V2']='true'
os.environ['LANGCHAIN_ENDPOINT']='https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY']='xxxxxxxxx'

#%pip install -qU langchain-groq

llm = ChatGroq(
    temperature=0,
    model="mixtral-8x7b-32768",
    api_key="xxxxxxxxxx"
)

# generation
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are an assistant for question-answering tasks.Only
    Use the following pieces of retrieved context to answer the question.If context doesnot provide information to answer that question, just say user to do web search.
    If the context provides needed informations to answer the question,use it to answer the question keeping the answer concise. <|eot_id|><|start_header_id|>user<|end_header_id|>
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
question = "how is pm selected in Nepal?"
docs = retriever.retrieve(question)
docs = [d.text for d in docs]
generation = rag_chain.invoke({"context":docs,"question": question})
print(generation)
end = time.time()
print(f"The time required to generate response by Router Chain in seconds:{end - start}")

# answer grader
prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether an
    answer is useful to resolve a question. Give a  score 'yes' or 'no' to indicate whether the answer is
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
answer_grader_response = answer_grader.invoke({"question": question,"generation": generation})
end = time.time()
print(f"The time required to generate response by the answer grader in seconds:{end - start}")
print(answer_grader_response)

os.environ['TAVILY_API_KEY'] = "xxxxxxxxxxx"
web_search_tool = TavilySearchResults(k=3)

class GraphState(TypedDict):
    question : str
    generation : str
    web_search : str
    documents : List[str]

def generate(state):

  question = state["question"]
  documents = state["documents"]

  query_engine = index.as_query_engine()
  # generation
  generation = query_engine.query(question)
  generation = generation.response
  print("GENERATING FROM CONTEXT")

  # using answer grader to grade our answer

  score = answer_grader.invoke({"question": question,"generation": generation})
  print(score['score'])

  if score['score']=='yes':
    print(" CONTEXT RESPONSE IS OK")
    return {"documents": documents, "question": question,"generation":generation}

  else:
    print("DOING WEB SEARCH")
    while score['score']=='no':

      question=state["question"]
      documents=state["documents"]

      # web searching

      docs = web_search_tool.invoke({"query": question})
      print(docs)
      web_results = "\n".join([d["content"] for d in docs])
      web_results = Document(page_content=web_results)
      if documents is not None:
          documents.append(web_results)
      else:
          documents = [web_results]


      # generation
      generation = rag_chain.invoke({"context": documents, "question": question})
      print("GENERATING FROM WEB_SEARCH")
      
      # grading answer
      score = answer_grader.invoke({"question": question,"generation": generation})
      if score['score']=='yes':
        print("WEBSEARCH RESULT IS OK")
        return {"documents": documents, "question": question,"generation":generation}
        break

workflow = StateGraph(GraphState)

workflow.add_node("generate",generate)

workflow.set_entry_point("generate")
workflow.set_finish_point("generate")

app = workflow.compile()

from pprint import pprint
inputs = {"question":"how blood pressure level varies with ages."}
for output in app.stream(inputs):
    for key, value in output.items():
        pprint(f"Finished running: {key}:")
pprint(value["generation"])