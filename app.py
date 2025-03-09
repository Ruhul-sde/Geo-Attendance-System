from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import uuid
from datetime import datetime, timedelta
import math
import calendar

app = Flask(__name__)
app.secret_key = 'geo_attendance_system_secret'

# Mock database - in a real app you'd use a proper database
DATABASE_FILE = 'database.json'

def initialize_db():
    if not os.path.exists(DATABASE_FILE):
        data = {
            'users': {
                'admin': {
                    'password': 'admin123',
                    'name': 'Admin User',
                    'role': 'admin',
                    'employee_id': 'ADMIN001'
                },
                'user': {
                    'password': 'user123',
                    'name': 'Test User',
                    'role': 'employee',
                    'employee_id': 'EMP001',
                    'manager': 'admin'
                }
            },
            'locations': {
                'loc1': {
                    'name': 'Main Office',
                    'latitude': 28.7041,
                    'longitude': 77.1025,
                    'radius': 100
                },
                'loc2': {
                    'name': 'Branch Office',
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'radius': 100
                }
            },
            'attendance': {},
            'leaves': {}
        }
        with open(DATABASE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

def get_db():
    with open(DATABASE_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Calculate distance between two points using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Earth's radius in meters
    φ1 = lat1 * math.pi / 180
    φ2 = lat2 * math.pi / 180
    Δφ = (lat2 - lat1) * math.pi / 180
    Δλ = (lon2 - lon1) * math.pi / 180

    a = math.sin(Δφ/2) * math.sin(Δφ/2) + \
        math.cos(φ1) * math.cos(φ2) * \
        math.sin(Δλ/2) * math.sin(Δλ/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c  # Distance in meters
    return d

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    db = get_db()
    if username in db['users'] and db['users'][username]['password'] == password:
        session['username'] = username
        session['role'] = db['users'][username]['role']
        session['name'] = db['users'][username]['name']
        session['employee_id'] = db['users'][username]['employee_id']
        
        # Get user's assigned location from their profile
        if 'latitude' in db['users'][username] and 'longitude' in db['users'][username]:
            session['latitude'] = db['users'][username]['latitude']
            session['longitude'] = db['users'][username]['longitude']
        else:
            # Set default location if none is assigned yet
            session['latitude'] = 0
            session['longitude'] = 0

        # Redirect admin to admin dashboard, regular users to regular dashboard
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('login.html', error='Invalid credentials')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    fullname = request.form.get('fullname')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    # Basic validation
    if not username or not password or not confirm_password or not fullname:
        return render_template('login.html', error='All fields are required')

    if password != confirm_password:
        return render_template('login.html', error='Passwords do not match')

    db = get_db()

    # Check if username already exists
    if username in db['users']:
        return render_template('login.html', error='Username already exists')

    # Generate a new employee ID
    employee_count = sum(1 for user in db['users'].values() if user['role'] == 'employee')
    new_emp_id = f"EMP{str(employee_count + 1).zfill(3)}"

    # Add the new user with location information
    db['users'][username] = {
        'password': password,
        'name': fullname,
        'role': 'employee',  # Default role is employee
        'employee_id': new_emp_id,
        'manager': 'admin',   # Default manager is admin
        'latitude': float(latitude) if latitude else 0,
        'longitude': float(longitude) if longitude else 0,
        'location_name': 'Custom Location'  # Default location name
    }

    save_db(db)

    return render_template('login.html', success='Account created successfully! You can now login.')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.form.get('username')

    if not username:
        return render_template('login.html', error='Username is required')

    db = get_db()

    if username not in db['users']:
        return render_template('login.html', error='Username not found')

    # Generate a simple random password
    import random
    import string
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # In a real application, you would send this password via email
    # For this demo, we'll just display it
    db['users'][username]['password'] = new_password
    save_db(db)

    return render_template('login.html', success=f'Password has been reset to: {new_password}')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))

    db = get_db()
    user_data = db['users'][session['username']]

    # Get today's attendance
    today = datetime.now().strftime('%Y-%m-%d')
    attendance_today = None
    if 'attendance' in db and session['employee_id'] in db['attendance']:
        if today in db['attendance'][session['employee_id']]:
            attendance_today = db['attendance'][session['employee_id']][today]

    # Get pending leaves
    pending_leaves = []
    if 'leaves' in db and session['employee_id'] in db['leaves']:
        for leave_id, leave in db['leaves'][session['employee_id']].items():
            if leave['status'] == 'pending':
                pending_leaves.append(leave)
    
    # Add attendance stats
    # These are mock values - in a real app, you'd calculate these based on actual data
    stats = {
        'attendance_percentage': 85,
        'present_days': 17,
        'absent_days': 3,
        'leave_days': 0
    }

    return render_template('dashboard.html', 
                          user=user_data, 
                          attendance_today=attendance_today,
                          pending_leaves=pending_leaves,
                          locations=db['locations'],
                          stats=stats)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})

    # Check if login location is available
    if 'latitude' not in session or 'longitude' not in session:
        return jsonify({'success': False, 'message': 'Login location not available. Please log in again.'})

    data = request.json
    user_lat = data.get('latitude')
    user_lon = data.get('longitude')
    login_lat = session.get('latitude')
    login_lon = session.get('longitude')
    location_id = data.get('location_id')

    db = get_db()

    # Verify location exists
    if location_id not in db['locations']:
        return jsonify({'success': False, 'message': 'Invalid location'})

    # First verify that current location matches login location (roughly)
    login_distance = calculate_distance(user_lat, user_lon, login_lat, login_lon)
    if login_distance > 100:  # Within 100 meters of login location
        return jsonify({
            'success': False, 
            'message': 'Your current location does not match your login location'
        })

    location = db['locations'][location_id]
    distance = calculate_distance(user_lat, user_lon, location['latitude'], location['longitude'])

    if distance > location['radius']:
        return jsonify({
            'success': False, 
            'message': f'You are not within the {location["name"]} area'
        })

    # Mark attendance
    today = datetime.now().strftime('%Y-%m-%d')
    time_now = datetime.now().strftime('%H:%M:%S')

    if 'attendance' not in db:
        db['attendance'] = {}

    if session['employee_id'] not in db['attendance']:
        db['attendance'][session['employee_id']] = {}

    db['attendance'][session['employee_id']][today] = {
        'check_in': time_now,
        'location': location['name'],
        'status': 'Present'
    }

    save_db(db)

    return jsonify({'success': True, 'message': 'Attendance marked successfully'})

