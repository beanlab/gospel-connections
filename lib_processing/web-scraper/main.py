import json
import os
import scraper
import unidecode

# Read the JSON file
with open('std-works-spec.json') as f:
    data = json.load(f)

# Get the verses for each chapter
for standard_work, standard_work_data in data['standard_works'].items():
    standard_work_code = standard_work_data['code']
    for book_data in standard_work_data['books']:
        book_code = book_data['code']
        chapters = book_data['chapters']
        for chapter in range(1, chapters + 1):
            print(standard_work + ' ' + book_code + ' ' + str(chapter))
            scripture = scraper.scrape(standard_work_code, book_code, str(chapter))
            scripture = unidecode.unidecode(scripture)

            if scripture == '':
                print('ERROR 404: ' + standard_work + ' ' + book_code + ' ' + str(chapter))

            directory = '../data/scriptures/' + standard_work + '/text/' + book_code
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(directory + '/' + "{:03d}".format(chapter) + '.txt', 'w') as f:
                f.write(scripture)

