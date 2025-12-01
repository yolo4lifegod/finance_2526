from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, IntegerField, TextAreaField, FileField, FloatField, DateField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, URL
from design_teams import DESIGN_TEAMS

# Helper for file validators - simple check for filename in route; Flask-WTF file validators are limited.

class AuditForm(FlaskForm):
    audit_date = DateField("Audit Date", validators=[DataRequired()])
    auditor_name = StringField("Auditor Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class ReimbursementForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    completed_before = BooleanField("Completed before")
    address = StringField("Address", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional()])
    design_team = SelectField("Design Team", choices=DESIGN_TEAMS, coerce=int, validators=[DataRequired()])
    proof_of_purchase = FileField("Proof of Purchase (pdf/png/jpg)", validators=[DataRequired()])
    proof_of_delivery = FileField("Proof of Delivery (pdf/png/jpg)", validators=[DataRequired()])
    line_item = StringField("Line Item Name", validators=[DataRequired()])
    link = StringField("Product Link", validators=[Optional()])
    amount = FloatField("Amount", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    apf_file = FileField("Associated APF (optional)", validators=[Optional()])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.design_team.choices = DESIGN_TEAMS   

class PurchaseItemForm(FlaskForm):
    item_name = StringField("Item name", validators=[Optional()])
    link = StringField("Link", validators=[DataRequired(), URL(message="Must be a valid URL")])
    unit_price = FloatField("Unit price", validators=[Optional()])
    quantity = IntegerField("Quantity", validators=[Optional()])
    submit = SubmitField("Submit")
    class Meta:
        csrf = False

class PurchaseRequestForm(FlaskForm):
    name = StringField("Requester Name", validators=[DataRequired()])
    design_team = SelectField("Design Team", coerce=int, validators=[DataRequired()])
    num_items = IntegerField("Number of items (1-10)", validators=[DataRequired(), NumberRange(min=1, max=10)])
    # items handled dynamically client-side, but server accepts fieldlist
    items = FieldList(FormField(PurchaseItemForm))
    apf_file = FileField("Associated APF (optional)", validators=[Optional()])
    submit = SubmitField("Submit")

class GrantAddForm(FlaskForm):
    grant_writer = StringField("Grant Writer", validators=[DataRequired()])
    grant_name = StringField("Grant Name", validators=[DataRequired()])
    response_link = StringField("Link to responses", validators=[DataRequired(), URL()])
    submission_deadline = DateField("Submission Deadline", validators=[Optional()])
    submit = SubmitField("Submit")

class GrantCommentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    comment = TextAreaField("Comment", validators=[DataRequired()])

class GrantUpdateForm(FlaskForm):
    update_date = DateField("Date of update", validators=[DataRequired()])
    amount_received = FloatField("Amount received", validators=[DataRequired()])

class ExpenditureForm(FlaskForm):
    design_team = SelectField("Design Team", coerce=int, validators=[DataRequired()])
    requester_name = StringField("Requester Name", validators=[DataRequired()])
    line_item_name = StringField("Line Item Name", validators=[DataRequired()])
    link = StringField("Link", validators=[Optional()])
    unit_price = FloatField("Unit Price", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models import DesignTeam
        self.design_team.choices = [(dt.id, dt.name) for dt in DesignTeam.query.order_by(DesignTeam.name).all()]

class IncomeForm(FlaskForm):
    date_confirmed = DateField("Date of payment", validators=[DataRequired()])
    source = StringField("Grant Name / Company", validators=[DataRequired()])
    amount = FloatField("Amount", validators=[DataRequired()])
    submit = SubmitField("Submit")
