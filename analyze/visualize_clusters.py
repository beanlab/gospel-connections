from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
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

def visualize_clusters(original_text, segments, cluster_assignments, cluster_colors, book_chapter_width_window):
    # Initialize a list of colors for each character in the original text
    colors_for_chars = [''] * len(original_text)
    verses = []
    book_chapter = ' '.join(book_chapter_width_window.split("/")[:2])
    
    # Iterate over each segment and apply color
    for (start, end, verse), cluster in zip(segments, cluster_assignments):
        color = cluster_colors[cluster]
        verses.append(verse)
        # if verse not in verse_start_indices:
            # verse_start_indices[verse] = start
        for i in range(start, min(end, len(original_text))):
            colors_for_chars[i] = color
    
    highlighted_text = []
    additional_length = 0 
    last_color = '' 
    verse = 1
    highlighted_text.append(f'<div><span style="font-weight:bold;"> {book_chapter} </span>') 
    for i, char in enumerate(original_text):
        # print("i", i)
        # print("char", char)
        color = colors_for_chars[i]
        
        # if i in verse_start_indices:
        #     verse_number = verse_start_indices[i]
        if i == 0 or original_text[i-1] == '\n':
            highlighted_text.append('</span>')
            highlighted_text.append(f'<div><span style="font-weight:bold;">{verse} </span>')
            additional_length += len(str(verse)) + len('<div><span style="font-weight:bold;"></span>')
            highlighted_text.append(f'<span style="background-color: {color};">')
            
            verse += 1  
        
        
        # if i + additional_length < len(original_text) + additional_l 
        if color != last_color:  # Start a new span whenever color changes
            if last_color:  # Close the last span
                highlighted_text.append('</span>')
            highlighted_text.append(f'<span style="background-color: {color};">')
        highlighted_text.append(char)
        last_color = color
        
        if char == '\n':
            highlighted_text.append('</div>')
    highlighted_text.append('</span>')  # Close the final span
    highlighted_text.append('</div>')
    # Display the highlighted text
    name = '_'.join(book_chapter_width_window.split("/"))
    with open(f'{name}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(''.join(highlighted_text))
    # display(HTML(''.join(highlighted_text)))

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

    text = get_texts_from_offset(offsets, book_chapter)

    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embedds)

    kmeans = KMeans(n_clusters=3, random_state=0).fit(reduced_embeddings)
    cluster_labels = kmeans.labels_

    data = {'x': reduced_embeddings[:, 0],
            'y': reduced_embeddings[:, 1],
            'text_labels': convert_all_text(text),
            'cluster_labels': cluster_labels}
    df = pd.DataFrame(data)

    cluster_colors = ['lightblue', 'lightgreen', 'lightpink']

    segments = [(row[0], row[1], row[2]) for row in offsets]
    groups = [{group: 1} for group in cluster_labels]

    with open(text_file, 'r', encoding='utf-8') as file:
        text = file.read()
    
    render(text, segments, groups, book_chapter)
    
    
    # visualize_clusters(contents, segments, cluster_labels, cluster_colors, book_chapter_width_window)

def main():
    if len(sys.argv) < 2:
        raise Exception('Requires arguments: (string) book/chapter/token_width/sliding_window  ex: 2-ne/8/40/20')
    book_chapter_width_window = sys.argv[1]
    create_clusters(book_chapter_width_window, render.render_html)

if __name__ == "__main__":
    main()