from flask import Blueprint, render_template, redirect, url_for, current_app, request, flash, send_from_directory, send_file, abort
from app import db
from models import *
from forms import *
from werkzeug.utils import secure_filename
import os
from datetime import date, datetime, timedelta
from design_teams import DESIGN_TEAMS

bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config.get("ALLOWED_EXTENSIONS", {"pdf","png","jpg","jpeg"})

# helper to save uploaded file
def save_file(file_storage):
    if file_storage and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(folder, exist_ok=True)
        # add timestamp to avoid collisions
        name = f"{int(datetime.utcnow().timestamp())}_{filename}"
        dest = os.path.join(folder, name)
        file_storage.save(dest)
        return name
    return None

@bp.route("/")
def index():
    # last audit date (max)
    last_audit = AuditLog.query.order_by(AuditLog.audit_date.desc()).first()
    next_due = None
    highlight = None
    if last_audit:
        next_due = last_audit.audit_date + timedelta(days=30)
        days_left = (next_due - date.today()).days
        if days_left < 0:
            highlight = "red"
        elif days_left <= 5:
            highlight = "warning"
    # design teams list
    # teams = DesignTeam.query.order_by(DesignTeam.name).all()
    return render_template("index.html", last_audit=last_audit, next_due=next_due, highlight=highlight, design_teams=DESIGN_TEAMS)

# ---- Audit log ----
@bp.route("/audit-log", methods=["GET", "POST"])
def audit_log():
    form = AuditForm()
    if form.validate_on_submit():
        a = AuditLog(audit_date=form.audit_date.data, auditor_name=form.auditor_name.data)
        db.session.add(a)
        db.session.commit()
        flash("Audit logged", "success")
        return redirect(url_for("main.audit_log"))
    items = AuditLog.query.order_by(AuditLog.audit_date.desc()).all()
    return render_template("audit_log.html", items=items, form=form)

# ---- Reimbursement ----
@bp.route("/reimbursement", methods=["GET", "POST"])
def reimbursement():
    form = ReimbursementForm()
    # Use static design teams list from `design_teams.py` to populate the dropdown
    # (the form's __init__ already defaults to `DESIGN_TEAMS`, but some routes
    # previously overwrote it with DB queries — prefer the static list here).
    form.design_team.choices = DESIGN_TEAMS
    if form.validate_on_submit():
        # if completed_before unchecked, require address & phone
        if not form.completed_before.data:
            if not form.address.data or not form.phone.data:
                flash("Address & phone required for first-time reimbursement", "danger")
                return render_template("reimbursement_form.html", form=form)
        f1 = save_file(request.files.get("proof_of_purchase"))
        f2 = save_file(request.files.get("proof_of_delivery"))
        apf = None
        if request.files.get("apf_file"):
            apf = save_file(request.files.get("apf_file"))
        if not f1 or not f2:
            flash("Invalid file upload (allowed: pdf/png/jpg)", "danger")
            return render_template("reimbursement_form.html", form=form)
        r = ReimbursementRequest(
            name=form.name.data,
            completed_before=form.completed_before.data,
            address=form.address.data,
            phone=form.phone.data,
            design_team_id=form.design_team.data,
            proof_of_purchase=f1,
            proof_of_delivery=f2,
            description=form.description.data,
            apf_file=apf
        )
        db.session.add(r)
        db.session.commit()  # Commit first to get r.id

        # Also create an Expenditure entry for the reimbursement
        e = Expenditure(
            request_type='R',
            design_team_id=form.design_team.data,
            requester_name=form.name.data,
            line_item_name=form.line_item.data,
            unit_price=form.amount.data,
            quantity=1,
            reimbursement_id=r.id
        )
        db.session.add(e)
        db.session.commit()
        flash("Reimbursement submitted", "success")
        return redirect(url_for("main.index"))
    return render_template("reimbursement_form.html", form=form)

