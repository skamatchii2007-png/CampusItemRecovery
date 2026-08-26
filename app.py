
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "campus-recovery-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campus_recovery.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER
# =========================================================

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


# =========================================================
# LOST ITEM
# =========================================================

class LostItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    item_name = db.Column(
        db.String(100),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    lost_location = db.Column(
        db.String(200),
        nullable=False
    )

    lost_date = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(40),
        default="Lost"
    )


# =========================================================
# FOUND ITEM
# =========================================================

class FoundItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    item_name = db.Column(
        db.String(100),
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    found_location = db.Column(
        db.String(200),
        nullable=False
    )

    found_date = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(40),
        default="Submitted to Admin"
    )


# =========================================================
# CLAIM REQUEST
# =========================================================

class ClaimRequest(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    found_item_id = db.Column(
        db.Integer,
        db.ForeignKey("found_item.id"),
        nullable=False
    )

    claim_reason = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    admin_message = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# NOTIFICATION
# =========================================================

class Notification(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        role="admin"
    ).first()

    if admin is None:

        admin = User(
            name="System Administrator",
            email="admin001",
            password=generate_password_hash(
                "Admin@123"
            ),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

    else:

        admin.email = "admin001"

        admin.password = generate_password_hash(
            "Admin@123"
        )

        admin.name = "System Administrator"

        db.session.commit()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# LOGIN CHOICE
# =========================================================

@app.route("/login")
def login_choice():

    return render_template(
        "login_choice.html"
    )


# =========================================================
# USER LOGIN
# =========================================================

@app.route(
    "/user-login",
    methods=["GET", "POST"]
)
def user_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and user.role in [
            "student",
            "staff"
        ] and user.active:

            if check_password_hash(
                user.password,
                password
            ):

                session["user_id"] = user.id
                session["user_name"] = user.name
                session["role"] = user.role

                return redirect(
                    url_for("dashboard")
                )

        flash(
            "Invalid email or password."
        )

    return render_template(
        "user_login.html"
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        user_id = request.form.get(
            "user_id",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        admin = User.query.filter_by(
            email=user_id,
            role="admin"
        ).first()

        if admin:

            if check_password_hash(
                admin.password,
                password
            ):

                session["user_id"] = admin.id
                session["user_name"] = admin.name
                session["role"] = "admin"

                return redirect(
                    url_for("admin_dashboard")
                )

        flash(
            "Invalid Admin ID or Password."
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        )

        if role not in [
            "student",
            "staff"
        ]:

            flash(
                "Please select Student or Staff."
            )

            return redirect(
                url_for("register")
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered."
            )

            return redirect(
                url_for("register")
            )

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(
                password
            ),
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful! Please login."
        )

        return redirect(
            url_for("login_choice")
        )

    return render_template(
        "register.html"
    )


# =========================================================
# USER DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] == "admin":

        return redirect(
            url_for("admin_dashboard")
        )

    unread_notifications = Notification.query.filter_by(
        user_id=session["user_id"],
        is_read=False
    ).count()

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        role=session["role"],
        unread_notifications=unread_notifications
    )


# =========================================================
# REPORT LOST ITEM
# =========================================================

@app.route(
    "/report-lost",
    methods=["GET", "POST"]
)
def report_lost():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] not in [
        "student",
        "staff"
    ]:

        flash(
            "Only students and staff can report lost items."
        )

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        item = LostItem(
            user_id=session["user_id"],
            item_name=request.form["item_name"],
            category=request.form["category"],
            description=request.form["description"],
            lost_location=request.form["lost_location"],
            lost_date=request.form["lost_date"],
            status="Lost"
        )

        db.session.add(item)
        db.session.commit()

        flash(
            "Lost item reported successfully!"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "report_lost.html"
    )


# =========================================================
# REPORT FOUND ITEM
# =========================================================

@app.route(
    "/report-found",
    methods=["GET", "POST"]
)
def report_found():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] not in [
        "student",
        "staff"
    ]:

        flash(
            "Only students and staff can report found items."
        )

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        item = FoundItem(
            user_id=session["user_id"],
            item_name=request.form["item_name"],
            category=request.form["category"],
            description=request.form["description"],
            found_location=request.form["found_location"],
            found_date=request.form["found_date"],
            status="Submitted to Admin"
        )

        db.session.add(item)
        db.session.commit()

        flash(
            "Found item reported successfully! "
            "It is now visible in the Found Items search portal. "
            "Please submit the physical item to the Admin Office."
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "report_found.html"
    )


# =========================================================
# SEARCH & MATCH LOST ITEMS
# =========================================================

