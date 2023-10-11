import openai
import os
import sys
import tiktoken
import numpy as np
import time
from tqdm import tqdm
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
    
        # Peform mean transform
        embeddings_list = np.asarray(embeddings_list)
        embeddings_mean = np.mean(embeddings_list, axis=0).tolist()
        #if embeddings_list.shape[0] > 1:
        #    embeddings_list = embeddings_list - np.mean(embeddings_list, axis=0)

        new_file_path = ("/".join(file.split("/")[0:-1]).replace("text", "embeddings/w"+ str(token_width).zfill(3) + "_i" + str(sliding_window_increment).zfill(3) , 1))
        file_name = file.split("/")[-1].split(".")[0]

        if not os.path.exists(new_file_path):
            os.makedirs(new_file_path)

        np.savetxt(new_file_path + "/" + file_name + ".embeddings.csv", np.asarray(embeddings_list), delimiter=',')
        np.savetxt(new_file_path + "/" + file_name + ".offsets.csv", np.asarray(indexes_list), delimiter=',', fmt="%i")
        
    price = (float(num_tokens) / 1000) * ADA_2_PRICING
    
    print('Final price: $', price)    
    print('Number tokens: ', num_tokens)

    return embeddings_mean

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

    file_means = []

    folder = '../data/text/' + corpus_name
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder).replace("\\","/")
            full_path = folder + "/" + relative_path
            embeddings_mean = process_embeddings(full_path, token_width, sliding_window_increment)
            # Add mean to total mean
            file_means.append(embeddings_mean)

    # Take mean of all means for full mean
    file_means = np.asarray(file_means)
    corpus_mean = np.mean(file_means, axis=0).tolist()

    # Save corpus mean
    # Get new path
    mean_path = (folder.replace("text", "means/w"+ str(token_width).zfill(3) + "_i" + str(sliding_window_increment).zfill(3), 1))

    print(mean_path)
    if not os.path.exists(mean_path):
        os.makedirs(mean_path)

    np.savetxt(mean_path + "/" + "mean.csv", corpus_mean, delimiter=',')


if __name__ == "__main__":
    main()
