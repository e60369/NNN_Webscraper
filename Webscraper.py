

#Imports
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import pandas as pd
import datetime
import time
import requests
import math

print('\n')

date_user_input = input('Enter the date of the last web scrape in mm/dd format: ' + '\n')

start_time = time.time()

print('\n')

if datetime.datetime.now().minute < 10:
    print('Start Time: ' + str(datetime.datetime.now().hour) + ':0' + str(datetime.datetime.now().minute))
else:
    print('Start Time: ' + str(datetime.datetime.now().hour) + ':' + str(datetime.datetime.now().minute))

print(str(datetime.datetime.now().month) + '/' + str(datetime.datetime.now().day) + '/' + str(datetime.datetime.now().year))

print('\n')

try:
    date_user_input = date_user_input.replace('-', '/')
except:
    pass

month = date_user_input.split('/')[0]
day = date_user_input.split('/')[1]

if month[0] == '0':
    month = month[-1]
else:
    pass

if day[0] == '0':
    day = day[-1]
else:
    pass
#Old Code used to give flexibility in the user interface
'''
if len(date_user_input.split('/')) == 1:
    month = date_user_input.split('/')[0]
else:
    if date_user_input.split('/')[0][0] == '0':
        month = date_user_input.split('/')[0][1]
    else:
        month = date_user_input.split('/')[0][:2]

if len(date_user_input.split('/')) == 1:
    day = date_user_input.split('/')[1]
else:
    if date_user_input.split('/')[1][0] == '0':
        day = date_user_input.split('/')[1][1]
    else:
        day = date_user_input.split('/')[1][:2]
'''
old_list = pd.read_excel('OBL ' + str(month) + ' - ' + str(day) + '.xlsx')

old_list = old_list.reset_index()
old_list.drop('index', axis = 1, inplace = True)

prop_list = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])

try:    
    ##Calkain
    #Getting the page
    calkain_url = 'https://www.calkain.com/properties/?view=list'
    
    #Making Soup
    uClient = uReq(calkain_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    props = page_soup.findAll('tr', {'class': 'property-item'})
    
    for i in range(len(props)):
        tenant = props[i].text.replace(',', ' ').replace('\n', ',').split(',')[1]
        city = props[i].text.replace(',', ' ').replace('\n', ',').split(',')[2]
        state = props[i].text.replace(',', ' ').replace('\n', ',').split(',')[3]
        price = props[i].text.replace(',', '').replace('\n', ',').split(',')[5]
        cap_rate = props[i].text.replace(',', ' ').replace('\n', ',').split(',')[6]
        status = props[i].text.replace(',', ' ').replace('\n', ',').split(',')[7]
        source = 'Calkain'
        
        if price[0] == '$':
            price = int(price[1:])
        else:
            pass
        
        if cap_rate[-1] == '%':
            cap_rate = float(cap_rate[:-1])/100
        else:
            pass
            
        info = tenant, city, state, price, cap_rate, status, source
        
        prop_list.loc[i] = info
    
    for i in range(len(prop_list)):
        if prop_list['Sale Status'][i] == 'A':
            prop_list['Sale Status'][i] = 'Available'
        elif prop_list['Sale Status'][i] == 'U':
            prop_list['Sale Status'][i] = 'Under Contract or LOI'
        elif prop_list['Sale Status'][i] == 'S':
            prop_list['Sale Status'][i] = 'Sold'
        else:
            prop_list['Sale Status'][i] = 'Issue found'
    
except Exception:
    print('Error with Calkain')

try:
    ##Stan Johnson Co
    #Getting the page
    stan_url = 'https://www.stanjohnsonco.com/listing-showcase?page='
    
    stan_list = pd.DataFrame(columns =  ['Property', 'City', 'State', 'Price','Cap Rate', 'Source'])
    middle_list = pd.DataFrame(columns =  ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Source'])

    uClient = uReq(stan_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    num_of_listings = float(page_soup.find('h2').text.split(' ')[0])
    num_of_pages = math.ceil(num_of_listings/12)
    
    #Making soup
    for y in range(num_of_pages):
        stan_johnson_url = stan_url+ str(y)
        uClient = uReq(stan_johnson_url)
        page_html = uClient.read()
        page_soup = soup(page_html, 'html.parser')

        blocks = page_soup.findAll('div', {'class':'card card-property'})
    
        for i in range(len(blocks)):
            prop = blocks[i].h3.text

            loc = blocks[i].p.text.strip()
            city = loc.split('\t')[0]
            state = loc.split('\t')[-1]
    
            notes = blocks[i].ul.text.replace('\n', ' ')
    
            footer = blocks[i].find('div', {'class':'card-footer'})
    
            try:
                p = footer.text.split('Price')[1].split('\n')[1]
                try:
                    price = int(p.replace('$','').replace(',',''))
                except:
                    price = p
            except:
                price = 'N/A'
    
            try:
                c = footer.text.split('Cap Rate/Equity')[1].split('\n')[1]
                try:
                    cap = float(c.replace('%',''))/100
                except:
                    cap = c        
            except:
                cap = 'N/A'
        
            info = prop, city, state, price, cap, 'Stan Johnson Co'
            
            middle_list.loc[i] = info
            
        stan_list = stan_list.append(middle_list, sort = True)
    
    prop_list = prop_list.append(stan_list, sort = True)

except Exception:
    print('Error with Stan Johnson')

try:   
    ##Fortis Net Lease Group
    #Getting the page
    fortis_url = 'https://fortisnetlease.com/category/properties/for-sale/'
    
    #Making soup
    uClient = uReq(fortis_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    fortis_list = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'SF', 'Sale Status', 'Source'])
    
    details = page_soup.findAll('div', {'class':'post-details'})
    c = page_soup.findAll('div', {'class':'cap_rate'})
    stat = page_soup.findAll('div',{'class':'details'})
    p = page_soup.findAll('div', {'class':'price'})
    
    for i in range(len(page_soup.findAll('div', {'class':'col s4'}))):    
        name = details[i].a.text
        
        city = details[i].text.split('\n')[2].split(',')[0][-25:]
        state = details[i].text.split('\n')[2].split(',')[1][2:4]
        
        price = int(p[i].text[1:].replace(',',''))
    
        cap = c[i].text[10:-1]
        
        if cap[0] == 'C':
            cap_rate = cap
        elif cap == 'N/A':
            cap_rate = cap
        else:
            cap_rate = float(cap)/100
    
        if str(details[i].span) == 'None':
            sf = 'N/A'
        else:
            sf = details[i].span.text
        
        avail = stat[i].a.text
        
        row = name, city, state, price, cap_rate, sf, avail, 'Fortis Net Lease Group'
        
        fortis_list.loc[i] = row

    prop_list = prop_list.append(fortis_list, sort = True)
 
except Exception:
    print('Error with Fortis')

try:    
    ##Hanley Investment Group
    #Getting the page
    hanley_url = 'http://listings.hanleyinvestment.com/'
    
    #Making Soup
    uClient = uReq(hanley_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    tens = page_soup.findAll('div', {'class':'wrap'})
    
    hanley = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Type', 'SF', 'Sale Status', 'Source'])
    
    for i in range(2,len(tens)-1):
        props = (tens[i].text.strip().split('\n'))[0]
        city = (tens[i].text.strip().replace(',', ' ').split('\n'))[3][:-4] 
        state = (tens[i].text.strip().replace(',', ' ').split('\n'))[3][-2:] 
        price = (tens[i].text.strip().replace(',', '').split('\n'))[4] 
        cap_rate = (tens[i].text.strip().split('\n'))[7][6:] 
        style = (tens[i].text.strip().split('\n'))[8][6:] 
        sf = (tens[i].text.strip().replace(',', '').split('\n'))[9][4:] 
        status = (tens[i].text.strip().split('\n'))[10][8:] 
        source = 'Hanley Investment Group'
        
        if len(price) == 0:
            price = 'N/A'
        else: 
            pass
        
        if price[0] == '$':
            price = int(price[1:])
        else:
            pass
        
        if cap_rate[-1] == '%':
            cap_rate = float(cap_rate[:-1])/100
        else:
            pass
        
        sf = int(sf)
    
        info = props, city, state, price, cap_rate, style, sf, status, source
    
        hanley.loc[i] = info
    
    prop_list = prop_list.append(hanley, sort = True)

except Exception:
    print('Error with Hanley')

try:
    #Sands Investment Group
    #Getting the page
    sands_url = 'http://signnn.com/listings/'
    
    #Making Soup
    uClient = uReq(sands_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'entry-content-header'})
    
    sands = pd.DataFrame(columns = ['Property', 'Address', 'City', 'State', 'Cap Rate', 'Sale Status', 'Price', 'Source'])
    
    for i in range(len(blocks)):
        prop = blocks[i].h3.text.split('|')[0]
        address = blocks[i].p.text.split('-')[0]
        city = blocks[i].p.text.split('-')[1].split(',')[0][1:]
        state = blocks[i].p.text.split('-')[-1].split(',')[1][1:3]
        cap = blocks[i].div.div.text
    
        try:
            price = int(blocks[i].text.replace('$','').replace(',', '').strip().split('\n')[4])
            status = 'N/A'
        except:
            status = blocks[i].text.strip().split('\n')[4]
            try:
                price = int(blocks[i].text.replace('$','').replace(',', '').strip().split('\n')[5])
            except:
                price = blocks[i].text.replace('$','').replace(',', '').strip().split('\n')[5]

        source = 'Sands Investment Group'   
    
        try:
            cap_rate = float(cap.split(':')[1].replace('%',''))/100
        except:
            cap_rate = cap.split(':')[1]
        
        info = prop, address, city, state, cap_rate, status, price, source

        sands.loc[i] = info
    
    prop_list = prop_list.append(sands, sort = True)

except Exception:
    print('Error with Sands')

try:
    #Snyder Carlton Team
    #Getting the page
    sc_url = 'http://snydercarlton.com/get_listings.cfm'
    
    #Making Soup
    uClient = uReq(sc_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'property'})
    
    snydercarlton = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Lease Term', 'SF', 'Source'])
    
    for i in range(len(blocks)):
        tenant = blocks[i].div.text.strip().replace('\r', ' ').split('\n')[0]
        location = blocks[i].div.text.strip().replace('\r', ' ').split('\n')[1].split(',')
        city = location[0]
        state = location[1][1:]
        price = blocks[i].div.text.strip().replace('\r', ' ').replace(',', '').split('\n')[3][7:]
        
        cap = 'N/A'
        lease_term = 'N/A'
        sf = 'N/A'

        for y in range(len(blocks[i].div.text.strip().replace('\r',' ').split('\n')[-1].split(':'))):

            if blocks[i].div.text.strip().replace('\r', ' ').split('\n')[-1].split(':')[y] == 'Cap Rate':
                cap = blocks[i].div.text.strip().replace('\r', ' ').split('\n')[-1].split(':')[(y+1)].split('%')[0]
            else:
                pass
    
            if blocks[i].div.text.strip().replace('\r', ' ').split('\n')[-1].split(':')[y][-10:] == 'Lease Term':
                lease_term = blocks[i].div.text.strip().replace('\r', ' ').split('\n')[-1].split(':')[(y+1)].split('SF')[0]
            else:
                pass
    
            if blocks[i].div.text.strip().replace('\r', ' ').split('\n')[-1].split(':')[y][-2:] == 'SF':
                sf = blocks[i].div.text.strip().replace('\r', ' ').split('\n')[-1].split(':')[(y+1)]
            else:
                pass
            
        if price[0] == '$':
            price = int(price[1:])
        else:
            pass
        
        try:
            cap = float(cap)/100
        except:
            pass        
        
        info = (tenant, city, state, price, cap, lease_term, sf, 'SnyderCarlton Team')
            
        snydercarlton.loc[i] = info
    
    prop_list = prop_list.append(snydercarlton, sort = True)

except Exception:
    print('Error with SnyderCarlton')

try:
    ##Quantum Real Estate Advisors
    #Getting the page
    quantum_url = 'https://qreadvisors.secure.force.com/forSale'
    
    #Making Soup
    uClient = uReq(quantum_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    title = page_soup.findAll('div', {'class':'title'})
    blocks = page_soup.findAll('h6')
    
    quantum = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Source'])
    
    for i in range(1, len(title)):
        prop = title[i].text.split('\n')[0]
    
        if len(title[i].text.split('\n')[1].split(',')) == 2:
            city = title[i].text.split('\n')[1].split(',')[0][-15:]
            state = title[i].text.split('\n')[1].split(',')[1][1:]
        else:
            city = title[i].text.split('\n')[1].split(',')[0][-15:]
            state = 'N/A'
    
        price = blocks[i].text.replace(',', '').split('\xa0')[0]
        cap_rate = blocks[i].text.split('\xa0')[2]

        if price == '':
            price = 'N/A'
        elif price[0] == '$':
            price = int(price[1:])
        else:
            pass
        
        if cap_rate[-1:] == '%': 
            cap_rate = float(cap_rate[:-1])/100
        else:
            cap_rate = 'N/A'
        
        info = (prop, city, state, price, cap_rate, 'Quantum Real Estate Advisors')
        
        quantum.loc[i] = info
    
    prop_list = prop_list.append(quantum, sort = True)

except Exception:
    print('Error with Quantum')

try:
    ##YAF Team
    #Getting the page
    yaf_url = 'https://www.yafteam.com/property-type/listings/'
    
    #Making Soup
    uClient = uReq(yaf_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'info'})

    yaf = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Lease Term', 'Status', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].h2.text
    
        loc = blocks[i].p.text
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:]
    
        details = blocks[i].div.text

        p = details.split('-')[1].replace(',','')[2:-9]
        try:
            price = int(p)
        except:
            price = p
    
        try:
            cap_rate = float(details.split('-')[2].split('%')[0])/100
        except:
            if details.split('-')[2][1:5] == 'CALL':
                cap_rate = details.split('-')[2][1:-5]
            else:
                cap_rate = 'N/A'
        
        term = details.split('-')[3][1:-7]
        status = details.split('-')[4][1:]
    
        info = prop, city, state, price, cap_rate, term, status, 'YAF Team'
    
        yaf.loc[i] = info
    
    prop_list = prop_list.append(yaf, sort = True)

