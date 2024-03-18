# CS242Project
# Instruction on how to deploy the crawler
The scrapy spiders implemented do not read from and add to existing json files. Instead it executes the entire job in one session. To execute the movie list spider, cd to the IMDBScraper folder, then run: ‘scrapy crawl list_spider -o <filename>.json’. This will deploy the spider and scrape the movie data of TOP 5000 FILMS (2021 UPDATE) movie list that has 6,329 titles.
  
To execute the ID iterator spider, cd to the IMDBScraper folder, then run: ‘scrapy crawl movie_spider -o <filename>.json -a start=120737 -a delta=5000’. This was the exact command used to get the scraped ID dataset. If needed the ‘start’ variable can be modified to provide a different starting ID, while the ‘delta’ variable can be modified to provide a different range to parse movies from (scraper goes from start - (start+delta))

# Instruction on how to build the PyLucene index.
To build the PyLucene index, we created an executable file called indexbuilder.sh to run the command, while also checking whether the file path is correct and the input file exists.
we run the executable file indexbuilder.sh with the following command: ./indexbuilder.sh <filepath/input_data_file>  
If ran successfully, the indexed data will be created in a folder called “imdb_lucene_index” in the same directory as the indexbuilder.sh file, and we can perform search queries on that data.  
Note that the json file we are using as input is the "cleaned" json which relies on the IMDB public dataset. Make sure to use the given input file rather than just using the direct output of the scraper.
