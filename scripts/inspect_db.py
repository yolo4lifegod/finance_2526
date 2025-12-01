import sys, os
# Ensure project root is on sys.path when running this script from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, db
from models import Expenditure, PurchaseRequest

def main():
    app = create_app()
    with app.app_context():
        total = Expenditure.query.count()
        print('Expenditure count:', total)
        recent = Expenditure.query.order_by(Expenditure.id.desc()).limit(20).all()
        for e in recent:
            print(e.id, e.request_type, e.requester_name, repr(e.line_item_name), e.unit_price, e.quantity, 'attached_apf=', e.attached_apf, 'pcard=', e.pcard_form_link, 'submitted=', e.submitted_purchase_request)

        pr_count = PurchaseRequest.query.count()
        print('PurchaseRequest count:', pr_count)
        prs = PurchaseRequest.query.order_by(PurchaseRequest.id.desc()).limit(5).all()
        for p in prs:
            items = [(i.id, i.item_name, i.link, i.unit_price, i.quantity) for i in p.items]
            print('PR', p.id, p.name, 'num_items=', p.num_items, 'apf=', p.apf_file, 'items=', items)

if __name__ == '__main__':
    main()