except Exception:
    print('Error with YAF')

try: 
    ##Issenberg & Britti Retail Group
    #Getting the site
    ib_url = 'http://www.issenbergbritti.com/all-listings/'
    
    #Making Soup
    uClient = uReq(ib_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    ib = pd.DataFrame(columns = ['Property', 'Address', 'City', 'State', 'Price', 'Sale Status', 'Source'])
    
    blocks = page_soup.findAll('div', {'class':'item-body'})
    tags = page_soup.findAll('div', {'class':'label-wrap label-right'})
    
    for i in range(len(blocks)):
        prop = blocks[i].h2.text
        
        if len(blocks[i].div.div.address.text.split(',')) == 4:
            address = blocks[i].div.div.address.text.split(',')[0]
            city = blocks[i].div.div.address.text.split(',')[1][1:]
            state = blocks[i].div.div.address.text.split(',')[2][1:3]
        elif len(blocks[i].div.div.address.text.split(',')) == 5:
            address = blocks[i].div.div.address.text.split(',')[1]
            city = blocks[i].div.div.address.text.split(',')[2][1:]
            state = blocks[i].div.div.address.text.split(',')[3][1:3]
        else:
            address =  blocks[i].div.div.address.text.split(',')[0]
            city =  blocks[i].div.div.address.text.split(',')[-2][1:]
            state = blocks[i].div.div.address.text.split(',')[-1][1:3]
        
        price = int(blocks[i].text.strip().split('\n')[2].replace(',', '')[1:])
        
        status = tags[i].span.text
        
        info = prop, address, city, state, price, status, 'Issenberg & Britti Group'
        
        ib.loc[i] = info
    
    prop_list = prop_list.append(ib, sort = True)

except Exception:
    print('Error with Issenberg & Britti Group')

try:
    ##Preserve West Capital
    #Getting the stie
    pwc_url = 'https://preservewestcapital.com/brokerage/featured-listings/'
    
    #Making Soup
    uClient = uReq(pwc_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'rmb-listing '})
    location = page_soup.findAll('div', {'class':'rmb-listing-location'})
    stuff = page_soup.findAll('div', {'class':'rmb-listing-details'})
    
    pwc = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'SF', 'Type', 'Source'])
    
    for i in range(len(blocks)):
        prop = blocks[i].img['alt']
        
        city = location[i].text.split(',')[0]
        state = location[i].text.split(',')[1][1:]
        
        price = int(stuff[i].text.split('\n')[1][1:].replace(',', ''))
        try:
            cap_rate = float(stuff[i].text.split('\n')[2][:-1])/100
        except:
            cap_rate = stuff[i].text.split('\n')[2]
        sf = stuff[i].text.split('\n')[3].replace(',', '')
        style = stuff[i].text.split('\n')[4]
        
        info = prop, city, state, price, cap_rate, sf, style, 'Preserve West Capital'
        
        pwc.loc[i] = info
    
    prop_list = prop_list.append(pwc, sort = True)

