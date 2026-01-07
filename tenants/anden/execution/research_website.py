#!/usr/bin/env python3
"""
Research a business website to extract key information for personalized outreach.
Scrapes homepage, about page, and contact page to build a profile.
"""
import sys
import json
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from pathlib import Path

def load_env():
    """Load .env file from current directory."""
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, _, value = line.partition('=')
                    os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def fetch_page(url: str, timeout: int = 15) -> str:
    """Fetch a webpage and return its text content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return ""


def extract_text(html: str) -> str:
    """Extract readable text from HTML, removing scripts/styles."""
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text[:10000]  # Limit to 10k chars


def extract_emails(html: str) -> list:
    """Extract email addresses from HTML."""
    # Match common email patterns
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(pattern, html)

    # Filter out common fake/placeholder emails
    filtered = []
    for email in emails:
        email_lower = email.lower()
        if not any(x in email_lower for x in ['example.com', 'domain.com', 'email.com', 'yoursite', 'yourdomain']):
            filtered.append(email)

    return list(set(filtered))


def extract_phones(html: str) -> list:
    """Extract phone numbers from HTML."""
    # Match US phone formats
    patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
    ]

    phones = []
    for pattern in patterns:
        matches = re.findall(pattern, html)
        phones.extend(matches)

    return list(set(phones))


def extract_social_links(html: str) -> dict:
    """Extract social media links."""
    social = {}

    patterns = {
        "linkedin": r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[a-zA-Z0-9_-]+',
        "facebook": r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9._-]+',
        "instagram": r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9._-]+',
        "twitter": r'https?://(?:www\.)?(?:twitter|x)\.com/[a-zA-Z0-9_]+',
    }

    for platform, pattern in patterns.items():
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            social[platform] = match.group(0)

    return social


def find_about_page(html: str, base_url: str) -> str:
    """Find the about page URL from navigation links."""
    patterns = [
        r'href=["\']([^"\']*(?:about|team|who-we-are|our-story)[^"\']*)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return urljoin(base_url, match.group(1))

    return ""


def find_contact_page(html: str, base_url: str) -> str:
    """Find the contact page URL from navigation links."""
    patterns = [
        r'href=["\']([^"\']*(?:contact|get-in-touch|reach-us)[^"\']*)["\']',
    ]

    for pattern in patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return urljoin(base_url, match.group(1))

    return ""


def extract_services(text: str) -> list:
    """Try to extract services mentioned on the page."""
    services = []

    # Common service-related keywords
    service_patterns = [
        r'(?:we offer|our services|services include|specializing in|we provide)[:\s]+([^.]+)',
        r'(?:residential|commercial|property|real estate|insurance|consulting)[^.]{0,50}(?:services|solutions)',
    ]

    for pattern in service_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) < 200:  # Reasonable length
                services.append(match.strip())

    return services[:5]  # Limit to 5


def research_website(url: str) -> dict:
    """
    Research a business website and extract key information.

    Args:
        url: Website URL to research

    Returns:
        Dictionary with extracted business information
    """
    # Ensure URL has scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    result = {
        "url": url,
        "domain": parsed.netloc,
        "emails": [],
        "phones": [],
        "social": {},
        "about_summary": "",
        "services": [],
        "pages_checked": []
    }

    # Fetch homepage
    homepage_html = fetch_page(url)
    if not homepage_html:
        return {"error": f"Could not fetch {url}"}

    result["pages_checked"].append(url)
    homepage_text = extract_text(homepage_html)

    # Extract from homepage
    result["emails"].extend(extract_emails(homepage_html))
    result["phones"].extend(extract_phones(homepage_html))
    result["social"].update(extract_social_links(homepage_html))
    result["services"].extend(extract_services(homepage_text))

    # Try about page
    about_url = find_about_page(homepage_html, base_url)
    if about_url and about_url != url:
        about_html = fetch_page(about_url)
        if about_html:
            result["pages_checked"].append(about_url)
            about_text = extract_text(about_html)
            result["about_summary"] = about_text[:500]  # First 500 chars
            result["emails"].extend(extract_emails(about_html))
            result["phones"].extend(extract_phones(about_html))

    # Try contact page
    contact_url = find_contact_page(homepage_html, base_url)
    if contact_url and contact_url != url and contact_url != about_url:
        contact_html = fetch_page(contact_url)
        if contact_html:
            result["pages_checked"].append(contact_url)
            result["emails"].extend(extract_emails(contact_html))
            result["phones"].extend(extract_phones(contact_html))

    # Deduplicate
    result["emails"] = list(set(result["emails"]))
    result["phones"] = list(set(result["phones"]))
    result["services"] = list(set(result["services"]))

    # Generate summary
    result["summary"] = f"Website for {parsed.netloc}. "
    if result["emails"]:
        result["summary"] += f"Contact: {result['emails'][0]}. "
    if result["phones"]:
        result["summary"] += f"Phone: {result['phones'][0]}. "
    if result["services"]:
        result["summary"] += f"Services mentioned: {', '.join(result['services'][:3])}."

    return result


def main():
    load_env()

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    url = input_data.get("url")
    if not url:
        print(json.dumps({"error": "url parameter is required"}))
        return

    result = research_website(url)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
