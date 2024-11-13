from typing import Any

from scrapy.spiders import Spider
from scrapy.http import Response
from tabulate import tabulate


class AvailableCitiesSpider(Spider):  # type: ignore[misc]
    name = "available_cities_spider"
    start_urls = ("https://api.fix-price.com/buyer/v1/location/city",)

    def parse(self, response: Response, **kwargs: Any) -> None:
        with open("available_cities.txt", "w", encoding="utf-8") as file:
            file.write(
                tabulate(
                    sorted(
                        ((city["name"], city["id"]) for city in response.json()), key=lambda city_and_id: city_and_id[0]  # type: ignore[index]
                    ),
                    headers=["City", "ID"],
                    tablefmt="grid",
                )
            )
