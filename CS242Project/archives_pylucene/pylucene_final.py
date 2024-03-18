import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
import time
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

# To run: python3 pylucene_final.py Field:"keyword"
# EX: python3 pylucene_final.py Title:"the"
# TO-DO: add handlers for different types of queries and to work with all fields

def parse_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def create_index(movies, dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    store = SimpleFSDirectory(Paths.get(dir))
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    writer = IndexWriter(store, config)

    contextType = FieldType()
    contextType.setStored(True)
    contextType.setTokenized(True)
    contextType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    for movie in movies:
        # tconst = movie['tconst']
        # ordering = movie['ordering']
        title = movie['title']
        synopsis = movie['synopsis']
        region = movie['region']
        # language = movie['language']
        # types = movie['types']
        # attributes = movie['attributes']
        # isOriginalTitle = movie['isOriginalTitle']
        # titleType = movie['titleType']
        # primaryTitle = movie['primaryTitle']
        # originalTitle = movie['originalTitle']
        # isAdult = movie['isAdult']
        startYear = movie['startYear']
        # endYear = movie['endYear']
        # runtimeMinutes = movie['runtimeMinutes']
        genres = movie['genres']
        # directors = movie['directors']
        # writers = movie['writers']
        # averageRating = movie['averageRating']
        # numVotes = movie['numVotes']
        directorsNames = movie['directors Names']
        writerNames = movie['writer Names']

        doc = Document()
        # doc.add(Field('Tconst', str(tconst), contextType))
        # doc.add(Field('Ordering', str(ordering), contextType))
        doc.add(Field('title', str(title), contextType))
        doc.add(Field('synopsis', str(synopsis), contextType))
        doc.add(Field('region', str(region), contextType))
        # doc.add(Field('Language', str(language), contextType))
        # doc.add(Field('Types', str(types), contextType))
        # doc.add(Field('Attributes', str(attributes), contextType))
        # doc.add(Field('Is Original Title', str(isOriginalTitle), contextType))
        # doc.add(Field('Title Type', str(titleType), contextType))
        # doc.add(Field('Primary Title', str(primaryTitle), contextType))
        # doc.add(Field('Original Title', str(originalTitle), contextType))
        # doc.add(Field('Is Adult', str(isAdult), contextType))
        doc.add(Field('start_year', str(startYear), contextType))
        # doc.add(Field('End Year', str(endYear), contextType))
        # doc.add(Field('Runtime Minutes', str(runtimeMinutes), contextType))
        doc.add(Field('genres', str(genres), contextType))
        # doc.add(Field('Directors', str(directors), contextType))
        # doc.add(Field('Writers', str(writers), contextType))
        # doc.add(Field('Average Rating', str(averageRating), contextType))
        # doc.add(Field('Num Votes', str(numVotes), contextType))
        doc.add(Field('directors_names', str(directorsNames), contextType))
        doc.add(Field('writer_names', str(writerNames), contextType))
        writer.addDocument(doc)
    writer.close()

def retrieve(storedir, field, keyword):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser(field, StandardAnalyzer())
    parsed_query = parser.parse(keyword)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            # "Tconst": doc.get("Tconst"),
            # "Ordering": doc.get("Ordering"),
            "title": doc.get("title"),
            "synopsis": doc.get("synopsis"),
            "region": doc.get("region"),
            # "Language": doc.get("Language"),
            # "Types": doc.get("Types"),
            # "Attributes": doc.get("Attributes"),
            # "Is Original Title": doc.get("Is Original Title"),
            # "Title Type": doc.get("Title Type"),
            # "Primary Title": doc.get("Primary Title"),
            # "Original Title": doc.get("Original Title"),
            # "Is Adult": doc.get("Is Adult"),
            "start_year": doc.get("start_year"),
            # "End Year": doc.get("End Year"),
            # "Runtime Minutes": doc.get("Runtime Minutes"),
            "genres": doc.get("genres"),
            # "Directors": doc.get("Directors"),
            # "Writers": doc.get("Writers"),
            # "Average Rating": doc.get("Average Rating"),
            # "Num Votes": doc.get("Num Votes"),
            "directors_names": doc.get("directors_names"),
            "writer_names": doc.get("writer_names")
        })
    
    print(topkdocs)


lucene.initVM(vmargs=['-Djava.awt.headless=true'])
json_data = parse_json('test.json')

# Index the data
index_startTime = time.time()
create_index(json_data ,'imdb_lucene_index/')
index_endTime = time.time()
index_runTime = index_endTime - index_startTime
print(f"Indexing Run Time: {round(index_runTime, 3)} seconds")

# Checking to make sure a search query is provided.
if len(sys.argv) <= 1:
    print("Please enter a search query in the format 'Field:\"keyword\"'.")
    sys.exit(1)

query_arg = sys.argv[1]
# Checking for the right format of the query
if ":" not in query_arg:
    print("Please enter a search query in the format 'Field:\"keyword\"'.")
    sys.exit(1)

# Extracting field and keyword from the query
field, keyword = query_arg.split(":", 1)
keyword = keyword.strip('"')

search_startTime = time.time()
retrieve('imdb_lucene_index/', field, keyword)
search_endTime = time.time()
search_runTime = index_endTime - index_startTime
print(f"Search Run Time: {round(search_runTime, 3)} seconds")