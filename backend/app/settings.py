import os
from llama_index.llms.ollama import Ollama
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def init_settings():
    hf_token = os.getenv("HF_TOKEN")
    embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    Settings.embedding_model = embedding_model
    llm_model = Ollama(model="llama3:latest", request_timeout=1000.0)
    Settings.llm = llm_model
    Settings.chunk_size = 1024
    Settings.chunk_overlap = 20