# ---- Purchase Request ----
@bp.route("/purchase-request", methods=["GET", "POST"])
def purchase_request():
    form = PurchaseRequestForm()
    # Use the static `DESIGN_TEAMS` list (from `design_teams.py`) for the dropdown.
    # This mirrors `ReimbursementForm` usage and avoids requiring DB seed data.
    form.design_team.choices = DESIGN_TEAMS
    if request.method == "POST" and not form.validate():
        # Log form validation errors for debugging automated submissions
        print("PurchaseRequest form validation failed:", form.errors)

    if request.method == "POST" and form.validate():
        print(f"[PURCHASE] Form validated. Processing {form.num_items.data} items...")
        # Save purchase request
        pr = PurchaseRequest(name=form.name.data, design_team_id=form.design_team.data, num_items=form.num_items.data)
        # process items posted dynamically from form fields named item-0-link, item-0-name ... OR use FieldList
        items = []
        # Try to use FieldList (if submitted as items-0-link etc.), otherwise fallback to parsing request.form
        idx = 0
        while True:
            key_link = f"items-{idx}-link"
            if key_link not in request.form:
                break
            link = request.form.get(key_link)
            item_name = request.form.get(f"items-{idx}-item_name")
            unit_price = request.form.get(f"items-{idx}-unit_price") or 0
            quantity = request.form.get(f"items-{idx}-quantity") or 1
            pi = PurchaseItem(item_name=item_name, link=link, unit_price=float(unit_price), quantity=int(quantity))
            pr.items.append(pi)
            print(f"  Item {idx}: {item_name} - {link}")
            idx += 1
        if request.files.get("apf_file"):
            apf = save_file(request.files.get("apf_file"))
            pr.apf_file = apf
        db.session.add(pr)
        db.session.commit()
        print(f"[PURCHASE] PurchaseRequest {pr.id} saved with {len(pr.items)} items")

        # Create Expenditure entries for each purchase item
        for item in pr.items:
            e = Expenditure(
                request_type='P',
                design_team_id=pr.design_team_id,
                requester_name=pr.name,
                line_item_name=item.item_name or item.link,
                link=item.link,
                unit_price=item.unit_price or 0,
                quantity=item.quantity or 1,
                # APF uploaded with the purchase request should be linked on each expenditure
                attached_apf=pr.apf_file,
                # p-card submission should be toggled by users after submitting the form
                submitted_purchase_request=False
            )
            db.session.add(e)
        db.session.commit()
        print(f"[PURCHASE] Flashing success and redirecting to index")

        flash("Purchase request submitted", "success")
        return redirect(url_for("main.index"))
    return render_template("purchase_request.html", form=form)

# ---- Grants list & add ----
@bp.route("/grants", methods=["GET", "POST"])
def grants():
    form = GrantAddForm()
    if form.validate_on_submit():
        g = GrantApplication(grant_writer=form.grant_writer.data,
                             grant_name=form.grant_name.data,
                             response_link=form.response_link.data,
                             submission_deadline=form.submission_deadline.data)
        db.session.add(g)
        db.session.commit()
        flash("Grant added", "success")
        return redirect(url_for("main.grants"))
    grants = GrantApplication.query.order_by(GrantApplication.submission_deadline.asc().nulls_last()).all()
    return render_template("grants.html", grants=grants, form=form)

@bp.route("/grant/<int:grant_id>", methods=["GET", "POST"])
def grant_detail(grant_id):
    grant = GrantApplication.query.get_or_404(grant_id)
    comment_form = GrantCommentForm()
    update_form = GrantUpdateForm()
    if comment_form.validate_on_submit() and "comment_submit" in request.form:
        c = GrantComment(grant_id=grant.id, name=comment_form.name.data, comment=comment_form.comment.data)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for("main.grant_detail", grant_id=grant.id))
    if update_form.validate_on_submit() and "update_submit" in request.form:
        u = GrantUpdate(grant_id=grant.id, update_date=update_form.update_date.data, amount_received=update_form.amount_received.data)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for("main.grant_detail", grant_id=grant.id))
    return render_template("grant_detail.html", grant=grant, comment_form=comment_form, update_form=update_form)

# ---- Expenditures & Income ----
@bp.route("/expenditures", methods=["GET", "POST"])
def expenditures():
    exp_form = ExpenditureForm()
    exp_form.design_team.choices = [(t.id, t.name) for t in DesignTeam.query.order_by(DesignTeam.name)]
    income_form = IncomeForm()
    if exp_form.validate_on_submit() and "exp_submit" in request.form:
        e = Expenditure(
            request_type='P',
            design_team_id=exp_form.design_team.data,
            requester_name=exp_form.requester_name.data,
            line_item_name=exp_form.line_item_name.data,
            link=exp_form.link.data,
            unit_price=exp_form.unit_price.data,
            quantity=exp_form.quantity.data
        )
        db.session.add(e)
        db.session.commit()
        flash("Expenditure added", "success")
        return redirect(url_for("main.expenditures"))
    if income_form.validate_on_submit() and "inc_submit" in request.form:
        i = Income(date_of_payment=income_form.date_of_payment.data, source_name=income_form.source_name.data, amount=income_form.amount.data)
        db.session.add(i)
        db.session.commit()
        flash("Income added", "success")
        return redirect(url_for("main.expenditures"))

    expenditures_query = Expenditure.query
    incomes_query = Income.query
    
    # Handle team filter from query parameter
    selected_team = request.args.get('team', '', type=str)
    if selected_team and selected_team != '':
        try:
            team_id = int(selected_team)
            expenditures_query = expenditures_query.filter_by(design_team_id=team_id)
        except (ValueError, TypeError):
            pass
    
    expenditures = expenditures_query.order_by(Expenditure.request_submission_date.desc()).all()
    incomes = incomes_query.order_by(Income.date_of_payment.desc()).all()

    # totals
    total_expenditures = sum((e.total_cost or 0) for e in expenditures)
    total_confirmed_expenditures = sum((e.total_cost or 0) for e in expenditures if e.completed)
    total_income = sum((i.amount or 0) for i in incomes)
    total_confirmed_income = sum((i.amount or 0) for i in incomes if i.payment_received)

    unofficial = total_income - total_expenditures
    official = total_confirmed_income - total_confirmed_expenditures
    worst = total_income - total_expenditures  # assuming worst case is all expenditures confirmed, no income confirmed? Wait, probably worst is all expenditures, no income
    worst = -total_expenditures

    totals = {
        'total_exp': total_expenditures,
        'total_exp_confirmed': total_confirmed_expenditures,
        'total_inc': total_income,
        'total_inc_confirmed': total_confirmed_income,
        'unofficial': unofficial,
        'official': official,
        'worst': worst
    }

    return render_template("expenditures.html", expenditures=expenditures, incomes=incomes, exp_form=exp_form,
                           income_form=income_form, totals=totals, design_teams=DESIGN_TEAMS, selected_team=selected_team)

