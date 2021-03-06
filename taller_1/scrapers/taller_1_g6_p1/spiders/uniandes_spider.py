import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from taller_1.scrapers.taller_1_g6_p1.items import Taller1G6P1Item
###from taller_1_g6_p1.items import Taller1G6P1Item
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import re

class Taller1G6P1(CrawlSpider):
	name = 'Taller1G6P1'
	item_count = 0
	limite_paginas = 2000
	allowed_domains = ['uniandes.edu.co']
	start_urls = ['https://www.uniandes.edu.co/']
#Cada retorno me trae una lista con los elementos:
#Facultad: Es el campo de texto (no debio llamarse Facultad...)
#URL: URL a la que apunta (en caso de ser un enlace)
#Fuente: URL donde se encuentra
#Orden: Primary key del hallazgo en su nivel
#Origen: Primary keys de los elementos de donde provino, hasta la raiz
#Nivel: Nivel de profundidad en el arbol de las paginas web

	def parse(self, response): #punto de partida. Busco las unidades academicas
		v_orden = 1
		v_nivel = 1
		for pag in response.xpath('//div[contains(@class, "menu-ppal")]//ul[contains(@class, "dropdown-menu")]/li[contains(@class, "leaf")]'):
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			base = response.url[:response.url.find("/", 8)]
			url = base + pag.xpath('.//a/@href').extract_first() if pag.xpath('.//a/@href').extract_first()[:1] == '/' else pag.xpath('.//a/@href').extract_first()
			if 'Listado de ' in pag.xpath('.//a/text()').extract_first().strip():
				facultad['facultad'] = pag.xpath('.//a/text()').extract_first().strip()
				facultad['url'] = url
				facultad['fuente'] = response.url
				facultad['orden'] = str(v_orden)
				facultad['origen'] = 0
				facultad['nivel'] = v_nivel
				yield facultad
				#url = urlparse.urljoin(response.url, url)
				yield scrapy.Request(url, callback = self.filtrar_facultades, meta = { 'origen': str(v_orden), 'nivel': v_nivel })
				v_orden += 1
			if 'Directivos' in pag.xpath('.//a/text()').extract_first().strip():
				facultad['facultad'] = pag.xpath('.//a/text()').extract_first().strip()
				facultad['url'] = url
				facultad['fuente'] = response.url
				facultad['orden'] = str(v_orden)
				facultad['origen'] = 0
				facultad['nivel'] = v_nivel
				yield facultad
				#url = urlparse.urljoin(response.url, url)
				yield scrapy.Request(url, callback = self.filtrar_directivos, meta = { 'origen': str(v_orden), 'nivel': v_nivel })
				v_orden += 1

	def filtrar_directivos(self, response): #busco los directivos
		v_orden = 1
		v_origen = response.meta['origen']
		v_nivel = response.meta['nivel'] + 1
		for pag in response.xpath('//div[contains(@class, "field-item")]//tr'):
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			base = response.url[:response.url.find("/", 8)]
			facultad['facultad'] = ': '.join(pag.xpath('.//td[(not(@colspan) or @colspan!="2")]/text()').extract()).strip()
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1

	def filtrar_facultades(self, response): #busco las facultades y los departamentos
		v_orden = 1
		v_origen = response.meta['origen']
		v_nivel = response.meta['nivel'] + 1
		for pag in response.xpath('//div[contains(@class, "view-vista-lista-departamentos")]//ul/li[contains(@class, "views-row")]'):
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			base = response.url[:response.url.find("/", 8)]
			url = base + pag.xpath('.//a/@href').extract_first() if pag.xpath('.//a/@href').extract_first()[:1] == '/' else pag.xpath('.//a/@href').extract_first()
			facultad['facultad'] = pag.xpath('.//span[@class="field-content"]/text()').extract_first().strip()
			facultad['url'] = url
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			yield scrapy.Request(url, callback = self.filtrar_noticias, meta = { 'origen': str(v_origen) + '-' + str(v_orden), 'nivel': v_nivel })
			v_orden += 1

	def filtrar_noticias(self, response): #busco las noticias - Hay varias reglas. Tantas como pudimos meter
		v_orden = 1
		v_origen = response.meta['origen']
		v_nivel = response.meta['nivel'] + 1
		for pag in response.xpath('//a'): #busco los enlaces a las listas de profesores
			base = response.url[:response.url.find("/", 8)]
			texto_url = pag.xpath('.//text()').extract_first()
			if texto_url is not None and 'profesores' in texto_url.lower():
				url = base + pag.xpath('./@href').extract_first() if pag.xpath('./@href').extract_first()[:1] == '/' else pag.xpath('./@href').extract_first()
				texto_url = pag.xpath('.//text()').extract_first()
				yield scrapy.Request(url, callback = self.filtrar_profesores, meta = { 'origen': str(v_origen), 'nivel': v_nivel })
		for pag in response.xpath('//div[contains(@class, "noticia-list")]//a[contains(@class, "item-nl")]'): #facultad de ingenieria
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			fecha_noticia = '<b>NOTICIA: </b>' + pag.xpath('.//div[contains(@class, "date-nl")]/p/text()').extract_first().strip()
			titulo_noticia = pag.xpath('.//div[contains(@class, "info-nl")]//p/text()').extract_first().strip()
			facultad = Taller1G6P1Item()
			facultad['facultad'] = fecha_noticia + ': ' + titulo_noticia
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1
		for pag in response.xpath('//div[contains(@class, "moduleItemIntrotext")]'): #facultad de administracion
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			titulo_noticia = '<b>NOTICIA: </b>' + pag.xpath('./following-sibling::a[1]/text()').extract_first().strip()
			descr_noticia = pag.xpath('./following-sibling::div/p/text()').extract_first()
			if descr_noticia is None:
				descr_noticia = '...'
			facultad = Taller1G6P1Item()
			facultad['facultad'] = titulo_noticia + ': ' + descr_noticia
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1
		for pag in response.xpath('//section[contains(@class, "noticias")]//ul/li'): #facultad de artes
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			descr_noticia = pag.xpath('./h3/text()').extract_first()
			if descr_noticia is None:
				descr_noticia = '...'
			else:
				descr_noticia = '<b>NOTICIA: </b>' + descr_noticia.replace('\r', '').replace('\n', '').strip()
			facultad['facultad'] = descr_noticia
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1
		for pag in response.xpath('//div[contains(@class, "noticias_home")]//p'): # facultad de medicina
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			descr_noticia = pag.xpath('./text()').extract_first()
			if descr_noticia is None:
				descr_noticia = '...'
			else:
				descr_noticia = descr_noticia.replace('\r', '').replace('\n', '').strip()
			if descr_noticia is not '...' and descr_noticia is not '':
				facultad['facultad'] = '<b>NOTICIA: </b>' + descr_noticia
				facultad['url'] = ''
				facultad['fuente'] = response.url
				facultad['orden'] = v_orden
				facultad['origen'] = str(v_origen)
				facultad['nivel'] = v_nivel
				yield facultad
				v_orden += 1
		for pag in response.xpath('//a[contains(@class, "noticia-info")]'): #cider
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			descr_noticia = pag.xpath('.//p[contains(@class, "texto")]/text()').extract_first()
			if descr_noticia is None:
				descr_noticia = '...'
			else:
				descr_noticia = descr_noticia.replace('\r', '').replace('\n', '').strip()
			if descr_noticia != '...':
				facultad['facultad'] = '<b>NOTICIA: </b>' + descr_noticia
				facultad['url'] = ''
				facultad['fuente'] = response.url
				facultad['orden'] = v_orden
				facultad['origen'] = str(v_origen)
				facultad['nivel'] = v_nivel
				yield facultad
				v_orden += 1
		for pag in response.xpath('//ul[contains(@class, "sprocket-lists-container")]/li'): #depto sistemas
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			descr_noticia = pag.xpath('./h4/text()').extract_first()
			if descr_noticia is None:
				descr_noticia = '...'
			else:
				descr_noticia = descr_noticia.replace('\r', '').replace('\n', '').strip()
			if descr_noticia != '...':
				facultad['facultad'] = '<b>NOTICIA: </b>' + descr_noticia
				facultad['url'] = ''
				facultad['fuente'] = response.url
				facultad['orden'] = v_orden
				facultad['origen'] = str(v_origen)
				facultad['nivel'] = v_nivel
				yield facultad
				v_orden += 1
		for pag in response.xpath('//div[contains(@class, "nspArt")]'): #depto electrica
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			descr_noticia = pag.xpath('.//p[contains(@class, "nspText")]/text()').extract_first()
			if descr_noticia is None:
				descr_noticia = '...'
			else:
				descr_noticia = descr_noticia.replace('\r', '').replace('\n', '').strip()
			if descr_noticia != '...':
				facultad['facultad'] = '<b>NOTICIA: </b>' + descr_noticia
				facultad['url'] = ''
				facultad['fuente'] = response.url
				facultad['orden'] = v_orden
				facultad['origen'] = str(v_origen)
				facultad['nivel'] = v_nivel
				yield facultad
				v_orden += 1

	def filtrar_profesores(self, response): #busco los profesores de las facultades y departamentos
		v_orden = 1000
		v_origen = response.meta['origen']
		v_nivel = response.meta['nivel']
		for pag in response.xpath('//div[contains(@class, "span8")]'): #profesores sistemas
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			descr_prof = pag.xpath('.//div[contains(@class, "sp-block")]//a/text()').extract_first()
			mail_prof = pag.xpath('.//a/@href').extract_first()
