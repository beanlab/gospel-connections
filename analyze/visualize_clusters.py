from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.spatial import distance
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(".")
from lib_processing import scriptures_structure
from lib_processing import render
from lib_processing.render import Render
# from lib_processing import generate_html

os.environ['OMP_NUM_THREADS'] = '1'

def get_texts_from_offset(offsets, book_chapter):
    text_array = []
    text_file = "./" + scriptures_structure.get_text_file_path(book_chapter)
    with open(text_file, 'r', encoding='utf-8') as file:
        contents = file.read()
        for offset in offsets:
            # print(contents[offset[0]:offset[1]])
            # print("-----------------------------------")
            text_array.append(contents[offset[0]:offset[1]])
    return text_array


def convert_text(text):
    lines = []
    text = text.split()
    for i in range(0, len(text), 10):
        line = ' '.join(text[i:i + 10])
        lines.append(line)

    result = '<br>'.join(lines)
    # print(result)
    return result


def convert_all_text(text):
    for i in range(len(text)):
        text[i] = convert_text(text[i])
    return text


# For each segment, compute embeddings, perform clustering and visualize
# Example usage (you will need to replace with actual clustering results):
def make_dict(clusters):
    unique_numbers = set(clusters)
    result = {num: [1 if x == num else 0 for x in clusters] for num in unique_numbers}
    return result


def create_clusters(book_chapter_width_window,  render: Render):
    files = scriptures_structure.get_embedding_file_path(book_chapter_width_window) 
    embedds = pd.read_csv("./" + files[0], header=None).to_numpy()
    offsets = pd.read_csv("./" + files[1], header=None).to_numpy()

    book_chapter = '/'.join(book_chapter_width_window.split("/")[:2])
    text_file = "./" + scriptures_structure.get_text_file_path(book_chapter)
    with open(text_file, 'r', encoding='utf-8') as file:
        contents = file.read()
        # print(contents)

    text = get_texts_from_offset(offsets, book_chapter)

    # pca = PCA(n_components=2)
    # reduced_embeddings = pca.fit_transform(embedds)
    cluster_range = range(2, 11)

    best_score = -1
    best_num_clusters = 0

    # Calculate Silhouette Score for each cluster number
    for n_clusters in cluster_range:
        kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(embedds)
        labels = kmeans.labels_
        score = silhouette_score(embedds, labels)
        
        if score > best_score:
            best_score = score
            best_num_clusters = n_clusters

    kmeans = KMeans(n_clusters=best_num_clusters, random_state=0).fit(embedds)
    cluster_labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    new_offsets = []
    new_cluster_assignments = []

    new_cluster_assignments.append(1)
    new_offsets.append((offsets[0][0], int(offsets[0][1]/2), offsets[0][2]))
    for i in range(len(embedds) - 1):
            # Compute the mean of the pair
            mean_embedding = (embedds[i] + embedds[i + 1]) / 2.0
            
            # Find the nearest cluster center for the mean embedding
            nearest_centroid_idx = np.argmin([distance.euclidean(mean_embedding, centroid) for centroid in centroids])
            
            # Append to our new cluster assignments list
            new_offsets.append((new_offsets[i-1][1], offsets[i][1], offsets[0][2]))
            new_cluster_assignments.append(nearest_centroid_idx + 1)
    print(new_cluster_assignments)


    data = {'x': embedds[:, 0],
            'y': embedds[:, 1],
            'text_labels': convert_all_text(text),
            'cluster_labels': cluster_labels}
    df = pd.DataFrame(data)

    segments = [(row[0], row[1], row[2]) for row in new_offsets]
    
    dict_groups = {}
    for i, group in enumerate(cluster_labels):
        if i not in dict_groups:
            dict_groups[i] = {}
        dict_groups[i][group] = 1

    list_groups = [{group: 1} for group in new_cluster_assignments]
    
    render(contents, segments, list_groups, book_chapter)
    

def main():
    if len(sys.argv) < 2:
        raise Exception('Requires arguments: (string) book/chapter/token_width/sliding_window  ex: 2-ne/8/40/20')
    book_chapter_width_window = sys.argv[1]
    create_clusters(book_chapter_width_window, render.render_html)

if __name__ == "__main__":
    main()