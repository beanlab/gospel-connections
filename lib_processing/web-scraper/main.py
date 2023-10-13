import json
import os
import scraper
import unidecode

def generate_scripture_text():

    # Read the JSON file
    with open("std-works-spec.json") as f:
        data = json.load(f)

    # Get the verses for each chapter
    for standard_work, standard_work_data in data["standard_works"].items():
        standard_work_code = standard_work_data["code"]
        for book_data in standard_work_data["books"]:
            book_code = book_data["code"]
            chapters = book_data["chapters"]
            for chapter in range(1, chapters + 1):
                print(standard_work + " " + book_code + " " + str(chapter))
                scripture = scraper.scrape_scriptures(standard_work_code, book_code, str(chapter))
                scripture = unidecode.unidecode(scripture)

                if scripture == "":
                    print("ERROR 404: " + standard_work + " " + book_code + " " + str(chapter))
                    continue

                directory = "../../data/text/scriptures/" + standard_work + "/" + book_code
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(directory + "/" + "{:03d}".format(chapter) + ".txt", "w") as f:
                    f.write(scripture)

def generate_conference_text(year, month):
    # get all the sessions for year/month
    sessions = scraper.get_conference_sessions(year, month)
    print(sessions)
    for session in sessions:
        print(session)
        title, speaker, text = scraper.scrape_conference(year, month, session)
        text = unidecode.unidecode(text)

        if text == "":
            print("ERROR 404: " + str(year) + " " + str(month) + " " + session)
            continue

        directory = "../../data/text/conference/" + str(year) + "_" + str(month)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(directory + "/" + title + "_" + speaker + ".txt", "w") as f:
            f.write(text)

generate_conference_text(2023, 10)