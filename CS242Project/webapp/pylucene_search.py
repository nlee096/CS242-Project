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

class search_pylucene_index():

    def retrieve(self, storedir, search_text, num_results):
        
        boost_val = None
        if "^" in search_text: # field/term boosting
            search_text, boost_str = search_text.rsplit("^", 1)
            boost_val = float(boost_str)
        if "start_year" in search_text and " TO " in search_text: # range search
            field, search_val = search_text.split(":", 1)
            search_val = search_val.strip('[')
            search_val = search_val.strip(']')
        else: # text search
            field, search_val = search_text.split(":", 1)
            search_val = search_val.strip('"')
        
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

        topDocs = searcher.search(parsed_query, num_results).scoreDocs

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
        
        return topkdocs