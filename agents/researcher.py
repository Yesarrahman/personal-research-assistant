"""
Researcher Agent - Research Assistant System

This agent performs web searches using Google Custom Search API.
It finds real sources, extracts information, and optimizes queries.

Model: Gemini 2.0 Flash Experimental
Author: Yesar Rahman
Date: November 2025
"""

import os
import requests
import logging
from typing import List, Dict
from google import generativeai as genai

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Researcher Agent that performs web searches using Google Custom Search API.

    Required Environment Variables:
        - GOOGLE_API_KEY: Gemini API key for AI operations
        - GOOGLE_SEARCH_API_KEY: Google Custom Search API key
        - GOOGLE_SEARCH_ENGINE_ID: Custom Search Engine ID

    Get these from:
        - GOOGLE_API_KEY: https://aistudio.google.com/apikey
        - GOOGLE_SEARCH_API_KEY & ENGINE_ID: https://programmablesearchengine.google.com/
    """

    def __init__(self):
        """Initialize the Researcher Agent with Gemini and Google Search."""
        # Initialize Gemini AI model
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # Load Google Custom Search credentials from environment
        self.search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        # Check if real search is available
        if not self.search_api_key or not self.search_engine_id:
            logger.warning(
                "Google Custom Search not configured. Using AI-generated fallback sources."
            )
            logger.warning("To use real search, add to .env file:")
            logger.warning("GOOGLE_SEARCH_API_KEY=your_key")
            logger.warning("GOOGLE_SEARCH_ENGINE_ID=your_engine_id")
            self.use_real_search = False
        else:
            logger.info("Google Custom Search API configured - using real web search")
            self.use_real_search = True

    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform web search and return results.

        Args:
            query: Search query string
            num_results: Number of results to return (max 10 for real search)

        Returns:
            List of dictionaries containing:
                - title: Article/page title
                - url: Full URL
                - snippet: Brief description/preview
                - source: Domain name (e.g., 'wikipedia.org')
        """
        logger.info(f"Searching for: '{query}'")

        try:
            if self.use_real_search:
                return self._google_custom_search(query, num_results)
            else:
                return self._fallback_search(query, num_results)
        except Exception as e:
            logger.error(f"Search error: {e}")
            # Return fallback results if main search fails
            return self._fallback_search(query, num_results)

    def _google_custom_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Perform real web search using Google Custom Search API.

        This uses your configured Custom Search Engine to find actual web pages.
        Free tier allows 100 searches per day.

        Args:
            query: Search query
            num_results: Number of results (max 10 per API call)

        Returns:
            List of search results with real URLs and content
        """
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"

        # Prepare search parameters
        params = {
            "key": self.search_api_key,  # Your API key from .env
            "cx": self.search_engine_id,  # Your Search Engine ID from .env
            "q": query,  # Search query
            "num": min(num_results, 10),  # Max 10 per request
        }

        try:
            # Send GET request to Google API
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes

            # Parse JSON response
            data = response.json()
            results = []

            # Extract relevant information from each result
            for item in data.get("items", []):
                results.append(
                    {
                        "title": item.get("title", "Untitled"),
                        "url": item.get("link", ""),
                        "snippet": item.get("snippet", "No description available"),
                        "source": self._extract_domain(item.get("link", "")),
                    }
                )

            logger.info(f"Found {len(results)} real search results")
            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Google Custom Search API error: {e}")

            # Check for common errors
            if "429" in str(e):
                logger.error("Rate limit exceeded. Free tier: 100 searches/day")
            elif "403" in str(e):
                logger.error("API key invalid or Custom Search API not enabled")
                logger.error(
                    "Enable at: https://console.cloud.google.com/apis/library/customsearch.googleapis.com"
                )

            raise

    def _fallback_search(self, query: str, num_results: int) -> List[Dict]:
        """
        Generate AI-suggested sources when real search is unavailable.

        WARNING: These are AI-generated suggestions, NOT actual web results!

        This is used when:
        - Google Custom Search API is not configured
        - Real search fails or exceeds quota
        - Testing without API keys

        For production use, always configure real Google Custom Search API.

        Args:
            query: Search query
            num_results: Number of sources to generate

        Returns:
            List of AI-generated source suggestions
        """
        logger.warning(f"Using AI-generated fallback sources (not real web search)")

        prompt = f"""
        Generate {num_results} realistic and credible research sources for: "{query}"
        
        Requirements:
        - Use ONLY real, authoritative domains (.edu, .gov, major publications)
        - Create realistic article titles related to the query
        - Write informative snippets (2-3 sentences)
        - Include variety: academic, news, research journals
        
        Examples of good domains:
        - Academic: mit.edu, stanford.edu, harvard.edu
        - Government: .gov sites (NIH, NASA, etc.)
        - Research: nature.com, science.org, arxiv.org
        - News: reuters.com, bbc.com, nytimes.com
        - Technical: ieee.org, acm.org
        
        Return ONLY valid JSON array (no markdown, no extra text):
        [
            {{
                "title": "Article title here",
                "url": "https://realdomain.com/article-path",
                "snippet": "Detailed description of the content and findings.",
                "source": "realdomain.com"
            }}
        ]
        """

        try:
            # Generate AI suggestions
            response = self.model.generate_content(prompt)
            results_text = response.text.strip()

            # Clean up markdown formatting if present
            if results_text.startswith("```"):
                # Remove code block markers
                results_text = results_text.split("```")[1]
                if results_text.startswith("json"):
                    results_text = results_text[4:]
                results_text = results_text.strip()

            # Parse JSON response
            import json

            results = json.loads(results_text)

            logger.info(f"Generated {len(results)} AI-suggested sources")
            logger.warning(
                "These are suggestions - configure real search for production!"
            )

            return results[:num_results]

        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            # Last resort: return basic structure
            return self._generate_basic_sources(query, num_results)

    def _generate_basic_sources(self, query: str, num_results: int) -> List[Dict]:
        """
        Generate minimal source structure as last resort.

        This is only used when both real search and AI fallback fail.

        Args:
            query: Search query
            num_results: Number of sources to generate

        Returns:
            List of basic source structures
        """
        logger.warning("Using basic fallback sources (last resort)")

        # Reputable domains for fallback
        domains = [
            "wikipedia.org",
            "britannica.com",
            "nature.com",
            "science.org",
            "arxiv.org",
            "scholar.google.com",
        ]

        results = []
        for i in range(min(num_results, len(domains))):
            results.append(
                {
                    "title": f"Research on {query} - Source {i+1}",
                    "url": f"https://{domains[i]}/search?q={query.replace(' ', '+')}",
                    "snippet": f"Information and research related to {query}",
                    "source": domains[i],
                }
            )

        return results

    def _extract_domain(self, url: str) -> str:
        """
        Extract clean domain name from URL.

        Args:
            url: Full URL string

        Returns:
            Clean domain name (e.g., 'example.com')
        """
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            domain = parsed.netloc

            # Remove 'www.' prefix for cleaner display
            if domain.startswith("www."):
                domain = domain[4:]

            return domain
        except Exception:
            # Return original URL if parsing fails
            return url

    def refine_query(self, original_query: str, focus_areas: List[str]) -> str:
        """
        Refine search query based on focus areas from coordinator.

        Args:
            original_query: The original user query
            focus_areas: List of focus areas to emphasize

        Returns:
            Refined search query optimized for better results
        """
        if not focus_areas:
            return original_query

        # Combine query with top focus areas for better results
        refined = f"{original_query} {' '.join(focus_areas[:2])}"

        logger.info(f"Refined query: '{original_query}' -> '{refined}'")

        return refined


# Factory function for backward compatibility
def create_agent():
    """Create and return a ResearcherAgent instance."""
    return ResearcherAgent()
