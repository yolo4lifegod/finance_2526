import requests, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import db, create_app
from models import PurchaseRequest, Expenditure

base = 'http://127.0.0.1:5000'
s = requests.Session()

# Get the form and extract CSRF token
r = s.get(base + '/purchase-request')
print('GET status', r.status_code)
csrf = None
m = re.search(r"id=[\"']csrf_token[\"'][^>]*value=[\"']([^\"']+)[\"']", r.text)
if m:
    csrf = m.group(1)
    print('CSRF found')
else:
    print('No CSRF found')
    sys.exit(1)

# Submit a purchase request with 2 items
form = {
    'name': 'MultiItemTester',
    'design_team': '1',
    'num_items': '2',
    'items-0-link': 'https://example.com/item1',
    'items-0-item_name': 'Item One',
    'items-0-unit_price': '10.50',
    'items-0-quantity': '2',
    'items-1-link': 'https://example.com/item2',
    'items-1-item_name': 'Item Two',
    'items-1-unit_price': '20.00',
    'items-1-quantity': '3',
    'csrf_token': csrf
}

r2 = s.post(base + '/purchase-request', data=form)
print(f'POST status {r2.status_code}')

# Check the database to verify items were saved
app = create_app()
with app.app_context():
    # Get the most recent PurchaseRequest
    pr = PurchaseRequest.query.order_by(PurchaseRequest.id.desc()).first()
    if pr:
        print(f'\nPurchaseRequest saved: PR {pr.id} ({pr.name})')
        print(f'  Items in DB: {len(pr.items)}')
        for item in pr.items:
            print(f'    - {item.item_name} ({item.link}): ${item.unit_price} x {item.quantity}')
        
        # Check Expenditures created from this purchase
        exps = Expenditure.query.filter_by(request_type='P').order_by(Expenditure.id.desc()).limit(2).all()
        print(f'\nExpenditure rows created: {len(exps)}')
        for exp in exps:
            print(f'  - {exp.line_item_name}: ${exp.unit_price} x {exp.quantity} = ${exp.total_cost}')
    else:
        print('No PurchaseRequest found in DB!')
