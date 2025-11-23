#!/usr/bin/env python3
"""
Comprehensive script to scrape all herb links from the Chinese Herbs Dictionary
and filter out ones we already have, producing a clean list of new herbs to review.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import urljoin, urlparse
import os

def get_page_content(url, retries=3, delay=1):
    """Fetch page content with retries and delay"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None
    return None

def extract_index_links(base_url):
    """Extract all the index page links from the main dictionary page"""
    print("Fetching main dictionary page...")
    content = get_page_content(base_url)
    if not content:
        print("Failed to fetch main dictionary page")
        return []
    
    soup = BeautifulSoup(content, 'html.parser')
    index_links = []
    
    # Find all links that match patterns for herb index pages
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link['href']
        text = link.get_text(strip=True)
        
        # Look for herb index patterns
        if any(pattern in href.lower() for pattern in ['herb_index', 'latin', 'pinyin', 'stroke']):
            full_url = urljoin(base_url, href)
            index_links.append({
                'url': full_url,
                'text': text,
                'type': 'index'
            })
        
        # Single letter links or short combinations like "I,J,K"
        elif len(text) <= 5 and re.match(r'^[A-Z,\s-]+$', text):
            full_url = urljoin(base_url, href)
            index_links.append({
                'url': full_url,
                'text': text,
                'type': 'alphabet'
            })
        
        # Chinese pinyin links
        elif len(text) <= 5 and any(c in text for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            full_url = urljoin(base_url, href)
            index_links.append({
                'url': full_url,
                'text': text,
                'type': 'pinyin'
            })
        
        # Stroke count links (numbers)
        elif re.match(r'^\d+[,\s\d-]*$', text):
            full_url = urljoin(base_url, href)
            index_links.append({
                'url': full_url,
                'text': text,
                'type': 'stroke'
            })
    
    # Remove duplicates
    seen_urls = set()
    unique_links = []
    for link in index_links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    print(f"Found {len(unique_links)} index pages")
    return unique_links

def extract_herb_links_from_page(url):
    """Extract individual herb links from an index page"""
    print(f"Scraping herbs from: {url}")
    content = get_page_content(url)
    if not content:
        return []
    
    soup = BeautifulSoup(content, 'html.parser')
    herb_links = []
    
    # Look for links that appear to be individual herbs
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link['href']
        text = link.get_text(strip=True)
        
        # Skip navigation and general links
        if any(skip in href.lower() for skip in ['index', 'dictionary', 'home', 'search', 'mailto', 'javascript']):
            continue
            
        if any(skip in text.lower() for skip in ['home', 'search', 'index', 'dictionary', 'back', 'next']):
            continue
        
        # Look for herb-like links
        if len(text) > 2 and not re.match(r'^[A-Z,\s-]*$', text):
            full_url = urljoin(url, href)
            herb_links.append({
                'url': full_url,
                'name': text,
                'source_page': url
            })
    
    print(f"Found {len(herb_links)} herb links on this page")
    return herb_links

def is_navigation_or_general_link(name, url):
    """Check if this is a navigation link or general page to filter out"""
    navigation_keywords = [
        'home', 'index', 'search', 'dictionary', 'library', 'back', 'next',
        'poll', 'notify', 'tell us', 'by:', 'joe hing', 'qigong', 'acupuncture',
        'massage', 'hypnotherapy', 'traditional chinese medicine', 'viagra',
        'list of', 'general online', 'teaching experience', 'copyright',
        'disclaimer', 'weather', 'site meter', 'problems with website',
        'samples of formulae', 'terms of traditional'
    ]
    
    navigation_url_patterns = [
        'index.htm', 'search', 'poll.htm', 'notify', 'teaching_experience',
        'qigong.htm', 'acupuncture', 'massage', 'hypnotherapy.htm', 'viagra',
        'general_online_library', 'copyright', 'disclaimer', 'weather',
        'chinese_herb_formulae.htm'
    ]
    
    name_lower = name.lower()
    url_lower = url.lower()
    
    # Check name keywords
    for keyword in navigation_keywords:
        if keyword in name_lower:
            return True
    
    # Check URL patterns
    for pattern in navigation_url_patterns:
        if pattern in url_lower:
            return True
    
    # Skip numeric-only names (stroke counts, etc.)
    if re.match(r'^[\d,\s-]+$', name.strip()):
        return True
    
    # Skip very short names that are likely navigation
    if len(name.strip()) <= 2:
        return True
    
    return False

def extract_filename_from_url(url):
    """Extract just the filename from a URL"""
    parsed = urlparse(url)
    filename = parsed.path.split('/')[-1]
    return filename

def load_existing_herbs(filename='json/herb_links.json'):
    """Load the existing herb links we already have"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        print(f"Warning: {filename} not found, assuming no existing herbs")
        return set()

def scrape_and_filter_herbs():
    """Main function to scrape all herbs and filter out existing ones"""
    base_url = "https://alternativehealing.org/Chinese_herbs_dictionary.htm"
    
    print("Starting comprehensive herb scraping and filtering...")
    print("=" * 60)
    
    # Load existing herbs to exclude
    existing_herbs = load_existing_herbs()
    print(f"Existing herbs to exclude: {len(existing_herbs)}")
    
    # Step 1: Get all index page links
    index_links = extract_index_links(base_url)
    
    if not index_links:
        print("No index links found. Exiting.")
        return
    
    print(f"\nIndex pages found:")
    for i, link in enumerate(index_links, 1):
        print(f"{i:2d}. [{link['type']}] {link['text']} -> {link['url']}")
    
    # Step 2: Extract herb links from each index page
    all_herbs = []
    total_pages = len(index_links)
    
    for i, index_link in enumerate(index_links, 1):
        print(f"\n[{i}/{total_pages}] Processing: {index_link['text']}")
        herbs = extract_herb_links_from_page(index_link['url'])
        all_herbs.extend(herbs)
        
        # Be respectful to the server
        time.sleep(2)
    
    print(f"\n" + "=" * 60)
    print(f"Raw extraction results:")
    print(f"Total links found: {len(all_herbs)}")
    
    # Step 3: Filter out navigation/general links
    filtered_herbs = []
    navigation_filtered = 0
    
    for herb in all_herbs:
        if not is_navigation_or_general_link(herb['name'], herb['url']):
            filtered_herbs.append(herb)
        else:
            navigation_filtered += 1
    
    print(f"After filtering navigation/general: {len(filtered_herbs)} (removed {navigation_filtered})")
    
    # Step 4: Remove duplicates based on URL
    seen_urls = set()
    unique_herbs = []
    duplicates_removed = 0
    
    for herb in filtered_herbs:
        if herb['url'] not in seen_urls:
            seen_urls.add(herb['url'])
            unique_herbs.append(herb)
        else:
            duplicates_removed += 1
    
    print(f"After removing duplicates: {len(unique_herbs)} (removed {duplicates_removed})")
    
    # Step 5: Filter out herbs we already have
    new_herbs = []
    already_have = 0
    
    for herb in unique_herbs:
        filename = extract_filename_from_url(herb['url'])
        if filename not in existing_herbs:
            new_herbs.append({
                **herb,
                'filename': filename
            })
        else:
            already_have += 1
    
    print(f"After excluding existing herbs: {len(new_herbs)} (already have {already_have})")
    
    # Step 6: Save results
    with open('new_herbs_to_review.json', 'w', encoding='utf-8') as f:
        json.dump(new_herbs, f, indent=2, ensure_ascii=False)
    
    # Create summary
    summary = {
        "scraping_summary": {
            "total_links_found": len(all_herbs),
            "navigation_filtered": navigation_filtered,
            "duplicates_removed": duplicates_removed,
            "already_have": already_have,
            "new_herbs_to_review": len(new_herbs)
        },
        "existing_herbs_count": len(existing_herbs),
        "index_pages_scraped": len(index_links)
    }
    
    with open('scraping_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Show sample results
    print(f"\n" + "=" * 60)
    print(f"FINAL RESULTS:")
    print(f"New herbs found that we don't have: {len(new_herbs)}")
    print(f"\nSample of new herbs (first 15):")
    for i, herb in enumerate(new_herbs[:15], 1):
        print(f"  {i:2d}. {herb['name']} ({herb['filename']})")
    
    if len(new_herbs) > 15:
        print(f"  ... and {len(new_herbs) - 15} more")
    
    print(f"\nFiles created:")
    print(f"  - new_herbs_to_review.json ({len(new_herbs)} herbs)")
    print(f"  - scraping_summary.json (detailed statistics)")
    
    print(f"\nNext steps:")
    print(f"  1. Review new_herbs_to_review.json")
    print(f"  2. Use AI or manual review to categorize into herbs/maladies/formulas")
    print(f"  3. Add valid herbs to your website")
    
    return new_herbs

if __name__ == "__main__":
    try:
        new_herbs = scrape_and_filter_herbs()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error during scraping: {e}")
        print("Make sure you have internet connection and required packages installed")