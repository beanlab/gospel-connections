import pandas as pd
import openai
import os
import tiktoken
from tenacity import retry, wait_random_exponential, stop_after_attempt

ADA_2_PRICING = 0.0001

# Check for env variable of api_key, otherwise load from file
if "OPENAI_API_KEY" in os.environ:
    openai.api_key = os.getenv("OPENAI_API_KEY") 
else:
    openai.api_key = open("./openai_api_key.txt", "r").read()

def get_num_tokens(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str, model="text-embedding-ada-002") -> list[float]:
    """Get the embedding for a text string."""
    return openai.Embedding.create(input=[text],
                                   model=model)["data"][0]["embedding"]


def process_embedding(text):
    """Get the embedding and price for a text string."""
    num_tokens = get_num_tokens(text, "cl100k_base")
    embedding = get_embedding(text)
    print("embedding: ", get_embedding(text))
    price = (float(num_tokens) / 1000) * ADA_2_PRICING
    print("price: ", price)
    return embedding, price


def process_embeddings(token_width, file):
    """Generate embeddings for a text file and save them to one csv
    file and their text locations to another."""
    byte_index = 0
    price = 0
    embeddings_dict = {"embeddings": []}
    text_dict = {"locations": []}
    with open(file) as f:
        text = f.read()
        words = text.split()
        for word_index in range(len(words) - (token_width-1)): # (token_width - 1) cuts out the partial chunks at the very end of the text line
            to_embedd = " ".join(words[word_index:word_index+token_width])
            embeddding, cur_price = process_embedding(to_embedd)
            price += cur_price
            end_index = byte_index + len(to_embedd)
            embeddings_dict["embeddings"].append(embeddding)
            text_dict["locations"].append((byte_index, end_index))
            # Update the starting byte index by finding the length of the next word, adding one for the space, and adding that length to the current byte index
            byte_index = byte_index + len(" ".join(words[word_index:word_index+1])) + 1
        embedding_df = pd.DataFrame(embeddings_dict)
        text_df = pd.DataFrame(text_dict)
        embedding_df.to_csv("embeddings.csv")
        text_df.to_csv("text.csv")

def main():
    process_embeddings(3, "./data/scriptures/book_of_mormon/1-ne/1-test.txt")

if __name__ == "__main__":
    main()