import numpy as np
from numpy import dot
from numpy.linalg import norm
import matplotlib.pyplot as plt
import matplotlib
import matplotlib as mpl
import plotly.express as px
import pandas as pd
import os

def get_label(index, indexes, text):
    if len(indexes.shape) != 1:
        text_indices = indexes[index]
    else:
        text_indices = indexes
    chunk = text[text_indices[0]:text_indices[1]]
    verse = text_indices[2]
    return chunk, verse

def generate_all_labels(index, indexes, text):
    labels = []
    for i in range(index):
        label, verse = get_label(i, indexes, text)
        labels.append(label)
    return labels

def explore(coordinate, cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values):
        cluster_coordinates.append(coordinate)
        cluster_values.append(thresholded_values[thresholded_coordinates.index(coordinate)])
        (i, j) = coordinate
        if (i+1, j) in thresholded_coordinates and (i+1, j) not in cluster_coordinates:
            explore((i+1, j), cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values)
        elif (i-1, j) in thresholded_coordinates and (i-1, j) not in cluster_coordinates:
            explore((i-1, j), cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values)
        elif (i, j+1) in thresholded_coordinates and (i, j+1) not in cluster_coordinates:
            explore((i, j+1), cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values)
        elif (i, j-1) in thresholded_coordinates and (i, j-1) not in cluster_coordinates:
            explore((i, j-1), cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values)

def create_heatmap(cos_sim: np.array, 
                   indexes_1: np.array, 
                   indexes_2: np.array, 
                   text_1: str, 
                   text_2: str, 
                   threshold: int):
    """
    Creates heatmap based on cos_sim values 

    cos_sim: 2d numpy array containing cosine similarity values
    indexes_1 - index offsets file for first data
    indexes_2 - index offsets file for second data
    text_1 - raw text for first data
    text_2 - raw text for second data
    threshold - zmin to use with heatmap; all values below threshold will be considered zero visually
    
    Ex:
    create_heatmap.create_heatmap(cos_sim_norm, offs, offs, text, text, 0)
    """
    length_1 = cos_sim.shape[0]
    length_2 = cos_sim.shape[1]
    labels_1 = generate_all_labels(length_1, indexes_1, text_1)
    labels_2 = generate_all_labels(length_2, indexes_2, text_2)

    im = px.imshow(cos_sim[:length_1, :length_2],
                x=labels_2, 
                y=labels_1,
                width=750,
                height=750,
                text_auto=False,
                zmin=threshold,
                zmax=1,
                color_continuous_scale='viridis')

    im.update_xaxes(showticklabels=False)
    im.update_yaxes(showticklabels=False)

    im.show()

    plt.figure()
    plt.hist(cos_sim.flatten(), bins=50)
    
def get_top_matches(cos_sim: np.array, 
                    indexes_1: np.array, 
                    indexes_2: np.array, 
                    text_1: str, 
                    text_2: str, 
                    threshold: int) -> np.array:
    """
    Performs a search across array to filter n top cosine values based on threshold
    
    cos_sim: 2d numpy array containing cosine similarity values
    indexes_1 - index offsets file for first data
    indexes_2 - index offsets file for second data
    text_1 - raw text for first data
    text_2 - raw text for second data
    threshold - all cosine values below threshold will automatically be filtered out, and not searched

    Returns: np.array representing new cosine similarity matrix, with matches maxed.

    Ex:
    cos_sim_cluster_max = create_heatmap.get_top_matches(cos_sim_norm, offs, offs, text, text, 0.5)
    create_heatmap.create_heatmap(cos_sim_cluster_max, offs, offs, text, text, 0)
    """
    thresholded_values = []
    thresholded_coordinates = []
    result_dict = {}
    cos_sim_thresholded = np.copy(cos_sim)
    cos_sim_cluster_max = np.copy(cos_sim)

    # Find the max cos_sim value
    max_sim_indexes = np.unravel_index(cos_sim.argmax(), cos_sim.shape)
    max_sim = cos_sim[max_sim_indexes[0]][max_sim_indexes[1]]

    # Find all values in the matrix above the given threshold, saving them
    num = 0
    for i in range(cos_sim.shape[0]):
        for j in range(cos_sim.shape[1]):
            cos_sim_val = cos_sim[i, j]
            if cos_sim_val >= threshold:
                thresholded_values.append(cos_sim_val)
                thresholded_coordinates.append((i,j))

                # Save to new cossim array - this is just for a heatmap, could return if wanted
                cos_sim_thresholded[i,j] = max_sim


    # Iterate through interim dict to discover clusters and take out top similarities from each
    for coordinate in thresholded_coordinates:
        num += 1
        # check all neighbors of coordinate and check if they exist in the thresholded list
        cluster_coordinates = []
        cluster_values = []

        explore(coordinate, cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values)

        # At the end, find max tile and remove all others in cluster from thresholded lists
        # Find max
        cos_sim_val_max = max(cluster_values)
        cluster_index = cluster_values.index(cos_sim_val_max)
        max_coordinate = cluster_coordinates[cluster_index]
        (max_i, max_j) = max_coordinate
        cos_sim_cluster_max[max_i, max_j] = max_sim
        
        # Add to final list
        line_1, verse_1 = get_label(max_i, indexes_1, text_1)
        line_2, verse_2 = get_label(max_j, indexes_2, text_2)

        # Save to dict
        result_dict[cos_sim_val_max] = (line_1, line_2, verse_1, verse_2)

        # Remove all in cluster from search list so we don't search again
        for final_coordinate in cluster_coordinates:
            index = thresholded_coordinates.index(final_coordinate)
            del thresholded_coordinates[index]
            del thresholded_values[index]
    

    print('Number found: ', num)

    sorted_dict = sorted(result_dict, reverse=True)
    #for key in sorted(result_dict, reverse=True):
    for i in range(len(sorted_dict)):
        print('////////////////////////////////////////////////////////////////////////////')
        print('Cosine Value: ', sorted_dict[i])
        #print('Source: ', source_1)
        print('Verse ', result_dict[sorted_dict[i]][2])
        print('LINE 1: ', result_dict[sorted_dict[i]][0])
        print('--------------------------------------------')
        #print('Source: ', source_2)
        print('Verse ', result_dict[sorted_dict[i]][3])
        print('LINE 2: ', result_dict[sorted_dict[i]][1])

    # TODO: could save these values, do something with them

    return cos_sim_cluster_max

