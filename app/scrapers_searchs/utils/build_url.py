import urllib.parse as urlparse

def build_url(url, params):
    url_parse = urlparse.urlparse(url)

    query = url_parse.query

    url_dict = dict(urlparse.parse_qsl(query))

    url_dict.update(params)

    url_new_query = urlparse.urlencode(url_dict)

    url_parse = url_parse._replace(query=url_new_query)

    new_url = urlparse.urlunparse(url_parse)
    
    return new_url