# The FixPrice Parser
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Static Badge](https://img.shields.io/badge/Scrapy-2.11-blue?logo=scrapy)](https://scrapy.org/)
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)

## Table of Contents
- [Set up and run](#set-up-and-run)
- [Get available cities](#get-available-cities)

## Set up and run

This will parse the data for `default city and categories` and save it to the `output.json`. To change it edit the [Makefile](Makefile)
```bash
python3 -m venv .venv

# Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

pip install -r requirements/main.txt

make run
```

## Get available cities

This command will create the `available_cities.txt`
```bash
make get-available-cities
```