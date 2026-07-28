import requests # pyright: ignore[reportMissingModuleSource]
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
import csv

def scrape_fake_jobs():
    # 1. Define the target URL and a standard User-Agent to avoid being blocked
    url = "https://realpython.github.io/fake-jobs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    print(f"Fetching data from {url}...")
    
    # 2. Fetch the webpage with error handling
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch the webpage: {e}")
        return

    # 3. Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("div", class_="card-content")
    
    if not job_cards:
        print("⚠️ No job cards found. The website structure might have changed.")
        return

    jobs_data = []
    
    # 4. Extract data from each job card
    for card in job_cards:
        # Extract Job Title (handles missing element)
        title_elem = card.find("h2", class_="title is-5")
        title = title_elem.text.strip() if title_elem else "N/A"
        
        # Extract Company Name (handles missing element)
        company_elem = card.find("h3", class_="subtitle is-6 company")
        company = company_elem.text.strip() if company_elem else "N/A"
        
        # Extract Location (handles missing element)
        location_elem = card.find("p", class_="location")
        location = location_elem.text.strip() if location_elem else "N/A"
        
        # Extract Job Detail Page URL
        # The URL is inside the <footer> tag, which is a sibling of the .card-content div
        footer = card.find_next_sibling("footer", class_="card-footer")
        job_url = "N/A"
        
        if footer:
            # Look for the "Apply" link specifically
            apply_link = footer.find("a", class_="card-footer-item", string="Apply")
            
            # Fallback: if exact string match fails (e.g., due to hidden whitespace), search manually
            if not apply_link:
                for link in footer.find_all("a", class_="card-footer-item"):
                    if "Apply" in link.text:
                        apply_link = link
                        break
            
            if apply_link:
                job_url = apply_link.get("href", "N/A")
        
        # Append the extracted data as a dictionary
        jobs_data.append({
            "title": title,
            "company": company,
            "location": location,
            "url": job_url
        })

    # 5. Save the results to a CSV file
    csv_filename = "fake_jobs.csv"
    try:
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
            fieldnames = ["title", "company", "location", "url"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(jobs_data)
            
        print(f"✅ Successfully scraped {len(jobs_data)} jobs and saved to '{csv_filename}'.")
    except IOError as e:
        print(f"❌ Failed to write to CSV file: {e}")

if __name__ == "__main__":
    scrape_fake_jobs()
