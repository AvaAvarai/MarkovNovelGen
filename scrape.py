import requests
from bs4 import BeautifulSoup
import os
import time

# Function to get the top N works' URLs from Project Gutenberg
def get_top_works_urls(n):
    base_url = "https://www.gutenberg.org/ebooks/search/?sort_order=downloads"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract the links to the top works
    ebook_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Only grab links to individual books (i.e., /ebooks/<id>)
        if '/ebooks/' in href and href.count('/') == 2:
            ebook_links.append("https://www.gutenberg.org" + href)
            if len(ebook_links) == n:
                break
    return ebook_links

# Function to get the title and .txt link for a given work
def get_title_and_txt_link(ebook_url):
    try:
        response = requests.get(ebook_url, timeout=10)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract title
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "unknown_title"

        # Find the .txt link
        for link in soup.find_all('a', href=True):
            href = link['href']
            if ".txt" in href and not "zip" in href:  # Ensure it's a plain text file
                if href.startswith("http"):
                    return title, href
                else:
                    return title, "https://www.gutenberg.org" + href
        return title, None
    except Exception as e:
        print(f"Error while processing {ebook_url}: {e}")
        return "unknown_title", None

# Function to download the .txt file with retry logic
def download_txt(url, folder, title, retries=3):
    try:
        for attempt in range(retries):
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Replace any characters in the title that are not allowed in filenames
                safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else "_" for c in title)
                file_path = os.path.join(folder, f"{safe_title}.txt")
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded: {title}.txt")
                return True
            else:
                print(f"Attempt {attempt+1} failed for {url}, status code: {response.status_code}")
            time.sleep(1)  # Wait before retrying
        print(f"Failed to download {title}.txt after {retries} attempts.")
        return False
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# Main program
def main():
    n = int(input("Enter the number of top works to download: "))

    # Create a timestamped folder for downloads
    folder_name = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(folder_name, exist_ok=True)

    # Get the top N works URLs
    ebook_urls = get_top_works_urls(n)

    for ebook_url in ebook_urls:
        print(f"Processing {ebook_url}...")
        # Get the title and text link
        title, txt_link = get_title_and_txt_link(ebook_url)
        if txt_link:
            print(f"Found .txt link for '{title}': {txt_link}")
            if not download_txt(txt_link, folder_name, title):
                print(f"Failed to download '{title}.txt'")
        else:
            print(f"Failed to find .txt link for {title}")

    print(f"All downloads completed. Files saved in folder: {folder_name}")

if __name__ == "__main__":
    main()
