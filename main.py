# main.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_manager.db'
db = SQLAlchemy(app)


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
    repeat = db.Column(db.String(20), nullable=True)  # Add 'repeat' column

    def __init__(self, name, deadline, description, priority, status, department, repeat=None):
        self.name = name
        self.deadline = deadline
        self.description = description
        self.priority = priority
        self.status = status
        self.department = department
        self.repeat = repeat


# Sample data
names = ["Ayesha Ibrahim", "Huda","Ayesha Rauf", "Hamza","Hassan", "Bilal", "Abdullah","Faizan","Marketing","Operations","Accounts","sales"]
departments = ["Marketing", "Operations", "Sales","Accounts"]
priorities = [1, 2, 3]
statuses = ["Pending", "Complete", "Overdue"]
performances = ["Excellent", "Good", "Average"]

# Store performance data for each department
performance_data = {department: None for department in departments}


@app.route('/', methods=['GET', 'POST'])
def task_manager():
    if request.method == 'POST':
        name = request.form['name']
        deadline = request.form['deadline']
        description = request.form['description']
        priority = int(request.form['priority'])
        status = request.form['status']
        department = request.form['department']
        repeat = request.form['repeat']

        new_task = Task(name, deadline, description, priority, status, department, repeat)
        db.session.add(new_task)
        db.session.commit()

        if repeat == 'daily':
            create_repeated_tasks(new_task, timedelta(days=1))
        elif repeat == 'weekly':
            create_repeated_tasks(new_task, timedelta(weeks=1))
        elif repeat == 'monthly':
            create_repeated_tasks(new_task, timedelta(days=30))  # Approximation for a month

    filter_name = request.args.get('filter_name')
    filter_status = request.args.get('filter_status')
    filter_deadline = request.args.get('filter_deadline')

    filtered_tasks = Task.query.filter_by(archived=False)

    if filter_name:
        filtered_tasks = filtered_tasks.filter(Task.name == filter_name)

    if filter_status:
        filtered_tasks = filtered_tasks.filter(Task.status == filter_status)

    if filter_deadline:
        filtered_tasks = filtered_tasks.filter(Task.deadline == filter_deadline)

    filtered_tasks = filtered_tasks.all()

    return render_template('task_manager.html',
                           names=names,
                           departments=departments,
                           priorities=priorities,
                           statuses=statuses,
                           performances=performances,
                           tasks=filtered_tasks,
                           filter_name=filter_name,
                           filter_status=filter_status,
                           filter_deadline=filter_deadline,
                           performance_data=performance_data
                           )


@app.route('/init_performance', methods=['GET'])
def init_performance():
    db.create_all()
    existing_departments = Performance.query.with_entities(Performance.department).all()
    existing_departments = [department[0] for department in existing_departments]

    for department in departments:
        if department not in existing_departments:
            performance = Performance(department, performances[0])
            db.session.add(performance)
    db.session.commit()

    return redirect(url_for('task_manager'))


@app.route('/restore_task/<int:task_id>', methods=['POST'])
def restore_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.archived = False  # Set the archived status to False
        db.session.commit()
    return redirect(url_for('task_manager'))


@app.route('/clean_database', methods=['GET', 'POST'])
def clean_database():
    if request.method == 'POST':
        # Delete all tasks from the database
        Task.query.delete()
        db.session.commit()
        return redirect(url_for('task_manager'))

    return render_template('clean_database.html')


@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        task.name = request.form['name']
        task.deadline = request.form['deadline']
        task.description = request.form['description']
        task.priority = int(request.form['priority'])
        task.status = request.form['status']
        task.department = request.form['department']
        task.repeat = request.form['repeat']
        db.session.commit()
        return redirect(url_for('task_manager'))

    return render_template('edit_task.html',
                           names=names,
                           departments=departments,
                           priorities=priorities,
                           statuses=statuses,
                           task=task)


@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('task_manager'))


@app.route('/archive_task/<int:task_id>', methods=['POST'])
def archive_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.archived = True
        db.session.commit()
    return redirect(url_for('task_manager'))


@app.route('/archive_all_tasks', methods=['GET', 'POST'])
def archive_all_tasks():
    tasks = Task.query.filter_by(archived=True).all()
    return render_template('archived_tasks.html', tasks=tasks)


@app.route('/update_status/<int:task_id>', methods=['POST'])
def update_status(task_id):
    task = Task.query.get(task_id)
    task.status = request.form['status']
    db.session.commit()
    return redirect(url_for('task_manager'))


@app.route('/update_performance', methods=['POST'])
def update_performance():
    for department in departments:
        performance_data[department] = request.form.get(department)
    return redirect(url_for('task_manager'))


def create_repeated_tasks(task, delta):
    deadline = datetime.strptime(task.deadline, '%Y-%m-%d')

    while deadline <= datetime.now():
        deadline += delta

    while deadline <= datetime.now() + timedelta(weeks=52):  # Limit to one year
        new_task = Task(task.name, deadline.strftime('%Y-%m-%d'), task.description,
                        task.priority, task.status, task.department, task.repeat)
        db.session.add(new_task)
        db.session.commit()
        deadline += delta


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