except Exception:
    print('Error with Preserve West Capital')

try:
    ##Mid Atlantic Retail
    #Getting the page
    zang_url = 'https://www.retailmidatlantic.com/net-lease-properties'
    
    #Making soup
    uClient = uReq(zang_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class': 'style-jajtwckq'})
    
    mar = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])
    
    for i in range(len(blocks)):
        bravo = blocks[i].findAll('h1')
        if bravo[1].text[:7] == 'Status:':
            pass
        else:
            if len(bravo) == 4:
                prop = bravo[0].text
                location = bravo[1].text
                if len(location.split(',')) == 1:
                    city = location
                    state = 'N/A'
                elif len(location.split(',')) > 2:
                    city = location
                    state = 'N/A'
                else:
                    city = location.split(',')[0]
                    state = location.split(',')[1][1:]
                
                if bravo[2].text[0] == '$':
                    price = int(bravo[2].text.split('-')[0].replace(',', '')[1:])
                    cap_rate = float(bravo[2].text.split('-')[1][:-6])/100
                else:
                    price = bravo[2].text
                    cap_rate = bravo[2].text
                
                
                status = bravo[3].text[8:]
                length = 4
            
            elif len(bravo) == 5:
                prop = bravo[0].text
            
                location = bravo[2].text
                if len(location.split(',')) == 1:
                    city = location
                    state = 'N/A'
                elif len(location.split(',')) > 2:
                    city = location
                    state = 'N/A'
                else:
                    city = location.split(',')[0]
                    state = location.split(',')[1][1:]
                
                if bravo[3].text[0] == '$':
                    price = int(bravo[3].text.split('-')[0].replace(',', '')[1:])
                    cap_rate = float(bravo[3].text.split('-')[1][:-6])/100
                else:
                    price = bravo[3].text
                    cap_rate = bravo[3].text
                    
                status = bravo[4].text[8:]
                length = 5
            
            else:
                prop = 'N/A'
                location = 'N/A'
                price = 'N/A'
                status = 'N/A'
            
            info = prop, city, state, price, cap_rate, status, 'Mid Atlantic Retail'
            
            mar.loc[i] = info 
    
    prop_list = prop_list.append(mar, sort = True)

except Exception:
    print('Error with Mid Atlantic Retail')

try:
    ##Exp Realty Advisors
    #Getting the page
    exp_url = 'http://www.exp1031.com/properties'
    
    #Making soup
    uClient = uReq(exp_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    cells = page_soup.findAll('div', {'class':'property_row_cell'})
    
    exp = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'SF', 'Acres', 'Lease Term', 'Lease Type', 'Source'])
    
    for i in range(int(len(cells)/9)):
        ten = cells[i*9].text
        city = cells[(i*9)+1].text
        state = cells[(i*9)+2].text
        price = int(cells[(i*9)+3].text.replace(',', '')[1:])
        
        if len(cells[(i*9)+4]) == 0:
            cap = 'N/A'
        else:
            cap = float(cells[(i*9)+4].text[:-1])/100
        
        sf = cells[(i*9)+5].text
        acres = cells[(i*9)+6].text
        years = cells[(i*9)+7].text
        lease = cells[(i*9)+8].text
            
        info = ten, city, state, price, cap, sf, acres, years, lease, 'EXP Realty Advisors'
        
        exp.loc[i] = info
    
    prop_list = prop_list.append(exp, sort = True)

except Exception:
    print('Error with EXP Realty Advisors')

try:
    ##NNN Investment Group
    #Getting the page
    ig_url = 'http://www.nnnig.com/active-listings.html'
    
    #Making Soup
    uClient = uReq(ig_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'elementor-slide-content'})
    
    ig = pd.DataFrame(columns = ['Property', 'Address', 'City', 'State', 'Price', 'Cap Rate', 'Source'])
    
    for i in range(len(blocks)):
        squares = blocks[i].text.split('\n') 
        
        prop = blocks[i].div.text
        
        if len(squares) == 4:
            
            address = squares[0][len(prop):-1]
            city = squares[1].split(',')[0]
            
            if len(squares[1].split(',')) == 2:
                state = squares[1].split(',')[1][1:3]
            else:
                state = 'N/A'
            
            price = int(squares[2].split('-')[1].replace(',', '')[2:])
            
            if len(squares[3].split('-')) == 1:
                cap = float(squares[3].split('%')[0][-2:-1])/100
            else:
                cap = float(squares[3].split('-')[1].split('%')[0][1:])/100
                
        else:
            address = blocks[i].text.split(',')[0][len(prop):]
            city = blocks[i].text.split(',')[1]
            state = blocks[i].text.split(',')[2][1:3]
            
            price = float(squares[1].split('-')[1].replace(',', '')[2:])
            
            cap = float(squares[2].split('-')[1].split('%')[0][1:])/100
            
        info = prop, address, city, state, price, cap, 'NNN Investment Group'
    
        ig.loc[i] = info
    
    prop_list = prop_list.append(ig, sort = True)

except Exception:
    print('Error with NNN Investment Group')

try:
    ##Stream Capital Partners
    #Getting the page
    stream_url = 'https://www.stream-cp.com/available-properties/'
    
    #Making soup
    uClient = uReq(stream_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    scp = pd.DataFrame(columns = ['Property', 'Address', 'City', 'State', 'Price', 'Cap Rate', 'Lease Term', 'Source'])
    
    blocks = page_soup.findAll('div', {'class':'boxstuff'})
    
    for i in range(len(blocks)):
        prop = blocks[i].h3.text
        
        if len(blocks[i].strong.text.split(',')) >= 3:
            address = blocks[i].strong.text.split(',')[0]
            city = blocks[i].strong.text.split(',')[1]
            state = blocks[i].strong.text.split(',')[2]
        else:
            address = blocks[i].strong.text
            city = 'N/A'
            state = 'N/A'
        
        try:
            price = int(blocks[i].text.split('Price: ')[1].split(' | ')[0].replace(',','').split('$')[-1])
        except:
            price = 'N/A'

        try:
            cap = float(blocks[i].text.split('Cap Rate: ')[1].split('%')[0])/100
        except:
            cap = 'N/A'

        try:
            term = blocks[i].text.split('Remaining Term: ')[1].split('View Details')[0]
        except:
            term = 'N/A'
        
        info = prop, address, city, state, price, cap, term, 'Stream Capital Partners'
        scp.loc[i] = info
    
    prop_list = prop_list.append(scp, sort = True)

except Exception:
    print('Error with Stream Capital Partners')

try:
    ##CIAdvisors
    #Getting the page
    cia_url = 'http://www.ciadvisor.com/properties/'
    
    #Making Soup
    uClient = uReq(cia_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'col-lg-8 d-flex align-items-stretch flex-wrap'})
    
    cia = pd.DataFrame(columns = ['Property', 'City', 'State', 'Cap Rate', 'Price', 'Type', 'Lease Type', 'Sale Status',  'SF', 'Notes', 'Source'])
    
    for i in range(len(blocks)):
        prop = blocks[i].div.text.strip().split('\n')[0]
        city = blocks[i].div.text.strip().split('\n')[-1].split(',')[0]
        state = blocks[i].div.text.strip().split('\n')[-1].split(',')[1][1:]
        
        for y in range(len(blocks[i].text.split('\n'))):
            try:
                if blocks[i].text.split('\n')[y] == 'Cap Rate':
                    cap = float(blocks[i].text.split('\n')[y+1][:-1])/100         
                else:
                    pass
            except:
                cap = 'N/A'

            try:    
                if blocks[i].text.split('\n')[y] == 'Price':
                    p = blocks[i].text.split('\n')[y+3].split('$')[1].replace(',','')
                    if p[-1] == ')':
                        price = int(p[:-1])
                    else:
                        price = int(p)
                else:
                    pass
            except:
                price = 'N/A'
            
            if blocks[i].text.split('\n')[y] == 'TYPE':
                sort = blocks[i].text.split('\n')[y+1]        
            else:
                pass
            
    
            if blocks[i].text.split('\n')[y] == 'STATUS':
                status = blocks[i].text.replace('\t', '').split('\n')[y+3]       
            else:
                pass
    
            if blocks[i].text.split('\n')[y] == 'LEASE TYPE':
                lease = blocks[i].text.split('\n')[y+1]        
            else:
                pass
            
            if blocks[i].text.split('\n')[y] == 'SQUARE FEET':
                sf = blocks[i].text.split('\n')[y+1]        
            else:
                pass
            
            if blocks[i].text.split('\n')[y] == 'Details':
                notes = blocks[i].text.split('\n')[y+1]        
            else:
                pass        
    
        info = prop, city, state, cap, price, sort, lease, status, sf, notes, 'CIAdvisors'
        cia.loc[i] = info
    
    prop_list = prop_list.append(cia, sort = True)

