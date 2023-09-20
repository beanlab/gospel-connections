BOOK_OF_MORMON = ["1-ne",
                  "2-ne",
                  "jacob",
                  "enos",
                  "jarom",
                  "omni",
                  "w-of-m",
                  "mosiah",
                  "alma",
                  "hel",
                  "3-ne",
                  "4-ne",
                  "morm",
                  "ether",
                  "moro"]

NEW_TESTAMENT = ["1-cor",
                 "1-jn",
                 "1-pet",
                 "1-thes",
                 "1-tim",
                 "2-cor",
                 "2-jn",
                 "2-pet",
                 "2-thes",
                 "2-tim",
                 "3-jn",
                 "acts",
                 "col",
                 "eph",
                 "gal",
                 "heb",
                 "james",
                 "john",
                 "jude",
                 "luke",
                 "mark",
                 "matt",
                 "philem",
                 "philip",
                 "rev",
                 "rom",
                 "titus"]

OLD_TESTAMENT = ["1-chr",
                 "1-kgs",
                 "1-sam",
                 "2-chr",
                 "2-kgs",
                 "2-sam",
                 "amos",
                 "dan",
                 "deut",
                 "eccl",
                 "esth",
                 "ex",
                 "ezek",
                 "ezra",
                 "gen",
                 "hab",
                 "hag",
                 "hosea",
                 "isa",
                 "jer",
                 "job",
                 "joel",
                 "jonah",
                 "josh",
                 "judg",
                 "lam",
                 "lev",
                 "mal",
                 "micah",
                 "nahum",
                 "neh",
                 "num",
                 "obad",
                 "prov",
                 "ps",
                 "ruth",
                 "song",
                 "zeph",
                 "zech"]

PEARL_OF_GREAT_PRICE = ["abr",
                        "js-m",
                        "js-h",
                        "a-of-f",
                        "moses"]


def get_text_file_path(book_chapter):
    book = book_chapter.split("/")[0]
    chapter = book_chapter.split("/")[1].zfill(3)
    if book in BOOK_OF_MORMON:
        return "data/scriptures/book_of_mormon/text/" + book + "/" + chapter + ".txt"
    elif book in NEW_TESTAMENT:
        return "data/scriptures/new_testament/text/" + book + "/" + chapter + ".txt"
    elif book in OLD_TESTAMENT:
        return "data/scriptures/old_testament/text/" + book + "/" + chapter + ".txt"
    elif book in PEARL_OF_GREAT_PRICE:
        return "data/scriptures/pearl_of_great_price/text/" + book + "/" + chapter + ".txt"
    else:
        raise Exception('Invalid book and chapter: ' + book_chapter)


def get_embedding_file_path(book_chapter_width):
    book = book_chapter_width.split("/")[0]
    chapter = book_chapter_width.split("/")[1].zfill(3)
    width = book_chapter_width.split("/")[2].zfill(3)
    increment = book_chapter_width.split("/")[3].zfill(3)
    if book in BOOK_OF_MORMON:
        return ("data/scriptures/book_of_mormon/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".embeddings.csv",
                "data/scriptures/book_of_mormon/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".offsets.csv")
    elif book in NEW_TESTAMENT:
        return ("data/scriptures/new_testament/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".embeddings.csv",
                "data/scriptures/new_testament/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".offsets.csv")
    elif book in OLD_TESTAMENT:
        return ("data/scriptures/old_testament/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".embeddings.csv",
                "data/scriptures/old_testament/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".offsets.csv")
    elif book in PEARL_OF_GREAT_PRICE:
        return ("data/scriptures/pearl_of_great_price/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".embeddings.csv",
                "data/scriptures/pearl_of_great_price/embeddings/" + book + "/" + chapter + ".w" + width + ".i" + increment + ".offsets.csv")
    else:
        raise Exception('Invalid book and chapter: ' + book_chapter_width)
