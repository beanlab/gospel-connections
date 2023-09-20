import openai
import os
import sys
import tiktoken
import numpy as np
import time
from tqdm import tqdm
from structure import scriptures_structure

ADA_2_PRICING = 0.0001

# Check for env variable of api_key, otherwise load from file
if "OPENAI_API_KEY" in os.environ:
    openai.organization = os.getenv("OPENAI_ORGANIZATION_BEAN")
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
        return embedding, num_tokens


def process_embeddings(token_width, file, sliding_window_increment):
    # Generate embeddings for a text file and save them to one csv
    # file and their text locations to another.
    byte_index = 0
    num_tokens = 0
    embeddings_list = []
    indexes_list = []
    with open(file) as f:
        text = f.read()
        words = text.split()
        # (token_width - sliding_window_increment) cuts out the partial chunks at the very end of the text line
        for word_index in tqdm(range(0, len(words) - (token_width-sliding_window_increment), sliding_window_increment)): 
            to_embedd = " ".join(words[word_index:word_index+token_width])
            embedding, tokens = process_embedding(to_embedd)
            num_tokens += tokens
            end_index = byte_index + len(to_embedd)
            embeddings_list.append(embedding)
            line_number = text.count("\n", 0, byte_index) + 1
            indexes_list.append((byte_index, end_index, line_number))
            # Update the starting byte index by finding the length of the next word, adding one for the space, and adding that length to the current byte index
            byte_index = byte_index + len(" ".join(words[word_index:word_index+sliding_window_increment])) + 1
   
        file_path = "/".join(file.split("/")[0:-3]) + "/embeddings/" + file.split("/")[-2] + "/"
        file_name = file.split("/")[-1].split(".")[0]
        file_name = file_name + ".w" + str(token_width).zfill(3) + ".i" + str(sliding_window_increment).zfill(3)
        print(file_path)
        print(file_name)

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        np.savetxt(file_path + file_name + ".embeddings.csv", np.asarray(embeddings_list), delimiter=',')
        np.savetxt(file_path + file_name + ".offsets.csv", np.asarray(indexes_list), delimiter=',', fmt="%i")
        
    price = (float(num_tokens) / 1000) * ADA_2_PRICING
    
    print('Final price: $', price)    
    print('Number tokens: ', num_tokens)

def main():
    if len(sys.argv) < 4:
        raise Exception('Requires arguments: (int) token width for sliding window, (string) book and chapter ex: 2-ne/1, (int) sliding window increment')
    token_width = int(sys.argv[1])
    book_chapter = sys.argv[2]
    sliding_window_increment = int(sys.argv[3])
    file_path = scriptures_structure.get_text_file_path(book_chapter)
    print(file_path)
    process_embeddings(token_width, file_path, sliding_window_increment)

if __name__ == "__main__":
    main()
