import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import json

def get_html_content(url, headers, proxies=None):
    """
    Fetches the HTML content from a given URL.

    Args:
        url (str): The URL to scrape.
        headers (dict): A dictionary of HTTP headers to send with the request.
        proxies (dict, optional): A dictionary of proxies for the request.
                                  Defaults to None.

    Returns:
        BeautifulSoup or None: A BeautifulSoup object if the request is successful,
                               None otherwise.
    """
    try:
        # Send a GET request to the URL with headers.
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"Successfully fetched content from {url}")
        return soup

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {url}: {e}")
        return None

def extract_links_from_search(soup):
    """
    Extracts business names and their individual page links from a search results page.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the page's HTML.

    Returns:
        list: A list of dictionaries, where each dictionary contains the
              name and link for a single business.
    """
    businesses = []

    # The main container for each listing is a div with the class 'listing_container'.
    listings = soup.find_all('div', class_='listing_container')

    if not listings:
        print("No business listings found with the given selector.")
        return []

    for listing in listings:
        # The link is in the <a> tag inside an <h3> with class 'listing_title'.
        link_element = listing.find('h3', class_='listing_title')
        link = link_element.find('a')['href'] if link_element and link_element.find('a') else None
        
        # The business name is also in the same <a> tag.
        name = link_element.find('a').text.split(".", 1) if link_element and link_element.find('a') else "Name not found"
        
        if link:
            # We only store the name and the relative link for now.
            businesses.append({'name': name[1].strip(), 'link': link})

    return businesses

def scrape_business_page(url, headers):
    """
    Scrapes a single business's page for detailed information.

    Args:
        url (str): The URL of the business page.
        headers (dict): Headers to use for the request.

    Returns:
        dict: A dictionary containing the scraped details.
    """
    print(f"    - Scraping details from: {url}")
    soup = get_html_content(url, headers)
    details = {
        'link': url,
        'email': 'Not found',
        'website': 'Not found'
    }

    if not soup:
        return details

    # LOGIC FOR FINDING WEBSITE URL AND EMAIL ADDRESS

    # Find the div with contact information
    business_contact_info = soup.find('div', class_='details_contact_other col_item width_2_4')
    if business_contact_info:

        # Step 1 : Try find website link using 'yext.' tag
        website_link_element = business_contact_info.find('a', class_='yext.homepage')
        

        # If website link not found using 'yext.' tag
        # Attempt to find via website_icon span class which is previous sibling of website <a> tag element
        if not website_link_element:
            print(f"- Website tag not found using 'yext.' class name. Attempting to search via icon")
            website_icon_element = business_contact_info.find('span', class_='icon_website')

            # Ensure website icon exists 
            if website_icon_element:
                print(f"- Website tag found using icon")
                website_link_element = website_icon_element.find_next_sibling()
            else:
                return details


        # Proceed to try find email via 'yext.' tag
        email_link_element = business_contact_info.find('a', class_='yext.email')

        # If email tag not found using 'yext.' tag
        # Attempt to find via email_icon span class which is previous sibling of email <a> tag element
        if not email_link_element:
            print(f"- Email tag not found using 'yext.' class name. Attempting to search via icon")
            email_icon_element = business_contact_info.find('span', class_='icon_email')

            #Ensure email icon exists
            if email_icon_element:
                print(f"- Email tag found using icon")
                email_link_element = email_icon_element.find_next_sibling()

        # Adding website and email to details obj
        if email_link_element:
            details['website'] = website_link_element['href']
            print(f"- Website succesfully put into details")

            details['email'] = email_link_element['href'].replace('mailto:', '').strip()
            print(f"- Email succesfully put into details")
  
    return details


