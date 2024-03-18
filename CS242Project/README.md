# CS242Project
# Instruction on how to deploy the crawler
The scrapy spiders implemented do not read from and add to existing json files. Instead it executes the entire job in one session. To execute the movie list spider, cd to the IMDBScraper folder, then run: ‘scrapy crawl list_spider -o <filename>.json’. This will deploy the spider and scrape the movie data of TOP 5000 FILMS (2021 UPDATE) movie list that has 6,329 titles.
  
To execute the ID iterator spider, cd to the IMDBScraper folder, then run: ‘scrapy crawl movie_spider -o <filename>.json -a start=120737 -a delta=5000’. This was the exact command used to get the scraped ID dataset. If needed the ‘start’ variable can be modified to provide a different starting ID, while the ‘delta’ variable can be modified to provide a different range to parse movies from (scraper goes from start - (start+delta))

# Instruction on how to build the PyLucene index.
To build the PyLucene index, we created an executable file called indexbuilder.sh to run the command, while also checking whether the file path is correct and the input file exists.
we run the executable file indexbuilder.sh with the following command: ./indexbuilder.sh <filepath/input_data_file>  
If ran successfully, the indexed data will be created in a folder called “imdb_lucene_index” in the same directory as the indexbuilder.sh file, and we can perform search queries on that data.  
Note that the json file we are using as input is the "cleaned" json which relies on the IMDB public dataset. Make sure to use the given input file rather than just using the direct output of the scraper.

# Instruction on how to perform search queries in PyLucene.
- After building the index, we will have a folder called “imdb_lucene_index”. 
- To perform queries, we run the file pylucene_retriever.py.  
- We have implemented the following query semantics: Basic query, Range search, Wildcard search, Field/term boosting.
- Commands to perform queries on the indexed data:
  - Basic query: python3 pylucene_retriever.py field:”search_value”
  - Range search: python3 pylucene_retriever.py start_year:[YYYY TO YYYY]
  - Wildcard search: python3 pylucene_retriever.py field:*value*
  - Field/term boosting: add ^X.X after the search value

# Instruction on how to Build the BERT Index
Open the BERT_FAISS_indexer.py file and scroll down to the bottom. 
There are several examples of how to run the BERT_indexer class; for running the indexer for a json dataset file, do the following:
- Uncomment out lines 154 - 157, comment out all lines below 157 that are unneeded
- Change the indexer.read_json() parameter to the file path of a json file (our dataset, 'CS242 Final Combined IMDB Dataset (nulls replaced).json',  is already there by default)
- Change the indexer.write_index() parameter to an index filename
- Run the code, the indexer will take time to create an index and write it out to your specified filename
Alternatively, we have created a bertBuilder.sh file that uses our sample dataset and indexes it and tosses the index in the webapp folder so you can simply jump into the webapp folder and run the webapp. To run bertBuilder simply do “bertBuilder.sh input_file.json”.

# Instruction on How to Perform Search Queries in the BERT Index 
Run search without using the webapp:
- Open the BERT_FAISS_indexer.py file and scroll down to the bottom
- Underneath lines 171, there are several examples of how to use the search_index class for searching, you can modify any of them for your purposes
- Change the search_index.read_index() input parameter to an index file of your choice (ours chosen by default)
- Change the “f = open('CS242 Final Combined IMDB Dataset (nulls replaced).json')” line to be the JSON file that your index file matches (using ours by default)
- Change query_string variable to a string that you want to search before running
  - Alternatively, you can uncomment out “query_string = input("Enter a search query: ")” and run the file, the program will prompt you in the command line for a search query
- Run the file, your results will be printed out

# Instruction on How to Deploy System(PREFERRED)
Instructions for how to Run webapp (With BERT and PyLucene) to search with BERT(Preferred method to test search on both indexers):
- cd webapp
- python3 webapp.py
- Open webpage ip:8080
- Select BERT/PyLucene as option and type string into textbox
- Submit and get results as DataFrame
