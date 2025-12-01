from app import db
from datetime import datetime

# Simple lookup table for design teams / pillars
class DesignTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    audit_date = db.Column(db.Date, nullable=False)
    auditor_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReimbursementRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    completed_before = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(250))
    phone = db.Column(db.String(50))
    design_team_id = db.Column(db.Integer, db.ForeignKey('design_team.id'), nullable=False)
    design_team = db.relationship('DesignTeam')
    proof_of_purchase = db.Column(db.String(250), nullable=False)
    proof_of_delivery = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)
    apf_file = db.Column(db.String(250))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    design_team_id = db.Column(db.Integer, db.ForeignKey('design_team.id'), nullable=False)
    design_team = db.relationship('DesignTeam')
    num_items = db.Column(db.Integer, nullable=False)
    apf_file = db.Column(db.String(250))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('PurchaseItem', backref='purchase', cascade='all, delete-orphan')

class PurchaseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase_request.id'), nullable=False)
    item_name = db.Column(db.String(250))
    link = db.Column(db.String(500), nullable=False)
    unit_price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=1)

class GrantApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grant_name = db.Column(db.String(250), nullable=False)
    grant_writer = db.Column(db.String(120), nullable=False)
    response_link = db.Column(db.String(500), nullable=False)
    submission_deadline = db.Column(db.Date)
    submitted = db.Column(db.Boolean, default=False)
    amount_received = db.Column(db.Float)
    date_received = db.Column(db.Date)
    approver_bod = db.Column(db.Boolean, default=False)
    approver_finance = db.Column(db.Boolean, default=False)
    approver_president = db.Column(db.Boolean, default=False)
    comments = db.relationship('GrantComment', backref='grant', cascade='all, delete-orphan')
    updates = db.relationship('GrantUpdate', backref='grant', cascade='all, delete-orphan')

class GrantComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grant_id = db.Column(db.Integer, db.ForeignKey('grant_application.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GrantUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grant_id = db.Column(db.Integer, db.ForeignKey('grant_application.id'), nullable=False)
    update_date = db.Column(db.Date, nullable=False)
    amount_received = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expenditure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_submission_date = db.Column(db.Date, default=datetime.utcnow)
    request_type = db.Column(db.String(2), default='P')
    design_team_id = db.Column(db.Integer, db.ForeignKey('design_team.id'), nullable=False)
    design_team = db.relationship('DesignTeam')
    requester_name = db.Column(db.String(120), nullable=False)
    line_item_name = db.Column(db.String(250), nullable=False)
    link = db.Column(db.String(500))
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    attached_apf = db.Column(db.String(250))
    submitted_purchase_request = db.Column(db.Boolean, default=False)
    pcard_form_link = db.Column(db.String(250))
    completed = db.Column(db.Boolean, default=False)
    reimbursement_id = db.Column(db.Integer, db.ForeignKey('reimbursement_request.id'))

    @property
    def total_cost(self):
        result = (self.unit_price or 0.0) * (self.quantity or 0)
        return round(result, 2)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_of_payment = db.Column(db.Date, nullable=False)
    source_name = db.Column(db.String(250), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_received = db.Column(db.Boolean, default=False)
