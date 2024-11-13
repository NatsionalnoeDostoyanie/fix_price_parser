# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import Any

from scrapy.item import (
    Field,
    Item,
)


# fmt: off
@dataclass
class PriceItem:
    current:  float | None = None
    original: float | None = None
    sale_tag:   str | None = None
# fmt: on


# fmt: off
@dataclass
class StockItem:
    in_stock: bool | None = None
    count:     int | None = None
# fmt: on


# fmt: off
@dataclass
class AssetsItem:
    main_image: str | None = None
    set_images: str | None = None
    view_360:   str | None = None
    video:      str | None = None
# fmt: on


class MetadataItem(Item):  # type: ignore[misc]
    _description: str = Field()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._extra_fields: list[str] = []
        super().__init__(*args, **kwargs)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.fields:
            self.__setitem__(name, value)
        elif isinstance(getattr(self.__class__, name, None), property):
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if name in self._extra_fields:
            return super().__getattr__(name)
        elif name in self.fields:
            return self.__getitem__(name)
        else:
            super().__getattr__(name)

    def __setitem__(self, key: Any, value: Any) -> None:
        if key not in self.fields:
            self._extra_fields.append(key)
        self.fields[key] = Field()
        super().__setitem__(key, value)


# fmt: off
@dataclass
class FixPriceParserItem:  
    timestamp:            int | None = None
    RPC:                  str | None = None
    url:                  str | None = None
    title:                str | None = None
    marketing_tags: list[str] | None = None
    brand:                str | None = None
    section:        list[str] | None = None
    price_data:     PriceItem | None = None
    stock:          StockItem | None = None
    assets:        AssetsItem | None = None
    metadata:    MetadataItem | None = None
    variants:             int | None = None
# fmt: on