@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')
        leave_type = request.form.get('leave_type')

        db = get_db()

        if 'leaves' not in db:
            db['leaves'] = {}

        if session['employee_id'] not in db['leaves']:
            db['leaves'][session['employee_id']] = {}

        leave_id = str(uuid.uuid4())

        # Find manager
        manager_id = db['users'][session['username']].get('manager')

        db['leaves'][session['employee_id']][leave_id] = {
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason,
            'type': leave_type,
            'status': 'pending',
            'manager': manager_id,
            'applied_on': datetime.now().strftime('%Y-%m-%d')
        }

        save_db(db)

        return redirect(url_for('leave_status'))

    # Define leave types
    leave_types = ['PL', 'CL', 'ML', 'Other']

    return render_template('apply_leave.html', leave_types=leave_types)

@app.route('/leave_status')
def leave_status():
    if 'username' not in session:
        return redirect(url_for('home'))

    db = get_db()
    user_leaves = {}

    if 'leaves' in db and session['employee_id'] in db['leaves']:
        user_leaves = db['leaves'][session['employee_id']]

    return render_template('leave_status.html', leaves=user_leaves)

@app.route('/admin/pending_leaves')
def admin_pending_leaves():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    db = get_db()
    pending_leaves = {}

    if 'leaves' in db:
        for emp_id, leaves in db['leaves'].items():
            for leave_id, leave in leaves.items():
                if leave['status'] == 'pending' and leave.get('manager') == session['employee_id']:
                    if emp_id not in pending_leaves:
                        pending_leaves[emp_id] = {}
                    pending_leaves[emp_id][leave_id] = leave
                    # Add employee name
                    for username, user_data in db['users'].items():
                        if user_data['employee_id'] == emp_id:
                            pending_leaves[emp_id][leave_id]['employee_name'] = user_data['name']
                            break

    return render_template('admin_leaves.html', pending_leaves=pending_leaves)

@app.route('/admin/update_leave', methods=['POST'])
def admin_update_leave():
    if 'username' not in session or session['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})

    data = request.json
    emp_id = data.get('employee_id')
    leave_id = data.get('leave_id')
    status = data.get('status')  # 'approved' or 'rejected'

    db = get_db()

    if 'leaves' in db and emp_id in db['leaves'] and leave_id in db['leaves'][emp_id]:
        db['leaves'][emp_id][leave_id]['status'] = status
        save_db(db)
        return jsonify({'success': True, 'message': f'Leave {status} successfully'})

    return jsonify({'success': False, 'message': 'Leave not found'})

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('home'))

    db = get_db()
    user_data = db['users'][session['username']]

    # Mock data for profile display
    # In a real app, you'd fetch this from the database
    user_data['email'] = user_data.get('email', f"{session['username']}@example.com")
    user_data['phone'] = user_data.get('phone', "N/A")
    user_data['address'] = user_data.get('address', "N/A")
    user_data['department'] = user_data.get('department', "General")
    user_data['position'] = user_data.get('position', "Staff")
    user_data['join_date'] = user_data.get('join_date', "2023-01-01")

    # Mock attendance stats
    stats = {
        'attendance_percentage': 85,
        'present_days': 17,
        'absent_days': 3,
        'leave_days': 0
    }

    # Mock leave balance
    leaves = {
        'pl_used': 2,
        'pl_remaining': 10,
        'pl_percentage': 20,
        'cl_used': 1,
        'cl_remaining': 5,
        'cl_percentage': 20,
        'ml_used': 0,
        'ml_remaining': 7,
        'ml_percentage': 0
    }

    return render_template('profile.html', user=user_data, stats=stats, leaves=leaves)



