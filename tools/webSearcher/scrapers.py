
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import io
import re
import os
from dotenv import load_dotenv
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

try:
    import trafilatura
except ImportError:
    trafilatura = None

import concurrent.futures
try:
    from keybert import KeyBERT
except ImportError:
    KeyBERT = None

load_dotenv()

# Global model cache
_kw_model = None
def get_kw_model():
    global _kw_model
    if _kw_model is None and KeyBERT is not None:
        try:
             # Use a smaller model for speed
            _kw_model = KeyBERT('all-MiniLM-L6-v2')
        except Exception as e:
            pass
    return _kw_model

# Try importing pypdf, handle if missing
try:
    import pypdf
except ImportError:
    pypdf = None

class BaseScraper(ABC):
    """
    Abstract base class for all web scrapers.
    """
    
    @abstractmethod
    def fetch(self, query: str) -> dict:
        """
        Fetches and extracts content from the given query (URL).
        
        Args:
            query (str): The URL to scrape.
            
        Returns:
            dict: A dictionary containing 'topic', 'content', and 'source'.
        """
        pass

    def _clean_text(self, text: str) -> str:
        """Helper to clean whitespace from text."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    # Fallback URL mappings for common queries (when SerpAPI quota exhausted)
    FALLBACK_URLS = {
        "geeksforgeeks.org": {
            "binary search": "https://www.geeksforgeeks.org/binary-search/",
            "data structures": "https://www.geeksforgeeks.org/data-structures/",
            "algorithms": "https://www.geeksforgeeks.org/fundamentals-of-algorithms/",
            "programming": "https://www.geeksforgeeks.org/introduction-to-programming-languages/",
            "control structures": "https://www.geeksforgeeks.org/decision-making-c-cpp/",
            "arrays": "https://www.geeksforgeeks.org/array-data-structure/",
            "stacks": "https://www.geeksforgeeks.org/stack-data-structure/",
            "queues": "https://www.geeksforgeeks.org/queue-data-structure/",
        },
        "w3schools.com": {
            "javascript": "https://www.w3schools.com/js/",
            "python": "https://www.w3schools.com/python/",
            "arrays": "https://www.w3schools.com/js/js_arrays.asp",
        },
        "wikipedia.org": {
            "machine learning": "https://en.wikipedia.org/wiki/Machine_learning",
            "programming": "https://en.wikipedia.org/wiki/Computer_programming",
        },
        "docs.python.org": {
            "python": "https://docs.python.org/3/tutorial/",
            "list": "https://docs.python.org/3/tutorial/datastructures.html",
        }
    }
    
    def _get_fallback_url(self, query: str, site_filter: str) -> str:
        """Try to find a fallback URL from predefined mappings"""
        if not site_filter:
            return None
            
        query_lower = query.lower()
        site_mappings = self.FALLBACK_URLS.get(site_filter, {})
        
        # Try exact match first
        if query_lower in site_mappings:
            return site_mappings[query_lower]
        
        # Try partial match
        for key, url in site_mappings.items():
            if key in query_lower or query_lower in key:
                return url
        
        return None
    
    def _resolve_url(self, query: str, site_filter: str = None) -> str:
        """
        Resolves a search query to a URL using multi-search engine.
        Priority: Tavily → DuckDuckGo → Google CSE → Fallback URLs
        If query is already a URL, returns it.
        Returns None if resolution fails.
        """
        # Check if query is a URL
        if re.match(r'^https?://', query):
            return query

        # Try Tavily first (best for RAG)
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key:
            try:
                from tavily import TavilyClient
                
                search_query = query
                if site_filter:
                    search_query += f" site:{site_filter}"
                
                print(f"🔍 Searching with Tavily: {search_query}")
                client = TavilyClient(api_key=tavily_key)
                response = client.search(query=search_query, max_results=1)
                
                if response and 'results' in response and len(response['results']) > 0:
                    url = response['results'][0].get('url')
                    if url:
                        print(f"✅ Found URL via Tavily: {url}")
                        return url
                
                print(f"⚠️ Tavily returned no results, trying DuckDuckGo...")
                
            except Exception as e:
                print(f"⚠️ Tavily error: {str(e)}, trying DuckDuckGo...")
        
        # Try DuckDuckGo (free, unlimited)
        if DDGS:
            try:
                search_query = query
                if site_filter:
                    search_query += f" site:{site_filter}"
                
                print(f"🔍 Searching with DuckDuckGo: {search_query}")
                
                # Use DuckDuckGo search
                with DDGS() as ddgs:
                    results = list(ddgs.text(search_query, max_results=1))
                
                if results and len(results) > 0:
                    url = results[0].get('href') or results[0].get('link')
                    if url:
                        print(f"✅ Found URL via DuckDuckGo: {url}")
                        return url
                
                print(f"⚠️ DuckDuckGo returned no results, trying fallback...")
                
            except Exception as e:
                print(f"⚠️ DuckDuckGo error: {str(e)}, trying fallback...")
        
        # Try Google CSE (100 queries/day free)
        google_cse_key = os.getenv("GOOGLE_CSE_API_KEY")
        google_cse_id = os.getenv("GOOGLE_CSE_ID")
        if google_cse_key and google_cse_id:
            try:
                from googleapiclient.discovery import build
                
                search_query = query
                if site_filter:
                    search_query += f" site:{site_filter}"
                
                print(f"🔍 Searching with Google CSE: {search_query}")
                service = build("customsearch", "v1", developerKey=google_cse_key)
                result = service.cse().list(q=search_query, cx=google_cse_id, num=1).execute()
                
                if 'items' in result and len(result['items']) > 0:
                    url = result['items'][0].get('link')
                    if url:
                        print(f"✅ Found URL via Google CSE: {url}")
                        return url
                
                print(f"⚠️ Google CSE returned no results, trying fallback...")
                
            except Exception as e:
                print(f"⚠️ Google CSE error: {str(e)}, trying fallback...")
        
        # Try fallback URL mapping
        if site_filter:
            fallback_url = self._get_fallback_url(query, site_filter)
            if fallback_url:
                print(f"✅ Using fallback URL: {fallback_url}")
                return fallback_url
        
        print(f"❌ Could not resolve URL for query: {query}")
        return None


    def _extract_additional_topics(self, content: str) -> list:
        """Extracts keywords/topics from content using KeyBERT with safe chunking and multi-threading."""
        kw_model = get_kw_model()
        if not kw_model or not content:
            return []

        try:
            # -------- Chunk into ~400-word blocks --------
            words = content.split()
            chunk_size = 400
            chunks = [
                " ".join(words[i:i + chunk_size])
                for i in range(0, len(words), chunk_size)
            ]

            all_keywords = []

            def process_chunk(chunk):
                try:
                    keywords = kw_model.extract_keywords(
                        chunk,
                        keyphrase_ngram_range=(1, 2),  # 1–2 word topics
                        stop_words='english',
                        top_n=5                         # topics per chunk
                    )
                    return [kw[0] for kw in keywords]
                except Exception:
                    return []

            # Use ThreadPoolExecutor for parallel processing
            # Using threads because KeyBERT/PyTorch might release GIL for heavy ops
            max_workers = 12
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(process_chunk, chunks))
            
            for res in results:
                all_keywords.extend(res)

            # -------- Deduplicate while keeping order --------
            seen = set()
            unique_topics = []
            for kw in all_keywords:
                kw_lower = kw.lower()
                if kw_lower not in seen:
                    seen.add(kw_lower)
                    unique_topics.append(kw)

            return unique_topics

        except Exception as e:
            # print(f"KeyBERT extraction failed: {e}") # Keeping clean logs
            return []

    def _get_soup_with_trafilatura(self, url: str) -> tuple:
        """
        Get both BeautifulSoup and Trafilatura-extracted content
        Returns: (soup, clean_text)
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get HTML
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract clean text with Trafilatura (removes ads, nav, etc.)
        clean_text = ""
        if trafilatura:
            try:
                clean_text = trafilatura.extract(response.text, output_format='txt') or ""
            except:
                pass
        
        return soup, clean_text


    def _get_soup(self, url: str) -> BeautifulSoup:
        """Helper to get BeautifulSoup object."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')

class W3SchoolsScraper(BaseScraper):
    """
    Scraper for W3Schools.
    Scrapes definitions, syntax, and simple examples.
    Ignores ads, navigation, and unrelated sections.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="w3schools.com")
            if not url:
                return {"topic": [], "content": "", "source": "W3Schools", "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            # Main content area usually in 'w3-main' or 'main'
            main_content = soup.find('div', {'id': 'main'}) or soup.find('div', class_='w3-main')
            
            if not main_content:
                return {"topic": "", "content": "", "source": "W3Schools", "error": "Could not find main content"}

            # Extract Topic (H1)
            h1 = main_content.find('h1')
            topic = h1.get_text(strip=True) if h1 else ""
            if h1:
                h1.decompose() # Remove from content flow to avoid duplication

            # Cleanup
            for unwanted in main_content.find_all(['div'], class_=['w3-col', 'w3-sidebar', 'w3-bar', 'nextprev']):
                unwanted.decompose()
            for pattern in [re.compile(r'ad'), re.compile(r'advert')]:
                for ad in main_content.find_all(class_=pattern):
                    ad.decompose()

            extracted_parts = []
            
            # We want definitions (h2 + p), syntax (pre/code), simple examples (div.w3-example)
            for element in main_content.find_all(['h2', 'p', 'pre', 'div']):
                if element.name == 'div' and 'w3-example' in element.get('class', []):
                    # Handle example
                    code_box = element.find(['div'], class_='w3-code')
                    if code_box:
                        extracted_parts.append(f"Example:\n{code_box.get_text(strip=True)}")
                elif element.name == 'h2':
                    extracted_parts.append(f"\n## {element.get_text(strip=True)}")
                elif element.name == 'p':
                    extracted_parts.append(element.get_text(strip=True))
                elif element.name == 'pre':
                    extracted_parts.append(f"Code:\n{element.get_text(strip=True)}")

            content = "\n\n".join(filter(None, extracted_parts))
            
            # Form topic list
            topics = [topic] if topic else []
            # topics.extend(self._extract_additional_topics(content))
            print(list(set(topics)))
            return {
                "topic": list(set(topics)), # Return distinct list
                "content": content,
                "source": "W3Schools"
            }

        except Exception as e:
            return {"topic": [], "content": "", "source": "W3Schools", "error": str(e)}


class GeeksForGeeksScraper(BaseScraper):
    """
    Scraper for GeeksForGeeks.
    Scrapes concept explanations, short theory, basic algorithms.
    Ignores full code dumps, interview Q&A.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="geeksforgeeks.org")
            if not url:
                return {"topic": [], "content": "", "source": "GeeksForGeeks", "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            # GFG content structure often changes
            article = soup.find('article') or soup.find('div', class_='text') or soup.find('div', class_='article_content')
            
            if not article:
                return {"topic": "", "content": "", "source": "GeeksForGeeks", "error": "Could not find article content"}

            # Extract Topic
            # Try to find H1 inside article or globally if not found
            h1 = article.find('h1') or soup.find('h1')
            topic = h1.get_text(strip=True) if h1 else ""
            # Don't decompose globally found h1 if it's outside article, but if inside, remove.
            if h1 and h1 in article.descendants:
                h1.decompose()

            # Remove unwanted elements
            for unwanted in article.find_all(['div'], class_=['comments', 'improved', 'print-main', 'share-icons']):
                unwanted.decompose()
            
            extracted_parts = []
            
            for element in article.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'pre']):
                text = element.get_text(strip=True)
                if not text:
                    continue
                
                # Heuristic to skip Interview Questions sections
                if "Interview Questions" in text and element.name in ['h2', 'h3']:
                    break 

                if element.name in ['h2', 'h3']:
                    extracted_parts.append(f"\n### {text}")
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        extracted_parts.append(f"- {li.get_text(strip=True)}")
                elif element.name == 'pre':
                     extracted_parts.append(f"```\n{text}\n```")
                else:
                    extracted_parts.append(text)

            content = "\n\n".join(extracted_parts)
            
            topics = [topic] if topic else []
            topics.extend(self._extract_additional_topics(content))

            return {
                "topic": list(set(topics)),
                "content": content,
                "source": "GeeksForGeeks"
            }

        except Exception as e:
             return {"topic": [], "content": "", "source": "GeeksForGeeks", "error": str(e)}

class NPTELScraper(BaseScraper):
    """
    Scraper for NPTEL.
    Scrapes lecture transcript text, definition paragraphs.
    Handles PDF if encountered.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="nptel.ac.in")
            if not url:
                return {"topic": [], "content": "", "source": "NPTEL", "error": "Could not resolve URL from query"}
            
            # Check if PDF
            if url.lower().endswith('.pdf'):
                return self._fetch_pdf(url, "NPTEL")
            
            soup = self._get_soup(url)
            
            content_div = soup.find('div', class_='content') or soup.find('div', id='content') or soup.body

            # Attempt to find topic
            h1 = soup.find('h1') or content_div.find('div', class_='header')
            topic = h1.get_text(strip=True) if h1 else "NPTEL Lecture"

            # Remove metadata
            for unwanted in content_div.find_all(['div'], class_=['header', 'footer', 'nav', 'menu', 'instructor']):
                unwanted.decompose()
            if h1 and h1.name: h1.decompose() # if h1 is a tag

            extracted_text = []
            for p in content_div.find_all('p'):
                text = p.get_text(strip=True)
                # Heuristic to ignore course metadata lines
                if "Course:" in text or "Instructor:" in text:
                    continue
                extracted_text.append(text)

            final_content = "\n\n".join(extracted_text)
            
            return {
                "topic": [topic],
                # "topic": list(set([topic] + self._extract_additional_topics(final_content))),
                "content": final_content,
                "source": "NPTEL"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "NPTEL", "error": str(e)}

    def _fetch_pdf(self, url: str, source_name: str) -> dict:
        if not pypdf:
            return {"topic": ["Unknown PDF"], "content": "pypdf not installed, cannot scrape PDF", "source": source_name}
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            with io.BytesIO(response.content) as f:
                reader = pypdf.PdfReader(f)
                text = []
                # Try to get metadata title
                topic = reader.metadata.get('/Title', source_name + " PDF") if reader.metadata else source_name + " PDF"
                for page in reader.pages:
                    text.append(page.extract_text())
            
            final_content = "\n".join(text)
            print("✨ Processing additional topics...")
            return {
                "topic": [topic],
                # "topic": list(set([topic] + self._extract_additional_topics(final_content[:5000]))),
                "content": final_content,
                "source": source_name
            }
        except Exception as e:
             return {"topic": [], "content": "", "source": source_name, "error": str(e)}

