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
    DATABASE_URL=/mnt/d/merkiso-scrapers/merkiso_scrapers/scraper_products/db/merkiso.db

    MINIO_ROOT_USER=98ua6O7Wp0Ciyl5m
    MINIO_ROOT_PASSWORD=FGx05ZyTCsp4gy6wryRUBJSMX4nIGubH
    MINIO_ENDPOINT=http://192.168.1.231:9000
    MINIO_ACCESS_KEY=98ua6O7Wp0Ciyl5m
    MINIO_SECRET_KEY=FGx05ZyTCsp4gy6wryRUBJSMX4nIGubH
    MINIO_BUCKET_NAME=merkiso
    MINIO_USES_SSL=False
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

## Contributing
Contributions are welcome! If you have any ideas or improvements, feel free to submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE).

## Disclaimer
Please use this project responsibly and in accordance with the terms and conditions of the websites you are scraping. Be respectful of the website owners' policies and do not engage in any illegal activities.

## Contact
For any questions or inquiries, please contact [your-email@example.com](mailto:your-email@example.com).
