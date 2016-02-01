#pip install BeautifulSoup4
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys

verbose = False

def verbose_print(msg):
    if verbose:
        print(msg)

def get_pricing(part_number):
    url = 'http://search.digikey.com/scripts/DkSearch/dksus.dll?vendor=0&keywords='
    verbose_print('Fetching webpage for "%s"...' % part_number)
    verbose_print(url + part_number)
    page = urlopen(url + part_number)
    verbose_print('Parsing webpage...')
    soup = BeautifulSoup(page, 'html.parser')
    #verbose_print(soup.encode('UTF-8'))
    page.close()
    
    prices = {}
    table = soup.find('table', attrs={'id':'product-dollars'})
    if not table:
        # This really should find the right link and open it so we can parse it correctly...
        verbose_print('Failed to find pricing table..., lets see if we got multiple results...')
        table = soup.find('table', attrs={'id':'productTable'})
        if not table:
            verbose_print('Failed to find pricing table...')
            return prices
        for row in table.find_all('tr'):
            min_cell = row.find_all('td', attrs={'class':'tr-minQty ptable-param'})
            qty = 0.0
            price = 0.0
            if len(min_cell) == 1:
                try:
                    qty = int(min_cell[0].find(text=True).strip().replace(',', ''))
                except:
                    qty = -1
            cell = row.find_all('td', attrs={'class':'tr-unitPrice ptable-param'})
            if len(cell) == 1:
                try:
                    price = float(cell[0].find(text=True).strip().replace(',', ''))
                except:
                    verbose_print(cell[0].find(text=True).encode('UTF-8'))
                    price = -1
            if qty != 0 and price != 0 and not qty in prices:
                prices[qty] = price
            
    else:
        for row in table.find_all('tr'):
            cell = row.find_all('td')
            if len(cell) == 3:
                try:
                    prices[int(cell[0].find(text=True).replace(',', ''))] = \
                        float(cell[1].find(text=True).replace(',', ''))
                except:
                    pass
    return prices
    verbose_print('Done...')

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            parts = sys.argv[1:]
        else:
            raise Exception()
    except:
        parts = [
           "BK-885-TR",
            "GRM155R71C104KA88D",
            "311-100HRCT-ND",
            "C1206C103K5RACTU",
        ]
    part_prices = {}
    # Lets build the container that has all the prices
    quantities = []
    for part in parts:
        verbose_print('')
        try:
            part_prices[part] = get_pricing(part)
            for quantity in part_prices[part]:
                quantities.append(quantity)
            verbose_print('Prices for "%s":' % part + str(part_prices[part]))
        except Exception as ex:
            part_prices[part] = {}
            verbose_print(ex)
            print(ex)
    # Make unique and in order
    #print(quantities)
    quantities = sorted(set(quantities))
    #print(quantities)
    # Print the header
    print('Part Number, ', end='')
    for q in quantities:
        print(q, end=', ')
    print()
    # Time to print the real data
    for k,v in part_prices.items():
        print('"%s"' % k, end=', ')
        last_price = -1
        for q in quantities:
            if q in v:
                last_price = v[q]
            print(last_price, end=', ')
        print()
