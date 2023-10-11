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
        return "data/text/scriptures/book_of_mormon/" + book + "/" + chapter + ".txt"
    elif book in NEW_TESTAMENT:
        return "data/text/scriptures/new_testament/" + book + "/" + chapter + ".txt"
    elif book in OLD_TESTAMENT:
        return "data/text/scriptures/old_testament/" + book + "/" + chapter + ".txt"
    elif book in PEARL_OF_GREAT_PRICE:
        return "data/text/scriptures/pearl_of_great_price/" + book + "/" + chapter + ".txt"
    else:
        raise Exception('Invalid book and chapter: ' + book_chapter)


def get_embedding_file_path(book_chapter_width):
    book = book_chapter_width.split("/")[0]
    chapter = book_chapter_width.split("/")[1].zfill(3)
    width = book_chapter_width.split("/")[2].zfill(3)
    increment = book_chapter_width.split("/")[3].zfill(3)
    if book in BOOK_OF_MORMON:
        return ("data/embeddings/w" + width + "_i" + increment + "/scriptures/book_of_mormon/" + book + "/" + chapter + ".embeddings.csv",
                "data/embeddings/w" + width + "_i" + increment + "/scriptures/book_of_mormon/" + book + "/" + chapter + ".offsets.csv")
    elif book in NEW_TESTAMENT:
        return ("data/embeddings/w" + width + "_i" + increment + "/scriptures/new_testament/" + book + "/" + chapter + ".embeddings.csv",
                "data/embeddings/w" + width + "_i" + increment + "/scriptures/new_testament/" + book + "/" + chapter + ".offsets.csv")
    elif book in OLD_TESTAMENT:
        return ("data/embeddings/w" + width + "_i" + increment + "/scriptures/old_testament/" + book + "/" + chapter + ".embeddings.csv",
                "data/embeddings/w" + width + "_i" + increment + "/scriptures/old_testament/" + book + "/" + chapter + ".offsets.csv")
    elif book in PEARL_OF_GREAT_PRICE:
        return ("data/embeddings/w" + width + "_i" + increment + "/scriptures/pearl_of_great_price/" + book + "/" + chapter + ".embeddings.csv",
                "data/embeddings/w" + width + "_i" + increment + "/scriptures/pearl_of_great_price/" + book + "/" + chapter + ".offsets.csv")
    else:
        raise Exception('Invalid book and chapter: ' + book_chapter_width)
