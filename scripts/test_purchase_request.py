#!/usr/bin/env python3
"""Simple smoke test: submit a Purchase Request and verify it appears in Expenditures.

Usage:
  python scripts/test_purchase_request.py --base-url http://127.0.0.1:5000

This script fetches the purchase form page to obtain the CSRF token (if present),
submits a single-item purchase request, then checks the expenditures page for the
submitted item. It uses only the `requests` library so it should work on deployed
servers accessible over HTTP(S).
"""
import requests
import re
import sys
import argparse


def extract_csrf(html: str):
    # Look for hidden input csrf_token value
    m = re.search(r'name=["\']csrf_token["\']\s+type=["\']hidden["\'][^>]*value=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    m = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    # Try Flask-WTF style: <input id="csrf_token" name="csrf_token" type="hidden" value="...">
    m = re.search(r'id=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', html)
    if m:
        return m.group(1)
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', default='http://127.0.0.1:5000', help='Base URL of running app')
    args = p.parse_args()

    s = requests.Session()
    base = args.base_url.rstrip('/')

    print(f"Fetching purchase form from {base}/purchase-request")
    r = s.get(f"{base}/purchase-request")
    if r.status_code != 200:
        print("FAILED: could not fetch purchase form, status", r.status_code)
        sys.exit(2)

    csrf = extract_csrf(r.text)
    if csrf:
        print("Found CSRF token in form")
    else:
        print("No CSRF token found; proceeding without one")

    form = {
        'name': 'AutoTester',
        'design_team': '1',
        'num_items': '1',
        'items-0-link': 'https://example.com/testitem',
        'items-0-item_name': 'AutoWidget',
        'items-0-unit_price': '12.34',
        'items-0-quantity': '1',
        'submit': 'Submit'
    }
    if csrf:
        form['csrf_token'] = csrf

    print('Submitting purchase request...')
    r2 = s.post(f"{base}/purchase-request", data=form, allow_redirects=True)
    if r2.status_code not in (200, 302):
        print('FAILED: POST returned', r2.status_code)
        sys.exit(3)

    print('Fetching expenditures page to verify item presence...')
    r3 = s.get(f"{base}/expenditures")
    if r3.status_code != 200:
        print('FAILED: could not fetch expenditures, status', r3.status_code)
        sys.exit(4)

    if 'AutoWidget' in r3.text or 'example.com/testitem' in r3.text:
        print('SUCCESS: purchase item found in expenditures page')
        sys.exit(0)
    else:
        print('FAILURE: purchase item NOT found in expenditures page')
        # For debugging, dump a short snippet
        snippet = r3.text[:2000]
        print('Page snippet:\n', snippet)
        sys.exit(5)


if __name__ == '__main__':
    main()
