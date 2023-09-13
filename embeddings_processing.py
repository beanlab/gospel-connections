import pandas as pd
import openai
import os
import tiktoken
import numpy as np
from tenacity import retry, wait_random_exponential, stop_after_attempt
import time

ADA_2_PRICING = 0.0001

# Check for env variable of api_key, otherwise load from file
if "OPENAI_API_KEY" in os.environ:
    openai.api_key = os.getenv("OPENAI_API_KEY") 
else:
    openai.api_key = open("./openai_api_key.txt", "r").read()

def get_num_tokens(string: str, encoding_name: str) -> int:
    # Returns the number of tokens in a text string.

    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_embedding(text: str, model="text-embedding-ada-002") -> list[float]:
    # Get the embedding for a text string.
    try:
        embedding = openai.Embedding.create(
            input=[text], model=model)["data"][0]["embedding"]

        return embedding
    except openai.error.RateLimitError:
        # Handle rate limit error by waiting and then retrying
        time.sleep(10)
        return get_embedding(text, model)  # Retry the request
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

  
def process_embedding(text):
    # Get the embedding and price for a text string.
    num_tokens = get_num_tokens(text, "cl100k_base")
    embedding = get_embedding(text)
    if embedding is not None:
        # print("embedding: ", get_embedding(text))
        price = (float(num_tokens) / 1000) * ADA_2_PRICING
        if price >= 0.0001:
            print("price: $", price)
        return embedding, price, num_tokens


def process_embeddings(token_width, file):
    # Generate embeddings for a text file and save them to one csv.
    # save their text loacations to another csv
    byte_index = 0
    price = 0
    num_tokens = 0
    embeddings_list = []
    indexes_list = []
    with open(file) as f:
        text = f.read()
        words = text.split()
        for word_index in range(len(words) - (token_width-1)): # (token_width - 1) cuts out the partial chunks at the very end of the text line
            to_embedd = " ".join(words[word_index:word_index+token_width])
            embedding, cur_price, tokens = process_embedding(to_embedd)
            price += cur_price
            num_tokens += tokens
            end_index = byte_index + len(to_embedd)
            embeddings_list.append(embedding)
            indexes_list.append((byte_index, end_index))
            # Update the starting byte index by finding the length of the next word, adding one for the space, and adding that length to the current byte index
            byte_index = byte_index + len(" ".join(words[word_index:word_index+1])) + 1
   
        np.savetxt('embeds.csv', np.asarray(embeddings_list), delimiter=',')
        np.savetxt('indexes.csv', np.asarray(indexes_list), delimiter=',', fmt="%i")

    print('Final price: ', price)
    print('Number tokens: ', num_tokens)

def main():
    # TODO: add token_width as a parameter, etc.
    process_embeddings(3, "./data/scriptures/book_of_mormon/1-ne/1-test.txt")

if __name__ == "__main__":
    main()