@app.route('/attendance_report')
def attendance_report():
    if 'username' not in session:
        return redirect(url_for('home'))

    # Get selected month or default to current month
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    year, month_num = map(int, month.split('-'))

    db = get_db()
    attendance_data = {}
    leaves_data = {}

    # Get days in the selected month
    days_in_month = calendar.monthrange(year, month_num)[1]
    month_dates = [f"{month}-{str(day).zfill(2)}" for day in range(1, days_in_month + 1)]

    # Get attendance for the month
    if 'attendance' in db and session['employee_id'] in db['attendance']:
        employee_attendance = db['attendance'][session['employee_id']]
        for date in month_dates:
            if date in employee_attendance:
                attendance_data[date] = employee_attendance[date]

    # Get leaves for the month
    leave_counts = {'PL': 0, 'CL': 0, 'ML': 0, 'Other': 0}
    leave_details = []

    if 'leaves' in db and session['employee_id'] in db['leaves']:
        for leave_id, leave in db['leaves'][session['employee_id']].items():
            start = datetime.strptime(leave['start_date'], '%Y-%m-%d')
            end = datetime.strptime(leave['end_date'], '%Y-%m-%d')

            # Check if leave falls in selected month
            if start.year == year and start.month == month_num:
                leave_type = leave['type']
                days = (end - start).days + 1

                if leave_type in leave_counts:
                    leave_counts[leave_type] += days
                else:
                    leave_counts['Other'] += days

                leave_details.append(leave)

    # Get all months with attendance or leave data
    all_months = set()
    # Add current selected month
    all_months.add(month)
    
    # Add months with attendance data
    if 'attendance' in db and session['employee_id'] in db['attendance']:
        for date in db['attendance'][session['employee_id']]:
            all_months.add(date[:7])  # YYYY-MM format

    # Add months with leave data
    if 'leaves' in db and session['employee_id'] in db['leaves']:
        for leave_id, leave in db['leaves'][session['employee_id']].items():
            all_months.add(leave['start_date'][:7])
    
    # Ensure all months of current year are available for selection
    current_year = datetime.now().year
    for m in range(1, 13):
        all_months.add(f"{current_year}-{str(m).zfill(2)}")
    
    # Also add all months of the selected year
    for m in range(1, 13):
        all_months.add(f"{year}-{str(m).zfill(2)}")

    all_months = sorted(list(all_months), reverse=True)

    return render_template('attendance_report.html', 
                          attendance_data=attendance_data,
                          leaves_data=leave_counts,
                          leave_details=leave_details,
                          month=month,
                          all_months=all_months,
                          month_dates=month_dates)

