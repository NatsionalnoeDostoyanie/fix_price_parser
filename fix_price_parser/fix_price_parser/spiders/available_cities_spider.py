from typing import Any

from scrapy.spiders import Spider
from scrapy.http import Response
from tabulate import tabulate


class AvailableCitiesSpider(Spider):  # type: ignore[misc]
    """
    Spider for fetching and formatting available cities infi from the FixPrice API.

    This spider sends a request to the FixPrice API to retrieve a list of available
    cities and their corresponding IDs. Then formats this data into a readable
    table and saves it to a file.
    """

    name = "available_cities_spider"
    start_urls = ("https://api.fix-price.com/buyer/v1/location/city",)

    def parse(self, response: Response, **kwargs: Any) -> None:
        """
        Parses the API response and saves formatted city data to a file.

        This method extracts city names and IDs from the JSON response,
        sorts them alphabetically by city name, formats the data into a
        grid-style table, and writes the result to `available_cities.txt`.

        :param response: 
            The `Response` object from the `self.start_requests` (defined in the `super()` class) 
            containing an available `cities` and their `corresponding IDs`.
        """

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
