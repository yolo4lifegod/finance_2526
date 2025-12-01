import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import db
from models import Expenditure, PurchaseRequest, PurchaseItem, ReimbursementRequest, Income, DesignTeam
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        # Create all tables first
        print("Creating tables...")
        db.create_all()
        
        # Seed DesignTeam if needed
        from design_teams import DESIGN_TEAMS
        if DesignTeam.query.count() == 0:
            print("Seeding DesignTeam table...")
            for team_id, team_name in DESIGN_TEAMS:
                dt = DesignTeam(id=team_id, name=team_name)
                db.session.add(dt)
            db.session.commit()
        
        # Now clear all submission data
        print("\nClearing submissions...")
        print("  - Expenditure table...")
        Expenditure.query.delete()
        
        print("  - PurchaseItem table...")
        PurchaseItem.query.delete()
        
        print("  - PurchaseRequest table...")
        PurchaseRequest.query.delete()
        
        print("  - ReimbursementRequest table...")
        ReimbursementRequest.query.delete()
        
        print("  - Income table...")
        Income.query.delete()
        
        db.session.commit()
        print("\n✅ All previous submissions cleared!")
        print("✅ DesignTeam table seeded!")
        print("✅ Database is now clean and ready for deployment.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
