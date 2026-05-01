from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# USER TABLE
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")

# PROJECT TABLE
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.Date, default=date.today, nullable=False)

    creator = db.relationship("User", backref="created_projects", foreign_keys=[created_by])

# TASK TABLE
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pending")
    due_date = db.Column(db.Date, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    project = db.relationship("Project", backref="tasks")
    assignee = db.relationship("User", foreign_keys=[assigned_to], backref="assigned_tasks")
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_tasks")
