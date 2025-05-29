# Household Services Marketplace

A web application for connecting users with professional household service providers. The platform supports multiple user types, service bookings, and includes an integrated chatbot for customer support.

## Features

- User Authentication (Regular Users, Service Providers, Admin)
- Service Provider Profiles
- Service Booking System
- Admin Dashboard with Statistics
- Real-time Chat Support
- Responsive Design

## Tech Stack

- Backend: Python Flask
- Database: SQLite with SQLAlchemy
- Frontend: HTML, Bootstrap CSS, JavaScript
- Authentication: Flask-Login

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd household-services
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Admin Credentials

- Email: admin@homeservices.com
- Password: admin123

## Project Structure

```
household-services/
├── app.py                  # Main application file
├── requirements.txt        # Project dependencies
├── static/                # Static files
│   ├── css/              # CSS files
│   ├── js/               # JavaScript files
│   └── images/           # Image assets
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── login.html       # Login page
│   ├── register.html    # Registration page
│   ├── user_dashboard.html
│   ├── provider_dashboard.html
│   └── admin_dashboard.html
└── README.md
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
