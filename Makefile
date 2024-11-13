.PHONY: lint format-code run parse-whole-fix-price get-available-cities

lint:
	mypy .

format-code:
	autoflake .; 
	isort .; 
	black .

run:
	cd fix_price_parser && scrapy crawl fix_price_spider -a city_id=55 -a categories_slugs=odezhda,produkty-i-napitki,dlya-doma/tovary-dlya-uborki,dlya-doma -O output.json

# parse-whole-fix-price:
# 	cd fix_price_parser && scrapy crawl fix_price_spider -a city_id=3 -a categories_slugs=vse-dlya-novogo-goda,pochti-darom,sad-i-ogorod,spets-tsena-po-karte,novinki,seychas-pokupayut,dlya-zdorovykh-nachinaniy,produkty-i-napitki,bytovaya-khimiya,igrushki,kosmetika-i-gigiena,krasota-i-zdorove,dlya-doma,dekor-dlya-doma-tovary-dlya-prazdnika,suveniry-i-podarki,kantstovary,knigi,avto-moto-velo,odezhda,aksessuary,sport-i-otdykh,dlya-zhivotnykh,meditsinskie-tovary,prazdnik-kruglyy-god -O whole_fix_price.json

get-available-cities:
	cd fix_price_parser && scrapy crawl available_cities_spider
