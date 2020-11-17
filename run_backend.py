# Function that creates file with predictions that serves app

from get_data import *
from prediction import *
import time

# Sympla: Headers Page
headers_page = {'authority': 'www.sympla.com.br',
           'method': 'GET',
           'scheme': 'https',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-fetch-dest': 'document',
           'sec-fetch-mode': 'navigate',
           'sec-fetch-site': 'none',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
          }

# Sympla: Headers API
headers_api = {'authority': 'bff-sales-api-cdn.bileto.sympla.com.br',
           'method': 'GET',
           'scheme': 'https',
           'accept': 'application/json', 
           'accept-encoding': 'gzip, deflate, br',
           'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
           'origin': 'https://bileto.sympla.com.br' ,
           'referer': 'https://bileto.sympla.com.br/',
           'sec-fetch-dest': 'empty',
           'sec-fetch-mode': 'cors',
           'sec-fetch-site': 'same-site',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
           'x-api-key': 'cQkazy2Wc'
          }

platforms = ['sympla', 'eventbrite']
    
def update_db():
    with open("new_events.json", 'w+') as output:
        for platform in platforms:
            # Take first 2 search pages from each website
            for page in range(1,3):
                if platform == 'eventbrite':
                    search_page = get_search_page(platform, page)
                elif platform == 'sympla':
                    search_page = get_search_page(platform, page, headers=headers_page)
                event_list = parse_search_page(platform, search_page)
                
                for event in event_list:
                    if platform == 'eventbrite':
                        event_page = get_event_page(event['link'])
                        event_data = parse_event_page(platform, event_page)
                    elif platform == 'sympla':
                        time.sleep(0.75)
                        if re.search("bileto", event['link']) != None:
                            event_api_data = get_event_api_data(event['link'], headers=headers_api)
                            event_data = parse_event_api_data(platform, event_api_data)
                        else:
                            event_page = get_event_page(event['link'], headers=headers_page)
                            event_data = parse_event_page(platform, event_page)
                   
                    if event_data['name'] != '':
                        prediction = compute_prediction(event_data)
                        event_data_front = {"link": event['link'], "name": event_data['name'], "prediction": float(prediction), 'platform': event_data['platform']}
                        output.write("{}\n".format(json.dumps(event_data_front, ensure_ascii=False)))
    return True