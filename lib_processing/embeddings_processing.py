import openai
import os
import csv
import sys
import tiktoken
import numpy as np
import time
from tqdm import tqdm
from pathlib import Path
import scriptures_structure

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


def process_embeddings(file, token_width, sliding_window_increment):
    """
    This function should not be called directly, call main instead.
    """
    # Generate embeddings for a text file and save them to one csv
    # file and their text locations to another.
    byte_index = 0
    num_tokens = 0
    embeddings_list = []
    indexes_list = []
    with open(file) as f:
        text = f.read()
        words = text.split()

        # Just do entire sequence if len(words) < increment
        if len(words) < sliding_window_increment:
            loop_range = len(words)
        else:
            loop_range = len(words) - (token_width - sliding_window_increment)

        # (token_width - sliding_window_increment) cuts out the partial chunks at the very end of the text line
        for word_index in tqdm(range(0, loop_range, sliding_window_increment)): 
            to_embedd = " ".join(words[word_index:word_index+token_width])
            embedding, tokens = process_embedding(to_embedd)
            num_tokens += tokens
            end_index = byte_index + len(to_embedd)
            embeddings_list.append(embedding)
            line_number = text.count("\n", 0, byte_index) + 1
            indexes_list.append((byte_index, end_index, line_number))
            # Update the starting byte index by finding the length of the next word, adding one for the space, and adding that length to the current byte index
            byte_index = byte_index + len(" ".join(words[word_index:word_index+sliding_window_increment])) + 1
    
        # Peform mean transform
        embeddings_list = np.asarray(embeddings_list)

        # Check if there's more than one embedding
        if embeddings_list.shape[0] > 1:
            embeddings_mean = np.mean(embeddings_list, axis=0).tolist()
        else:
            embeddings_mean = embeddings_list[0].tolist()
        
    price = (float(num_tokens) / 1000) * ADA_2_PRICING
    
    print('Final price: $', price)    
    print('Number tokens: ', num_tokens)

    return embeddings_list, indexes_list, embeddings_mean

def normalize(corpus_name, token_width, sliding_window_increment, embeddings_array: np.array):
    """
    Loads in corpus mean and subtracts it from given embeddings

    Args:
        corpus_name: String - Subfolder name in data/text folder; ex: scriptures
        embeddings_array: np.array - Array of embeddings to normalize

    Returns: Normalized embeddings
    """
    corpus_mean = np.genfromtxt("../data/means/w"+ str(token_width).zfill(3) + "_i" + str(sliding_window_increment).zfill(3) + "/" + corpus_name + "/mean.csv", delimiter=",")
    normalized_embeddings = embeddings_array - corpus_mean
    return normalized_embeddings

def main():
    """
    Args:
        corpus_name: String - Subfolder name in data/text folder; ex: scriptures
        token width: Int - token width for sliding window
        increment: Int - sliding window increment - number of tokens to slide by
    """
    if len(sys.argv) < 4:
        raise Exception('Requires arguments: (str) corpus_name, (int) token width for sliding window, (int) sliding window increment')
    corpus_name = sys.argv[1]
    token_width = int(sys.argv[2])
    sliding_window_increment = int(sys.argv[3])

    width_increment_string = 'w' + str(token_width).zfill(3) + '_i' + str(sliding_window_increment).zfill(3)

    data_path = Path('../data').absolute().resolve()
    text_folder = data_path / 'text' / corpus_name
    mean_folder = data_path / 'means' / width_increment_string / corpus_name
    mean_path = mean_folder / "mean.csv"
    mean_temp_path = mean_folder / "temp_means.csv"

    if not mean_folder.exists():
        #os.makedirs(mean_path)
        mean_folder.mkdir(parents=True)

    for path in text_folder.rglob("*.txt"):
        new_file_path = Path(str(path).replace("text", "embeddings/" + width_increment_string))
        embeddings_path = new_file_path.with_suffix(".embeddings.csv")
        offsets_path = new_file_path.with_suffix(".offsets.csv")
        
        # Make path if it doesn't exist yet
        if not embeddings_path.parent.exists():
            embeddings_path.parent.mkdir(parents=True)

        # Only get embeddings if the file doesn't exist
        if not embeddings_path.exists():
            embeddings_list, indexes_list, embeddings_mean = process_embeddings(path, token_width, sliding_window_increment)

            np.savetxt(embeddings_path, np.asarray(embeddings_list), delimiter=',')
            np.savetxt(offsets_path, np.asarray(indexes_list), delimiter=',', fmt="%i")

            # Save temporary means to temp file
            with open(mean_temp_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(embeddings_mean)
                
    # Take mean of all means for full mean
    temp_file_means = np.genfromtxt(mean_temp_path, delimiter=',')
    corpus_mean = np.mean(temp_file_means, axis=0).tolist()

    # Save corpus mean
    np.savetxt(mean_path, corpus_mean, delimiter=',')

    # Remove temp file
    mean_temp_path.unlink()


if __name__ == "__main__":
    main()
