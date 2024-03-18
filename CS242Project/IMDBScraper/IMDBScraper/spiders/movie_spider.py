import scrapy
from scrapy import Spider, Request
import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

# REFERENCES: https://doc.scrapy.org/en/latest/intro/tutorial.html#following-links
# https://docs.scrapy.org/en/latest/topics/practices.html

class Product(scrapy.Item):
    title = scrapy.Field()
    plot = scrapy.Field()
    ratings = scrapy.Field()
    director = scrapy.Field()
    writers = scrapy.Field()
    stars = scrapy.Field()
    genre = scrapy.Field()
    img = scrapy.Field()
    synopsis = scrapy.Field()
    url = scrapy.Field()
    descriptors = scrapy.Field() # will usually contain: type (other than movie), PG rating, release year, etc

# EX: scrapy crawl movie_spider -o results.json OR scrapy crawl movie_spider -o results1.json -a start=120737 -a delta=2
# starts from https://www.imdb.com/title/tt0120737/ and goes up
class movie_spider(Spider):
    name = "movie_spider"
    custom_settings = {
		'FEED': { 'result_%(storage_file_num)s.json': { 'format': 'json'}}
		}
    # doing 57692 first
    # START = 120737
    # DELTA = 2
    # start_urls = ["https://www.imdb.com/title/tt%07d/?ref_=chttp_i_3" % ID for ID in range(START, START+DELTA)]

    def __init__(self, start=None, delta=None, *args, **kwargs):
        super(movie_spider, self).__init__(*args, **kwargs)
        COUNT = 1 # CHANGE THIS TO INCREMENT START POSITION
        DELTA = int(delta)
        START = int(start)+DELTA*COUNT
        self.start_urls = ["https://www.imdb.com/title/tt%07d/?ref_=chttp_i_3" % ID for ID in range(START, START+DELTA)]
        # self.storage_file_num = str(START) + "_" + str(COUNT)

    def parse(self,response):
        m = Product()
        m["title"] = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
        m["plot"] = response.xpath("//p[@data-testid='plot']/span[1]/text()").extract()
        m["ratings"] = response.xpath("//div[@data-testid='hero-rating-bar__aggregate-rating__score']/span/text()").extract_first()
        m["director"] = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[1]/div/ul/li/a/text()").extract()
        m["writers"] = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[2]/div/ul//li/a/text()").extract()
        m["stars"] = response.xpath("//div[@data-testid='title-cast-item']/div[2]/a/text()").extract()
        m["img"] = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a/@href").extract()
        m["descriptors"] = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul//li/a/text()").extract()
        m["url"] = response.request.url
        yield response.follow(response.url + "plotsummary", callback=self.parse_summary, dont_filter=True, meta={"item":m})

    def parse_summary(self, response):
        item_data = response.meta["item"]
        try:
            item_data["synopsis"] = response.xpath("//div[@class='ipc-html-content-inner-div']/text()").getall()[1:] #Also includes synopsis but ignores the short summary already grabbed
        except:
            item_data["synopsis"] = ""
        yield item_data

    def close(self, reason):
        print("\n=======================================")
        start_time = self.crawler.stats.get_value('start_time')
        finish_time = datetime.datetime.now(datetime.timezone.utc)
        print("Total run time: ", finish_time-start_time)
        print("Total movies parsed: ", self.crawler.stats.get_value('item_scraped_count'))
        print("\n=======================================")

# process = CrawlerProcess(get_project_settings())
# process.crawl("movie_spider", start=120737, delta=5)
# process.start()  # the script will block here until the crawling is finished
# print("----------------------FINISHED")

# # EX: scrapy crawl old_movie_spider -o result.json
# # first crawls start_urls for links, then goes through every link and gets movie attributes
# class old_movie_spider(Spider):
#     name = "old_movie_spider"
#     start_urls = ["https://www.imdb.com/chart/top?ref_=nv_mv_250"]
    
#     def parse(self,response):
#         yield from response.follow_all(xpath="//*[contains(@class, 'cli-title')]/a/@href", callback=self.parse_movie_link)

