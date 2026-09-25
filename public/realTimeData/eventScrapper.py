from bs4 import BeautifulSoup
from selenium import webdriver
import schedule
import re
import time
import json

#Scrapper class that get the event information from the website
def scrapperEvents():
    #options on loading the driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    #Grab the web api of the gobbler connect website that will collect the meta data of the events
    event_urls = webdriver.Chrome(options=options)
    event_urls.get("https://gobblerconnect.vt.edu/events")
    
    #Next we want to parse the url request through html format 
    #after the url is fetched by the driver
    time.sleep(3)
    event_soup = BeautifulSoup(event_urls.page_source, "html.parser")
    event_urls.quit()
    
    #After that we want to locate the dev container that holds the information for the website
    #We are looking to find the date, time, event tag and location which we can do by a for loop
    content = event_soup.find_all('li', class_='list-group-item')
    events_data = []
    
    for locateInfo in content:
        #Locate the date, time, location, and general description for the all events
        #happening across campus along with the tag seperate
        all_events_info = locateInfo.find('h3', class_='media-heading header-cg--h4')
        
        #Finds the general information of all the events and tag
        description = all_events_info.find('a')
        event_format = description.get('aria-description', '')
        
        event_tag_classified = locateInfo.find('p', class_='rsvp__event-tags')
        #In case there are no tags left
        if event_tag_classified:
            event_tag = [a.get_text(strip=True) for a in event_tag_classified.find_all('a')]
        else:
            event_tag = []
            
        #Any error check to skip any non important elements
        event_parts = event_format.split(', ')
        if len(event_parts) < 3:
            continue
        
        #Find the event name and the day/date and the tag
        event_name = description.get_text(strip=True)
        event_day = event_format.split(', ')[0].split('. ')[-1]
        event_date = event_format.split(', ')[1].split(' At ')[0]
        
        #Break down the format to isolate just the time now
        #and then links through the format
        time_start = event_format.find("At ") + len("At ")
        time_end = event_format.find(", EDT")
        event_time = event_format[time_start: time_end]
        
        #Now we can add to a dictonary that will then be passed into a JSON file
        #and later formatted to the front-end aspect
        extracted_event_info = {
            "Name": event_name, 
            "Day": event_day,
            "Date": event_date,
            "Time": event_time,
            "Tag": event_tag
        }
        events_data.append(extracted_event_info)
    
    #Then we write our saved data to a json which can later be translated to the react
    with open("events.json", mode="w", encoding="utf-8") as file:
        json.dump(events_data, file, indent=3)
        
    print("Events were added to json")
        
#Have it update every 15 minutes with new events to display
schedule.every(15).minutes.do(scrapperEvents)

if __name__ == "__main__":
    scrapperEvents()
    while True:
        schedule.run_pending()
        time.sleep(1)