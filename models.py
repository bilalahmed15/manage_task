from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    deadline = db.Column(db.String(100))
    description = db.Column(db.String(500))
    priority = db.Column(db.Integer)
    status = db.Column(db.String(100))
    department = db.Column(db.String(100))
    archived = db.Column(db.Boolean, default=False)  # Add 'archived' column
    daily = db.Column(db.Boolean, default=False)  # Add 'daily' column

    def __init__(self, name, deadline, description, priority, status, department, daily=False):
        self.name = name
        self.deadline = deadline
        self.description = description
        self.priority = priority
        self.status = status
        self.department = department
        self.daily = daily



