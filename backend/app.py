from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from functools import wraps
import jwt
import datetime
from datetime import datetime as dt, date

from models import db, User, Project, Task

# 🚀 INIT
app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = "team-task-secret-very-long-key-123456789"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///teamtask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()


# ================= TOKEN =================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                raise Exception("Invalid user")
        except Exception as e:
            print("TOKEN ERROR:", str(e))
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# ================= ADMIN =================
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(current_user, *args, **kwargs)
    return decorated


# ================= HOME =================
@app.route("/")
def home():
    return jsonify({"message": "Backend Running 🚀"})


# ================= AUTH =================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data or not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "All fields required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed,
        role=data.get("role", "member")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email & password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    })


# ================= PROFILE =================
@app.route("/profile")
@token_required
def profile(current_user):
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    })


# ================= USERS =================
@app.route("/users")
@token_required
@admin_required
def users(current_user):
    users = User.query.all()
    return jsonify([
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
        for u in users
    ])


# ================= PROJECT =================
@app.route("/projects", methods=["GET"])
@token_required
def get_projects(current_user):
    projects = Project.query.all()
    return jsonify([
        {"id": p.id, "name": p.name}
        for p in projects
    ])


@app.route("/projects", methods=["POST"])
@token_required
@admin_required
def create_project(current_user):
    try:
        data = request.get_json()

        if not data or not data.get("name"):
            return jsonify({"error": "Project name required"}), 400

        project = Project(
            name=data.get("name"),
            created_by=current_user.id
        )

        db.session.add(project)
        db.session.commit()

        return jsonify({"message": "Project created"})

    except Exception as e:
        print("PROJECT ERROR:", str(e))
        return jsonify({"error": "Server error"}), 500


# ================= TASK =================
@app.route("/tasks", methods=["GET"])
@token_required
def get_tasks(current_user):
    if current_user.role == "admin":
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(assigned_to=current_user.id).all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "project_id": t.project_id,
            "assigned_to": t.assigned_to,
            "due_date": str(t.due_date) if t.due_date else None  # 🔥 FIX
        }
        for t in tasks
    ])


@app.route("/tasks", methods=["POST"])
@token_required
@admin_required
def create_task(current_user):
    try:
        data = request.get_json()

        if not data or not data.get("title") or not data.get("project_id") or not data.get("assigned_to"):
            return jsonify({"error": "Missing fields"}), 400

        due_date = None
        if data.get("due_date"):
            due_date = dt.strptime(data["due_date"], "%Y-%m-%d").date()

        task = Task(
            title=data["title"],
            description=data.get("description", ""),
            status="pending",
            project_id=data["project_id"],
            assigned_to=data["assigned_to"],
            created_by=current_user.id,
            due_date=due_date
        )

        db.session.add(task)
        db.session.commit()

        return jsonify({"message": "Task created"})

    except Exception as e:
        print("TASK ERROR:", str(e))
        return jsonify({"error": "Server error"}), 500


# ================= TASK STATUS =================
@app.route("/tasks/<int:task_id>/status", methods=["PUT"])
@token_required
def update_task_status(current_user, task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    task.status = request.json.get("status")
    db.session.commit()

    return jsonify({"message": "Status updated"})


# ================= DASHBOARD =================
@app.route("/dashboard-stats")
@token_required
def dashboard_stats(current_user):
    tasks = Task.query.all()

    total = len(tasks)
    completed = len([t for t in tasks if t.status == "completed"])
    pending = len([t for t in tasks if t.status == "pending"])

    overdue = len([
        t for t in tasks
        if t.due_date and t.due_date < date.today() and t.status != "completed"
    ])

    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue  # 🔥 NEW
    })


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)