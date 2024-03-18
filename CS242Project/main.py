import scrapy
from scrapy import Spider, Request
from scrapy.utils.defer import maybe_deferred_to_future
from twisted.internet.defer import DeferredList

class MultipleRequestsSpider(Spider):
    name = "multiple"
    start_urls = ["https://example.com/product"]
    def parse(self,response):
      yield {
          "h1": response.css("h1::text").get()
      }

    # async def parse(self, response, **kwargs):
    #     additional_requests = [
    #         Request("https://example.com/price"),
    #         Request("https://example.com/color"),
    #     ]
    #     deferreds = []
    #     for r in additional_requests:
    #         deferred = self.crawler.engine.download(r)
    #         deferreds.append(deferred)
    #     responses = await maybe_deferred_to_future(DeferredList(deferreds))
    #     yield {
    #         "h1": response.css("h1::text").get(),
    #         "price": responses[0][1].css(".price::text").get(),
    #         "price2": responses[1][1].css(".color::text").get(),
    #     }
