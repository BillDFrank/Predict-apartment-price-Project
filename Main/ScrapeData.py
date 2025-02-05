# flake8: noqa

import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import numpy as np
import time
import random
from fake_useragent import UserAgent
from ConnectDB import connect_to_database, save_data_to_db, update_details_in_db, get_last_scraped_page_today


def scrape_page(page):
    """
    Scrape a single page of listings from Imovirtual (Portuguese version).

    Args:
        page (int): The page number to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing the basic data.
    """
    url = f"https://www.imovirtual.com/pt/resultados/comprar/apartamento/todo-o-pais?viewType=listing&page={page}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(
            f"❌ Failed to retrieve page {page}. Status code: {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.find_all("article", {"data-cy": "listing-item"})

    if not listings:
        print(
            f"⚠️ No listings found on page {page}. Check selectors or page structure.")
        return pd.DataFrame()

    data = []

    for listing in listings:
        # Extract URL
        a_tag = listing.find("a")
        ad_url = "https://www.imovirtual.com" + \
            a_tag.get("href") if a_tag and a_tag.get("href") else np.nan

        # Extract title
        title_el = listing.find("p", class_="css-u3orbr")
        title = title_el.get_text(strip=True) if title_el else np.nan

        # Extract price
        price_el = listing.find("span", class_="css-2bt9f1")
        price = price_el.get_text(strip=True) if price_el else np.nan

        # Extract location
        location_el = listing.find("p", class_="css-42r2ms")
        location = location_el.get_text(strip=True) if location_el else np.nan

        # Extract details (rooms and area)
        dl = listing.find("dl", class_="css-12dsp7a")
        # Default to NaN (better for numerical processing)
        rooms, area = np.nan, np.nan
        if dl:
            dt_dd = {dt.text.strip(): dd.text.strip()
                     for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd"))}

            # Rooms (Tipologia)
            rooms = dt_dd.get("Tipologia", np.nan)

            # Area can be under "Área" or "Zona"
            area = dt_dd.get("Área", dt_dd.get("Zona", np.nan))
            if isinstance(area, str):
                area = area.split()[0]  # Extract numeric value from "120 m²"

        scrape_date = datetime.datetime.now().strftime("%Y-%m-%d")
        data.append([page, title, price, location,
                    rooms, area, ad_url, scrape_date])

    df = pd.DataFrame(data, columns=[
                      "Page", "Title", "Price", "Location", "Rooms", "Area", "URL", "ScrapeDate"])
    return df


def scrape_listings(num_pages=1, force_start_page=None):
    """
    Scrape multiple pages of basic advertising info and save each page to the database.

    Args:
        num_pages (int): Number of pages to scrape.
        force_start_page (int, optional): If provided, forces the scraper to start at this page number,
                                          overriding the resume logic.
        upper_limit (int): The maximum page number to scrape (if the starting page exceeds this,
                           the scraper stops).
    """
    conn = connect_to_database()
    if conn is None:
        print("❌ Database connection failed. Exiting.")
        return

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Determine the starting page
    if force_start_page is not None:
        start_page = force_start_page
    else:
        last_page_today = get_last_scraped_page_today(conn, today_str)
        # If there are records for today, resume from last_page_today + 1; otherwise, start from page 1.
        start_page = last_page_today + 1 if last_page_today > 0 else 1

    if start_page > num_pages:
        print(
            f"ℹ️ Already scraped up to page {start_page - 1} for today (num pages {num_pages}). No new pages to scrape.")
        conn.close()
        return

    end_page = num_pages
    print(f"🟢 Scraping pages {start_page} to {end_page}...")

    for page in range(start_page, end_page + 1):
        df = scrape_page(page)
        if not df.empty:
            save_data_to_db(conn, df)
            print(f"✅ Page {page} data saved to database.")
        else:
            print(f"ℹ️ No data found on page {page}. Stopping.")
            break

        time.sleep(random.uniform(1, 3))  # Delay between page requests

    conn.close()
    print("🎯 Basic scraping completed!")


def scrape_details(order_by="bottom", scrape_date=None):
    """
    Scrapes missing details (bathrooms, construction_year, energetic_certificate) from ads.

    Parameters:
        order_by (str): "top" to start from the first record, "bottom" to start from the last.
        scrape_date (str): The specific date (YYYY-MM-DD) to filter records. If None, all dates are considered.
    """
    ua = UserAgent()
    session = requests.Session()

    conn = connect_to_database()
    if conn is None:
        print("❌ Database connection failed. Exiting.")
        return

    # Determine order for fetching records
    order_clause = "ASC" if order_by == "top" else "DESC"

    # Build query with optional date filter
    query = f"""
        SELECT id, url FROM advertisings 
        WHERE bathrooms IS NULL AND construction_year IS NULL AND energetic_certificate IS NULL
    """
    
    params = []
    if scrape_date:
        query += " AND ScrapeDate = ?"
        params.append(scrape_date)
    
    query += f" ORDER BY id {order_clause}"

    cursor = conn.cursor()
    cursor.execute(query, params)
    records = cursor.fetchall()

    print(
        f"🟢 Found {len(records)} records needing detail extraction. (Order: {order_by}, Date: {scrape_date if scrape_date else 'All'})")

    for rec in records:
        record_id, ad_url = rec[0], rec[1]

        try:
            response = session.get(
                ad_url, headers={'User-Agent': ua.random}, timeout=10)
            if response.status_code != 200:
                print(
                    f"⚠️ Failed to retrieve details for record {record_id}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')

            # --- Extract Bathrooms ---
            try:
                buttons = soup.find_all('button', class_='eezlw8k1 css-ds0a69')
                bathrooms = buttons[2].find(
                    'div', class_='css-1ftqasz').get_text(strip=True) if len(buttons) >= 3 else "N/A"
            except Exception:
                bathrooms = "N/A"

            # --- Extract Construction Year & Energetic Certificate ---
            try:
                construction_year = "N/A"
                energetic_certificate = "N/A"

                divs = soup.find_all('div', class_='css-t7cajz e16p81cp1')
                for div in divs:
                    p_elements = div.find_all(
                        'p', class_='e16p81cp2 css-nlohq6')
                    for i in range(len(p_elements) - 1):
                        text = p_elements[i].get_text(strip=True)
                        if "Ano de construção" in text:
                            construction_year = p_elements[i +
                                                           1].get_text(strip=True)
                        elif "Certificado energético" in text:
                            energetic_certificate = p_elements[i +
                                                               1].get_text(strip=True)

                        # Stop searching if both values are found
                        if construction_year != "N/A" and energetic_certificate != "N/A":
                            break
            except Exception:
                pass  # Keep default "N/A" if an error occurs

            update_details_in_db(conn, record_id, bathrooms,
                                 construction_year, energetic_certificate)
            print(
                f"✅ Updated record {record_id}: Bathrooms={bathrooms}, Year={construction_year}, Cert={energetic_certificate}")

            time.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f"❌ Error processing record {record_id} ({ad_url}): {e}")

    conn.close()
    print("🎯 Detail extraction completed!")
