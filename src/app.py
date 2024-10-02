import requests
from bs4 import BeautifulSoup
import json
import re
from flask import Flask, jsonify

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

@app.route('/api/data', methods=['GET'])
def get_data():
    return get_ipo_data_detail() 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5678)

