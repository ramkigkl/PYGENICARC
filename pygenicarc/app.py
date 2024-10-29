from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your real secret key

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/pygenicarc'
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Courses Page
@app.route('/courses')
def courses():
    courses = list(mongo.db.courses.find())
    return render_template('courses.html', courses=courses)

# Contact Page
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Login and Register Route
@app.route('/login', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('login_type')  # admin or student
        action = request.form.get('action')  # Either 'login' or 'register'

        if action == 'register':
            # Registration logic for both admin and student
            if role == 'student':
                existing_user = mongo.db.users.find_one({"email": email, "role": "student"})
                if existing_user:
                    flash('Student already exists! Please log in.', 'danger')
                    return redirect(url_for('login_register'))

                # Hash the password and store student in the database
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                mongo.db.users.insert_one({
                    "email": email,
                    "password": hashed_password,
                    "role": "student",
                    "enrolled_courses": []
                })
                flash('Student registration successful! Please log in.', 'success')
                return redirect(url_for('login_register'))

            elif role == 'admin':
                existing_admin = mongo.db.users.find_one({"email": email, "role": "admin"})
                if existing_admin:
                    flash('Admin already exists! Please log in.', 'danger')
                    return redirect(url_for('login_register'))

                # Hash the password and store admin in the database
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                mongo.db.users.insert_one({
                    "email": email,
                    "password": hashed_password,
                    "role": "admin"
                })
                flash('Admin registration successful! Please log in.', 'success')
                return redirect(url_for('login_register'))

        elif action == 'login':
            # Login logic for both admin and student
            if role == 'student':
                user = mongo.db.users.find_one({"email": email, "role": "student"})
                if user and bcrypt.check_password_hash(user['password'], password):
                    session['user_id'] = str(user['_id'])
                    session['email'] = user['email']
                    session['role'] = 'student'
                    flash('Student login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid student credentials.', 'danger')
                    return redirect(url_for('login_register'))

            elif role == 'admin':
                admin = mongo.db.users.find_one({"email": email, "role": "admin"})
                if admin and bcrypt.check_password_hash(admin['password'], password):
                    session['admin_id'] = str(admin['_id'])
                    session['email'] = admin['email']
                    session['role'] = 'admin'
                    flash('Admin login successful!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid admin credentials.', 'danger')
                    return redirect(url_for('login_register'))

    return render_template('login_register.html')

# Student Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access your dashboard.', 'danger')
        return redirect(url_for('login_register'))
    
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    enrolled_courses_ids = user.get('enrolled_courses', [])
    enrolled_courses = mongo.db.courses.find({"_id": {"$in": [ObjectId(cid) for cid in enrolled_courses_ids]}})
    
    return render_template('dashboard.html', enrolled_courses=enrolled_courses)

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please log in as admin to access the dashboard.', 'danger')
        return redirect(url_for('login_register'))
    
    # Fetch all students and their enrolled courses
    students = mongo.db.users.find({"role": "student"})
    
    # Prepare data for display
    student_data = []
    for student in students:
        enrolled_courses_ids = student.get('enrolled_courses', [])
        enrolled_courses = list(mongo.db.courses.find({"_id": {"$in": [ObjectId(cid) for cid in enrolled_courses_ids]}}))
        student_data.append({
            "email": student['email'],
            "enrolled_courses": [course['title'] for course in enrolled_courses]
        })
    
    return render_template('admin_dashboard.html', student_data=student_data)

# Course Enrollment for Students
@app.route('/enroll/<course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        flash('Please log in to enroll in a course.', 'danger')
        return redirect(url_for('login_register'))

    # Add the course to the student's enrolled courses list
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if course_id not in user.get('enrolled_courses', []):
        mongo.db.users.update_one({"_id": ObjectId(session['user_id'])}, {"$push": {"enrolled_courses": course_id}})
        flash('You have successfully enrolled in the course!', 'success')

    return redirect(url_for('dashboard'))

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out.', 'info')
    return redirect(url_for('login_register'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
