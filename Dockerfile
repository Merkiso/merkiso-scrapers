FROM python:3.9

# update and install git
RUN apt-get update && apt-get install -y git
RUN pip install --upgrade pip
RUN apt-get install nano

WORKDIR /merkiso_scrapers

# Instala las dependencias del proyecto
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /merkiso_scrapers/merkiso_scrapers