# Toggle checkboxes via AJAX
@bp.route("/expenditure/<int:id>/toggle_completed", methods=["POST"])
def toggle_completed(id):
    e = Expenditure.query.get_or_404(id)
    e.completed = not e.completed
    db.session.commit()
    return '', 204  # No content response for AJAX


@bp.route("/expenditure/<int:id>/toggle_submitted_pcard", methods=["GET", "POST"])
def toggle_submitted_pcard(id):
    e = Expenditure.query.get_or_404(id)
    e.submitted_purchase_request = not e.submitted_purchase_request
    db.session.commit()
    # allow both AJAX (POST) and simple link (GET) usage
    if request.method == 'POST':
        return '', 204
    return redirect(url_for("main.expenditures"))

@bp.route("/income/<int:id>/toggle_received")
def toggle_received(id):
    i = Income.query.get_or_404(id)
    i.payment_received = not i.payment_received
    db.session.commit()
    return redirect(url_for("main.expenditures"))

# Design team / pillar page
@bp.route("/team/<int:team_id>")
def team_page(team_id):
    team = DesignTeam.query.get_or_404(team_id)
    expenditures = Expenditure.query.filter_by(design_team_id=team.id).all()
    total_expenditures = sum(e.total_cost for e in expenditures)
    total_confirmed = sum(e.total_cost for e in expenditures if e.completed)
    return render_template("design_team.html", team=team, expenditures=expenditures,
                           total_expenditures=total_expenditures, total_confirmed=total_confirmed)

# Serve uploaded files
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/download_reimbursement_files/<int:reimbursement_id>')
def download_reimbursement_files(reimbursement_id):
    r = ReimbursementRequest.query.get_or_404(reimbursement_id)
    import zipfile
    import io
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        if r.proof_of_purchase:
            zf.write(os.path.join(current_app.config['UPLOAD_FOLDER'], r.proof_of_purchase), arcname='proof_of_purchase.pdf')
        if r.proof_of_delivery:
            zf.write(os.path.join(current_app.config['UPLOAD_FOLDER'], r.proof_of_delivery), arcname='proof_of_delivery.pdf')
    memory_file.seek(0)
    return send_file(memory_file, download_name='reimbursement_files.zip', as_attachment=True)


# Upload P-card form for a specific expenditure (purchase requests only)
@bp.route('/expenditure/<int:id>/upload_pcard', methods=['GET', 'POST'])
def upload_pcard(id):
    e = Expenditure.query.get_or_404(id)
    # Only allow for purchase request expenditures
    if e.request_type != 'P':
        abort(400)
    if request.method == 'POST':
        f = request.files.get('pcard_file')
        if f:
            filename = save_file(f)
            if filename:
                e.pcard_form_link = filename
                e.submitted_purchase_request = True
                db.session.commit()
                flash('P-Card form uploaded', 'success')
                return redirect(url_for('main.expenditures'))
        flash('Invalid file upload', 'danger')
    return render_template('pcard_upload.html', expenditure=e)

@bp.route("/design_team/<int:team_id>")
def design_team_detail(team_id):
    # find matching team
    team = next((t for t in DESIGN_TEAMS if t[0] == team_id), None)
    if team is None:
        abort(404)

    # get expenditures for this team
    expenditures = Expenditure.query.filter_by(design_team_id=team_id).all()

    return render_template(
        "design_team.html",
        team_name=team[1],
        expenditures=expenditures
    )