def save_to_csv(data, filename, mode='w', header=True):
    """
    Saves the scraped data to a CSV file.

    Args:
        data (list): A list of dictionaries containing the scraped data.
        filename (str): The name of the CSV file to save.
        mode (str): File open mode. 'w' for write, 'a' for append.
        header (bool): True to write header, False otherwise.
    """
    if not data:
        print("No data to save to CSV.")
        return

    try:
        with open(filename, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            if header:
                writer.writeheader()
            writer.writerows(data)
        
        print(f"Successfully wrote {len(data)} businesses to {filename}")

    except IOError as e:
        print(f"An I/O error occurred while writing to the CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """
    Main function to run the web scraper.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Set the maximum number of pages to scrape.
    MAX_PAGES = 95

    base_url_pattern = "https://www.goldenpages.ie/q/business/advanced/what/plumbers/"
    
    # Use a set to automatically handle duplicate links
    all_business_links_set = set()

    # --- PHASE 1: Scrape all search results pages for links ---
    print("\n--- Starting Phase 1: Collecting all business links ---")
    for page_num in range(1, MAX_PAGES + 1):
        # Construct the URL for the current page using the correct pattern.
        current_url = f"{base_url_pattern}{page_num}/" if page_num > 1 else base_url_pattern

        print(f"\n--- Scraping search results page {page_num} at {current_url} ---")
        soup = get_html_content(current_url, headers)

        if soup:
            links_on_page = extract_links_from_search(soup)
            
            # If no links are found on a page, it might be the end of the results.
            if not links_on_page:
                print(f"No more listings found on page {page_num}. Stopping pagination.")
                break

            # Add all new links to the set to prevent duplicates
            for link_data in links_on_page:
                all_business_links_set.add(tuple(link_data.items())) # Convert dict to tuple to be hashable

            # DEBUG: Print the number of links found on this page
            print(f"      - Found {len(links_on_page)} links on this page. Total unique links so far: {len(all_business_links_set)}")
            time.sleep(2)
        else:
            print("Failed to fetch search results, stopping.")
            break

    # Convert the set of unique links back to a list of dictionaries
    all_business_links = [dict(link_tuple) for link_tuple in all_business_links_set]

    print(f"\nPhase 1 Complete. Found a total of {len(all_business_links)} unique business links.")
    
    if not all_business_links:
        print("No links found in Phase 1. Check your search query or selectors. Exiting.")
        return

    # --- PHASE 2: Visit each business page and scrape details and filter ---
    print("\n--- Starting Phase 2: Scraping details from individual business pages ---")

    # Create a list to store all the final scraped data
    all_scraped_data = []

    for business in all_business_links:
        # DEBUG: Print the business being processed
        print(f"      - Processing business: {business['name']}")

        full_url = "https://www.goldenpages.ie" + business['link']
        
        # Scrape the detailed info from the business's page
        details = scrape_business_page(full_url, headers)
        
        # --- NEW FILTERING LOGIC ---
        if details['website'] != 'Not found':
            print(f"      - Found website for '{business['name']}'. Adding to data list.")
            
            # Combine the original name with the new details
            final_data = {'name': business['name'], **details}
            
            # Append the single dictionary to our list
            all_scraped_data.append(final_data)
        
        else:
            print(f"      - No website found for '{business['name']}'. Skipping.")
        
        time.sleep(2) # Add a delay between requests to individual pages

    # --- FINAL STEP: Save all the collected data to a JSON file ---
    print("\n--- Phase 3: Saving data to JSON file ---")
    if all_scraped_data:
        json_file_name = 'golden_pages_data.json'
        try:
            with open(json_file_name, 'w', encoding='utf-8') as json_file:
                # Use json.dump() to write the list of dictionaries to the file
                json.dump(all_scraped_data, json_file, indent=4)
            print(f"Successfully wrote {len(all_scraped_data)} businesses to {json_file_name}")
        except IOError as e:
            print(f"An I/O error occurred while writing to the JSON file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    else:
        print("No data was collected to save.")

    print("\nScraping complete.")


if __name__ == "__main__":
    main()