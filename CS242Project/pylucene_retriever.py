import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
import json
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.search import TermRangeQuery
from org.apache.lucene.search import WildcardQuery
from org.apache.lucene.search import BoostQuery
from org.apache.lucene.util import BytesRef

def retrieve(storedir, field, search_val, boost_val):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    if field == "start_year" and " TO " in search_val: # range search
        start, end = search_val.split(" TO ")
        parsed_query = TermRangeQuery(field, BytesRef(start.encode('utf-8')), BytesRef(end.encode('utf-8')), True, True)
    elif "*" in search_val: # wildcard search
        parser = QueryParser(field, StandardAnalyzer())
        parser.setAllowLeadingWildcard(True)
        parsed_query = parser.parse(search_val)
    else: # basic text search
        parser = QueryParser(field, StandardAnalyzer())
        parsed_query = parser.parse(search_val)

    if boost_val: # field/term boosting
        boost_query = BoostQuery(parsed_query, boost_val)
        parsed_query = boost_query

    topDocs = searcher.search(parsed_query, 5).scoreDocs

    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "tconst": doc.get("tconst"),
            "title": doc.get("title"),
            "synopsis": doc.get("synopsis"),
            "region": doc.get("region"),
            "start_year": doc.get("start_year"),
            "genres": doc.get("genres"),
            "directors_names": doc.get("directors_names"),
            "writer_names": doc.get("writer_names")
        })
    
    # print(topkdocs)
    
    for record in topkdocs:
        print("Score: ", record["score"])
        print("tconst: ", record["tconst"])
        print("Title: ", record["title"])
        print("Synopsis: ", record["synopsis"])
        print("Region: ", record["region"])
        print("Start Year: ", record["start_year"])
        print("Genres: ", record["genres"])
        print("Directors Names: ", record["directors_names"])
        print("Writer Names: ", record["writer_names"])
        print("\n")
    
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

# Checking to make sure a search query is provided.
if len(sys.argv) <= 1:
    print("Please enter a search query.")
    print("For a basic text search, enter a search query with the format 'field:\"search_val\"'.")
    print("For a range search on start_year, enter a search query with the format 'start_year:[YYYY TO YYYY]'.")
    print("For a wildcard search, enter a search query with the format 'field:*value*'.")
    print("For field/term boosting, add ^X.X after the search value.")
    sys.exit(1)

query_arg = ' '.join(sys.argv[1:])
# Checking for the right format of the query
if ":" not in query_arg:
    print("For a basic text search, enter a search query with the format 'field:\"search_val\"'.")
    print("For a range search on start_year, enter a search query with the format 'start_year:[YYYY TO YYYY]'.")
    print("For a wildcard search, enter a search query with the format 'field:*value*'.")
    print("For field/term boosting, add ^X.X after the search value.")
    sys.exit(1)

boost_val = None
if "^" in query_arg: # field/term boosting
    query_arg, boost_str = query_arg.rsplit("^", 1)
    boost_val = float(boost_str)

if "start_year" in query_arg and " TO " in query_arg: # range search
    field, search_val = query_arg.split(":", 1)
    search_val = search_val.strip('[')
    search_val = search_val.strip(']')
else: # text search
    field, search_val = query_arg.split(":", 1)
    search_val = search_val.strip('"')

retrieve('imdb_lucene_index/', field, search_val, boost_val)