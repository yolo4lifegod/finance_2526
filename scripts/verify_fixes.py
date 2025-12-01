import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from models import DesignTeam, Expenditure

app = create_app()
with app.app_context():
    print("=== DesignTeam table ===")
    teams = DesignTeam.query.all()
    print(f"Total teams in DB: {len(teams)}")
    for team in teams:
        print(f"  ID {team.id}: {team.name}")
    
    print("\n=== Expenditures (last 3) ===")
    exps = Expenditure.query.order_by(Expenditure.id.desc()).limit(3).all()
    for exp in exps:
        print(f"  ID {exp.id}: {exp.line_item_name}")
        print(f"    Design Team: {exp.design_team.name if exp.design_team else 'None'}")
        print(f"    Total: ${exp.total_cost} (unit_price: {exp.unit_price}, qty: {exp.quantity})")
