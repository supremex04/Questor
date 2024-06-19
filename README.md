<p align="center">
  <img src="web/src/assets/logo.png" alt="Logo" style="vertical-align: middle;">
  <span style="font-size: 24px; vertical-align: middle;">Questor</span>
</p>

### Contents:
- [Introduction](https://github.com/supremex04/contextual-search?tab=readme-ov-file#introduction)
- [Why Questor?](https://github.com/supremex04/contextual-search?tab=readme-ov-file#why-questor)
- [Tech Stack](https://github.com/supremex04/contextual-search?tab=readme-ov-file#tech-stack)
- [How to run locally?](https://github.com/supremex04/contextual-search?tab=readme-ov-file#how-to-run-locally)

### Introduction
Questor is a domain-specific search engine designed to provide precise and relevant information based on predefined contexts. Currently, it has been implemented for two domains: Health (specifically cardio-vascular) and Legal. It takes context specific natural language as input and provides relevant output using contextual and semantic searching.

### Why Questor?
The traditional Google Search is highly effiecient in fetching relevant web pages based on user keyword but doesn't understand the actual context/meaning of the search query. But on the other hand, LLM's performance starts degrading as we narrow down the domain field and give more domain specific prompts. So Questor solves this problem by extracting additional context from the domain specific pdf files and feeding this context to the LLM,thereby using the generative abilities of LLM to generate human like texts. Questor also can do web search if user prompt doesn't match with the information available in the 
given pdf files



### Tech Stack
![Alt text](web/src/assets/workflow.png)



## How to run locally?

On the project folder:

> ``` npm install ```

> ```pip install -r requirements.txt```



Run server:
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
