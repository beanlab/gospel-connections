from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
import plotly.graph_objects as go
import pandas as pd
import sys

sys.path.append(".")
from structure import scriptures_structure


alma_32_files = scriptures_structure.get_embedding_file_path('alma/32/40/20') 
alma_32_embedds = pd.read_csv("./" + alma_32_files[0], header=None).to_numpy()
alma_32_offsets = pd.read_csv("./" + alma_32_files[1], header=None).to_numpy()


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


text = get_texts_from_offset(alma_32_offsets, 'alma/32')

pca = PCA(n_components=2)
reduced_embeddings = pca.fit_transform(alma_32_embedds)

kmeans = KMeans(n_clusters=3, random_state=0).fit(reduced_embeddings)
cluster_labels = kmeans.labels_

data = {'x': reduced_embeddings[:, 0],
        'y': reduced_embeddings[:, 1],
        'text_labels': convert_all_text(text),
        'cluster_labels': cluster_labels}
df = pd.DataFrame(data)

html_strings = []
# for i, text_point in enumerate(text):  # Replace 'text_data' with your text data
#     cluster_label = cluster_labels[i]
#     highlighted_text = f'<span class="cluster-{cluster_label}">{text_point}</span>'
#     html_strings.append(highlighted_text)
    

# html_content = "<html><head><style>.cluster-0{color:red;}.cluster-1{color:blue;}.cluster-2{color:green;}.cluster-3{color:orange;}.cluster-4{color:purple;}</style></head><body>"
# html_content += "<br>".join(html_strings)
# html_content += "</body></html>"

html_content = "<html><head><style>.highlight-0{background-color:lightblue;}.highlight-1{background-color:blue;}.highlight-2{background-color:green;}.highlight-3{background-color:orange;}.highlight-4{background-color:purple;}</style></head><body>"
for i, text_point in enumerate(text):  # Replace 'text_data' with your text data
    cluster_label = cluster_labels[i]
    highlighted_text = f'<span class="highlight-{cluster_label}">{text_point}</span>'
    html_content += highlighted_text + "<br>"
html_content += "</body></html>"


# Save the HTML content to a file
with open('clustered_text.html', 'w', encoding='utf-8') as html_file:
    html_file.write(html_content)