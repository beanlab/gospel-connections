'''
TODO: handle special characters
TODO: decide on format of output, (csv, json, txt, etc.) 
      (including paragraph symbols, footnotes, where to get verse & chapter numbers?)
TODO: error handling & logging if necessary
'''

import requests
from bs4 import BeautifulSoup

# Get the HTML from the URL when given a book of scripture and chapter number
def get_html(text, book, chapter):
    url = 'https://www.churchofjesuschrist.org/study/scriptures/' + text + '/' + book + '/' + chapter + '?lang=eng'
    response = requests.get(url)
    return response.text

# Get the scripture verses from the HTML
def get_scripture(html):
    soup = BeautifulSoup(html, 'html.parser')
    verses = soup.find_all('p', class_='verse')
    scripture = ''
    for verse in verses:
        # get rid of all <sup> elements, (references)
        for sup in verse.find_all('sup'):
            sup.decompose()
        # get rid of the verse number
        verse.span.decompose()
        scripture += verse.text.replace('Â¶ ', '') + '\n'
    return scripture

# Main function that prints verses given a book of scripture and chapter number
def scrape(text, book, chapter):
    html = get_html(text, book, chapter)
    scripture = get_scripture(html)
    return scripture


