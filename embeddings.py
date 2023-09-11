import openai
import tiktoken
from tenacity import retry, wait_random_exponential, stop_after_attempt

openai.api_key = "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"

ADA_2_PRICING = 0.0001

def get_num_tokens(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, model="text-embedding-ada-002") -> list[float]:
    return openai.Embedding.create(input=[text], model=model)["data"][0]["embedding"]

def get_embeddings():
    test = "Once upon a time"
    num_tokens = get_num_tokens(test, "cl100k_base")
    print("embedding: ", get_embedding(test))
    price = (float(num_tokens) / 1000) * ADA_2_PRICING
    print("price: ", price)
    
get_embeddings()
    
# import chromadb
# # setup Chroma in-memory, for easy prototyping. Can add persistence easily!
# client = chromadb.Client()

# # Create collection. get_collection, get_or_create_collection, delete_collection also available!
# collection = client.create_collection("all-my-documents")
 
# # Add docs to the collection. Can also update and delete. Row-based API coming soon!
# collection.add(
#     metadatas=[{"source": "notion"}, {"source": "google-docs"}], # filter on these!
#     ids=["doc1", "doc2"], # unique for each doc
# )

# # Query/search 2 most similar results. You can also .get by id
# results = collection.query(
#     query_texts=["This is a query document"],
#     n_results=2,
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
# )