#     def parse_movie_link(self,response):
#         title = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
#         plot = response.xpath("//p[@data-testid='plot']/span[1]/text()").extract()
#         # synopsis = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
#         ratings = response.xpath("//div[@data-testid='hero-rating-bar__aggregate-rating__score']/span/text()").extract_first()
#         director = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[1]/div/ul/li/a/text()").extract()
#         writers = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[2]/div/ul//li/a/text()").extract()
#         stars = response.xpath("//div[@data-testid='title-cast-item']/div[2]/a/text()").extract()
#         # genres = response.xpath("//*[@data-testid='storyline-genres']/div/ul//li/a/text()").extract()
#         img = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a/@href").extract()
        
#         yield {
#             "title": title, 
#             "plot" : plot,
#             # "synopsis" : synopsis,
#             "ratings" : ratings,
#             "director": director,
#             "writers": writers,
#             "stars": stars,
#             # "genres": genres,
#             "img" : img
#         }

# # EX: scrapy crawl test_spider -o test_result.json
# # Currently set to crawl one movie (dark knight) to see if parsing correct data
# class test_spider(Spider):
#     name = "test_spider"
#     start_urls = ["https://www.imdb.com/title/tt0468569/?ref_=chttp_i_3"]
    
#     def parse(self,response):
#         title = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
#         plot = response.xpath("//p[@data-testid='plot']/span[1]/text()").extract()
#         # synopsis = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
#         ratings = response.xpath("//div[@data-testid='hero-rating-bar__aggregate-rating__score']/span/text()").extract_first()
#         director = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[1]/div/ul/li/a/text()").extract()
#         writers = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[2]/div/ul//li/a/text()").extract()
#         stars = response.xpath("//div[@data-testid='title-cast-item']/div[2]/a/text()").extract()
#         # genres = response.xpath("//*[@data-testid='storyline-genres']/div/ul//li/a/text()").extract()
#         img = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a/@href").extract()
        
#         yield {
#             "title": title, 
#             "plot" : plot,
#             # "synopsis" : synopsis,
#             "ratings" : ratings,
#             "director": director,
#             "writers": writers,
#             "stars": stars,
#             # "genres": genres,
#             "img" : img
#         }

#     def parse_movie(self,response):
#         test = response.xpath("//h1/text()").extract()
#         yield {
#             "test": test
#         }

#     def close(self, reason):
#         print("\n=======================================")
#         start_time = self.crawler.stats.get_value('start_time')
#         finish_time = datetime.datetime.now(datetime.timezone.utc)
#         print("Total run time: ", finish_time-start_time)
#         print("\n=======================================")

# # EX: scrapy crawl test_spider2 -o test_result2.json
# # Currently set to crawl old movies in range to see if parsing correct data
# class test_spider2(Spider):
#     name = "test_spider2"
#     start_urls = ["https://www.imdb.com/title/tt%07d/?ref_=chttp_i_3" % ID for ID in range(3000)]
    
#     def parse(self,response):
#         title = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
#         plot = response.xpath("//p[@data-testid='plot']/span[1]/text()").extract()
#         # synopsis = response.xpath("//span[contains(@class, 'hero__primary-text')]/text()").extract()
#         ratings = response.xpath("//div[@data-testid='hero-rating-bar__aggregate-rating__score']/span/text()").extract_first()
#         director = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[1]/div/ul/li/a/text()").extract()
#         writers = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[2]/div/ul//li/a/text()").extract()
#         stars = response.xpath("//div[@data-testid='title-cast-item']/div[2]/a/text()").extract()
#         # genres = response.xpath("//*[@data-testid='storyline-genres']/div/ul//li/a/text()").extract()
#         img = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a/@href").extract()
#         url = response.request.url
#         yield {
#             "url" : url,
#             "title": title, 
#             "plot" : plot,
#             # "synopsis" : synopsis,
#             "ratings" : ratings,
#             "director": director,
#             "writers": writers,
#             "stars": stars,
#             # "genres": genres,
#             "img" : img
#         }

#     def close(self, reason):
#         print("\n=======================================")
#         start_time = self.crawler.stats.get_value('start_time')
#         finish_time = datetime.datetime.now(datetime.timezone.utc)
#         print("Total run time: ", finish_time-start_time)
#         print("\n=======================================")

