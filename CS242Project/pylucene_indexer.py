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
        tconst = movie['tconst']
        title = movie['title']
        synopsis = movie['synopsis']
        region = movie['region']
        startYear = movie['startYear']
        genres = movie['genres']
        directorsNames = movie['directors Names']
        writerNames = movie['writer Names']

        doc = Document()
        doc.add(Field('tconst', str(tconst), contextType))
        doc.add(Field('title', str(title), contextType))
        doc.add(Field('synopsis', str(synopsis), contextType))
        doc.add(Field('region', str(region), contextType))
        doc.add(Field('start_year', str(startYear), contextType))
        doc.add(Field('genres', str(genres), contextType))
        doc.add(Field('directors_names', str(directorsNames), contextType))
        doc.add(Field('writer_names', str(writerNames), contextType))
        writer.addDocument(doc)
    writer.close()

lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Parse in the json data file
filepath = sys.argv[1]
with open(filepath, 'r') as file:
    json_data = json.load(file)

# Index the data
index_startTime = time.time()
create_index(json_data ,'imdb_lucene_index/')
index_endTime = time.time()
index_runTime = index_endTime - index_startTime
print(f"Indexing Run Time: {round(index_runTime, 3)} seconds")