def get_top_matches_test(cos_sim: np.array, 
                    indexes_1: np.array, 
                    indexes_2: np.array, 
                    text_1: str, 
                    text_2: str, 
                    threshold: int) -> np.array:
    """
    Performs a search across array to filter n top cosine values based on threshold
    
    cos_sim: 2d numpy array containing cosine similarity values
    indexes_1 - index offsets file for first data
    indexes_2 - index offsets file for second data
    text_1 - raw text for first data
    text_2 - raw text for second data
    threshold - all cosine values below threshold will automatically be filtered out, and not searched

    Returns: np.array representing new cosine similarity matrix, with matches maxed.

    Ex:
    cos_sim_cluster_max = create_heatmap.get_top_matches(cos_sim_norm, offs, offs, text, text, 0.5)
    create_heatmap.create_heatmap(cos_sim_cluster_max, offs, offs, text, text, 0)
    """
    thresholded_values = []
    thresholded_coordinates = []
    result_dict = {}
    cos_sim_thresholded = np.copy(cos_sim)
    cos_sim_cluster_max = np.copy(cos_sim)

    # Find the max cos_sim value
    max_sim_indexes = np.unravel_index(cos_sim.argmax(), cos_sim.shape)
    max_sim = cos_sim[max_sim_indexes[0]][max_sim_indexes[1]]

    # Find all values in the matrix above the given threshold, saving them
    num = 0
    for i in range(cos_sim.shape[0]):
        for j in range(cos_sim.shape[1]):
            cos_sim_val = cos_sim[i, j]
            if cos_sim_val >= threshold:
                thresholded_values.append(cos_sim_val)
                thresholded_coordinates.append((i,j))

                # Save to new cossim array - this is just for a heatmap, could return if wanted
                cos_sim_thresholded[i,j] = max_sim


    # Iterate through interim dict to discover clusters and take out top similarities from each
    for coordinate in thresholded_coordinates:
        num += 1
        # check all neighbors of coordinate and check if they exist in the thresholded list
        cluster_coordinates = []
        cluster_values = []

        explore(coordinate, cluster_coordinates, cluster_values, thresholded_coordinates, thresholded_values)

        # At the end, find max tile and remove all others in cluster from thresholded lists
        # Find max
        cos_sim_val_max = max(cluster_values)
        cluster_index = cluster_values.index(cos_sim_val_max)
        max_coordinate = cluster_coordinates[cluster_index]
        (max_i, max_j) = max_coordinate
        cos_sim_cluster_max[max_i, max_j] = max_sim
        
        # Add to final list
        line_1, verse_1 = get_label(max_i, indexes_1, text_1)
        line_2, verse_2 = get_label(max_j, indexes_2, text_2)

        # Save to dict
        result_dict[cos_sim_val_max] = (line_1, line_2, verse_1, verse_2)

        # Remove all in cluster from search list so we don't search again
        for final_coordinate in cluster_coordinates:
            index = thresholded_coordinates.index(final_coordinate)
            del thresholded_coordinates[index]
            del thresholded_values[index]
    

    print('Number found: ', num)

    sorted_dict = sorted(result_dict, reverse=True)
    #for key in sorted(result_dict, reverse=True):
    for i in range(len(sorted_dict)):
        print('////////////////////////////////////////////////////////////////////////////')
        print('Cosine Value: ', sorted_dict[i])
        #print('Source: ', source_1)
        print('Verse ', result_dict[sorted_dict[i]][2])
        print('LINE 1: ', result_dict[sorted_dict[i]][0])
        print('--------------------------------------------')
        #print('Source: ', source_2)
        print('Verse ', result_dict[sorted_dict[i]][3])
        print('LINE 2: ', result_dict[sorted_dict[i]][1])

    # TODO: return result_dict in the right form
    # tuple of (cos_val, line_1, line_2, verse_1, verse_2, book_1, book_2)
    # OR dict:j (locations) -> value

    return cos_sim_cluster_max