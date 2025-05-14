from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
from dotenv import load_dotenv
import stripe

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Configure other environment variables
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'user', 'provider', 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    experience = db.Column(db.Integer)
    hourly_rate = db.Column(db.Float)
    availability = db.Column(db.Boolean, default=True)
    user = db.relationship('User', backref='provider_profile')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    base_price = db.Column(db.Float)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='bookings')
    provider = db.relationship('ServiceProvider', backref='bookings')
    service = db.relationship('Service', backref='bookings')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    services = Service.query.all()
    providers = ServiceProvider.query.filter_by(availability=True).all()
    return render_template('index.html', services=services, providers=providers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        user_type = request.form.get('user_type')

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('register'))

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            name=name,
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()

        if user_type == 'provider':
            service_type = request.form.get('service_type')
            description = request.form.get('description')
            experience = request.form.get('experience', '0')
            hourly_rate = request.form.get('hourly_rate', '0')
            
            # Validate service type exists
            service = Service.query.filter_by(name=service_type).first()
            if not service:
                flash('Invalid service type selected')
                return redirect(url_for('register'))
            
            try:
                provider = ServiceProvider(
                    user_id=user.id,
                    service_type=service_type,
                    description=description,
                    experience=int(experience),
                    hourly_rate=float(hourly_rate),
                    availability=True
                )
                db.session.add(provider)
                db.session.commit()
            except ValueError:
                flash('Invalid experience or hourly rate values')
                return redirect(url_for('register'))

        flash('Registration successful')
        return redirect(url_for('login'))

    # Get list of services for the registration form
    services = Service.query.all()
    return render_template('register.html', services=services)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.user_type == 'provider':
                return redirect(url_for('provider_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))

        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/book_service', methods=['POST'])
@login_required
def book_service():
    if current_user.user_type != 'user':
        flash('Only users can book services')
        return redirect(url_for('home'))

    service_id = request.form.get('service_id')
    provider_id = request.form.get('provider_id')
    booking_date = request.form.get('booking_date')

    if not all([service_id, provider_id, booking_date]):
        flash('Please fill all required fields')
        return redirect(url_for('user_dashboard'))

    try:
        booking_date = datetime.strptime(booking_date, '%Y-%m-%dT%H:%M')
        booking = Booking(
            user_id=current_user.id,
            provider_id=provider_id,
            service_id=service_id,
            booking_date=booking_date,
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        flash('Booking request submitted successfully')
    except Exception as e:
        flash('Error creating booking')
        print(str(e))

    return redirect(url_for('user_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.user_type != 'user':
        return redirect(url_for('home'))
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    services = Service.query.all()
    providers = ServiceProvider.query.filter_by(availability=True).all()
    return render_template('user_dashboard.html', bookings=bookings, services=services, providers=providers)

@app.route('/provider_dashboard')
@login_required
def provider_dashboard():
    if current_user.user_type != 'provider':
        return redirect(url_for('home'))
    provider = ServiceProvider.query.filter_by(user_id=current_user.id).first()
    bookings = Booking.query.filter_by(provider_id=provider.id).all()
    return render_template('provider_dashboard.html', provider=provider, bookings=bookings)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.user_type != 'admin':
        return redirect(url_for('home'))
    users = User.query.all()
    providers = ServiceProvider.query.all()
    services = Service.query.all()
    bookings = Booking.query.all()
    return render_template('admin_dashboard.html', users=users, providers=providers, services=services, bookings=bookings)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    message = request.json.get('message')
    # Simple response logic (you can integrate with a more sophisticated chatbot)
    responses = {
        'hello': 'Hi! How can I help you today?',
        'services': 'We offer various household services including cleaning, plumbing, electrical work, and more.',
        'booking': 'You can book a service by logging in and selecting a service provider.',
        'contact': 'You can reach us at support@homeservices.com',
    }
    response = responses.get(message.lower(), "I'm sorry, I don't understand. Please try asking about our services, booking process, or contact information.")
    return jsonify({'response': response})

def init_sample_data():
    # Add sample services if they don't exist
    services = [
        {
            'name': 'House Cleaning',
            'description': 'Professional home cleaning services including deep cleaning, regular maintenance, and specialized cleaning tasks.',
            'category': 'Cleaning',
            'base_price': 50.00
        },
        {
            'name': 'Plumbing',
            'description': 'Expert plumbing services including repairs, installations, and maintenance for all your household needs.',
            'category': 'Maintenance',
            'base_price': 75.00
        },
        {
            'name': 'Electrical',
            'description': 'Professional electrical services for repairs, installations, and safety inspections.',
            'category': 'Maintenance',
            'base_price': 80.00
        },
        {
            'name': 'Gardening',
            'description': 'Complete garden maintenance including lawn care, pruning, and landscaping services.',
            'category': 'Outdoor',
            'base_price': 45.00
        }
    ]
    
    for service_data in services:
        if not Service.query.filter_by(name=service_data['name']).first():
            service = Service(**service_data)
            db.session.add(service)
    
    # Add a sample service provider if they don't exist
    provider_email = 'provider@example.com'
    if not User.query.filter_by(email=provider_email).first():
        provider_user = User(
            email=provider_email,
            password_hash=generate_password_hash('provider123'),
            name='John Provider',
            user_type='provider'
        )
        db.session.add(provider_user)
        db.session.commit()
        
        provider = ServiceProvider(
            user_id=provider_user.id,
            service_type='House Cleaning',
            description='Experienced cleaner with 5 years of professional experience',
            experience=5,
            hourly_rate=30.00,
            availability=True
        )
        db.session.add(provider)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@homeservices.com').first()
        if not admin:
            admin = User(
                email='admin@homeservices.com',
                password_hash=generate_password_hash('admin123'),
                name='Admin',
                user_type='admin'
            )
            db.session.add(admin)
            db.session.commit()
        
        # Initialize sample data
        init_sample_data()

    app.run(debug=True)