###			texto_prof = '. '.join(pag.xpath('//*[not(contains(@href, "tab")) and not(self::script)]/text()').extract())
			if descr_prof is None:
				descr_prof = '...'
			else:
				descr_prof = descr_prof.replace('\r', '').replace('\n', '').strip()
			if mail_prof is None:
				mail_prof = '...'
			else:
				mail_prof = mail_prof.replace('\r', '').replace('\n', '').strip()
			if descr_prof != '...':
				facultad['facultad'] = '<b>PROFESOR: </b>' + descr_prof + ' (' + mail_prof + ')'
				facultad['url'] = ''
				facultad['fuente'] = response.url
				facultad['orden'] = v_orden
				facultad['origen'] = str(v_origen)
				facultad['nivel'] = v_nivel
				yield facultad
				v_orden += 1
		for pag in response.xpath('//div[contains(@class, "infoProfesor")]'): #profesores economia
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			profesor = '. '.join(pag.xpath('.//*[contains(@class, "Profesor") and not(contains(@class, "Profesores"))]/text()').extract())
			profesor = profesor.replace('\r', '').replace('\n', '').replace('\t', '').strip()
			facultad['facultad'] = '<b>PROFESOR: </b>' + profesor
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1
		for pag in response.xpath('//div[contains(text(), "Profesores de planta")]/following-sibling::ul[contains(@class, "listTeamContentEO")]'): #profesores CIDER
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			profesor = ': '.join(pag.xpath('.//*[not(self::a)]/text()').extract()[1:])
			profesor = profesor.replace('\r', '').replace('\n', '').replace('\t', '').strip()
			facultad['facultad'] = '<b>PROFESOR: </b>' + profesor
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1
		for pag in response.xpath('//table[contains(@id, "professor-list")]//tr/td[contains(@class, "sorting_1")]'): #profesores administracion
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			profesor = ': '.join(pag.xpath('./p//text()').extract()).strip()
			profesor = profesor.replace('\r', '').replace('\n', '').replace('\t', '').strip()
			facultad['facultad'] = '<b>PROFESOR: </b>' + profesor
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1
		for pag in response.xpath('//div[contains(@id, "wsp-container")]'): #profesores ciencias biologicas
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			profesor = ': '.join(pag.xpath('.//div[contains(@class, "element")]//text()').extract()).strip()
			profesor = profesor.replace('\r', '').replace('\n', '').replace('\t', '').strip()
			facultad['facultad'] = '<b>PROFESOR: </b>' + profesor
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1

		for pag in response.xpath('//div[contains(@class, "uk-panel-space")]'): #profesores facultad de educacion
			self.item_count += 1
			if self.item_count > self.limite_paginas:
				raise CloseSpider('demasiadas_paginas')
			facultad = Taller1G6P1Item()
			profesor = ': '.join(pag.xpath('.//text()').extract()).strip()
			profesor = profesor.replace('\r', '').replace('\n', '').replace('\t', '').strip()
			facultad['facultad'] = '<b>PROFESOR: </b>' + profesor
			facultad['url'] = ''
			facultad['fuente'] = response.url
			facultad['orden'] = v_orden
			facultad['origen'] = str(v_origen)
			facultad['nivel'] = v_nivel
			yield facultad
			v_orden += 1


