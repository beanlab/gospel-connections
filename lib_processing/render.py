from lib_processing import scriptures_structure
from typing import Callable, Protocol
import random

class Render(Protocol):
    def __call__(self, text: str, offsets: list[tuple], groups: list | dict, book_chapter: str): ...

def random_color(alpha):
    r = random.randint(128, 255)  
    g = random.randint(128, 255)  
    b = random.randint(128, 255)       
    return f'rgb({r}, {g}, {b}, {alpha})'
    
def render_html(text: str, offsets: list[tuple], groups: list | dict, book_chapter: str):
    """
    Render the text with the given offsets and groups to an HTML file.
    Groups can be a list of dicts or a dict of dicts.
    Text is assigned to the group with the highest weight. 
    Colors are randomly generated for each group. Transparency is set to the weigth of the group.
    """

    colors = {}
    colors_for_chars = [''] * len(text)
    verses = []

    # Handle groups as a list ex [{grp1: 0.5}, {grp3: 0.7}, {grp2: 0.9}]
    if type(groups) == list:    
        for (start, end, verse), group_list in zip(offsets, groups):
            best_group = None
            best_weight = 0
            for group, weight in group_list.items():
                if weight > best_weight:
                    best_weight = weight
                    best_group = group

            if best_group not in colors:
                alpha = best_weight
                colors[best_group] = random_color(alpha)
            color = colors[best_group]
            # verses.append(verse)
            for i in range(start, min(end, len(text))):
                colors_for_chars[i] = color

    # Handle groups as a dict ex {0: {grp1: 0.5, grp2: 0.7}, 1: {grp3: 0.9}}
    else:
        for offset, weights in groups.items():
            best_group = None
            best_weight = 0
            for group, weight in weights.items():
                if weight > best_weight:
                    best_weight = weight
                    best_group = group

            if best_group not in colors:
                alpha = best_weight
                colors[best_group] = random_color(alpha)
            color = colors[best_group]

            for i in range(offsets[offset][0], min(offsets[offset][1], len(text))):
                colors_for_chars[i] = color

    # create html
    highlighted_text = []
    additional_length = 0 
    last_color = '' 
    verse = 1
    title = ' '.join(book_chapter.split("/"))
    title = f"{title[0].upper()}{title[1:]}"
    highlighted_text.append(f'<div><span style="font-weight:bold;"> {title} </span>') 
    for i, char in enumerate(text):
        color = colors_for_chars[i]
        
        if i == 0 or text[i-1] == '\n':
            highlighted_text.append('</span>')
            highlighted_text.append(f'<div><span style="font-weight:bold;">{verse} </span>')
            additional_length += len(str(verse)) + len('<div><span style="font-weight:bold;"></span>')
            highlighted_text.append(f'<span style="background-color: {color};">')
            
            verse += 1  
        
        if color != last_color:  # Start a new span whenever color changes
            if last_color:  # Close the last span
                highlighted_text.append('</span>')
            highlighted_text.append(f'<span style="background-color: {color};">')
        highlighted_text.append(char)
        last_color = color
        
        if char == '\n':
            highlighted_text.append('</div>')
    highlighted_text.append('</span>') 
    highlighted_text.append('</div>')

    # Display the highlighted text
    name = '_'.join(book_chapter.split("/"))
    with open(f'./html/{name}.html', 'w', encoding='utf-8') as html_file:
        html_file.write(''.join(highlighted_text))
