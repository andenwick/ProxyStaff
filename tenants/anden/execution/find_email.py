#!/usr/bin/env python3
"""
Find email address for a person using pattern matching and verification.
Generates common email patterns and optionally verifies via SMTP.
"""
import sys
import json
import os
import re
import socket
import smtplib
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


def normalize_name(name: str) -> dict:
    """Parse and normalize a person's name."""
    # Remove common suffixes/prefixes
    name = re.sub(r'\b(Mr|Mrs|Ms|Dr|Jr|Sr|III|II|IV)\.?\b', '', name, flags=re.IGNORECASE)
    name = name.strip()

    parts = name.split()
    if len(parts) == 0:
        return {"first": "", "last": "", "middle": ""}
    elif len(parts) == 1:
        return {"first": parts[0].lower(), "last": "", "middle": ""}
    elif len(parts) == 2:
        return {"first": parts[0].lower(), "last": parts[1].lower(), "middle": ""}
    else:
        return {
            "first": parts[0].lower(),
            "middle": parts[1].lower() if len(parts) > 2 else "",
            "last": parts[-1].lower()
        }


def generate_email_patterns(name: dict, domain: str) -> list:
    """
    Generate common email address patterns.
    Returns list of (pattern_name, email) tuples ordered by likelihood.
    """
    first = name["first"]
    last = name["last"]
    middle = name.get("middle", "")

    if not first or not last or not domain:
        return []

    first_initial = first[0] if first else ""
    last_initial = last[0] if last else ""
    middle_initial = middle[0] if middle else ""

    patterns = []

    # Most common patterns (ordered by popularity)
    patterns.append(("first.last", f"{first}.{last}@{domain}"))
    patterns.append(("firstlast", f"{first}{last}@{domain}"))
    patterns.append(("first", f"{first}@{domain}"))
    patterns.append(("flast", f"{first_initial}{last}@{domain}"))
    patterns.append(("firstl", f"{first}{last_initial}@{domain}"))
    patterns.append(("first_last", f"{first}_{last}@{domain}"))
    patterns.append(("last.first", f"{last}.{first}@{domain}"))
    patterns.append(("lastf", f"{last}{first_initial}@{domain}"))
    patterns.append(("last", f"{last}@{domain}"))

    # With middle initial
    if middle_initial:
        patterns.append(("first.m.last", f"{first}.{middle_initial}.{last}@{domain}"))
        patterns.append(("fmlast", f"{first_initial}{middle_initial}{last}@{domain}"))

    return patterns


def verify_email_smtp(email: str, timeout: int = 10) -> dict:
    """
    Verify email exists using SMTP RCPT TO check.
    Note: Many servers don't support this or will always say yes.

    Returns: {"valid": bool, "method": str, "note": str}
    """
    domain = email.split('@')[1]

    try:
        # Get MX record
        import dns.resolver
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_host = str(sorted(mx_records, key=lambda x: x.preference)[0].exchange).rstrip('.')
    except:
        # If no dnspython, try direct connection
        mx_host = domain

    try:
        # Connect to mail server
        smtp = smtplib.SMTP(timeout=timeout)
        smtp.connect(mx_host, 25)
        smtp.helo('verify.local')
        smtp.mail('verify@verify.local')
        code, message = smtp.rcpt(email)
        smtp.quit()

        if code == 250:
            return {"valid": True, "method": "smtp", "note": "Server accepted recipient"}
        elif code == 550:
            return {"valid": False, "method": "smtp", "note": "Mailbox does not exist"}
        else:
            return {"valid": None, "method": "smtp", "note": f"Uncertain: {code} {message}"}
    except Exception as e:
        return {"valid": None, "method": "smtp_failed", "note": str(e)}


def check_domain_mx(domain: str) -> bool:
    """Check if domain has MX records (can receive email)."""
    try:
        socket.setdefaulttimeout(5)
        # Try to resolve MX
        import dns.resolver
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        # Fallback: check if domain resolves at all
        try:
            socket.gethostbyname(domain)
            return True
        except:
            return False


def find_email(name: str, company: str = None, domain: str = None, verify: bool = False) -> dict:
    """
    Find the most likely email address for a person.

    Args:
        name: Person's full name
        company: Company name (used to guess domain if not provided)
        domain: Email domain (e.g., "acme.com")
        verify: Whether to attempt SMTP verification

    Returns:
        Dictionary with email candidates and confidence scores
    """
    # Parse name
    parsed_name = normalize_name(name)
    if not parsed_name["first"]:
        return {"error": "Could not parse name"}

    # Determine domain
    if not domain and company:
        # Simple heuristic: lowercase company, remove spaces/common suffixes
        company_clean = company.lower()
        company_clean = re.sub(r'\b(inc|llc|ltd|corp|co|company|group|agency)\b', '', company_clean)
        company_clean = re.sub(r'[^a-z0-9]', '', company_clean)
        domain = f"{company_clean}.com"

    if not domain:
        return {"error": "Could not determine email domain. Provide domain or company."}

    # Check domain validity
    if not check_domain_mx(domain):
        return {
            "warning": f"Domain {domain} may not receive email",
            "domain": domain,
            "candidates": []
        }

    # Generate patterns
    patterns = generate_email_patterns(parsed_name, domain)

    candidates = []
    for pattern_name, email in patterns:
        candidate = {
            "email": email,
            "pattern": pattern_name,
            "confidence": get_pattern_confidence(pattern_name)
        }

        # Optionally verify
        if verify:
            verification = verify_email_smtp(email)
            candidate["verification"] = verification
            if verification.get("valid") == True:
                candidate["confidence"] = 0.95
            elif verification.get("valid") == False:
                candidate["confidence"] = 0.05

        candidates.append(candidate)

    # Sort by confidence
    candidates.sort(key=lambda x: x["confidence"], reverse=True)

    return {
        "name": name,
        "parsed_name": parsed_name,
        "domain": domain,
        "best_guess": candidates[0]["email"] if candidates else None,
        "candidates": candidates[:5]  # Top 5
    }


def get_pattern_confidence(pattern: str) -> float:
    """Return confidence score for a pattern based on common usage."""
    scores = {
        "first.last": 0.85,
        "firstlast": 0.75,
        "first": 0.60,
        "flast": 0.55,
        "firstl": 0.50,
        "first_last": 0.45,
        "last.first": 0.40,
        "lastf": 0.35,
        "last": 0.30,
        "first.m.last": 0.45,
        "fmlast": 0.35,
    }
    return scores.get(pattern, 0.25)


def main():
    load_env()

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    name = input_data.get("name")
    if not name:
        print(json.dumps({"error": "name parameter is required"}))
        return

    company = input_data.get("company")
    domain = input_data.get("domain")
    verify = input_data.get("verify", False)

    result = find_email(name, company, domain, verify)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
