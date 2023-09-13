import pandas as pd
import openai
import os
import tiktoken
import time

ADA_2_PRICING = 0.0001
openai.api_key = os.getenv("OPENAI_API_KEY")


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
        return embedding, price


def process_embeddings(token_width, file):
    # Generate embeddings for a text file and save them to one csv.
    # save their text loacations to another csv
    byte_index = 0
    price = 0
    embeddings_dict = {"embeddings": []}
    text_dict = {"locations": []}
    with open(file) as f:
        text = f.read()
        words = text.split()
        for word_index in range(len(words)):
            # break out when the chunk of words is too small
            if len(words[word_index:]) < token_width:
                break
            to_embedd = ' '.join(words[word_index:word_index+token_width])
            embeddding, cur_price = process_embedding(to_embedd)
            price += cur_price
            end_index = byte_index + len(to_embedd)
            embeddings_dict["embeddings"].append(embeddding)
            text_dict["locations"].append((byte_index, end_index))
            byte_index = end_index
        embedding_df = pd.DataFrame(embeddings_dict)
        text_df = pd.DataFrame(text_dict)

        # If results doesn't exist, create it
        if not os.path.exists("results"):
            os.makedirs("results")

        embedding_df.to_csv("results/embeddings.csv")
        text_df.to_csv("results/text.csv")


process_embeddings(8, "data/test.txt")
