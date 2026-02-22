#pip install flask flask-sqlalchemy flask-wtf python-dotenv

#To open db
#Press Ctrl+Shift+P
#Type SQLite: New Query and select it

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    timing_window = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

@app.before_request  # ✅ This runs ONLY before the first request
def create_tables():
    import os
    # Only delete existing database if you want to reset (comment out after first run)
    if os.path.exists('jobs.db'):
        print("⚠️ Database exists - deleting to apply schema changes")
        os.remove('jobs.db')
    db.create_all()
    print("✅ Database initialized with latest schema")

@app.route('/')
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('index.html', jobs=jobs)

@app.route('/post', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        new_job = Job(
            title=request.form['title'],
            description=request.form['description'],
            location=request.form['location'],
            category=request.form['category'],
            urgency=request.form['urgency'],
            timing_window=request.form['timing_window']
        )
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_job(id):
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