except Exception:
    print('Error with CIAdvisors')

try:
    ##Chetek Group
    #Getting the page
    chetek_url = 'http://thechetekgroup.com/feature-listing/'
    
    #Making soup
    uClient = uReq(chetek_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    start = page_soup.find('ul', {'class':'feature_lists'})
    blocks = start.findAll('li')
    
    chetek = pd.DataFrame(columns = ['Property', 'Price', 'Notes', 'Cap Rate', 'City', 'State', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].h3.text
    
        cells = blocks[i].findAll('p')
    
        for y in range(len(cells)):
            if cells[y].text == 'PRICE: Unpriced' or cells[y].text == 'UNPRICED' or cells[y].text == 'Price: UNPRICED':
                p = 'Unpriced'
                try:
                    noi = cells[y+1].text.split(':')[1]
                except:
                    noi = ''
            elif len(cells[y].text.split('$')) == 2 and cells[y].text[:3] != 'NOI':
                p = cells[y].text.split('$')[1]
                noi = ''
            elif len(cells) == 3:
                p = 'N/A'
                noi = ''
            else:
                pass
    
        loc = blocks[i].find('p', {'class':'pl-location'}).text[:30]
        if len(loc.split(',')) == 2:
            city = loc.split(',')[0]
            state = loc.split(',')[1]
        else:
            city = loc
            state = 'N/A'

        info = prop, price, noi, cap, city, state, 'Chetek Group'
        chetek.loc[i] = info
    
    prop_list = prop_list.append(chetek, sort = True)

except Exception:
    print('Error with Chetek Group')

try:
    ##Sambazis Retail Group
    #Getting the page
    sam_url = 'http://www.sambazisretailgroup.com/listings/'
    
    #Making soup
    uClient = uReq(sam_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('div', {'class':'listing-info-column'})
    
    sam = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])
    
    for i in range(len(blocks)):
        prop = blocks[i].h4.text
        location = blocks[i].p.text
        city = location.split(',')[0]
        state = location.split(',')[1][1:]
    
        details = blocks[i].dl.findAll('dd')
    
        if len(details) == 3:
            price = int(details[0].text.replace(',', '')[1:])
            cap = float(details[1].text[:-1])/100
            status = details[2].text
        else:
            price = 'N/A'
            try:
                cap = float(details[0].text[:1])/100
            except:
                cap = details[0].text
            status = details[1].text
        
        info = prop, city, state, price, cap, status, 'Sambazis Retail Group'
        sam.loc[i] = info
    
    prop_list = prop_list.append(sam, sort = True)

except Exception:
    print('Error with Sambazis Retail Group')

try:
    ##Matthews Real Estate Investment Services
    #Getting the page
    matthews_url = 'http://www.matthews.com/listings/'
    
    #Making soup
    uClient = uReq(matthews_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')
    
    blocks = page_soup.findAll('figure')
    
    matt = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Lease Term', 'Source'])
    
    for i in range(len(blocks)):
        prop = blocks[i].h3.text
        details = blocks[i].findAll('p')
        
        location = details[0].text.split(',')
        city = location[0]
        state = location[1]
        
        if len(blocks[i].findAll('p')) == 4:
            price = int(details[1].text.replace(',','')[1:])
            if details[2].text[:8] == 'CAP RATE':
                cap = float(details[2].text[9:-1])/100
            else:
                cap = 'N/A'
            if details[3].text[:4] == 'TERM':
                term = details[3].text[5:]
            else:
                term = 'N/A'
            
        elif len(blocks[i].findAll('p')) == 3:
            price = int(details[1].text.replace(',','')[1:])
            if details[2].text[:8] == 'CAP RATE':
                cap = float(details[2].text[9:-1])/100
            else:
                cap = 'N/A'
            term = 'N/A'
            
        elif len(blocks[i].findAll('p')) == 2:
            if details[1].text == 'Best Offer':
                price = details[1].text
            else:
                price = int(details[1].text.replace(',','')[1:])
            cap = 'N/A'
            term = 'N/A'   
            
        else:
            price = 'N/A'
            cap = 'N/A'
            term = 'N/A'
            
        info = prop, city, state, price, cap, term, 'Matthews Real Estate Investment Services'
        matt.loc[i] = info

    prop_list = prop_list.append(matt, sort = True)

except Exception:
    print('Error with Matthews Real Estate')

try:
    ##Baum Realty Group
    #Getting the page
    baum_url = 'http://www.baumrealty.com/Listings/NetLease'

    #Making Soup
    uClient = uReq(baum_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'box slider-static-item'})

    baum = pd.DataFrame(columns = ['Property', 'City', 'State', 'Address', 'Price', 'Cap Rate', 'Lease Type', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].h2.text
    
        loc = blocks[i].h3.text
        city = loc.split(',')[0]
    
        if len(loc.split(',')) == 2:
            state = loc.split(',')[1]
        else:
            state = 'N/A'

        address = blocks[i].address.text.split(blocks[i].h3.text)[0]
        
        details = blocks[i].findAll('li')
    
        p = details[0].em.text
        if p[0] == '$':
            price = int(p[1:].replace(',',''))
        else:
            price = p
        
        c = details[1].em.text
        if c[-1] == '%':
            cap = float(c[:-1])/100
        else:
            cap = c
        
        lease = details[2].em.text
        
        stat = blocks[i].div.text.strip()
        if len(stat) == 0:
            status = 'Available'
        else:
            status = stat
    
        info = prop, city, state, address, price, cap, lease, status, 'Baum Realty Group'
        baum.loc[i] = info

    prop_list = prop_list.append(baum, sort = True)

except Exception:
    print('Error with Baum Realty Group')

try:
    ##Nisbet Group
    #Getting the page
    nisbet_url = 'https://www.thenisbetgroup.com/current-listings'

    #Making soup
    uClient = uReq(nisbet_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'txtNew'})

    nisbet = pd.DataFrame(columns = ['Property', 'City', 'State', 'Address', 'Price', 'Cap Rate', 'Notes', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        try:
            title = blocks[i].h6.text

            prop = title.split('|')[0]
            loc = title.split('|')[1][1:]
            city = loc.split(',')[0]
            state = loc.split(',')[1]
        
            address = blocks[i].text.split('\n')[1].split(':')[1].split(',')[0][1:]
            price = int(blocks[i].text.split('\n')[2].split(':')[1].replace(',','').replace('$','')[1:])
            cap = float(blocks[i].text.split('\n')[3].split(':')[1][1:-1])/100
            note = blocks[i].text.split('\n')[4].split(':')[1][1:]
        
        except:
            title = 'N/A'
            prop = 'N/A'
            loc = 'N/A'
            address = 'N/A'
            price = 'N/A'
            cap = 'N/A'
            note = 'N/A'
    
        if prop == 'N/A':
            pass
        else:
            info = prop, city, state, address, price, cap, notes, status, 'Nisbet Group'
            nisbet.loc[i] = info

    prop_list = prop_list.append(nisbet, sort = True)

except Exception:
    print('Error with Nisbet Group')

try:
    ##NNN Retail Investment Group
    rig = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Source'] )

    #Getting the page & Making soup
    for y in range(1,3):
        nnn_rig_url = 'https://www.retail1031.com/property_group/for-sale/page/' + str(y)
    
        #Making Soup
        uClient = uReq(nnn_rig_url)
        page_html = uClient.read()
        page_soup = soup(page_html, 'html.parser')
        
        blocks = page_soup.findAll('div', {'class':'sc_property_title'})
    
        middle = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Source'] )
        
        for i in range(len(blocks)):
            prop = blocks[i].text.split('\n')[2].split('|')[0]

            try:
                loc = blocks[i].text.split('\n')[2].split('|')[1].split(',')
                city = loc[0][1:]
                state = loc[1][1:]
            except:
                loc = 'N/A'
                city = 'N/A'
                state = 'N/A'
    
            try:
                price = int(blocks[i].text.split('\n')[3].split('|')[0][1:].replace(',',''))
            except:
                price = 'N/A'
        
            try:
                if blocks[i].text.split('\n')[3].split('|')[1].split('%')[1] == '':
                    cap = float(blocks[i].text.split('\n')[3].split('|')[1].split(':')[1][1:-1])/100
                else:
                    cap = float(blocks[i].text.split('\n')[3].split('|')[1].split('%')[0][1:])/100
            except:
                cap = 'N/A'
    
            info = prop, city, state, price, cap, 'NNN Retail Investment Group'
    
            middle.loc[i] = info
    
        rig = rig.append(middle, sort = True)
    prop_list = prop_list.append(rig, sort = True)

except Exception:
    print('Error with NNN Retail Investment Group')

try:
    ##Realty Link Dev
    #Getting the page
    realtylink_url = 'http://www.realtylinkdev.com/investment-sales/'

    #Making soup
    uClient = uReq(realtylink_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'col-lg-8 col-md-8 col-xs-12 col-sm-12'})

    realtylinkdev = pd.DataFrame(columns = ['Property', 'Address','City', 'State', 'SF', 'Acres', 'Cap Rate', 'Price', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].h4.text
        address = blocks[i].text.split('\n')[2].split('\r')[0]
        loc = blocks[i].text.split('\n')[3]
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:4]
    
        if prop.split('(')[-1] == 'In Contract)':
            status = 'In Contract'
        elif prop.split('(')[-1] == 'Sold)':
            status = 'Sold'
        else:
            status = 'For Sale'
        
        a = blocks[i].findAll('p')
    
        for y in range(len(a)):
            if a[y].text[:5] == 'Price':
                p = a[y].text.split(':')[1]
                if p[:3] == 'Con' or p[:3] == 'Cal':
                    price = 'Contact Broker For Details'
                else:
                    try:
                        price = int(p.replace('$', '').replace(',',''))
                    except:
                        price = p
             
            elif a[y].text[:4] == 'Cap ':
                try:
                    cap = float(a[y].text.split(':')[1].replace('%',''))/100
                except:
                    cap = a[y].text.split(':')[1]
                
            elif a[y].text[:4] == 'Acre':
                acres = a[y].text.split(':')[1]
            
            elif a[y].text[:4] == 'Squa':
                sf = a[y].text.split(':')[1]
            
            else:
                pass

        info = prop, address, city, state, sf, acres, cap, price, status, 'Realty Link Dev'   

        realtylinkdev.loc[i] = info

    prop_list = prop_list.append(realtylinkdev, sort = True)

except Exception:
    print('Error with Realty Link Dev')

try:
    ##Pinnacle Real Estate Advisors
    #Getting the page
    pinn_url = 'http://listings.pinnaclerea.com/'

    #Making soup
    uClient = uReq(pinn_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    pinn = pd.DataFrame(columns = ['Property', 'Type', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])

    blocks = page_soup.findAll('div', {'class':'deal'})

    for i in range(len(blocks)):

        b = blocks[i].find('div', {'class': 'status-bar'})
    
        status = b.text
        if status != 'SOLD':
            a = blocks[i].find('div', {'class': 'dealInfo'})
    
            prop = a.text.split('\r\n')[2]
            sector = a.text.split('\r\n')[3]
            loc = a.text.split('\r\n')[4]
            try:
                city = loc.split(',')[0]
                state = loc.split(',')[1][1:3]
            except:
                city = 'N/A'
                state = 'N/A'
    
            p = a.text.split('\r\n')[5].split(':')[1]

            if p[1] == '$':
                price = int(p[2:].replace(',',''))
            else:
                price = p

            c = a.text.split('\r\n')[7].split(':')[1].split('%')[0]
            try:
                cap = float(c)/100
            except:
                cap = 'N/A'
        else:
            break

        info = prop, sector, city, state, price, cap, status, 'Pinnacle Real Estate Advisors'
        pinn.loc[i] = info
    
    prop_list = prop_list.append(pinn, sort = True)

except Exception:
    print('Error with Pinnacle Real Estate Advisors')

try:
    ##Matysek Investment Group
    #Getting the page
    mig_url = 'https://matysekinvestment.com/off-market-deals/'

    #Making soup
    uClient = uReq(mig_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('td')

    mig = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Lease Term', 'Lease Type', 'Notes', 'Source'])

    for i in range(int(len(blocks)/8)):
        prop = blocks[i*8].text
        city = blocks[(i * 8)+ 1].text
        state = blocks[(i * 8)+ 2].text

        try:    
            price = int(blocks[(i * 8)+ 3].text.replace(',','')[1:])
        except:
            price = blocks[(i * 8)+ 3].text

        try:
            cap = float(blocks[(i * 8)+ 4].text[:-1])/100
        except:
            cap = blocks[(i * 8)+ 4].text

        lease_term = blocks[(i * 8)+ 5].text
        lease_type = blocks[(i * 8)+ 6].text
        lead_broker = blocks[(i * 8)+ 7].text
    
        info = prop, city, state, price, cap, lease_term, lease_type, lead_broker, 'Matysek Investment Group Off-Market'
        mig.loc[i] = info

except Exception:
    print('Error with Matysek Investment Group Off-Market')
    mig = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Lease Term', 'Lease Type', 'Notes', 'Source'])

try:
    ##Matysek Investment Group

    #Getting the second page
    mig_2_url = 'https://matysekinvestment.com/listing/'

    #Making soup again
    uClient = uReq(mig_2_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    block_2 = page_soup.findAll('div', {'class':'col-md-4 bx4img'})
    b = page_soup.findAll('div', {'class':'single1'})

    mig['SF'] = 'N/A'
    mig['Sale Status'] = 'N/A'

    length = len(mig)

    for i in range(len(block_2)):
        prop = block_2[i].h2.text.strip()
        status = block_2[i].a.text.strip()
        loc = block_2[i].h6.text
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:]
        notes = block_2[i].p.text
    
        prop_type = b[i].text.split('\n')[1].strip()
    
        try:
            price = int(b[i].text.split('\n')[4].replace(',','').replace('$',''))
        except:
            price = b[i].text.split('\n')[4]
        
        try:
            cap = float(b[i].text.split('\n')[5].split('%')[0])/100
        except:
            cap = b[i].text.split('\n')[5]
    
        stuff = b[i].text.split('\n')[6]
        if stuff[-4:] == 'Term':
            lease_term = stuff
            sf = 'N/A'
        elif stuff[-8:] == 'Building':
            lease_term = 'N/A'
            sf = stuff
        else:
            lease_term = 'N/A'
            sf = 'N/A'
        
        info = prop, city, state, price, cap, lease_term, prop_type, notes, 'Matysek Investment Group', sf, status
        mig.loc[(length + i)] = info

    prop_list = prop_list.append(mig, sort = True)

except Exception:
    print('Error with Matysek Investment Group')
    prop_list = prop_list.append(mig, sort = True)

try:
    ##Sharko Weisenbeck Property Advisors
    #Getting the page
    sw_url = 'http://swpropertyadvisors.com/listings/'

    #Making soup
    uClient = uReq(sw_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('li')

    sw = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        try:
            prop = blocks[i].h4.text
        except:
            prop = 'N/A'
    
        details = blocks[i].findAll('p')
    
        city = 'N/A'
        state = 'N/A'
        price = 'N/A'
        cap = 'N/A'
    
        for y in range(len(details)):
            if details[y].text[:5] == 'city:':
                city =  details[y].text[6:]
            else:
                pass
        
            if details[y].text[:6] == 'state:':
                state = details[y].text[7:]
            else:
                pass
        
            if details[y].text[:6] == 'price:':
                p = details[y].text[7:]
                try:
                    price = int(p.replace(',','').replace('$',''))
                except:
                    price = p
            else:
                pass
        
            if details[y].text[:4] == 'cap:':
                c = details[y].text[5:]
                try:
                    cap = float(c.replace('%',''))/100
                except:
                    cap = c
            else:
                pass        
        
        try:
            status = blocks[i].div.text
        except:
            status = 'Available'
    
        if prop != 'N/A':
            info = prop, city, state, price, cap, status, 'Sharko Weisenbeck Property Advisors'
            sw.loc[i] = info   
        else:
            pass

    prop_list = prop_list.append(sw, sort = True)

except Exception:
    print('Error with Sharko Weisenbeck Property Advisors')

try:
    ##Brisky Net Lease
    #Getting the page
    brisky_url = 'http://www.briskynetlease.com/listings/'

    #Making soup
    headers = {'User-Agent':'Mozilla/5.0'}
    page = requests.get(brisky_url, headers = headers)
    page_soup = soup(page.text, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'listing-wrap'})

    brisky = pd.DataFrame(columns = ['Property', 'Address', 'City', 'State', 'Price', 'Cap Rate', 'Lease Type', 'SF', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        loc = blocks[i].find('p', {'class':'listing-address'})
        address = loc.span.text
        city_state = loc.text[len(address):]
        city = city_state.split(',')[0]
        state = city_state.split(',')[1][1:3]
    
        p = blocks[i].h3.text
        
        if p[:len(city)] == city:
            prop = p[(len(city_state)-5) :]
        else:
            prop = p

        try:
            price = int(blocks[i].find('span', {'class':'listing-price'}).text.replace(',','').replace('$',''))
            cap = float(blocks[i].find('span', {'class':'listing-text'}).text.split('%')[0])/100
        except:
            price = 'N/A'
            cap = 'N/A'
    
        lease_type = blocks[i].find('li', {'class':'baths'}).text.split('Lease')[0]
        sf = blocks[i].find('li', {'class':'sqft'}).text.split('Sq')[0]
    
    
        status = blocks[i].span.text
    
        info = prop, address, city, state, price, cap, lease_type, sf, status, 'Brisky Net Lease'
    
        brisky.loc[i] = info
    
    prop_list = prop_list.append(brisky, sort = True)

except Exception:
    print('Error with Brisky Net Lease')

try:
    ##Landmark Invesment Sales
    #Getting the page
    landmark_url = 'https://landmarkinvestmentsales.com/properties-available/'

    #Making soup
    headers = {'User-Agent':'Mozilla/5.0'}
    page = requests.get(landmark_url, headers = headers)
    page_soup = soup(page.text, 'html.parser')

    blocks = page_soup.findAll('article')

    landmark = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Notes', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].h3.text
    
        details = blocks[i].findAll('span')
        loc = 'N/A'
        price = 'N/A'
        cap = 'N/A'
        notes = 'N/A'
        for y in range(len(details)):
            if details[y].text[:9] == 'Location:':
                loc = details[y].text[10:]
                city = loc.split(',')[0]
                state = loc.split(',')[1][1:]
            else:
                pass
        
            if details[y].text[:12] == 'Sales Price:':
                try:
                    price = int(details[y].text[13:].replace(',','').replace('$',''))
                except:
                    price = details[y].text[13:]
            else:   
                pass
        
            if details[y].text[:9] == 'Cap Rate:':
                try:
                    cap = float(details[y].text[10:].replace('%',''))/100
                except:
                    cap = details[y].text[10:]
            else:
                pass
        
            if details[y].text[:17] == 'Lease Expiration:':
                notes = details[y].text[18:]
            else:
                pass
    
        info = prop, city, state, price, cap, notes, 'Landmark Investment Sales'

        landmark.loc[i] = info

    prop_list = prop_list.append(landmark, sort = True)

except Exception:
    print('Error with Landmark Invesment Sales')

try:
    ##Upland Real Estate Group
    #Getting the page
    upland_url = 'http://www.upland.com/users/properties.cfm'

    #Making soup
    uClient = uReq(upland_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('td', {'width':'100%'})

    upland = pd.DataFrame(columns = ['Property', 'City', 'State', 'Property Type', 'Price', 'Cap Rate', 'Acres', 'SF', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].find('td', {'class':'medtitle3'}).text.strip()
        loc = blocks[i].find('td', {'class':'data5blue'}).text.strip()
        city = loc.split('|')[0]
        state = loc.split('|')[1]
        status = blocks[i].find('td', {'class':'data7'}).text.strip()
    
        details = blocks[i].findAll('td', {'class':'data4'})
    
        status = 'N/A'
        prop_type = 'N/A'
        cap = 'N/A'
        lot_size = 'N/A'
        price = 'N/A'
        sf = 'N/A'
    
        for y in range(len(details)):
            if details[y].text[:14] == 'PROPERTY TYPE:':
                prop_type = details[y].text[15:]
            else:
                pass
        
            if details[y].text[:7] == 'STATUS:':
                status = details[y].text[8:]
            else:   
                pass
            
            if details[y].text[:9] == 'CAP RATE:':
                try:
                    cap = float(details[y].text[10:].replace('%',''))/100
                except:
                    cap = details[y].text[10:]
            else:
                pass

            if details[y].text[:12] == 'LOT ACREAGE:':
                lot_size = details[y].text[13:]
            else:
                pass

            if details[y].text[:11] == 'SALE PRICE:':
                try:
                    price = int(details[y].text[12:].replace(',','').replace('$',''))
                except: 
                    price = details[y].text[12:]
            else:
                pass
            
            if details[y].text[:12] == 'BUILDING SF:':
                sf = details[y].text[13:]
            else:
                pass       
    
        info = prop, city, state, prop_type, price, cap, lot_size, sf, status, 'Upland Real Estate Group'
        
        upland.loc[i] = info

    upland = upland[upland['Price'] != 'N/A']

    prop_list = prop_list.append(upland, sort = True)

except Exception:
    print('Error with Upland Real Estate Group') 

try:
    ##Cambridge Capital Advisors
    #Getting the page
    cca_url = 'http://www.cambridgeca.com/property'

    #Making soup
    uClient = uReq(cca_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'property'})

    cca = pd.DataFrame(columns = ['Property', 'Address', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].h2.text
    
        details = blocks[i].p.text.split('\n\t\t')
        address = details[1]
        loc = details[2].split(',')
        city = loc[0]
        state = loc[1][1:]
        try:
            price = int(details[3].replace('$','').replace(',',''))
        except:
            price = details[3]
        try:
            cap = float(details[5].split(':')[1][1:].replace('%',''))/100
        except:
            cap = details[5]
        status = details[6].split('\t')[0]
    
        info = prop, address, city, state, price, cap, status, 'Cambridge Capital Advisors'
    
        cca.loc[i] = info

    prop_list = prop_list.append(cca, sort = True)

except Exception:
    print('Error with Cambridge Capital Advisors') 

try:
    ##Isaac Group
    #Getting the page
    isaac_url = 'http://www.isaacbrokerage.com/get_listings.cfm'

    #Making soup
    uClient = uReq(isaac_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'listing'})

    isaac = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Type', 'Sale Status', 'Source'])

    for y in range(len(blocks)):
        prop = blocks[y].h1.text
        loc = blocks[y].h2.text
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:]
    
    
        price = 'N/A'
        cap = 'N/A'
        prop_type = 'N/A'
        status = 'N/A'
    
        a = blocks[y].findAll('tr')
    
        for i in range(len(a)):
            if a[i].text.split(':')[0].strip() == 'Price':
                p = a[i].text.split(':')[1].strip()
                try:
                    price = int(p.replace(',','').replace('$',''))
                except:
                    price = p
            else:
                pass
        
            if a[i].text.split(':')[0].strip() == 'Cap Rate':
                c = a[i].text.split(':')[1].strip()
                try:
                    cap = float(c.replace('%',''))/100
                except:
                    cap = c
            else:
                pass
        
            if a[i].text.split(':')[0].strip() == 'Type':
                prop_type = a[i].text.split(':')[1].strip()
            else:
                pass
        
            if a[i].text.split(':')[0].strip() == 'Status':
                status = a[i].text.split(':')[1].strip()
            else:
                pass
    
        info = prop, city, state, price, cap, prop_type, status, 'Isaac Group'

        isaac.loc[y] = info

    prop_list = prop_list.append(isaac, sort = True)

except Exception:
    print('Error with Isaac Group') 

try:
    ##Iacono Retail Group
    #Getting the page
    iacono_url = 'http://www.iaconoretailgroup.com/listings/'

    #Making soup
    uClient = uReq(iacono_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div',{'class':'info'})

    iac = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'SF', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        pr = blocks[i].h3.text
        try:
            prop = pr.split('-')[0]
        except:
            prop = pr
        loc = blocks[i].h6.text.strip()
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:]
    
        stats = blocks[i].findAll('p')
    
        for y in range(len(stats)):
            
            p = stats[0].text
        
            try:
                price = int(p.replace(',','').replace('$',''))
            except:
                price = p
            
            cap = stats[1].text
        
            try:
                cap_rate = float(cap.replace('%',''))/100
            except:
                cap_rate = cap
            
            sf = stats[2].text
            status = stats[3].text
        
        info = prop, city, state, price, cap_rate, sf, status, 'Iacono Retail Group'
        iac.loc[i] = info
        iacono = iac[iac['Sale Status'] != 'Closed']

    prop_list = prop_list.append(iacono, sort = True)

except Exception:
    print('Error with Iacono Retail Group')

try:
    #NNN Pros
    nnn_pros = pd.DataFrame(columns = ['Property', 'City', 'State', 'Cap Rate', 'Price', 'SF', 'Notes', 'Source'])
    middle_list = pd.DataFrame(columns = ['Property', 'City', 'State', 'Cap Rate', 'Price', 'SF', 'Notes', 'Source'])

    for y in range(1,31):
        nnn_pro_url = 'http://www.nnnpro.com/properties-listing/page/' + str(y)
        headers = {'User-Agent':'Mozilla/5.0'}
        page = requests.get(nnn_pro_url, headers = headers)
        page_soup = soup(page.text, 'html.parser')
    
        blocks = page_soup.findAll('div', {'class':'property_listing'})
    
        for i in range(len(blocks)):
            prop = blocks[i].h4.text.strip()
        
            loc = blocks[i].find('div', {'class':'property_location'}).div.text
            city = loc.split(',')[0]
            state = loc.split(',')[1].strip()
        
            try:
                c = blocks[i].find('div', {'class':'property_location'}).span.text.split('%')[0]
                try:
                    cap = float(c)/100
                except:
                    cap = c
                noi = blocks[i].find('div', {'class':'property_location'}).span.nextSibling.text.split('R')[0]
                sf = blocks[i].find('div', {'class':'property_location'}).span.nextSibling.nextSibling.nextSibling.text.split('Sq')[0]
            except:
                cap = 'N/A'
                noi = 'N/A'
                sf = 'N/A'
            
            p = blocks[i].find('div', {'class':'listing_unit_price_wrapper'}).text.strip()
            try:
                price = int(p.replace(',','').replace('$',''))
            except:
                price = p

            info = prop, city, state, cap, price, sf, noi, 'NNN Pros'
        
            middle_list.loc[i] = info
    
        nnn_pros = nnn_pros.append(middle_list, sort = True)

    prop_list = prop_list.append(nnn_pros, sort = True)

except Exception:
    print('Error with NNN Pro Group')

try:
    ##Barr & Benne
    #Getting the page
    b_b_url = 'https://nnninvestmentgroup.com/buy-commercial-property/'

    #Making Soup
    headers = {'User-Agent':'Mozilla/5.0'}
    page = requests.get(b_b_url, headers = headers)
    page_soup = soup(page.text, 'html.parser')

    blocks = page_soup.findAll('div', {'id':'bbnl_property_fields'})

    b_b = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].text.split('|')[0]
    
        details = blocks[i].findAll('li')
    
        loc = details[0].text
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:]
    
        p = details[1].text
        try:
            price = int(p.replace('$','').replace(',',''))
        except:
            price = p
        c = details[2].text.split(':')[-1][1:]
        try:
            cap = float(c.replace('%',''))/100
        except:
            cap = c
        status = details[3].text.split(':')[-1][1:]
    
        info = prop, city, state, price, cap, status, 'Barr & Benne'
        b_b.loc[i] = info

    prop_list = prop_list.append(b_b, sort = True)

except Exception:
    print('Error with Barr & Benne')

try:
    ##NNN Investment Advisors
    #Getting the page
    nnn_ia_url = 'https://nnninvestmentadvisors.com/properties/'

    #Making soup
    uClient = uReq(nnn_ia_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'landz-box-property box-home'})

    nnn_ia = pd.DataFrame(columns = ['Property', 'Price', 'Cap Rate', 'City', 'State', 'Source'])

    for y in range(1,5):
        nnn_ia_url = 'https://nnninvestmentadvisors.com/properties/page/' + str(y)
    
        uClient = uReq(nnn_ia_url)
        page_html = uClient.read()
        page_soup = soup(page_html, 'html.parser')
    
        blocks = page_soup.findAll('div', {'class':'landz-box-property box-home'})
    
        middle_list = pd.DataFrame(columns = ['Property', 'Price', 'Cap Rate', 'City', 'State', 'Source'])
    
        for i in range(len(blocks)):
            prop = blocks[i].span.nextSibling.nextSibling.text.strip()
            loc = blocks[i].p.text
            city = loc.split(',')[0]
            state = loc.split(',')[1]
            p = blocks[i].span.text
            try:
                price = int(p.replace('$','').replace(',',''))
            except:
                price = p
            c = blocks[i].dd.text
            try:
                cap = float(c.replace('%',''))/100
            except:
                cap = c
        
            info = prop, price, cap, city, state, 'NNN Investment Advisors'
        
            middle_list.loc[i] = info
    
        nnn_ia = nnn_ia.append(middle_list, sort = True)    

    prop_list = prop_list.append(nnn_ia, sort = True)

except Exception:
    print('Error with NNN Investment Advisors')

try:
    ##Ground and Space Partners
    #Getting the page
    gs_url = 'https://groundandspacepartners.com/active-listings/'

    #Making soup
    uClient = uReq(gs_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'active-listings__list-item'})

    gs = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Source'])

    for i in range(len(blocks)):
        prop = blocks[i].div.nextSibling.nextSibling.div.div.text
    
        loc = blocks[i].div.nextSibling.nextSibling.div.div.nextSibling.nextSibling.text
        city = loc.split(',')[0]
        state = loc.split(',')[1][1:]
    
        details = blocks[i].findAll('span')
    
        p = 'N/A'
        c = 'N/A'
    
        for y in range(len(details)):
            if details[y].text.strip() == 'Price':
                p = details[y + 1].text.strip()
            else:
                pass
        
            if details[y].text.strip() == 'Cap Rate':
                c = details[y +1].text.strip()
            else:
                pass
    
        try:
            price = int(p.replace(',','').replace('$',''))
        except:
            price = p
    
        try:
            cap = float(c.replace('%',''))/100
        except:
            cap = c
        
        info = prop, city, state, price, cap, 'Ground and Space'
    
        gs.loc[i] = info

    prop_list = prop_list.append(gs, sort = True)

except Exception:
    print('Error with Ground and Space Partners')

try:
    ##Ben-Moshe Brothers
    #Getting the page
    bm_url = 'https://www.caprates.com/listings.html'

    #Making Soup
    uClient = uReq(bm_url)
    page_html = uClient.read()
    page_soup = soup(page_html, 'html.parser')

    blocks = page_soup.findAll('div', {'class':'panel text-center'})

    bm = pd.DataFrame(columns = ['Property', 'City', 'State', 'Price', 'Cap Rate', 'Sale Status', 'Acres', 'Source'])

    for i in range(len(blocks)):
        status = blocks[i].h3.text
        tenant = blocks[i].strong.text
        loc = blocks[i].findAll('strong')[-1].text
    
        city = loc.split(',')[0]
        state = loc.split(',')[-1][1:]
    
        price = 'N/A'
        cap = 'N/A'
        lot = 'N/A'
    
        a = blocks[i].find('div', {'class':'panel-footer'})
                               
        for y in range(len(a.findAll('h2'))):
            b = a.findAll('h2')
    
            if b[y].text.split(':')[0] == 'Price':
                price = b[y].text.split(':')[1]
                try:
                    price = int(price.replace('$','').replace(',',''))
                except:
                    pass
            else:
                pass
    
            if b[y].text.split(':')[0] == 'Cap Rate':
                c = b[y].text.split(':')[1]
                try:
                    cap = float(cap.replace('%',''))/100
                except:
                    pass
            else:
                pass
    
            if b[y].text.split(':')[0] == 'Lot Size':
                lot = b[y].text.split(':')[1]
            else:
                pass
    
        info = tenant, city, state, price, cap, status, lot, 'Ben-Moshe Brothers'
        bm.loc[i] = info

    bm = bm[bm['Sale Status'] != 'Successfully Sold']

    prop_list = prop_list.append(bm, sort = True)

except Exception:
    print('Error with Ben-Moshe Brothers')

print('\n' + 'Number of Brokerages Scraped:  ' + str(prop_list['Source'].nunique()) + '\n')

print('End of the Scrape --- %s seconds ---' % (time.time() - start_time))

prop_list = prop_list[['Property', 'City', 'State', 'Price', 'Cap Rate', 'Type', 'Sale Status', 'Source', 'Address', 'Notes', 'Lease Type', 'Lease Term', 'SF', 'Acres']]

prop_list = prop_list.reset_index()

'''
length = prop_list.shape[0]

for i in range(length):
	if prop_list['Sale Status'][i] == 'Sold':
		prop_list = prop_list.drop(i, inplace = True)
	elif prop_list['Sale Status'][i] == 'Under Contract or LOI':
		prop_list = prop_list.drop(i, inplace = True)
	elif prop_list['Sale Status'][i] == 'In Escrow':
		prop_list = prop_list.drop(i, inplace = True)
	elif prop_list['Sale Status'][i] == 'Contract':
		prop_list = prop_list.drop(i, inplace = True)
	else:
		pass
'''
prop_list.drop('index', axis = 1, inplace = True)

prop_list['Change'] = 'Yes'
prop_list['Main Change'] = 'N/A'
prop_list['Week to Week Change'] = 'N/A'
prop_list['Previous Price'] = 'N/A'
prop_list['Price Change ($)'] = 'N/A'
prop_list['Price Change (%)'] = 'N/A'
prop_list['Previous Cap Rate'] = 'N/A'

for i in range(len(prop_list)):
    for y in range(len(old_list)):
        if prop_list['Property'][i] == old_list['Property'][y] and prop_list['City'][i] == old_list['City'][y] and prop_list['State'][i] == old_list['State'][y] and prop_list['Price'][i] == old_list['Price'][y] and prop_list['Source'][i] == old_list['Source'][y]:
            prop_list['Change'][i] = 'No'

        elif prop_list['Property'][i] == old_list['Property'][y] and prop_list['City'][i] == old_list['City'][y] and prop_list['State'][i] == old_list['State'][y] and prop_list['Source'][i] == old_list['Source'][y]:
            prop_list['Main Change'][i] = 'No'
            prop_list['Previous Price'][i] = old_list['Price'][y]
            try:
                prop_list['Price Change ($)'][i] = (prop_list['Price'][i] - old_list['Price'][y])
            except:
                prop_list['Price Change ($)'][i] = 'Other Change'
            try:
                prop_list['Price Change (%)'][i] = prop_list['Price Change ($)'][i] / old_list['Price'][y]
            except:
                prop_list['Price Change (%)'][i] = 'Other Change'

            prop_list['Previous Cap Rate'][i] = old_list['Cap Rate'][y]

        else:
            pass
'''        
for i in range(len(prop_list)):
    for y in range(len(old_list)):
        if prop_list['Property'][i] == old_list['Property'][y] and prop_list['City'][i] == old_list['City'][y] and prop_list['State'][i] == old_list['State'][y]:
            prop_list['Main Change'][i] = 'No'
            prop_list['Previous Price'][i]= old_list['Price'][y]
        else:
            pass
'''
        
for i in range(len(prop_list)):
    if prop_list['Change'][i] == 'No':
        prop_list['Week to Week Change'][i] = 'No'
        prop_list['Previous Price'][i] = 'N/A'

    elif prop_list['Change'][i] == 'Yes' and prop_list['Main Change'][i] == 'No':
        prop_list['Week to Week Change'][i] = 'Price Change'
        prop_list['Previous Price'][i] = prop_list['Previous Price'][i]

    elif prop_list['Change'][i] == 'Yes' and prop_list['Main Change'][i] == 'N/A':
        prop_list['Week to Week Change'][i] = 'New Property'
        prop_list['Previous Price'][i] = 'N/A'

    else:
        prop_list['Week to Week Change'][i] = 'Error'

print('End of Comparing --- %s seconds ---' % (time.time() - start_time))

old_list['Dropped'] = 'Yes'

for i in range(len(prop_list)):
    for y in range(len(old_list)):
        if prop_list['Property'][i] == old_list['Property'][y] and prop_list['City'][i] == old_list['City'][y] and prop_list['State'][i] == old_list['State'][y] and prop_list['Source'][i] == old_list['Source'][y]:
            old_list['Dropped'][y] = 'No'
        else:
            pass

dropped_list = old_list[old_list['Dropped'] == 'Yes']

dropped_list.reset_index(inplace = True)

for i in range(len(dropped_list)):
    if dropped_list['Week to Week Change'][i] == 'New Property' or dropped_list['Week to Week Change'][i] == 'Price Change':
        dropped_list.drop(i, inplace = True)
    else:
        pass

stats = pd.DataFrame(columns = ['Number of Brokerages', 'Number of Listings', '# of Price Changes','# of Properties Dropped from Week to Week'])

stats.loc[0] = 0

stats['Number of Brokerages'] = prop_list['Source'].nunique()
stats['Number of Listings'] = len(prop_list)
stats['# of Price Changes'] = len(prop_list[prop_list['Week to Week Change'] == 'Price Change'])
stats['# of Properties Dropped from Week to Week'] = len(dropped_list)

'''       
for i in range(len(prop_list)):
    if prop_list['Week to Week Change'][i] == 'Price Change':
        prop_list['Previous Price'][i] = prop_list['Previous Price'][i]
    else:
        prop_list['Previous Price'][i] = 'N/A'

        '''

print('End of Stats Loop --- %s seconds ---' % (time.time() - start_time))

prop_list = prop_list[['Property', 'City', 'State', 'Price', 'Cap Rate', 'Type', 'Sale Status', 'Source', 'Address', 'Notes', 'Lease Type', 'Lease Term', 'SF', 'Acres', 'Week to Week Change', 'Previous Price', 'Price Change ($)', 'Price Change (%)', 'Previous Cap Rate']]

#Getting a timestamp
datetime = datetime.datetime.now()

writer = pd.ExcelWriter('OBL ' + str(datetime.month) + ' - ' + str(datetime.day) + '.xlsx', engine = 'xlsxwriter')
prop_list.to_excel(writer, sheet_name = 'OBL', columns = prop_list.columns)
dropped_list.to_excel(writer, sheet_name = 'Dropped From Last Week', columns = dropped_list.columns)
stats.to_excel(writer, sheet_name = 'Stats', columns = stats.columns)
writer.save()

print('End of Program --- %s seconds ---' % (time.time() - start_time))