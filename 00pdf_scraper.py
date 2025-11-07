#!/usr/bin/env python3
"""
PDF Downloader with Selenium - Handles JavaScript-loaded content
"""

import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import requests
import os
from pathlib import Path
import time

def collect_pdf_links(driver):
    collect_pdf_links_list = []
    links = driver.find_elements(By.TAG_NAME, "a")

    for link in links:
        try:
            href = link.get_attribute("href")
            if href and href.lower().endswith('.pdf'):
                text = link.text.strip()
                collect_pdf_links_list.append({
                    'url': href,
                    'text': text if text else 'Unnamed PDF'
                })
                print(text if text else 'Unnamed PDF', href)
        except:
            continue

    return collect_pdf_links_list


def download_pdfs_with_selenium(url, download_folder, headless=True, wait_time=5):
    """
    Download all PDFs from a webpage using Selenium (handles JavaScript)
    
    Args:
        url: The URL to scrape
        download_folder: Where to save PDFs
        headless: Run browser in headless mode (no GUI)
        wait_time: Seconds to wait for page to fully load
    """
    Path(download_folder)
    
    # Setup Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    
    try:
        print(f"Starting browser and loading page: {url}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait for page to load
        print(f"Waiting {wait_time} seconds for JavaScript to load...")
        time.sleep(wait_time)
        

        #######################################################
        ############# Extract PDF links #######################
        #######################################################
        pdf_links_list = []

        while True:
            try:
                pdf_links_list.extend(collect_pdf_links(driver))

                next_button = driver.find_element(By.ID, "DataTables_Table_0_next")

                #check if button is disabled aka no more pages
                classes = next_button.get_attribute("class")
                if "disabled" in classes:
                    print("No more pages to load.")
                    break

                next_button.click()
                time.sleep(.2)  

            except:
                print("No more 'Load More' button found or unable to click.")
                break

    


        print(f"Found {len(pdf_links_list)} PDF links\n")
        
       
        #######################################################
        ############# Process PDF links #######################
        #######################################################
        pdf_count = 0
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for pdf_info in pdf_links_list:
            pdf_url = pdf_info['url']
            
            try:
                # Download the PDF
                response = requests.get(pdf_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Verify it's a PDF
                content = response.content
                if b'%PDF' not in content[:10]:# the first 4 bytes of a PDF file should be '%PDF' but can be '\n%PDF' or similar so we check 10 bytes
                    print(f"     Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                    print(f"     Content length: {len(content)} bytes")
                    print(f"     First 20 bytes: {content[:20]}")
                    print(f"     ⚠ Skipped {pdf_info['text']}: {pdf_url}  : Not a valid PDF")
                    print()
                    continue
                
                # Generate filename
                filename = os.path.basename(pdf_url.split('?')[0])  # ? is to remove query params if they exist
                
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                
                filepath = os.path.join(download_folder, filename)
                
                # Handle duplicates
                if os.path.exists(filepath):
                    name, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(filepath):
                        filename = f"{name}_{counter}{ext}"
                        filepath = os.path.join(download_folder, filename)
                        counter += 1
                
                # Save PDF
                with open(filepath, 'wb') as f:
                    f.write(content)
                
                pdf_count += 1
                
            except Exception as e:
                print(f"     ✗ Failed: {e}")
                print()
        
        print("="*80)
        print(f"Download complete! Successfully downloaded: {pdf_count}/{len(pdf_links_list)} PDFs")
        print(f"Files saved in: {os.path.abspath(download_folder)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")


if __name__ == "__main__":
    print("PDF Downloader ")
    print("-" * 80)
    
    parser = argparse.ArgumentParser(description="Download PDFs from a webpage")
    parser.add_argument("--url", help="URL of the webpage to scrape")
    parser.add_argument("--save_folder", help="Path to the folder where PDFs will be saved", default="/home/kuba/data/usc-policy-docs/raw")
    parser.add_argument("--headless", help="Run browser in headless mode (y/n)", default="y")
    parser.add_argument("--wait_time", help="Seconds to wait for page to load", type=int, default=5)

    args = parser.parse_args()

    download_pdfs_with_selenium(args.url, args.save_folder, args.headless, args.wait_time)