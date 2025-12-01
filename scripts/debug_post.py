import requests, re

base = 'http://127.0.0.1:5000'
s = requests.Session()
r = s.get(base + '/purchase-request')
print('GET status', r.status_code)
csrf = None
m = re.search(r"id=[\"']csrf_token[\"'][^>]*value=[\"']([^\"']+)[\"']", r.text)
if m:
    csrf = m.group(1)
    print('CSRF found')
else:
    print('No CSRF')

form = {
    'name': 'DebugTester',
    'design_team': '1',
    'num_items': '1',
    'items-0-link': 'https://example.com/debug',
    'items-0-item_name': 'DebugWidget',
    'items-0-unit_price': '9.99',
    'items-0-quantity': '1',
    'submit': 'Submit'
}
if csrf:
    form['csrf_token'] = csrf

r2 = s.post(base + '/purchase-request', data=form)
print('POST status', r2.status_code)
open('scripts/last_post_response.html','w', encoding='utf-8').write(r2.text)
print('Wrote scripts/last_post_response.html')
