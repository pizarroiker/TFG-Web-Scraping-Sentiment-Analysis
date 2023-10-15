#MeteCritic URL Retriever
import requests, pandas as pd, time
from bs4 import BeautifulSoup

url_dict = {'url':[]} # Data Structure

def webpage(pageNum, year): #function that navigates the Metacritic SRP(Search Results Pages) based on the page number and the year
    url = "https://www.metacritic.com/browse/movie/all/all/"+ year +"/metascore/?network=netflix&network=disney-plus&page=" + str(pageNum)
    userAgent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.1234.567 Safari/537.36'}
    response = requests.get(url, headers=userAgent)
    return response

def numberPages(response): # Helper Function that determines how many pages are in a SRP to know how many times to run scrapper function
    soup = BeautifulSoup(response.text, 'html.parser')
    pages = soup.find_all('span', {"class":"c-navigationPagination_itemButtonContent"})
    pagesCleaned = pages[-2].get_text().strip()
    print(pagesCleaned)
    return (pagesCleaned)

def scrapper(num_loops, content):
    for i in range(0, num_loops):
        url = content[i].find('a', href=True)['href']
        url_dict['url'].append(url)
        print(url)

def pages(lastPageNum, year): #Function that returns the html(code) and initiates the URL Retriever
    currentPage = 1
    while currentPage <= int(lastPageNum):
        response = webpage(currentPage, year)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find_all('div', {"class":"c-finderProductCard"})
        num_loops = len(content)
        scrapper(num_loops, content)
        print(currentPage)
        currentPage += 1
        time.sleep(6)

#Main code
years = ["2020","2021","2022","2023"]
for year in years:
    numPage = (numberPages(webpage(1, year)))
    print(numPage)
    pages(int(numPage), year)
    time.sleep(5)
    print(year)
    
url_data = (pd.DataFrame.from_dict(url_dict))
url_data.to_csv(r".\moviesurls.csv")