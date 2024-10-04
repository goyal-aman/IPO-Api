import requests
from bs4 import BeautifulSoup
import json
import re
from flask import Flask, jsonify
from datetime import datetime
import pytz


# Function to clean and convert text
def clean_and_convert(text):
    # Remove unwanted characters
    cleaned_text = re.sub(r'[^0-9.]+', '', text).strip()
    # Try converting to float if the cleaned text is a number
    try:
        return float(cleaned_text) if cleaned_text else None
    except ValueError:
        return cleaned_text  # Return as string if it can't be converted



def get_ipo_data_detail():

    # URL of the webpage
    url = "https://www.investorgain.com/report/live-ipo-gmp/331/"

    # Send a GET request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parse the content of the page
    soup = BeautifulSoup(response.content, 'lxml')

    # Locate the table using XPath-like navigation
    # /html/body/div[8]/div[3]/div[1]/div[4]/div/div
    # /html/body/div[8]/div[3]/div[1]/div[4]/div/div
    # table = soup.select_one('#main > div:nth-child(8)')
    # /html/body/div[8]/div[3]/div[1]/div[4]/div/div/div[2]
    table = soup.select_one('div:nth-of-type(8) > div:nth-of-type(3) > div:nth-of-type(1) > div:nth-of-type(4) > div > div > div:nth-of-type(2)')

    # Check if the table exists
    if table:
        # Initialize a list to store the JSON data
        json_data = []

        # Extract column names from the table header (if available)
        headers = table.find('thead')
        # column_names = [item.get_text().strip().replace(" ", "_").replace("BoA_Dt", "Allotment_Date").replace("GMP(₹)", "GMP") for item in headers.find_all('th')]
        column_names = [item.get_text().strip() for item in headers.find_all('th')]
        
        # Iterate through the rows of the table
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')

            """
            below ancor tag has span in it as well this is why doing this [item for item in cols[0].find('a').strings][0] 
            <a href="/gmp/forge-auto-international-sme-ipo-gmp/1015/" target="_parent" title="">
                Forge Auto International NSE SME<span class="badge rounded-pill bg-primary ms-2">Close (Sub:49.28x)</span>
            </a>
            """
            ipo_name = [item for item in cols[0].find('a').strings][0] 

            remainging_cols = [clean_and_convert(col.get_text()) for col in cols[1:]]
            remainging_cols = [col.get_text() for col in cols[1:]]

            cols = [ipo_name, *remainging_cols]
            # Only append rows with the expected number of columns
            if len(cols) == len(column_names):
                # Create a dictionary for the current row
                row_data = {column_names[i]: cols[i] for i in range(len(column_names))}
                json_data.append(row_data)

        # Save the JSON data to a file
        # with open('output_new.json', 'w', encoding='utf-8') as json_file:
            # json.dump(json_data, json_file, ensure_ascii=False, indent=4)
        
        return json_data
        print("Data has been successfully extracted and saved to output.json")
    else:
        print("Table not found.")





# get_ipo_data_detail()  

app = Flask(__name__)


# def str_date_to_date(date_string):
#     try:
#         timezone = pytz.timezone('Asia/Kolkata')  # Replace with your desired timezone
#         day, month_abbr = date_string.split('-')
#         month = datetime.strptime(month_abbr, '%b').month
#         date = datetime(2022, month, int(day), tzinfo=timezone)
#         return date
#     except:
#         return None

def compare_dates(date1, date2):
    """Compare two datetime objects based on day, month, and year."""
    # Check if both dates are valid
    if date1 is None or date2 is None:
        raise ValueError("Both dates must be provided.")

    # Extract year, month, and day for both dates
    year1, month1, day1 = date1.year, date1.month, date1.day
    year2, month2, day2 = date2.year, date2.month, date2.day

    # Compare years first
    if year1 < year2:
        return -1  # date1 is earlier
    elif year1 > year2:
        return 1  # date2 is earlier

    # If years are the same, compare months
    if month1 < month2:
        return -1  # date1 is earlier
    elif month1 > month2:
        return 1  # date2 is earlier

    # If months are the same, compare days
    if day1 < day2:
        return -1  # date1 is earlier
    elif day1 > day2:
        return 1  # date2 is earlier

    # Dates are equal
    return 0


def str_date_to_date(date_str):
    """Convert date string in 'DD-MMM' format to a datetime object with the current year."""
    if date_str:
        # Add the current year to the date string and convert it
        current_year = datetime.now().year
        full_date_str = f"{date_str}-{current_year}"
        datetime_= datetime.strptime(full_date_str, "%d-%b-%Y").replace(tzinfo=pytz.timezone('Asia/Kolkata'))
        print("CONV", date_str, datetime_)
        if int(date_str.split("-")[0]) != datetime_.day:
            print("ERROR", date_str, datetime_)
        return datetime_
    return None

def group_by_tags(items):
    # Current date in 'Asia/Kolkata' timezone
    current_date = datetime.now(pytz.timezone('Asia/Kolkata'))

    # Initialize groups
    live = []
    upcoming = []
    past = []
    unannounced = []

    # Grouping logic
    for item in items:
        _open = str_date_to_date(item["Open"])
        _close = str_date_to_date(item["Close"])
        
        if _open and _close:
            if compare_dates(_open,  current_date) in [-1, 0] and compare_dates(current_date, _close) in [0, 1]:
                # Item is live
                live.append(item)
            elif compare_dates(_open,  current_date) == 1:
                # Item is upcoming
                upcoming.append(item)
            elif compare_dates(current_date, _close) == -1:
                # Item is past
                past.append(item)
        else:
            # Unannounced items (no open/close date)
            unannounced.append(item)

    return {
        "past": past,
        "live": live,
        "upcoming": upcoming,
        "unannounced": unannounced
    }

@app.route('/api/data', methods=['GET'])
def get_data():
    return get_ipo_data_detail() 

@app.route('/api/v2/data', methods=['GET'])
def get_data_v2():
    raw_data = get_ipo_data_detail() 
    # raw_data = [
    #     {"Open":"9-SEP", "Close":"11-Sep"},
    #     {"Open":"9-SEP", "Close":"4-Oct"},
    # ]
    print(group_by_tags(raw_data))
            
    return raw_data



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678)