# class Product(scrapy.Item):
#     #pos = scrapy.Field()
#     title = scrapy.Field()
#     plot = scrapy.Field()
#     ratings = scrapy.Field()
#     director = scrapy.Field()
#     writers = scrapy.Field()
#     stars = scrapy.Field()
#     genre = scrapy.Field()
#     img = scrapy.Field()
#     synopsis = scrapy.Field()
#     url = scrapy.Field()
#     descriptors = scrapy.Field() # will usually contain: type (other than movie), PG rating, release year, etc


# EX: scrapy crawl list_spider -o list_result.json
class list_spider(Spider):
    name = "list_spider"
    start_urls = ["https://m.imdb.com/list/ls502982263/"]
    
    def parse_summary(self, response):
        item_data = response.meta["item"]
        try:
            item_data["synopsis"] = "".join(response.xpath("//div[@class='ipc-html-content-inner-div']/text()").getall()[1:]) #Also includes synopsis but ignores the short summary already grabbed
        except:
            item_data["synopsis"] = ""
        yield item_data

    def parse_indiv(self, response):
        m = response.meta["item"]
        try:
            m["plot"] = response.xpath("//p[@data-testid='plot']/span[3]/text()").extract()
        except:
            try:
                m["plot"] = response.xpath("//p[@data-testid='plot']/span[2]/text()").extract()
            except:
                try:
                    m["plot"] = response.xpath("//p[@data-testid='plot']/span[1]/text()").extract()
                except:
                    m["plot"] = ""
        try:
            m["ratings"] = response.xpath("//div[@data-testid='hero-rating-bar__aggregate-rating__score']/span/text()").extract_first()
        except:
            m["ratings"] = ""

        try:
            m["director"] = response.xpath("/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[2]/div[2]/div/div/div/ul/li[1]/div/text()").extract()
        except:
            m["director"] = ""
        

        try:
            m["writers"] = response.xpath("//*[@id='__next']/main/div/section[1]/div/section/div/div[1]/section[4]/ul/li[2]/div/ul//li/a/text()").extract()
        except: 
            m["writers"] = ""

        try:
            m["stars"] = response.xpath("//div[@data-testid='title-cast-item']/div[2]/a/text()").extract()
        except:
            m["stars"] = ""

        try:
            m["img"] = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[3]/div[1]/div[1]/div/a/@href").extract()
        except:
            m["img"] = ""
        m["img"] = "https://m.imdb.com" + "".join(m["img"])

        try:
            m["descriptors"] = response.xpath("//*[@id='__next']/main/div/section[1]/section/div[3]/section/section/div[2]/div[1]/ul//li/a/text()").extract()
        except:
            m["descriptors"] = ""

        try:
            m["url"] = response.request.url
        except:
            m["url"] = ""
        yield response.follow(response.url + "plotsummary", callback=self.parse_summary, dont_filter=True, meta={"item":m})

    def parse(self,response):
        for movie in response.css("div.media"):
            m = Product()
            #m["pos"] = movie.xpath("a/span/span[@class='h4 unbold']/text()").get()
            m["title"]= movie.xpath("a/span/span[@class='h4']/text()").get()
            try:
                m["genre"] = movie.xpath("a/span/span[contains(@class, 'cert-and-genres')]/p/span[@class='genre']/text()").get().replace("\n", "").strip()
            except:
                m["genre"] = ""
            yield response.follow("https://m.imdb.com/title/" + movie.xpath("span/@data-tconst").get(), callback=self.parse_indiv, dont_filter=True, meta={"item":m})            

        next_page = response.xpath("//div[contains(@class, 'list-pagination')]/a[contains(@class, 'next-page')]/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
    
    def close(self, reason):
        print("\n=======================================")
        start_time = self.crawler.stats.get_value('start_time')
        finish_time = datetime.datetime.now(datetime.timezone.utc)
        print("Total run time: ", finish_time-start_time)
        print("Total movies parsed: ", self.crawler.stats.get_value('item_scraped_count'))
        print("\n=======================================")