class MITOCWScraper(BaseScraper):
    """
    Scraper for MIT OCW.
    Scrapes lecture notes, theory sections.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="ocw.mit.edu")
            if not url:
                return {"topic": [], "content": "", "source": "MITOCW", "error": "Could not resolve URL from query"}
            
            # Check for PDF lecture notes
            if url.lower().endswith('.pdf'):
                 return self._scrape_pdf(url)

            soup = self._get_soup(url)
            
            main_content = soup.find('main') or soup.find('div', id='course-content-section')
            
            if not main_content:
                return {"topic": "", "content": "", "source": "MITOCW", "error": "Main content not found"}

            # Extract Topic
            h1 = main_content.find('h1')
            topic = h1.get_text(strip=True) if h1 else "MIT OCW Lecture"
            if h1: h1.decompose()

            # Remove syllabus/schedule
            for section in main_content.find_all(['div', 'section']):
                if section.get('id') in ['syllabus', 'calendar', 'schedule']:
                    section.decompose()
            
            # Extract text
            content = []
            for element in main_content.find_all(['h2', 'h3', 'p', 'div']):
                 if element.name == 'div' and not element.get_text(strip=True):
                     continue
                 content.append(element.get_text(strip=True))

            final_content = "\n\n".join(content)
            
            return {
                "topic": [topic],
                # "topic": list(set([topic] + self._extract_additional_topics(final_content))),
                "content": final_content,
                "source": "MITOCW"
            }
        except Exception as e:
             return {"topic": [], "content": "", "source": "MITOCW", "error": str(e)}

    def _scrape_pdf(self, url):
        if not pypdf:
            return {"topic": [], "content": "pypdf missing", "source": "MITOCW"}
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            reader = pypdf.PdfReader(io.BytesIO(r.content))
            topic = reader.metadata.get('/Title', "MIT OCW PDF") if reader.metadata else "MIT OCW PDF"
            text = [p.extract_text() for p in reader.pages]
            final_content = "\n".join(text)
            return {"topic": [topic], "content": final_content, "source": "MITOCW"}
        except Exception as e:
            return {"topic": [], "content": "", "source": "MITOCW", "error": str(e)}


class OpenStaxScraper(BaseScraper):
    """
    Scraper for OpenStax.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="openstax.org")
            if not url:
                return {"topic": [], "content": "", "source": "OpenStax", "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            main_content = soup.find('div', {'data-type': 'page'}) or soup.find('main')

            if not main_content:
                 return {"topic": "", "content": "", "source": "OpenStax", "error": "Content not found"}

            # Topic extraction
            # OpenStax pages often have a title span or h1
            title_elem = main_content.find('span', {'data-type': 'title'}) or main_content.find('h1')
            topic = title_elem.get_text(strip=True) if title_elem else "OpenStax Page"
            # Don't decompose if it's the only reference, or do if inside content.

            extracted = []
            
            # Prioritize definitions
            definitions = main_content.find_all('div', {'data-type': 'definition'})
            for de in definitions:
                extracted.append(f"Definition: {de.get_text(strip=True)}")
            
            intro = main_content.find('div', {'data-type': 'introduction'})
            if intro:
                extracted.append(f"Introduction: {intro.get_text(strip=True)}")
                
            summary = main_content.find('div', {'class': 'summary'})
            if summary:
                 extracted.append(f"Summary: {summary.get_text(strip=True)}")
                 
            if not extracted:
                 count = 0
                 for p in main_content.find_all('p'):
                     extracted.append(p.get_text(strip=True))
                     count += 1
                     if count > 10: 
                         extracted.append("[...Content Trucated...]")
                         break
            
            final_content = "\n\n".join(extracted)
            return {
                "topic": [topic],
                # "topic": list(set([topic] + self._extract_additional_topics(final_content))),
                "content": final_content,
                "source": "OpenStax"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "OpenStax", "error": str(e)}


class UniversityEDUScraper(BaseScraper):
    """
    Scraper for .edu sites.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter=".edu")
            if not url:
                return {"topic": [], "content": "", "source": "UniversityEDU", "error": "Could not resolve URL from query"}
            
            if url.lower().endswith('.pdf'):
                return self._scrape_pdf(url)

            soup = self._get_soup(url)
            
            # Topic: Title of the page
            topic = soup.title.get_text(strip=True) if soup.title else "University Page"
            
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {
                "topic": [topic],
                # "topic": list(set([topic] + self._extract_additional_topics(clean_text))),
                "content": clean_text,
                "source": "UniversityEDU"
            }
            
        except Exception as e:
            return {"topic": [], "content": "", "source": "UniversityEDU", "error": str(e)}

    def _scrape_pdf(self, url):
        if not pypdf:
             return {"topic": [], "content": "pypdf missing", "source": "UniversityEDU"}
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            reader = pypdf.PdfReader(io.BytesIO(r.content))
            topic = reader.metadata.get('/Title', "University PDF") if reader.metadata else "University PDF"
            text = [p.extract_text() for p in reader.pages]
            final_content = "\n".join(text)
            return {"topic": [topic], "content": final_content, "source": "UniversityEDU"}
        except Exception as e:
            return {"topic": [], "content": "", "source": "UniversityEDU", "error": str(e)}


# ============ INDIAN EDUCATIONAL CONTENT SCRAPERS ============

class NCERTScraper(BaseScraper):
    """
    Scraper for NCERT official content.
    Priority scraper for Indian 12th grade syllabus.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="ncert.nic.in")
            if not url:
                return {"topic": [], "content": "", "source": "NCERT", "error": "Could not resolve URL from query"}
            
            if url.lower().endswith('.pdf'):
                return self._fetch_pdf(url, "NCERT")
            
            soup = self._get_soup(url)
            
            # NCERT pages typically have content in main or article
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            
            if not main_content:
                main_content = soup.body
            
            # Extract topic
            h1 = soup.find('h1')
            topic = h1.get_text(strip=True) if h1 else "NCERT Content"
            
            # Remove navigation, footer, header
            for unwanted in main_content.find_all(['nav', 'footer', 'header', 'aside']):
                unwanted.decompose()
            
            # Extract meaningful content
            extracted = []
            for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'div']):
                text = element.get_text(strip=True)
                if text and len(text) > 20:  # Filter out short/empty elements
                    if element.name in ['h2', 'h3']:
                        extracted.append(f"\n### {text}")
                    elif element.name in ['ul', 'ol']:
                        for li in element.find_all('li'):
                            extracted.append(f"- {li.get_text(strip=True)}")
                    else:
                        extracted.append(text)
            
            final_content = "\n\n".join(extracted)
            
            return {
                "topic": [topic],
                "content": final_content,
                "source": "NCERT"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "NCERT", "error": str(e)}
    
    def _fetch_pdf(self, url: str, source_name: str) -> dict:
        if not pypdf:
            return {"topic": ["Unknown PDF"], "content": "pypdf not installed", "source": source_name}
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            with io.BytesIO(response.content) as f:
                reader = pypdf.PdfReader(f)
                text = []
                topic = reader.metadata.get('/Title', source_name + " PDF") if reader.metadata else source_name + " PDF"
                for page in reader.pages:
                    text.append(page.extract_text())
            
            final_content = "\n".join(text)
            return {
                "topic": [topic],
                "content": final_content,
                "source": source_name
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": source_name, "error": str(e)}


class CBSEScraper(BaseScraper):
    """
    Scraper for CBSE official content.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="cbse.gov.in")
            if not url:
                return {"topic": [], "content": "", "source": "CBSE", "error": "Could not resolve URL from query"}
            
            if url.lower().endswith('.pdf'):
                return self._fetch_pdf(url, "CBSE")
            
            soup = self._get_soup(url)
            
            # Extract topic
            h1 = soup.find('h1')
            topic = h1.get_text(strip=True) if h1 else "CBSE Content"
            
            # Remove unwanted elements
            for unwanted in soup.find_all(['nav', 'footer', 'header', 'script', 'style']):
                unwanted.decompose()
            
            # Extract content
            main_content = soup.find('main') or soup.find('article') or soup.body
            
            extracted = []
            for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
                text = element.get_text(strip=True)
                if text and len(text) > 15:
                    extracted.append(text)
            
            final_content = "\n\n".join(extracted)
            
            return {
                "topic": [topic],
                "content": final_content,
                "source": "CBSE"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "CBSE", "error": str(e)}
    
    def _fetch_pdf(self, url: str, source_name: str) -> dict:
        if not pypdf:
            return {"topic": ["Unknown PDF"], "content": "pypdf not installed", "source": source_name}
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            with io.BytesIO(response.content) as f:
                reader = pypdf.PdfReader(f)
                text = []
                topic = reader.metadata.get('/Title', source_name + " PDF") if reader.metadata else source_name + " PDF"
                for page in reader.pages:
                    text.append(page.extract_text())
            
            final_content = "\n".join(text)
            return {
                "topic": [topic],
                "content": final_content,
                "source": source_name
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": source_name, "error": str(e)}


class DIKSHAScraper(BaseScraper):
    """
    Scraper for DIKSHA platform (Government of India).
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="diksha.gov.in")
            if not url:
                return {"topic": [], "content": "", "source": "DIKSHA", "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            # Extract topic
            h1 = soup.find('h1')
            topic = h1.get_text(strip=True) if h1 else "DIKSHA Content"
            
            # Remove unwanted elements
            for unwanted in soup.find_all(['nav', 'footer', 'header', 'script', 'style']):
                unwanted.decompose()
            
            # Extract content
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.body
            
            extracted = []
            for element in main_content.find_all(['h2', 'h3', 'p', 'div']):
                text = element.get_text(strip=True)
                if text and len(text) > 20:
                    extracted.append(text)
            
            final_content = "\n\n".join(extracted)
            
            return {
                "topic": [topic],
                "content": final_content,
                "source": "DIKSHA"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "DIKSHA", "error": str(e)}


class NROERScraper(BaseScraper):
    """
    Scraper for NROER (National Repository of Open Educational Resources).
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="nroer.gov.in")
            if not url:
                return {"topic": [], "content": "", "source": "NROER", "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            # Extract topic
            h1 = soup.find('h1')
            topic = h1.get_text(strip=True) if h1 else "NROER Content"
            
            # Remove unwanted elements
            for unwanted in soup.find_all(['nav', 'footer', 'header', 'script', 'style']):
                unwanted.decompose()
            
            # Extract content
            main_content = soup.find('main') or soup.find('article') or soup.body
            
            extracted = []
            for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
                text = element.get_text(strip=True)
                if text and len(text) > 15:
                    extracted.append(text)
            
            final_content = "\n\n".join(extracted)
            
            return {
                "topic": [topic],
                "content": final_content,
                "source": "NROER"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "NROER", "error": str(e)}


# ============ OFFICIAL DOCUMENTATION SCRAPERS ============

class OfficialDocsScraper(BaseScraper):
    """
    Generic scraper for official documentation sites.
    Supports: docs.python.org, pytorch.org/docs, tensorflow.org, 
    developer.mozilla.org, kubernetes.io/docs, etc.
    """
    def fetch(self, query: str) -> dict:
        try:
            # Determine site filter based on query
            site_filter = None
            source_name = "Official Docs"
            
            if "python" in query.lower():
                site_filter = "docs.python.org"
                source_name = "Python Docs"
            elif "pytorch" in query.lower():
                site_filter = "pytorch.org"
                source_name = "PyTorch Docs"
            elif "tensorflow" in query.lower():
                site_filter = "tensorflow.org"
                source_name = "TensorFlow Docs"
            elif "javascript" in query.lower() or "mdn" in query.lower():
                site_filter = "developer.mozilla.org"
                source_name = "MDN"
            elif "kubernetes" in query.lower():
                site_filter = "kubernetes.io"
                source_name = "Kubernetes Docs"
            
            url = self._resolve_url(query, site_filter=site_filter)
            if not url:
                return {"topic": [], "content": "", "source": source_name, "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            # Extract topic
            h1 = soup.find('h1')
            topic = h1.get_text(strip=True) if h1 else source_name
            
            # Find main content
            main_content = (soup.find('main') or 
                          soup.find('article') or 
                          soup.find('div', class_='document') or
                          soup.find('div', class_='content'))
            
            if not main_content:
                main_content = soup.body
            
            # Remove navigation, sidebar, footer
            for unwanted in main_content.find_all(['nav', 'footer', 'header', 'aside', 'script', 'style']):
                unwanted.decompose()
            
            # Extract structured content
            extracted = []
            for element in main_content.find_all(['h2', 'h3', 'p', 'pre', 'code', 'ul', 'ol']):
                text = element.get_text(strip=True)
                if not text or len(text) < 10:
                    continue
                
                if element.name in ['h2', 'h3']:
                    extracted.append(f"\n### {text}")
                elif element.name in ['pre', 'code']:
                    extracted.append(f"```\n{text}\n```")
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        extracted.append(f"- {li.get_text(strip=True)}")
                else:
                    extracted.append(text)
            
            final_content = "\n\n".join(extracted)
            
            return {
                "topic": [topic],
                "content": final_content,
                "source": source_name
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "Official Docs", "error": str(e)}


class WikipediaScraper(BaseScraper):
    """
    Scraper for Wikipedia content.
    Good for definitions, history, and fundamental concepts.
    """
    def fetch(self, query: str) -> dict:
        try:
            url = self._resolve_url(query, site_filter="wikipedia.org")
            if not url:
                return {"topic": [], "content": "", "source": "Wikipedia", "error": "Could not resolve URL from query"}
            soup = self._get_soup(url)
            
            # Extract topic from title
            h1 = soup.find('h1', class_='firstHeading')
            topic = h1.get_text(strip=True) if h1 else "Wikipedia Article"
            
            # Find main content
            content_div = soup.find('div', id='mw-content-text')
            
            if not content_div:
                return {"topic": [], "content": "", "source": "Wikipedia", "error": "Content not found"}
            
            # Remove unwanted elements
            for unwanted in content_div.find_all(['table', 'div'], class_=['infobox', 'navbox', 'metadata', 'reflist']):
                unwanted.decompose()
            for unwanted in content_div.find_all(['sup', 'style', 'script']):
                unwanted.decompose()
            
            # Extract paragraphs and headings
            extracted = []
            for element in content_div.find_all(['h2', 'h3', 'p'], limit=50):
                text = element.get_text(strip=True)
                if not text or len(text) < 20:
                    continue
                
                # Stop at "See also" or "References" sections
                if element.name in ['h2', 'h3'] and any(x in text for x in ['See also', 'References', 'External links']):
                    break
                
                if element.name in ['h2', 'h3']:
                    extracted.append(f"\n### {text}")
                else:
                    extracted.append(text)
            
            final_content = "\n\n".join(extracted)
            
            return {
                "topic": [topic],
                "content": final_content,
                "source": "Wikipedia"
            }
        except Exception as e:
            return {"topic": [], "content": "", "source": "Wikipedia", "error": str(e)}

