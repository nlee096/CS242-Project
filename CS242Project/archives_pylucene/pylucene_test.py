import logging, sys
logging.disable(sys.maxsize)

import lucene
import os
from org.apache.lucene.store import MMapDirectory, SimpleFSDirectory, NIOFSDirectory
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, DirectoryReader
from org.apache.lucene.search import IndexSearcher, BoostQuery, Query
from org.apache.lucene.search.similarities import BM25Similarity

sample_doc = [
    {
        "tconst": "tt0000005",
        "ordering": 10,
        "title": "Blacksmith Scene",
        "region": "US",
        "language": "\\N",
        "types": "imdbDisplay",
        "attributes": "\\N",
        "isOriginalTitle": "0",
        "titleType": "short",
        "primaryTitle": "Blacksmith Scene",
        "originalTitle": "Blacksmith Scene",
        "isAdult": 0,
        "startYear": "1893",
        "endYear": "\\N",
        "runtimeMinutes": "1",
        "genres": "Comedy,Short",
        "directors": "nm0005690",
        "writers": "\\N",
        "averageRating": 6.2,
        "numVotes": 2722,
        "directors Names": [
            "William K.L. Dickson"
        ],
        "writer Names": []
    },
    {
        "tconst": "tt0000022",
        "ordering": 1,
        "title": "The Blacksmiths",
        "region": "US",
        "language": "\\N",
        "types": "\\N",
        "attributes": "literal English title",
        "isOriginalTitle": "0",
        "titleType": "short",
        "primaryTitle": "Blacksmith Scene",
        "originalTitle": "Les forgerons",
        "isAdult": 0,
        "startYear": "1895",
        "endYear": "\\N",
        "runtimeMinutes": "1",
        "genres": "Documentary,Short",
        "directors": "nm0525910",
        "writers": "\\N",
        "averageRating": 5.1,
        "numVotes": 1124,
        "directors Names": [
            "Louis Lumi\u00e8re"
        ],
        "writer Names": []
    },
    {
        "tconst": "tt0000029",
        "ordering": 10,
        "title": "Repas de b\u00e9b\u00e9",
        "region": "FR",
        "language": "\\N",
        "types": "imdbDisplay",
        "attributes": "\\N",
        "isOriginalTitle": "0",
        "titleType": "short",
        "primaryTitle": "Baby's Meal",
        "originalTitle": "Repas de b\u00e9b\u00e9",
        "isAdult": 0,
        "startYear": "1895",
        "endYear": "\\N",
        "runtimeMinutes": "1",
        "genres": "Documentary,Short",
        "directors": "nm0525910",
        "writers": "\\N",
        "averageRating": 5.9,
        "numVotes": 3466,
        "directors Names": [
            "Louis Lumi\u00e8re"
        ],
        "writer Names": []
    }
]

def create_index(dir):
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

    for sample in sample_doc:
        tconst = sample['tconst']
        ordering = sample['ordering']
        title = sample['title']
        region = sample['region']
        language = sample['language']
        types = sample['types']
        attributes = sample['attributes']
        isOriginalTitle = sample['isOriginalTitle']
        titleType = sample['titleType']
        primaryTitle = sample['primaryTitle']
        originalTitle = sample['originalTitle']
        isAdult = sample['isAdult']
        startYear = sample['startYear']
        endYear = sample['endYear']
        runtimeMinutes = sample['runtimeMinutes']
        genres = sample['genres']
        directors = sample['directors']
        writers = sample['writers']
        averageRating = sample['averageRating']
        numVotes = sample['numVotes']
        directorsNames = sample['directors Names']
        writerNames = sample['writer Names']

        doc = Document()
        doc.add(Field('Tconst', str(tconst), contextType))
        doc.add(Field('Ordering', str(ordering), contextType))
        doc.add(Field('Title', str(title), contextType))
        doc.add(Field('Region', str(region), contextType))
        doc.add(Field('Language', str(language), contextType))
        doc.add(Field('Types', str(types), contextType))
        doc.add(Field('Attributes', str(attributes), contextType))
        doc.add(Field('Is Original Title', str(isOriginalTitle), contextType))
        doc.add(Field('Title Type', str(titleType), contextType))
        doc.add(Field('Primary Title', str(primaryTitle), contextType))
        doc.add(Field('Original Title', str(originalTitle), contextType))
        doc.add(Field('Is Adult', str(isAdult), contextType))
        doc.add(Field('Start Year', str(startYear), contextType))
        doc.add(Field('End Year', str(endYear), contextType))
        doc.add(Field('Runtime Minutes', str(runtimeMinutes), contextType))
        doc.add(Field('Genres', str(genres), contextType))
        doc.add(Field('Directors', str(directors), contextType))
        doc.add(Field('Writers', str(writers), contextType))
        doc.add(Field('Average Rating', str(averageRating), contextType))
        doc.add(Field('Num Votes', str(numVotes), contextType))
        doc.add(Field('Directors Names', str(directorsNames), contextType))
        doc.add(Field('Writer Names', str(writerNames), contextType))
        writer.addDocument(doc)
    writer.close()

def retrieve(storedir, query):
    searchDir = NIOFSDirectory(Paths.get(storedir))
    searcher = IndexSearcher(DirectoryReader.open(searchDir))
    
    parser = QueryParser('Title', StandardAnalyzer())
    parsed_query = parser.parse(query)

    topDocs = searcher.search(parsed_query, 10).scoreDocs
    topkdocs = []
    for hit in topDocs:
        doc = searcher.doc(hit.doc)
        topkdocs.append({
            "score": hit.score,
            "Tconst": doc.get("Tconst"),
            "Ordering": doc.get("Ordering"),
            "Title": doc.get("Title"),
            "Region": doc.get("Region"),
            "Language": doc.get("Language"),
            "Types": doc.get("Types"),
            "Attributes": doc.get("Attributes"),
            "Is Original Title": doc.get("Is Original Title"),
            "Title Type": doc.get("Title Type"),
            "Primary Title": doc.get("Primary Title"),
            "Original Title": doc.get("Original Title"),
            "Is Adult": doc.get("Is Adult"),
            "Start Year": doc.get("Start Year"),
            "End Year": doc.get("End Year"),
            "Runtime Minutes": doc.get("Runtime Minutes"),
            "Genres": doc.get("Genres"),
            "Directors": doc.get("Directors"),
            "Writers": doc.get("Writers"),
            "Average Rating": doc.get("Average Rating"),
            "Num Votes": doc.get("Num Votes"),
            "Directors Names": doc.get("Directors Names"),
            "Writer Names": doc.get("Writer Names")
        })
    
    print(topkdocs)


lucene.initVM(vmargs=['-Djava.awt.headless=true'])
create_index('sample_lucene_index/')
retrieve('sample_lucene_index/', 'Blacksmith')