# Questor ![Alt text](web/src/assets/logo.png) 

### Contents:
- [Introduction](https://github.com/supremex04/contextual-search?tab=readme-ov-file#introduction)
- [Why Questor?](https://github.com/supremex04/contextual-search?tab=readme-ov-file#why-questor)
- [How Questor Works?](https://github.com/supremex04/contextual-search?tab=readme-ov-file#how-questor-works)
- [How to run locally?](https://github.com/supremex04/contextual-search?tab=readme-ov-file#how-to-run-locally)

### Introduction
Questor is a domain-specific search engine designed to provide precise and relevant information based on predefined contexts. Currently, it has been implemented for two domains: Health (specifically cardio-vascular) and Legal. It takes domain-specific contexts as input and provides relevant output using contextual and semantic searching.

### Why Questor?
- **Traditional Google Search**:
  - Highly efficient in fetching relevant web pages based on user keywords.
  - Lacks understanding of the actual context/meaning of the search query.

- **Limitations of LLMs**:
  - Performance degrades as the domain field is narrowed down.
  - Struggles with more domain-specific prompts.

- **Questor's Solution**:
  - Extracts additional context from domain-specific PDF files.
  - Feeds this context to the LLM.
  - Utilizes the generative abilities of LLM to produce human-like text.
  - Capable of performing web searches if the user prompt does not match the information available in the provided PDF files.




### How Questor Works?

![Alt text](web/src/assets/workflow.png)

**Context Sources**
- To ensure accuracy and reliability, Questor uses authoritative and widely accepted context sources to enhance the knowledge of the language model (LLM) for each domain:
  - Health Domain (Cardio-Vascular):
    - Davidson's Medicine (a widely accepted reference book in the medical field)
  - Legal Domain:
    - The Constitution of Nepal
    - Various other legal acts and documents
 
**Context Parsing**
- Relevant information from the selected sources is parsed into multiple chunks using llama Parse from llamaIndex.
- These chunks are stored in Qdrant as embeddings (numerical vector representations of text).
- Each chunk is assigned an index.

**Query Processing**
- When a search query is made, Meta's Open Source Model llama3 retrieves the relevant context chunks from Qdrant.
- The generator then provides an answer based on these retrieved chunks.

**Answer Grading**
- The generated answer is graded by Answer Grader (another agent/LLM).
- If the answer is relevant, it is provided as the final response.
- If the answer is not relevant, Tavily AI performs a web search to fetch the necessary context to answer the question.



## How to run locally?

On the project folder:

> ``` npm install ```

> ```pip install -r requirements.txt```



Run servers:
> ```python3 medilens_server.py```
> ```python3 legallens_server.py```

### Backend Server will run at: [http://localhost:5000](http://localhost:5000)

Change the directory to projectFolder/web:
> ```cd web```

Install npm packages:
> ```npm install```

Run the frontend:
> ```npm start```


### Frontend will run at: [http://localhost:3000/](http://localhost:3000/)
