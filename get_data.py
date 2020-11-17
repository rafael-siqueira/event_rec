# Functions that collect recent events' data for prediction

import requests as rq
import bs4 as bs4
import re
import time
import pandas as pd

def get_search_page(platform, page, headers=None):

    if platform == 'eventbrite':
        url = "https://www.eventbrite.com.br/d/brazil--s%C3%A3o-paulo/all-events/?page={page}"
    elif platform == 'sympla':
        url = "https://www.sympla.com.br/eventos/sao-paulo-sp?ordem=data&pagina={page}&value=sao-paulo-sp"
    response = rq.get(url.format(page=page), headers=headers)
    return response.text

def parse_search_page(platform, html_page):
    
    parsed_html = bs4.BeautifulSoup(html_page, 'html.parser')
    event_list = []
    
    if platform == 'eventbrite':
        tags = parsed_html.find_all('div', attrs={'class': 'eds-event-card-content__content'})      
    elif platform == 'sympla':
        tags = parsed_html.find_all('a', attrs={'class': 'sympla-card card-normal w-inline-block'})
        
    for t in tags:
        if platform == 'eventbrite':
            link = t.find('a', attrs={'class': 'eds-event-card-content__action-link'})['href']
            name_aux = t.find('div', attrs={'class': 'eds-is-hidden-accessible'}).text
        elif platform == 'sympla':
            link = t['href']
            name_aux = t.find('div', attrs={'class': 'event-name event-card'}).text
        name = re.sub(' +', ' ', name_aux)
        event_data = {"link": link, "name": name}
        event_list.append(event_data)
        
    # Remove duplicate events
    event_list = [dict(tuple_) for tuple_ in {tuple(sorted(dict_.items())) for dict_ in event_list}]
            
    return event_list

def get_event_page(url, headers=None):
    return rq.get(url, headers=headers).text

def parse_event_page(platform, html_page):
    
    parsed_html = bs4.BeautifulSoup(html_page, 'html.parser')
    name, organizer, date, description, location, price, info = '', '', '', '', '', '', ''
    
    if platform == 'eventbrite':
        # Name
        if parsed_html.find('h1', attrs={"class":re.compile(r"listing")}) != None:
            name = parsed_html.find('h1', attrs={"class":re.compile(r"listing")}).text.strip()
        # Organizer
        if parsed_html.find('div', attrs={"class":re.compile(r"title")}) != None:
            organizer = parsed_html.find('div', attrs={"class":re.compile(r"title")}).text.strip()  
        # Date
        #if parsed_html.find('p', attrs={'class', re.compile(r"date-time-first-line")}) != None:
            #date = parsed_html.find('p', attrs={'class', re.compile(r"date-time-first-line")}).get_text(" ").strip()
        # Description
        if parsed_html.find('div', attrs={"class":re.compile(r"structured-content g-cell g-cell-10-12 g-cell")}) != None:
            description = parsed_html.find('div', attrs={"class":re.compile(r"structured-content g-cell g-cell-10-12 g-cell")}).get_text(" ").strip()
        # Location
        if parsed_html.find_all("div", attrs={'class': 'event-details__data'}) != None:
            location = parsed_html.find_all("div", attrs={'class': 'event-details__data'})[1].get_text(" ").strip()     
        # Price
        #if parsed_html.find("div", attrs={'class': 'js-display-price'}) != None:
            #price = parsed_html.find("div", attrs={'class': 'js-display-price'}).text.strip()
    
    elif platform == 'sympla':
        # Name
        if parsed_html.find('h1') != None:
            name = parsed_html.find('h1').text.strip()
        # Dates
        #if parsed_html.find('div', attrs={"class":'event-info-calendar'}) != None:
            #date = parsed_html.find('div', attrs={"class":'event-info-calendar'}).text.strip()
        # Location
        if parsed_html.find('div', attrs={"class":'event-info-city'}) != None:
            location = parsed_html.find('div', attrs={"class":'event-info-city'}).text.strip()  
        # Organizer
        if parsed_html.find('div', attrs={"id":'produtor'}) != None:
            org_aux = parsed_html.find('div', attrs={"id":'produtor'})
            if org_aux.find('h4', attrs={"class":re.compile(r"kill")}) != None:
                organizer = org_aux.find('h4', attrs={"class":re.compile(r"kill")}).text.strip()
        # Description
        if parsed_html.find('div', attrs={"id":'event-description'}) != None:
            description = parsed_html.find('div', attrs={"id":'event-description'}).get_text(" ").strip()
            description = re.sub(' +', ' ', description)
        # Price, first one
        #if parsed_html.find('form', attrs={"id":'ticket-form'}) != None:
            #price_aux = parsed_html.find('form', attrs={"id":'ticket-form'})
            #if len(price_aux.find_all('span')) >= 3:
                #price = price_aux.find_all('span')[2].text.strip()
    
    event_data = dict()
    event_data['platform'] = platform
    event_data['name'] = name
    event_data['location'] = location
    event_data['description'] = description
    event_data['organizer'] = organizer
    #event_data['date'] = date
    #event_data['price'] = price

    return event_data

def get_event_api_data(url, headers=None):
    
    # Build API request
    event_id = re.search("event/(\d*)\/?", url).group(1)
    api = 'https://bff-sales-api-cdn.bileto.sympla.com.br/api/v1/events/{event_id}'.format(event_id=event_id)
    response = rq.get(api, headers=headers)
    if response.status_code == 404:
        event_api_data = None
    else:
        event_api_data = response.json()
    return event_api_data
    
def parse_event_api_data(platform, event_api_data):
    
    event_data = dict()
    
    if event_api_data != None:
        df = pd.json_normalize(event_api_data)

        event_data['platform'] = platform
        event_data['name'] = df['data.name'][0]
        event_data['location'] = df['data.venue.locale.address'][0]
        
        if ('data.planner_information.corporate_name' in df.columns):
            organizer = df['data.planner_information.corporate_name'][0]
            organizer = organizer.split('|')
            event_data['organizer'] = organizer[0].strip()
        else:
            event_data['organizer'] = df['data.venue.name'][0]
        
        if ('data.description.raw' in df.columns):
            desc_html = bs4.BeautifulSoup(df['data.description.raw'][0], 'html.parser')
            description = desc_html.get_text(' ').strip()
            description = re.sub("\n|\xa0","", description)
            event_data['description'] = description
        else:
            event_data['description'] = ''
        #event_data['date'] = ''
        #event_data['price'] = ''

    return event_data