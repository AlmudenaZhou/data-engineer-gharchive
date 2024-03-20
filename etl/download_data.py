from urllib.request import Request, urlopen


def download_gharchive_data(year, month, day, hour):
    url = f'http://data.gharchive.org/{year}-{month:02d}-{day:02d}-{hour}.json.gz'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req)
    compressed_data = response.read()
    
    return compressed_data
