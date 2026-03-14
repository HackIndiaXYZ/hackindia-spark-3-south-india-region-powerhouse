"""
Enhanced Web Search Module with Multiple Free Alternatives
Supports: DuckDuckGo, Tavily, Google CSE, and Direct Scraping
"""

import os
from dotenv import load_dotenv
try:
    import trafilatura
except ImportError:
    trafilatura = None
import requests

load_dotenv()

# Import all available search engines
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

try:
    from googleapiclient.discovery import build
except ImportError:
    build = None


class MultiSearchEngine:
    """
    Multi-engine search with automatic fallback
    Priority: Tavily > DuckDuckGo > Google CSE > Fallback URLs
    """
    
    def __init__(self):
        # Load API keys (optional - most are free)
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        self.google_cse_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        
        # Initialize clients
        self.tavily_client = None
        if self.tavily_key and TavilyClient:
            try:
                self.tavily_client = TavilyClient(api_key=self.tavily_key)
            except:
                pass
    
    def search(self, query: str, site_filter: str = None, max_results: int = 1) -> list:
        """
        Search using multiple engines with automatic fallback
        Returns list of {'title': str, 'url': str, 'snippet': str}
        """
        
        # Try Tavily first (best for RAG)
        if self.tavily_client:
            try:
                results = self._search_tavily(query, site_filter, max_results)
                if results:
                    print(f"✅ Found {len(results)} results via Tavily")
                    return results
            except Exception as e:
                print(f"⚠️ Tavily search failed: {e}")
        
        # Try DuckDuckGo (free, unlimited)
        if DDGS:
            try:
                results = self._search_duckduckgo(query, site_filter, max_results)
                if results:
                    print(f"✅ Found {len(results)} results via DuckDuckGo")
                    return results
            except Exception as e:
                print(f"⚠️ DuckDuckGo search failed: {e}")
        
        # Try Google CSE (100 queries/day free)
        if self.google_cse_key and self.google_cse_id and build:
            try:
                results = self._search_google_cse(query, site_filter, max_results)
                if results:
                    print(f"✅ Found {len(results)} results via Google CSE")
                    return results
            except Exception as e:
                print(f"⚠️ Google CSE search failed: {e}")
        
        print(f"❌ All search engines failed for query: {query}")
        return []
    
    def _search_tavily(self, query: str, site_filter: str = None, max_results: int = 1) -> list:
        """Search using Tavily (best for RAG)"""
        search_query = query
        if site_filter:
            search_query += f" site:{site_filter}"
        
        response = self.tavily_client.search(
            query=search_query,
            max_results=max_results,
            include_raw_content=True
        )
        
        results = []
        for item in response.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'snippet': item.get('content', '')
            })
        return results
    
    def _search_duckduckgo(self, query: str, site_filter: str = None, max_results: int = 1) -> list:
        """Search using DuckDuckGo (free, unlimited)"""
        search_query = query
        if site_filter:
            search_query += f" site:{site_filter}"
        
        with DDGS() as ddgs:
            search_results = list(ddgs.text(search_query, max_results=max_results))
        
        results = []
        for item in search_results:
            results.append({
                'title': item.get('title', ''),
                'url': item.get('href', '') or item.get('link', ''),
                'snippet': item.get('body', '') or item.get('snippet', '')
            })
        return results
    
    def _search_google_cse(self, query: str, site_filter: str = None, max_results: int = 1) -> list:
        """Search using Google Custom Search Engine"""
        service = build("customsearch", "v1", developerKey=self.google_cse_key)
        
        search_query = query
        if site_filter:
            search_query += f" site:{site_filter}"
        
        result = service.cse().list(
            q=search_query,
            cx=self.google_cse_id,
            num=max_results
        ).execute()
        
        results = []
        for item in result.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        return results


class EnhancedContentExtractor:
    """
    Enhanced content extraction using Trafilatura
    Automatically removes ads, navigation, and noise
    """
    
    @staticmethod
    def extract_from_url(url: str) -> dict:
        """
        Extract clean content from URL using Trafilatura
        Returns: {'content': str, 'title': str, 'author': str, 'date': str}
        """
        try:
            print(f"📥 Downloading content from: {url}")
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                print(f"⚠️ Failed to download: {url}")
                return {'content': '', 'title': '', 'author': '', 'date': ''}
            
            # Extract with metadata
            content = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                include_images=False,
                output_format='txt'
            )
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            result = {
                'content': content or '',
                'title': metadata.title if metadata else '',
                'author': metadata.author if metadata else '',
                'date': metadata.date if metadata else ''
            }
            
            if content:
                print(f"✅ Extracted {len(content)} characters of clean content")
            else:
                print(f"⚠️ No content extracted from: {url}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error extracting content from {url}: {e}")
            return {'content': '', 'title': '', 'author': '', 'date': ''}
    
    @staticmethod
    def extract_from_html(html: str) -> str:
        """Extract clean content from HTML string"""
        try:
            content = trafilatura.extract(html, output_format='txt')
            return content or ''
        except Exception as e:
            print(f"❌ Error extracting from HTML: {e}")
            return ''


# Convenience functions
def search_and_extract(query: str, site_filter: str = None, max_results: int = 1) -> list:
    """
    Search for URLs and extract clean content in one step
    Returns list of {'url': str, 'title': str, 'content': str}
    """
    searcher = MultiSearchEngine()
    extractor = EnhancedContentExtractor()
    
    # Search for URLs
    search_results = searcher.search(query, site_filter, max_results)
    
    # Extract content from each URL
    results = []
    for item in search_results:
        url = item['url']
        extracted = extractor.extract_from_url(url)
        
        results.append({
            'url': url,
            'title': extracted['title'] or item['title'],
            'content': extracted['content'],
            'snippet': item['snippet']
        })
    
    return results


if __name__ == "__main__":
    # Test the multi-search engine
    print("\n" + "="*80)
    print("TESTING MULTI-SEARCH ENGINE")
    print("="*80 + "\n")
    
    # Test 1: Search with DuckDuckGo
    print("Test 1: Searching for 'python programming' on GeeksForGeeks")
    print("-"*80)
    results = search_and_extract("python programming", site_filter="geeksforgeeks.org", max_results=1)
    
    if results:
        print(f"\n✅ SUCCESS!")
        print(f"Title: {results[0]['title']}")
        print(f"URL: {results[0]['url']}")
        print(f"Content Preview: {results[0]['content'][:300]}...")
    else:
        print("\n❌ No results found")
    
    print("\n" + "="*80)
