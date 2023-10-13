import requests
from bs4 import BeautifulSoup

# Get the HTML from the URL when given a book of scripture and chapter number
def get_scripture_html(text, book, chapter):
    url = 'https://www.churchofjesuschrist.org/study/scriptures/' + text + '/' + book + '/' + chapter + '?lang=eng'
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text

def get_conference_html(year, month, session):
    url = 'https://www.churchofjesuschrist.org/study/general-conference/' + str(year) + '/' + str(month) + '/' + str(session) + '?lang=eng'
    response = requests.get(url)
    response.encoding = 'utf-8'
    return response.text

# Get the scripture verses from the HTML
def get_scripture_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    verses = soup.find_all('p', class_='verse')
    scripture = ''
    for verse in verses:
        # get rid of all <sup> elements, (references)
        for sup in verse.find_all('sup'):
            sup.decompose()
        
        # get rid of verse numbers
        for span in verse.find_all('span', class_='verse-number'):
            span.decompose()

        # post processing
        verse_text = verse.text.replace('¶ ', '')
        verse_text = ' '.join(verse_text.split())

        scripture += verse_text + '\n'
    return scripture

def get_conference_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    conference = ''
    # go through each paragraph where id is p# where # is a number
    for paragraph in paragraphs:
        p_id = paragraph.get('id')
        if p_id is not None and p_id[0] == 'p':
            # get rid of all <sup> elements, (references)
            for sup in paragraph.find_all('sup'):
                sup.decompose()

            # post processing
            paragraph_text = ' '.join(paragraph.text.split())

            conference += paragraph_text + '\n'
    return conference

# Main function that prints verses given a book of scripture and chapter number
def scrape_scriptures(text, book, chapter):
    html = get_scripture_html(text, book, chapter)
    scripture = get_scripture_text(html)

    if scripture[-1] == '\n':
        scripture = scripture[:-1]

    return scripture

def get_conference_sessions(year, month):
    sitemap_urls = []
    sessions = []
    # read xml file
    url = "https://sitemaps.churchofjesuschrist.org/sitemap-service/www.churchofjesuschrist.org/en/index.xml"
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, features="xml")
    for loc in soup.find_all("loc"):
        sitemap_urls.append(loc.text)
    for sitemap_url in sitemap_urls:
        url = sitemap_url
        response = requests.get(url)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, features="xml")
        for loc in soup.find_all("loc"):
            if loc.text.startswith("https://www.churchofjesuschrist.org/study/general-conference/" + str(year) + '/' + str(month)):
                sessions.append((loc.text.split('/')[-1]).split('?')[0])

    return sessions


def scrape_conference(year, month, session):
    html = get_conference_html(year, month, session)
    conference = get_conference_text(html)

    if conference != '' and conference[-1] == '\n':
        conference = conference[:-1]

    return conference