@app.route('/admin/attendance_report')
def admin_attendance_report():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    emp_id = request.args.get('employee_id')
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))

    db = get_db()
    employees = {}
    for username, user in db['users'].items():
        if user['role'] != 'admin':
            employees[user['employee_id']] = user['name']

    if not emp_id and employees:
        emp_id = list(employees.keys())[0]

    attendance_data = {}
    leaves_data = {}

    if emp_id:
        year, month_num = map(int, month.split('-'))

        # Get days in the selected month
        days_in_month = calendar.monthrange(year, month_num)[1]
        month_dates = [f"{month}-{str(day).zfill(2)}" for day in range(1, days_in_month + 1)]

        # Get attendance for the month
        if 'attendance' in db and emp_id in db['attendance']:
            employee_attendance = db['attendance'][emp_id]
            for date in month_dates:
                if date in employee_attendance:
                    attendance_data[date] = employee_attendance[date]

        # Get leaves for the month
        leave_counts = {'PL': 0, 'CL': 0, 'ML': 0, 'Other': 0}
        leave_details = []

        if 'leaves' in db and emp_id in db['leaves']:
            for leave_id, leave in db['leaves'][emp_id].items():
                start = datetime.strptime(leave['start_date'], '%Y-%m-%d')
                end = datetime.strptime(leave['end_date'], '%Y-%m-%d')

                # Check if leave falls in selected month
                if start.year == year and start.month == month_num:
                    leave_type = leave['type']
                    days = (end - start).days + 1

                    if leave_type in leave_counts:
                        leave_counts[leave_type] += days
                    else:
                        leave_counts['Other'] += days

                    leave_details.append(leave)

        # Get all months with attendance or leave data
        all_months = set()
        if 'attendance' in db:
            for employee_id in db['attendance']:
                for date in db['attendance'][employee_id]:
                    all_months.add(date[:7])  # YYYY-MM format

        if 'leaves' in db:
            for employee_id in db['leaves']:
                for leave_id, leave in db['leaves'][employee_id].items():
                    all_months.add(leave['start_date'][:7])

        all_months = sorted(list(all_months), reverse=True)
    else:
        month_dates = []
        all_months = []

    return render_template('admin_attendance_report.html', 
                          employees=employees,
                          selected_employee=emp_id,
                          attendance_data=attendance_data,
                          leaves_data=leave_counts,
                          leave_details=leave_details,
                          month=month,
                          all_months=all_months,
                          month_dates=month_dates)

@app.route('/admin/locations', methods=['GET', 'POST'])
def admin_locations():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    db = get_db()

    if request.method == 'POST':
        name = request.form.get('name')
        latitude = float(request.form.get('latitude'))
        longitude = float(request.form.get('longitude'))
        radius = float(request.form.get('radius'))

        location_id = str(uuid.uuid4())

        if 'locations' not in db:
            db['locations'] = {}

        db['locations'][location_id] = {
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius
        }

        save_db(db)

        return redirect(url_for('admin_locations'))

    return render_template('admin_locations.html', locations=db['locations'])

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    
    db = get_db()
    
    # Count total employees, present today, absent today, and pending leaves
    total_employees = sum(1 for user in db['users'].values() if user['role'] == 'employee')
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Count present employees today
    present_today = 0
    if 'attendance' in db:
        for emp_id, dates in db['attendance'].items():
            if today in dates:
                present_today += 1
    
    # Count pending leaves
    pending_leaves = 0
    if 'leaves' in db:
        for emp_id, leaves in db['leaves'].items():
            for leave_id, leave in leaves.items():
                if leave['status'] == 'pending':
                    pending_leaves += 1
    
    # Calculate absent employees (total - present)
    absent_today = total_employees - present_today
    
    # Prepare stats for the admin dashboard
    stats = {
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'pending_leaves': pending_leaves
    }
    
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/employee_directory')
def employee_directory():
    if 'username' not in session:
        return redirect(url_for('home'))

    db = get_db()
    
    # Get all employees
    employees = []
    for username, user in db['users'].items():
        if user['role'] == 'employee':
            # Add some mock data for display purposes
            employee_data = user.copy()
            employee_data['email'] = f"{username}@example.com"
            employee_data['phone'] = '+1 555-123-4567'
            employee_data['department'] = 'General'
            employee_data['avatar'] = None
            employees.append(employee_data)
    
    return render_template('employee_directory.html', employees=employees)

@app.route('/admin/employee_locations', methods=['GET', 'POST'])
def admin_employee_locations():
    if 'username' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    db = get_db()
    
    # Get all employees
    employees = {}
    for username, user in db['users'].items():
        if user['role'] == 'employee':
            employees[username] = user
    
    if request.method == 'POST':
        username = request.form.get('username')
        location_id = request.form.get('location_id')
        custom_lat = request.form.get('custom_latitude')
        custom_lng = request.form.get('custom_longitude')
        
        if username in db['users']:
            if location_id == 'custom' and custom_lat and custom_lng:
                # Set custom location
                db['users'][username]['latitude'] = float(custom_lat)
                db['users'][username]['longitude'] = float(custom_lng)
                db['users'][username]['location_name'] = 'Custom Location'
            elif location_id in db['locations']:
                # Set to predefined location
                db['users'][username]['latitude'] = db['locations'][location_id]['latitude']
                db['users'][username]['longitude'] = db['locations'][location_id]['longitude']
                db['users'][username]['location_name'] = db['locations'][location_id]['name']
            
            save_db(db)
            return redirect(url_for('admin_employee_locations', success='Employee location updated'))
    
    # Get success message if any
    success = request.args.get('success')
    
    return render_template('admin_employee_locations.html', 
                          employees=employees, 
                          locations=db['locations'],
                          success=success)

if __name__ == '__main__':
    initialize_db()
    app.run(host='0.0.0.0', port=8080, debug=True)