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

retrieve('imdb_lucene_index/', field, keyword)