#!/usr/bin/env python3
"""
Script to scrape content from herb links in json/new_herbs_to_review.json
and save them as clean text files in text2/ directory
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import re
from urllib.parse import urlparse

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
            print(f"  ❌ Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None
    return None

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Remove common HTML entities that might have been missed
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&mdash;': '—',
        '&ndash;': '–',
        '&hellip;': '...'
    }
    
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    return text.strip()

def extract_main_content(soup):
    """Extract the main content from the HTML, filtering out navigation and ads"""
    
    # Remove unwanted elements
    unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove common ad-related elements
    ad_selectors = [
        {'class_': lambda x: x and any(ad in str(x).lower() for ad in ['ad', 'google', 'sponsor', 'banner'])},
        {'id': lambda x: x and any(ad in str(x).lower() for ad in ['ad', 'google', 'sponsor', 'banner'])}
    ]
    
    for selector in ad_selectors:
        for element in soup.find_all(attrs=selector):
            element.decompose()
    
    # Try to find main content area
    main_content = None
    
    # Look for common content containers
    content_selectors = [
        'main',
        'article',
        {'class_': lambda x: x and any(content in str(x).lower() for content in ['content', 'main', 'body', 'text'])},
        {'id': lambda x: x and any(content in str(x).lower() for content in ['content', 'main', 'body', 'text'])}
    ]
    
    for selector in content_selectors:
        if isinstance(selector, dict):
            main_content = soup.find(attrs=selector)
        else:
            main_content = soup.find(selector)
        if main_content:
            break
    
    # If no specific content area found, use body
    if not main_content:
        main_content = soup.find('body')
    
    # If still nothing, use the whole soup
    if not main_content:
        main_content = soup
    
    # Extract text and clean it
    text = main_content.get_text(separator='\n', strip=True)
    return clean_text(text)

def get_safe_filename(filename):
    """Convert filename to safe format for filesystem"""
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*%]', '_', filename)
    # Handle URL encoding
    filename = filename.replace('%20', '_')
    # Ensure it ends with .txt
    if not filename.endswith('.txt'):
        if filename.endswith('.htm') or filename.endswith('.html'):
            filename = filename.rsplit('.', 1)[0] + '.txt'
        else:
            filename = filename + '.txt'
    return filename

def load_herb_links(filename='json/new_herbs_to_review.json'):
    """Load the herb links to scrape"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {filename} not found")
        return []

def scrape_all_herbs():
    """Main function to scrape all herb content"""
    print("🌿 Starting herb content scraping...")
    print("=" * 50)
    
    # Load herb links
    herb_links = load_herb_links()
    if not herb_links:
        return
    
    print(f"📄 Found {len(herb_links)} herb pages to scrape")
    
    # Create output directory
    output_dir = 'text2'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}/")
    
    # Track progress
    successful = 0
    failed = 0
    
    for i, herb in enumerate(herb_links, 1):
        url = herb['url']
        name = herb['name']
        filename = herb.get('filename', 'unknown.htm')
        
        print(f"[{i:3d}/{len(herb_links)}] {name}")
        print(f"  🔗 {url}")
        
        # Check if file already exists
        safe_filename = get_safe_filename(filename)
        output_path = os.path.join(output_dir, safe_filename)
        
        if os.path.exists(output_path):
            print(f"  ⏭️  Already exists, skipping {safe_filename}")
            successful += 1
            continue
        
        # Get page content
        html_content = get_page_content(url)
        if not html_content:
            print(f"  ❌ Failed to fetch content")
            failed += 1
            continue
        
        # Parse HTML and extract text
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            clean_content = extract_main_content(soup)
            
            if not clean_content or len(clean_content.strip()) < 50:
                print(f"  ⚠️  Little to no content found")
                clean_content = f"URL: {url}\nName: {name}\n\nNo significant content found or page may be empty."
            
            # Save to file (we already know it doesn't exist from the check above)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Source: {url}\n")
                f.write(f"Name: {name}\n")
                f.write(f"Filename: {filename}\n")
                f.write("=" * 50 + "\n\n")
                f.write(clean_content)
            
            print(f"  ✅ Saved to {safe_filename}")
            successful += 1
            
        except Exception as e:
            print(f"  ❌ Error processing content: {e}")
            failed += 1
        
        # Be respectful to the server
        time.sleep(1)
        
        # Progress update every 10 items
        if i % 10 == 0:
            print(f"  📊 Progress: {successful} successful, {failed} failed")
    
    # Final summary
    print("\n" + "=" * 50)
    print("🏁 SCRAPING COMPLETE")
    print(f"✅ Successfully scraped: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Text files saved in: {output_dir}/")
    
    if successful > 0:
        print(f"\n📝 Next steps:")
        print(f"  1. Review the text files in {output_dir}/")
        print(f"  2. Use AI or manual review to categorize content")
        print(f"  3. Identify which are herbs, maladies, or formulas")

if __name__ == "__main__":
    try:
        scrape_all_herbs()
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("Make sure json/new_herbs_to_review.json exists and you have internet connection")