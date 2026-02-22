#pip install flask flask-sqlalchemy flask-wtf python-dotenv

#To open db
#Press Ctrl+Shift+P
#Type SQLite: New Query and select it

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    urgency = db.Column(db.String(20), nullable=False)
    timing_window = db.Column(db.String(50), nullable=False)
    photo_filename = db.Column(db.String(255))  # New field for photo filename
    created_at = db.Column(db.DateTime, default=datetime.now)

@app.before_request
def create_tables():
    import os
    # If database exists but needs schema update, delete it for this demo
    if os.path.exists('jobs.db'):
        os.remove('jobs.db')
    db.create_all()

@app.route('/')
def index():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('index.html', jobs=jobs)

@app.route('/post', methods=['GET', 'POST'])
def post_job():
    if request.method == 'POST':
        # Handle file upload
        photo_filename = None
        if 'photo' in request.files and request.files['photo'].filename != '':
            file = request.files['photo']
            if file and allowed_file(file.filename):
                # Secure the filename and save it
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_filename = filename
        
        new_job = Job(
            title=request.form['title'],
            description=request.form['description'],
            location=request.form['location'],
            category=request.form['category'],
            urgency=request.form['urgency'],
            timing_window=request.form['timing_window'],
            photo_filename=photo_filename
        )
        db.session.add(new_job)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_job(id):
    job = Job.query.get_or_404(id)
    # Delete the associated photo file if it exists
    if job.photo_filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], job.photo_filename))
        except:
            pass
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True)
