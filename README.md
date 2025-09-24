# 🇮🇪 Golden Pages Scraper

This Python script is a web scraper for GoldenPages.ie, designed to efficiently extract business information. It's built for anyone who needs to compile a clean dataset of Irish businesses, including their names, websites, and email addresses.

---

## 🚀 Key Features

* **Automated Pagination:** The script can automatically navigate through multiple search results pages to collect a comprehensive list of businesses.
* **Efficient Data Collection:** It first gathers all unique business links from search pages, then visits each one to scrape detailed contact information. This two-phase approach is more robust and organized.
* **Smart Filtering:** Only businesses with a discovered website are included in the final output, ensuring a higher quality and more useful dataset.
* **Robust Error Handling:** The code includes `try-except` blocks to gracefully handle network issues or missing data, preventing crashes during the scraping process.
* **Structured Output:** The final data is saved in a clean, human-readable JSON file, making it easy to use in other applications or for data analysis.

---

## ⚙️ How to Use

### Prerequisites

Before you begin, make sure you have **Python 3.6+** installed. You'll also need the following libraries:

* **`requests`**: To send HTTP requests and fetch web pages.
* **`BeautifulSoup4`**: To parse the HTML and find the data you need.

You can install them with `pip`:

```bash
pip install requests beautifulsoup4
Configuration
Open the golden_pages_scraper.py file and modify the following two variables in the main() function to suit your needs:

MAX_PAGES: Set this to the maximum number of search results pages you want to scrape. Be sure to check the total pages for your search query on the Golden Pages website.

base_url_pattern: Change the category at the end of this URL to search for different types of businesses (e.g., change plumbers to electricians).

Running the Script
Once configured, simply run the script from your terminal:

Bash

python golden_pages_scraper.py
The script will print its progress as it works. A file named golden_pages_data.json will be created in the same directory upon completion.

📂 Output Format
The final output is a JSON file containing a list of dictionaries. Each dictionary represents a single business and includes the following details:

JSON

[
  {
    "name": "Acme Plumbers Dublin",
    "link": "/plumbers/acme-plumbers-dublin/",
    "email": "info@acmeplumbers.ie",
    "website": "[https://www.acmeplumbers.ie](https://www.acmeplumbers.ie)"
  },
  {
    "name": "City Pipes Solutions",
    "link": "/plumbers/city-pipes-solutions/",
    "email": "contact@citypipes.ie",
    "website": "[https://www.citypipes.ie](https://www.citypipes.ie)"
  }
]