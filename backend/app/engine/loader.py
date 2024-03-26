from llama_index.core.readers import SimpleDirectoryReader
transcript_directory = "path/to/your/transcripts"

DATA_DIR = "data"  # directory containing the documents


def get_documents():
    return SimpleDirectoryReader(DATA_DIR).load_data()
