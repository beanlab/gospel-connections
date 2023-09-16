import numpy as np
import pandas as pd
from numpy import dot
import argparse
from numpy.linalg import norm
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from structure import scriptures_structure


def generate_PCA(files1, files2=None):
    file1_df = pd.read_csv(files1[0], header=None)
    file1_embeds = file1_df.to_numpy()

    if files2 is not None:
        file2_df = pd.read_csv(files2[0], header=None)
        file2_embeds = file2_df.to_numpy()
        cos_sim = dot(file1_embeds, file2_embeds.transpose()) / (norm(file1_embeds) * norm(file2_embeds))
    else:
        cos_sim = dot(file1_embeds, file1_embeds.transpose()) / (norm(file1_embeds))
    
    # Assuming 'cosine_similarity_matrix' is your cosine similarity matrix
    # Rows represent items/features, and columns represent similarity scores

    # Center the data (subtract the mean)
    mean_centered_data = cos_sim - np.mean(cos_sim, axis=0)

    # Perform PCA
    n_components = 2  # Choose the number of components for dimensionality reduction
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(mean_centered_data)

    plt.scatter(pca_result[:, 0], pca_result[:, 1])
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.title('PCA of Cosine Similarity Matrix')
    plt.show()


def main():
    parser = argparse.ArgumentParser(description="Run visualizations on embeddings")
    parser.add_argument("file_info1", help="provide the information for the first file (book, chapter, width) ex: 2-ne/1/100")
    parser.add_argument("file_info2", nargs="?", help="provide the information for the second file if desired (book, chapter, width) ex: 2-ne/1/100")
    
    args = parser.parse_args()
    file_info1 = args.file_info1
    file_info2 = args.file_info2
    
    if file_info2 is not None:
        file1_paths = scriptures_structure.get_text_file_path(file_info1)
        file2_paths = scriptures_structure.get_text_file_path(file_info2)
        generate_PCA(file1_paths, file2_paths)
    else:
        file1_paths = scriptures_structure.get_text_file_path(file_info1)
        generate_PCA(file1_paths)


if __name__ == "__main__":
    main()
