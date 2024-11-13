import math
from datetime import datetime
from functools import lru_cache
from typing import (
    Any,
    Iterable,
)

import requests
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.spiders import Spider

from fix_price_parser.items import (
    AssetsItem,
    FixPriceParserItem,
    MetadataItem,
    PriceItem,
    StockItem,
)


class FixPriceSpider(Spider):  # type: ignore[misc]
    """
    Spider for scraping product data from the FixPrice website.

    This spider fetches product information based on specified city and category slugs.
    It constructs requests to the FixPrice API and processes the responses to extract
    product details such as title, price, and metadata.
    """

    name = "fix_price_spider"

    def __init__(self, city_id: int, categories_slugs: str | tuple[str, ...], *args: Any, **kwargs: Any) -> None:
        """
        Initializes the FixPriceSpider object with city and categories information.

        This constructor sets up the spider with the necessary city ID and category slugs
        to filter the products that will be scraped. It also initializes the headers and
        base URLs required for making requests to the FixPrice API.

        :param city_id: 
            The ID of the city for which to fetch product data. 
            You can get it by calling the `available_cities_spider` (`make get-available-cities` command).
        :param categories_slugs: 
            A single category slug or a tuple of category slugs to filter products.
        
        :raises ValueError: 
            If `city_id` is not an integer or `categories_slugs` is not a tuple of strings or a single string.
        :raises JSONDecodeError: 
            If the FixPrice API blocks the request (most likely due to rate limiting).
        """

        super().__init__(*args, **kwargs)

        try:
            self.city_id = int(city_id)
        except ValueError:
            raise ValueError("`city_id` should be an integer")

        if isinstance(categories_slugs, tuple) and all(isinstance(slug, str) for slug in categories_slugs):
            self.categories_slugs = categories_slugs
        elif isinstance(categories_slugs, str):
            self.categories_slugs = tuple(filter(None, categories_slugs.split(",")))
        else:
            raise ValueError("`categories_slugs` should be a tuple of strings or a single string")

        self.MAX_LIMIT_VALUE = 99

        self.BASE_URL = (
            "https://api.fix-price.com/buyer/v1/product/in/{category_slug}?limit={limit_value}&page={page_number}"
        )

        self.CATEGORIES_URL = "https://api.fix-price.com/buyer/v1/category/menu"

        self.BASE_ITEM_JSON_URL = "https://api.fix-price.com/buyer/v1/product/{item_url}"

        self.BASE_ITEM_URL = "https://fix-price.com/catalog/{item_url}"

        try:
            self.categories_json: list[dict[str, Any]] = requests.get(self.CATEGORIES_URL).json()
        except requests.exceptions.JSONDecodeError as e:
            raise e

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "utf-8",
            "Content-Type": "application/json",
            "Referer": "https://fix-price.com/",
            "x-language": "ru",
            "x-city": str(self.city_id),
            "X-Key": "058446550cb5b9c60f4b480c1d90cd31",
            "Origin": "https://fix-price.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Connection": "keep-alive",
            "TE": "trailers",
        }

    @lru_cache()
    def build_category_hierarchy(self, base_category_slug: str) -> list[str]:
        """
        Builds a hierarchy of category titles from a `base category` slug.

        This method takes a `base category` slug and traverses the category JSON 
        to construct a list of category titles representing the hierarchy of
        categories leading to the base category.

        :param base_category_slug: 
            The slug representing the `base category`.

        :returns: 
            A list of category titles representing the hierarchy based on `base category`.
        """

        category_hierarchy: list[str] = []
        categories = self.categories_json
        for category_slug_from_splitted_base_category_slug in base_category_slug.split("/"):
            for category in categories:
                if category["alias"] == category_slug_from_splitted_base_category_slug:
                    category_hierarchy.append(category["title"])
                    categories = category["items"]
                    break
        return category_hierarchy

    def start_requests(self) -> Iterable[Request]:
        """
        Generates initial requests for each `category`.

        This method constructs the initial POST requests for each `category slug`
        specified in the spider's configuration. It uses the `base URL` template
        to create requests that will determine the number of pages available
        for each category. The requests are configured with necessary headers
        and a callback to handle the response.

        :returns: 
            An iterable of `Request` objects with `self.get_pages_amount` as `callback`.
        """

        for category_slug in self.categories_slugs:
            url_with_defined_category = self.BASE_URL.format(
                category_slug=category_slug, limit_value="{limit_value}", page_number="{page_number}"
            )
            yield Request(
                method="POST",
                url=url_with_defined_category.format(limit_value=1, page_number=1),
                headers=self.headers,
                callback=self.get_pages_amount,
                meta={"category_slug": category_slug, "url_with_defined_category": url_with_defined_category},
            )

    def get_pages_amount(self, response: Response, **kwargs: Any) -> Iterable[Request]:
        """
        Determines the total `number of pages` for recieved category and generates requests for each page.

        This method is called as a callback after the initial request for each category.
        It calculates the total number of pages based on the "x-count" header in the response
        and the maximum number of items per page (`MAX_LIMIT_VALUE`). Then generates
        new requests for each page of the category.

        :param response: 
            The `Response` object from the `self.start_requests` containing a `number of pages`.

        :returns: 
            An iterable of `Request` objects - one for each page of the category. 
            Uses the `self.get_remaining_item_data` as `callback`.
        """

        url_with_defined_category_and_max_limit: str = response.meta["url_with_defined_category"].format(
            limit_value=self.MAX_LIMIT_VALUE, page_number="{page_number}"
        )
        pages_amount = math.ceil(int(response.headers["x-count"]) / self.MAX_LIMIT_VALUE)
        for page_number in range(1, pages_amount + 1):
            yield Request(
                method="POST",
                url=url_with_defined_category_and_max_limit.format(page_number=page_number),
                headers=self.headers,
                callback=self.get_remaining_item_data,
                meta={"category_slug": response.meta["category_slug"]},
            )

    def get_remaining_item_data(self, response: Response, **kwargs: Any) -> Iterable[Request]:
        """
        Processes the response from `each category page` and generates requests for individual items.

        This method is called as a callback for each page of a category. It extracts
        information about individual items from the JSON response and generates new
        requests to fetch detailed data for each item.

        :param response: 
            The `Response` object from the `self.get_pages_amount` containing a surface data about items on this page.

        :returns: 
            An iterable of `Request` objects - one for each item on the page.
            Uses the `self.parse` as `callback`.
        """

        for item_from_catalog_json in response.json():
            yield Request(
                method="GET",
                url=self.BASE_ITEM_JSON_URL.format(item_url=item_from_catalog_json["url"]),
                headers=self.headers,
                callback=self.parse,
                meta={"category_slug": response.meta["category_slug"]},
            )

    def parse(self, response: Response, **kwargs: Any) -> Iterable[FixPriceParserItem]:
        """
        Parses the detailed product information from the API response.

        This method is the final step in the scraping process. It extracts all relevant
        product data from the JSON response and constructs a FixPriceParserItem object
        with the parsed information.

        :param response: 
            The `Response` object from the `self.get_remaining_item_data` containing full data about item.

        :returns: 
            An iterable of `FixPriceParserItem` - one for each item. 
            Each element contains full data about item.
        """

        category_slug: str = response.meta["category_slug"]
        timestamp_value = int(
            datetime.strptime(response.headers["date"].decode("utf-8"), "%a, %d %b %Y %H:%M:%S %Z").timestamp()
        )

        item_json: dict[str, Any] = response.json()

        item = FixPriceParserItem()
        item.timestamp = timestamp_value
        item.RPC = item_json["sku"]
        item.url = self.BASE_ITEM_URL.format(item_url=item_json["url"])
        item.title = item_json["title"]

        # TODO: Parse data for `marketing_tags`
        item.marketing_tags = []

        item.brand = item_json["brand"]["title"] if item_json["brand"] else None
        item.section = self.build_category_hierarchy(base_category_slug=category_slug)

        price_item = PriceItem()
        original_price = float((item_variants_json := item_json["variants"])[0]["price"])
        price_item.original = original_price
        if special_price_json := item_json["specialPrice"]:
            price_item.current = (current_price := float(special_price_json["price"]))
            price_item.sale_tag = f"Скидка {(original_price - current_price) / original_price * 100}%"
        else:
            price_item.current = original_price
            price_item.sale_tag = None
        item.price_data = price_item

        stock_item = StockItem()
        stock_item.in_stock = (
            True
            if (stock_count := sum(item_variant_json["count"] for item_variant_json in item_variants_json)) > 0
            else False
        )
        stock_item.count = stock_count
        item.stock = stock_item

        assets_item = AssetsItem()
        if item_images := item_json.get("images"):
            assets_item.main_image = item_images[0]["src"]
            assets_item.set_images = [item_image["src"] for item_image in item_images]
        else:
            assets_item.main_image = None
            assets_item.set_images = None

        # TODO: Parse data for `view_360`
        assets_item.view_360 = None

        assets_item.video = item_json["videoLink"]
        item.assets = assets_item

        metadata_item = MetadataItem()
        metadata_item.description = item_json["description"]
        for k, v in item_variants_json[0].items():
            if k not in ("id", "image", "title", "properties", "count", "price", "fixPrice"):
                metadata_item[k] = v
        if item_properties_json := item_json.get("properties"):
            metadata_item["country_of_origin"] = item_properties_json[0]["value"]
        item.metadata = metadata_item

        item.variants = len(item_variants_json)

        yield item
