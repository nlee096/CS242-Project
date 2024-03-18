import pandas as pd
import json
import sys
filename = sys.argv[1]
f = open(filename)
data = json.load(f)
output_file = open("movie_strings.txt", "a")
for movie in data:
    title = movie["title"]
    genres = movie["genres"]

    directors = ""
    for director in movie["directors Names"]:
        if director is not None:
            directors += (director + ",")
    if directors == "":
        directors = "Unknown"
    else:
        directors = directors[:-1]

    writers = ""
    for writer in movie["writer Names"]:
        if writer is not None:
            writers += (writer + ",")
    if writers == "":
        writers = "Unknown"
    else:
        writers = writers[:-1]

    summary = movie["synopsis"] if len(movie["synopsis"]) > 0 else "Nonexistent"

    movie_str = f"Movie title is {title}, Genres are {genres}, Directors are {directors}, Writers are {writers}, Plot is {summary}\n"
    output_file.write(movie_str)
output_file.close()
