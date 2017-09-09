from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
from taller_1.scrapers.taller_1_g6_p1.spiders.uniandes_spider import Taller1G6P1
###from taller_1_g6_p1.spiders.uniandes_spider import Taller1G6P1

from pydispatch import dispatcher
from scrapy import signals

def spider_results():
	results = {}

	def crawler_results(item):
		results[item['facultad']] = [item['url'], item['fuente'], item['orden'], item['origen'], item['nivel']]
	
	spider = Taller1G6P1()
	settings = get_project_settings()
	#configure_logging()
	runner = CrawlerRunner(settings)
	
	d = runner.crawl(spider)
	dispatcher.connect(crawler_results, signal = signals.item_passed)
	d.addBoth(lambda _: reactor.stop())
	reactor.run()
	return results

def traer_facultades():
	return spider_results()
###if __name__ == "__main__":
###	print(spider_results())
