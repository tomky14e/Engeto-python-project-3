"""
project_3.py: třetí projekt do Engeto Online Python Akademie
author: Tomáš Matějíček
email: tomas.matejicek@hotmail.com
discord: tomas_38052

"""

import sys
import csv

import requests
from bs4 import BeautifulSoup

def check_args(bad_urls: list, base_url: str, argv: list) -> list:

    if len(argv) != 3:

        sys.exit('Wrong number of arguments')

    else:

        try:

            url = str(argv[1])
            csv_file = str(argv[2])

            if (base_url not in url) or url in bad_urls:

                sys.exit('Wrong URL')

            else:

                return url, csv_file

        except ValueError:

            sys.exit('Wrong type of arguments')
        

def get_soup(url: str) -> BeautifulSoup:

    try:

        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')

    except requests.exceptions.ConnectionError:

        sys.exit(

            f"Unable to connect to the specified URL."
            f"\nCheck URL or Internet connection."

        )


def get_municipality_id(html_table_row, data_holder: dict) -> None:

    data_holder["code"] = html_table_row.find("a").text
    data_holder["location"] = html_table_row.a.findNext("td").text


def get_municipality_votes_info(html_table_row, base_url: str, data_holder: dict) -> None:

    soup: BeautifulSoup = get_soup(base_url + html_table_row.find("a")["href"])

    data_holder["registered"] = (soup.find("td", {"headers": "sa2"}).text).replace('\xa0', '')
    data_holder["envelopes"] = (soup.find("td", {"headers": "sa3"}).text).replace('\xa0', '')
    data_holder["valid"] = (soup.find("td", {"headers": "sa6"}).text).replace('\xa0', '')

    html_table_tags = soup.find_all("table", {"class": "table"})[1:]

    for html_table_tag in html_table_tags:
        
        parties = html_table_tag.find_all("tr")[2:]

        for party in parties:

            party_name = party.td.findNext("td").text
            
            if party_name == "-":

                continue
            
            data_holder[party_name] = (party.td.findNext("td").findNext("td").text).replace('\xa0', '')

    
def get_data(teritory_url: str, base_url: str) -> list:
    
    municipalities_list: list = list()
    soup: BeautifulSoup = get_soup(teritory_url)
    
    html_table_tags = soup.find_all("table", {"class": "table"})

    for html_table_tag in html_table_tags:

        html_table_rows = html_table_tag.find_all("tr")[2:]

        for html_table_row in html_table_rows:

            if html_table_row.find("td").text == "-":

                continue    
            
            municipality_data_holder: dict = {

                "code": "",
                "location": "",
                "registered": 0,
                "envelopes": 0,
                "valid": 0
                
                }
            
            get_municipality_id(html_table_row, municipality_data_holder)
            get_municipality_votes_info(html_table_row, base_url, municipality_data_holder)  
    
            municipalities_list.append(municipality_data_holder)
            
    return municipalities_list


def export_to_csv(data: list, file: str) -> None:

    with open(file + ".csv", "w", newline="") as csv_file:

        header = data[0].keys()
        writer = csv.DictWriter(csv_file, fieldnames = header)

        try:

            writer.writeheader()
            writer.writerows(data)

        except csv.Error:

            sys.exit(f"Failed to write to csv file")
        
        else:

            print('Successful write to csv file')


if __name__ == "__main__":

    BASE_URL: str = 'https://volby.cz/pls/ps2017nss/'

    BAD_URLS: list = [ # Skip foreign voting places and main page
        'https://volby.cz/pls/ps2017nss/ps36?xjazyk=CZ',
        'https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ',
    ]

    TERITORY_URL, CSV_FILE = check_args(BAD_URLS, BASE_URL, sys.argv)

    export_to_csv(get_data(TERITORY_URL, BASE_URL), CSV_FILE)