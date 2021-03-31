import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BohItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BohSpider(scrapy.Spider):
	name = 'boh'
	start_urls = ['https://www.boh.com/newsroom?page=1']

	def parse(self, response):
		post_links = response.xpath('//a[@data-analytics-dcr-identifier="readMore"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@aria-label="Next page"]/@href').get()
		if post_links:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="date-stamp"]//text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="col-md-8"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BohItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