def calculate_match_score(lost_item, found_item):

    score = 0

    lost_name = (lost_item.item_name or "").lower().strip()
    found_name = (found_item.item_name or "").lower().strip()

    lost_category = (lost_item.category or "").lower().strip()
    found_category = (found_item.category or "").lower().strip()

    lost_location = (lost_item.lost_location or "").lower().strip()
    found_location = (found_item.found_location or "").lower().strip()

    lost_date = (lost_item.lost_date or "").strip()
    found_date = (found_item.found_date or "").strip()

    lost_description = (
        lost_item.description or ""
    ).lower()

    found_description = (
        found_item.description or ""
    ).lower()

    if (
        lost_category
        and found_category
        and lost_category == found_category
    ):
        score += 30

    if lost_name and found_name:

        if lost_name == found_name:
            score += 30

        else:

            lost_words = set(lost_name.split())
            found_words = set(found_name.split())

            if lost_words.intersection(found_words):
                score += 20

    if lost_location and found_location:

        if lost_location == found_location:
            score += 20

        elif (
            lost_location in found_location
            or found_location in lost_location
        ):
            score += 10

    if (
        lost_date
        and found_date
        and lost_date == found_date
    ):
        score += 10

    lost_words = set(
        word.strip(".,!?;:()[]{}")
        for word in lost_description.split()
        if len(word.strip(".,!?;:()[]{}")) >= 3
    )

    found_words = set(
        word.strip(".,!?;:()[]{}")
        for word in found_description.split()
        if len(word.strip(".,!?;:()[]{}")) >= 3
    )

    if lost_words and found_words:

        common_words = lost_words.intersection(
            found_words
        )

        if common_words:
            score += 10

    return score


@app.route("/matches")
def matches():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] not in [
        "student",
        "staff"
    ]:

        return redirect(
            url_for("dashboard")
        )

    lost_items = LostItem.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        LostItem.id.desc()
    ).all()

    found_items = FoundItem.query.filter(
        FoundItem.status.in_([
            "Submitted to Admin",
            "Received by Admin"
        ])
    ).order_by(
        FoundItem.id.desc()
    ).all()

    match_results = []

    for lost_item in lost_items:

        possible_matches = []

        for found_item in found_items:

            score = calculate_match_score(
                lost_item,
                found_item
            )

            if score >= 30:

                possible_matches.append(
                    {
                        "item": found_item,
                        "score": score
                    }
                )

        possible_matches.sort(
            key=lambda result: result["score"],
            reverse=True
        )

        match_results.append(
            {
                "lost_item": lost_item,
                "matches": possible_matches
            }
        )

    return render_template(
        "matches.html",
        match_results=match_results
    )


# =========================================================
# FOUND ITEMS
# =========================================================

@app.route("/found-items")
def found_items():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] not in [
        "student",
        "staff"
    ]:

        return redirect(
            url_for("dashboard")
        )

    search = request.args.get(
        "search",
        ""
    ).strip()

    category = request.args.get(
        "category",
        ""
    ).strip()

    query = FoundItem.query.filter(
        FoundItem.status.in_([
            "Submitted to Admin",
            "Received by Admin"
        ])
    )

    if search:

        search_text = "%" + search + "%"

        query = query.filter(
            db.or_(
                FoundItem.item_name.ilike(
                    search_text
                ),
                FoundItem.description.ilike(
                    search_text
                ),
                FoundItem.found_location.ilike(
                    search_text
                )
            )
        )

    if category:

        query = query.filter_by(
            category=category
        )

    items = query.order_by(
        FoundItem.id.desc()
    ).all()

    return render_template(
        "found_items.html",
        items=items,
        search=search,
        category=category
    )


# =========================================================
# CLAIM ITEM
# =========================================================

@app.route(
    "/claim-item/<int:item_id>",
    methods=["GET", "POST"]
)
def claim_item(item_id):

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] not in [
        "student",
        "staff"
    ]:

        return redirect(
            url_for("dashboard")
        )

    item = db.session.get(
        FoundItem,
        item_id
    )

    if item is None:

        flash(
            "Found item not found."
        )

        return redirect(
            url_for("found_items")
        )

    if item.status not in [
        "Submitted to Admin",
        "Received by Admin"
    ]:

        flash(
            "This found item is not available for claiming."
        )

        return redirect(
            url_for("matches")
        )

    existing_request = ClaimRequest.query.filter_by(
        user_id=session["user_id"],
        found_item_id=item.id
    ).first()

    if existing_request:

        flash(
            "You have already submitted a claim request for this item."
        )

        return redirect(
            url_for("my_claims")
        )

    approved_claim = ClaimRequest.query.filter_by(
        found_item_id=item.id,
        status="Approved"
    ).first()

    if approved_claim:

        flash(
            "This item has already been claimed and recovered."
        )

        return redirect(
            url_for("matches")
        )

    if request.method == "POST":

        claim_reason = request.form.get(
            "claim_reason",
            ""
        ).strip()

        if not claim_reason:

            flash(
                "Please provide details to prove that this item belongs to you."
            )

            return redirect(
                url_for(
                    "claim_item",
                    item_id=item.id
                )
            )

        claim = ClaimRequest(
            user_id=session["user_id"],
            found_item_id=item.id,
            claim_reason=claim_reason,
            status="Pending"
        )

        db.session.add(claim)
        db.session.commit()

        flash(
            "Claim request submitted successfully. "
            "It has been sent to the Admin."
        )

        return redirect(
            url_for("my_claims")
        )

    return render_template(
        "claim_item.html",
        item=item
    )


