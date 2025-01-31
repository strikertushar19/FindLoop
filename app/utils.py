import requests
import fitz  # PyMuPDF
import os
import pickle
from dotenv import load_dotenv
import hashlib
import urllib.parse

# Load environment variables from .env file
load_dotenv()

# Get API Key from .env
API_KEY = os.getenv("GOOGLE_API_KEY")
CX =os.getenv("GOOGLE_SEARCH_ID")

CACHE_DIR = os.getenv("CACHE_DIR")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_filename(key):
    """Generate a cache filename based on the hash of the key."""
    return os.path.join(CACHE_DIR, hashlib.md5(key.encode()).hexdigest() + ".pkl")

def load_cache(key):
    """Load cached data from file."""
    cache_filename = get_cache_filename(key)
    if os.path.exists(cache_filename):
        with open(cache_filename, "rb") as f:
            return pickle.load(f)
    return None

def save_cache(key, data):
    """Save data to cache."""
    cache_filename = get_cache_filename(key)
    with open(cache_filename, "wb") as f:
        pickle.dump(data, f)

def get_pdf_links(query, num_pages=1):
    """Fetch PDF links using Google Custom Search API with caching and pagination."""
    cached_result = load_cache(query)
    if cached_result:
        print("🔄 Using cached results for:", query)
        return cached_result

    search_url = "https://www.googleapis.com/customsearch/v1"
    pdf_links = []
    start = 1  # Start from the first result

    for page in range(num_pages):
        params = {
            "q": query + " filetype:pdf",  # Search only PDFs
            "key": API_KEY,
            "cx": CX,  # Google Custom Search Engine ID
            "num": 10,  # Max 10 results per page
            "start": start  # Pagination start value
        }

        print(f"🔍 Searching PDFs for: {query} (Page {page + 1})")
        response = requests.get(search_url, params=params)
        print(f"📝 Response Status Code: {response.status_code}")

        if response.status_code != 200:
            print("⚠️ Error: Failed to fetch search results!")
            print("Response:", response.text)
            break

        data = response.json()
        pdf_links += [item["link"] for item in data.get("items", []) if item["link"].endswith(".pdf")]

        # If fewer than 10 results are returned, stop pagination
        if len(data.get("items", [])) < 10:
            break

        start += 10  # Move to the next set of results

    print("📜 PDF LINKS FOUND:")
    for pdf in pdf_links:
        print(pdf)

    # Cache the result
    save_cache(query, pdf_links)

    return pdf_links


def sanitize_filename(url):
    """Generate a sanitized filename from the URL."""
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Get the path from the URL and strip leading '/'. Split it by '/'
    file_name = parsed_url.path.strip('/').replace('/', '_')
    
    # Replace ? and . with '_'
    file_name = file_name.replace('?', '_').replace('.', '_')
    
    # Ensure the file has a .pdf extension
    if not file_name.endswith('.pdf'):
        file_name += '.pdf'
    
    return file_name

def download_pdfs(links, save_dir="pdfs"):
    """Download PDFs from the extracted links with sanitized names."""
    os.makedirs(save_dir, exist_ok=True)
    print("📥 Starting PDF download...")

    for idx, link in enumerate(links):
        try:
            # Sanitize the file name
            pdf_filename = sanitize_filename(link)
            file_path = os.path.join(save_dir, pdf_filename)

            # Check if the PDF is already downloaded
            if os.path.exists(file_path):
                print(f"📂 Already exists: {file_path}")
                continue

            print(f"⬇️ Downloading: {link}")
            pdf_data = requests.get(link, timeout=10).content
            
            with open(file_path, "wb") as f:
                f.write(pdf_data)
            print(f"✅ Saved: {file_path}")
        except Exception as e:
            print(f"❌ Failed to download {link}: {e}")

def extract_text_from_pdfs(pdf_dir="pdfs"):
    """Extract text from downloaded PDFs with caching."""
    cached_text = load_cache("pdf_text")
    if cached_text:
        print("🔄 Using cached text extraction.")
        return cached_text

    text_data = ""
    print("📖 Extracting text from PDFs...")

    for file in os.listdir(pdf_dir):
        if file.endswith(".pdf"):
            file_path = os.path.join(pdf_dir, file)
            print(f"📝 Processing: {file_path}")

            try:
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text_data += page.get_text()
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
    
    print("✅ Text extraction completed!")
    # Cache the extracted text
    save_cache("pdf_text", text_data)

    return text_data

# # Example Usage
# query = "recurrence relation of heap sort"
# pdf_links = get_pdf_links(query)

# if pdf_links:
#     download_pdfs(pdf_links)
#     extracted_text = extract_text_from_pdfs()
#     print("📜 Extracted Content Preview:\n", extracted_text[:500])  # Show first 500 chars
# else:
#     print("⚠️ No PDF links found!")
