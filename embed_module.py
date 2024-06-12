from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

class ModelSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Initializing model...")
            cls._instance = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
            print("Model initialized successfully.")
        return cls._instance

# Access the model instance
embed_model = ModelSingleton.get_instance()
