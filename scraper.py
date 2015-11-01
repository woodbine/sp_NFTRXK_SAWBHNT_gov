import requests
from bs4 import BeautifulSoup as bs
import scraperwiki
from datetime import datetime
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
import grequests

start_urls = ['http://www.amazon.com/Best-Sellers-Toys-Games-Toy-Figures-Playsets/zgbs/toys-and-games/165993011/ref=zg_bs_nav_t_1_t', 
'http://www.amazon.com/Best-Sellers-Toys-Games-Balls-Babies-Toddlers/zgbs/toys-and-games/2522032011/ref=zg_bs_nav_t_2_196601011', 
'http://www.amazon.com/Best-Sellers-Toys-Games-Baby-Toddler/zgbs/toys-and-games/196601011/ref=zg_bs_nav_t_1_t']
pool = Pool(cpu_count() * 20)

def scrape(response, **kwargs):
        listing_soup = bs(response.text, 'lxml')
        asin_nums = listing_soup.find_all('div', 'zg_itemImmersion')
        for asin_num in asin_nums:
            asin = ''
            try:
                asin = asin_num.find('a')['href'].split('dp/')[-1].strip()
            except:
                pass
            amazon_price = ''
            try:
                amazon_price = asin_num.find('strong', 'price').text.strip()
            except:
                pass
            total_offer_count = ''
            try:
                total_offer_count = asin_num.find('div', 'zg_usedPrice').find('a').text.strip().split(u'\xa0')[0].replace('used & new', '')
            except:
                pass
            lowest_price = ''
            try:
                lowest_price = asin_num.find('div', 'zg_usedPrice').find('span', 'price').text.strip()
            except:
                pass
            today_date = str(datetime.now())
            scraperwiki.sqlite.save(unique_keys=['Date'], data={'ASIN': asin, 'Date': today_date, 'Amazon Price': amazon_price, 'Total Offer Count': total_offer_count, 'Lowest Price': lowest_price})


def multiparse(links):
         l = links.find('a')['href'].encode('utf-8')
         if l:
             return l


def parse(url):
    if url in start_urls:
        async_list = []
        print (url)
        for i in xrange(1, 6):
            rs = (grequests.get(url+'?&pg={}'.format(i), hooks = {'response' : scrape}))
            async_list.append(rs)
        grequests.map(async_list)
    page = requests.get(url)
    soup = bs(page.text, 'lxml')
    try:
        active_sel = soup.find('span', 'zg_selected').find_next()
        if active_sel.name == 'ul':
            links_lists= active_sel.find_all('li')
            asins = pool.map(multiparse, links_lists)
            for asin in asins:
                async_list = []
                print (asin)
                for i in xrange(1, 6):
                    rs = (grequests.get(asin+'?&pg={}'.format(i), hooks = {'response' : scrape}))
                    async_list.append(rs)
                parse(asin)
                grequests.map(async_list)


    except:
        parse(url)


if __name__ == '__main__':

   for start_url in start_urls:
       parse( start_url)
