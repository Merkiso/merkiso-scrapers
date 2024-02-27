## Description
This project contains a collection of web scrapers developed in Python for the purpose of data extraction.

## Installation
1. Clone the repository: `git clone https://github.com/your-username/merkiso-scrapers.git`
2. Create virtualenv: `virtualenv venv`
3. entry to virtualenv, in windows: `venv\Scripts\activate` or in linux: `source venv_bash/bin/activate`
4. Install the required dependencies: `pip install -r requirements.txt`
5. create .env, example:
    ```
    PYTHONPATH=$PYTHONPATH:/mnt/d/merkiso-scrapers/merkiso_scrapers
    MONGO_URI="mongodb+srv://merki057:<password>@cluster0.qtwthhb.mongodb.net/merkiso_db?retryWrites=true&w=majority&appName=Cluster0"
    ```
6. and, if you use windows, entry to folder venv/Scripts/activate and write in the last line: 

    ```bash
    @echo off
    setlocal enabledelayedexpansion
    for /f "delims=" %%a in ('type .env ^| find "="') do (
        set "%%a"
    )
    endlocal
    ```
    or if you use linux, entry to venv/bin/activate and write in the last line:
    ```bash
    export PATH="$_OLD_VIRTUAL_PATH"
    export $(grep -v '^#' .env | xargs)
    ```
    to scrapers read all variables from .env

## Usage
1. Navigate to the project directory: `cd merkiso-scrapers`
2. Navigate to the spiders directory: `cd merkiso_scrapers/scraper_products/spiders`
3. Run the desired specific spider to scraper: `python any_spider.py`
4. or execute scrapy command: `scrapy crawl scrapers_vtex -a product_name=ensalada -o outputs/json_result.json`
5. and see in the  `outputs/` the json generated with data scraped