# =========================================================
# MY LOST ITEMS
# =========================================================

@app.route("/my-lost-items")
def my_lost_items():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] not in [
        "student",
        "staff"
    ]:

        return redirect(
            url_for("dashboard")
        )

    lost_items = LostItem.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        LostItem.id.desc()
    ).all()

    return render_template(
        "my_lost_items.html",
        lost_items=lost_items
    )


# =========================================================
# MY CLAIMS
# =========================================================

@app.route("/my-claims")
def my_claims():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    claims = ClaimRequest.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        ClaimRequest.id.desc()
    ).all()

    claim_details = []

    for claim in claims:

        item = db.session.get(
            FoundItem,
            claim.found_item_id
        )

        claim_details.append(
            {
                "claim": claim,
                "item": item
            }
        )

    return render_template(
        "my_claims.html",
        claim_details=claim_details
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route("/notifications")
def notifications():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    user_notifications = Notification.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Notification.id.desc()
    ).all()

    for notification in user_notifications:

        notification.is_read = True

    db.session.commit()

    return render_template(
        "notifications.html",
        notifications=user_notifications
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    found_items_list = FoundItem.query.order_by(
        FoundItem.id.desc()
    ).all()

    lost_items_list = LostItem.query.order_by(
        LostItem.id.desc()
    ).all()

    pending_claims = ClaimRequest.query.filter_by(
        status="Pending"
    ).order_by(
        ClaimRequest.id.desc()
    ).all()

    pending_claim_details = []

    for claim in pending_claims:

        user = db.session.get(
            User,
            claim.user_id
        )

        item = db.session.get(
            FoundItem,
            claim.found_item_id
        )

        pending_claim_details.append(
            {
                "claim": claim,
                "user": user,
                "item": item
            }
        )

    total_claims_count = ClaimRequest.query.count()

    pending_claims_count = ClaimRequest.query.filter_by(
        status="Pending"
    ).count()

    return render_template(
        "admin_dashboard.html",
        found_items=found_items_list,
        lost_items=lost_items_list,
        claim_details=pending_claim_details,
        total_claims_count=total_claims_count,
        pending_claims_count=pending_claims_count,
        name=session["user_name"]
    )


# =========================================================
# ADMIN CLAIMS - FULL CLAIM HISTORY
# =========================================================

@app.route("/admin/claims")
def admin_claims():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    claim_requests = ClaimRequest.query.order_by(
        ClaimRequest.id.desc()
    ).all()

    claim_details = []

    for claim in claim_requests:

        user = db.session.get(
            User,
            claim.user_id
        )

        item = db.session.get(
            FoundItem,
            claim.found_item_id
        )

        claim_details.append(
            {
                "claim": claim,
                "user": user,
                "item": item
            }
        )

    return render_template(
        "admin_claims.html",
        claim_details=claim_details
    )


# =========================================================
# ADMIN RECEIVES FOUND ITEM
# =========================================================

@app.route(
    "/admin/receive-found/<int:item_id>",
    methods=["POST"]
)
def receive_found_item(item_id):

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    item = db.session.get(
        FoundItem,
        item_id
    )

    if item is None:

        flash(
            "Found item not found."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    if item.status == "Claimed / Recovered":

        flash(
            "This item has already been claimed and recovered."
        )

        return redirect(
            url_for("admin_dashboard")
        )

    item.status = "Received by Admin"

    db.session.commit()

    flash(
        "Found item received by Admin Office."
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================================================
# ADMIN APPROVE CLAIM
# =========================================================

@app.route(
    "/admin/approve-claim/<int:claim_id>",
    methods=["POST"]
)
def approve_claim(claim_id):

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    claim = db.session.get(
        ClaimRequest,
        claim_id
    )

    if claim is None:

        flash(
            "Claim request not found."
        )

        return redirect(
            url_for("admin_claims")
        )

    if claim.status != "Pending":

        flash(
            "This claim has already been processed."
        )

        return redirect(
            url_for("admin_claims")
        )

    item = db.session.get(
        FoundItem,
        claim.found_item_id
    )

    if item is None:

        flash(
            "The found item connected to this claim no longer exists."
        )

        return redirect(
            url_for("admin_claims")
        )

    claim.status = "Approved"

    claim.admin_message = (
        "Your claim has been approved. "
        "Please collect your item from the Admin Office."
    )

    item.status = "Claimed / Recovered"

    other_pending_claims = ClaimRequest.query.filter(
        ClaimRequest.found_item_id == claim.found_item_id,
        ClaimRequest.id != claim.id,
        ClaimRequest.status == "Pending"
    ).all()

    for other_claim in other_pending_claims:

        other_claim.status = "Rejected"

        other_claim.admin_message = (
            "This item has already been approved "
            "for another claimant."
        )

        other_notification = Notification(
            user_id=other_claim.user_id,
            message=(
                "Your claim request has been REJECTED "
                "because this item has already been "
                "approved for another claimant."
            ),
            is_read=False
        )

        db.session.add(
            other_notification
        )

    notification = Notification(
        user_id=claim.user_id,
        message=(
            "Your claim request for the item "
            "has been APPROVED. "
            "Please collect your item from the Admin Office."
        ),
        is_read=False
    )

    db.session.add(
        notification
    )

    db.session.commit()

    flash(
        "Claim approved. Item marked as Claimed / Recovered."
    )

    return redirect(
        url_for("admin_claims")
    )


# =========================================================
# ADMIN REJECT CLAIM
# =========================================================

@app.route(
    "/admin/reject-claim/<int:claim_id>",
    methods=["POST"]
)
def reject_claim(claim_id):

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    claim = db.session.get(
        ClaimRequest,
        claim_id
    )

    if claim is None:

        flash(
            "Claim request not found."
        )

        return redirect(
            url_for("admin_claims")
        )

    if claim.status != "Pending":

        flash(
            "This claim has already been processed."
        )

        return redirect(
            url_for("admin_claims")
        )

    claim.status = "Rejected"

    claim.admin_message = (
        "Your claim request has been rejected "
        "by the Admin."
    )

    notification = Notification(
        user_id=claim.user_id,
        message=(
            "Your claim request for the item "
            "has been REJECTED by the Admin."
        ),
        is_read=False
    )

    db.session.add(
        notification
    )

    db.session.commit()

    flash(
        "Claim rejected. The found item remains available."
    )

    return redirect(
        url_for("admin_claims")
    )


# =========================================================
# ADMIN USER MANAGEMENT
# =========================================================

@app.route("/admin/users")
def manage_users():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    users = User.query.order_by(
        User.id.desc()
    ).all()

    return render_template(
        "manage_users.html",
        users=users
    )


@app.route(
    "/admin/add-user",
    methods=["GET", "POST"]
)
def add_user():

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        ).strip().lower()

        if not name or not email or not password:

            flash(
                "Please fill all required fields."
            )

            return redirect(
                url_for("add_user")
            )

        if role not in [
            "student",
            "staff"
        ]:

            flash(
                "Please select Student or Staff."
            )

            return redirect(
                url_for("add_user")
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "This User ID / Email already exists."
            )

            return redirect(
                url_for("add_user")
            )

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(
                password
            ),
            role=role,
            active=True
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            f"{role.capitalize()} account created successfully."
        )

        return redirect(
            url_for("manage_users")
        )

    return render_template(
        "add_user.html"
    )


@app.route(
    "/admin/deactivate-user/<int:user_id>",
    methods=["POST"]
)
def deactivate_user(user_id):

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    user = db.session.get(
        User,
        user_id
    )

    if user is None:

        flash(
            "User not found."
        )

        return redirect(
            url_for("manage_users")
        )

    if user.role == "admin":

        flash(
            "The administrator account cannot be deactivated."
        )

        return redirect(
            url_for("manage_users")
        )

    user.active = False

    db.session.commit()

    flash(
        f"{user.name}'s account has been deactivated."
    )

    return redirect(
        url_for("manage_users")
    )


@app.route(
    "/admin/activate-user/<int:user_id>",
    methods=["POST"]
)
def activate_user(user_id):

    if "user_id" not in session:

        return redirect(
            url_for("login_choice")
        )

    if session["role"] != "admin":

        return redirect(
            url_for("dashboard")
        )

    user = db.session.get(
        User,
        user_id
    )

    if user is None:

        flash(
            "User not found."
        )

        return redirect(
            url_for("manage_users")
        )

    if user.role == "admin":

        flash(
            "The administrator account is already active."
        )

        return redirect(
            url_for("manage_users")
        )

    user.active = True

    db.session.commit()

    flash(
        f"{user.name}'s account has been activated."
    )

    return redirect(
        url_for("manage_users")
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

