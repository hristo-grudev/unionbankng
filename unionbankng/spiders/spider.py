import scrapy

from scrapy.loader import ItemLoader

from ..items import UnionbankngItem
from itemloaders.processors import TakeFirst


class UnionbankngSpider(scrapy.Spider):
	name = 'unionbankng'
	start_urls = ['https://www.unionbankng.com/blog/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="details-inner"]')
		for post in post_links:
			url = post.xpath('.//h3/a/@href').get()
			date = post.xpath('.//time/text()[normalize-space()]').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//li[@class="next"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@itemprop="articleBody"]//text()[normalize-space() and not(descendant-or-self::div)]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=UnionbankngItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
