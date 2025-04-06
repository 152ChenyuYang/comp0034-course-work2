1.Introduction
This project is a web-based local housing dashboard developed using Flask. Its purpose is to provide users with an interactive interface to explore affordable housing data and waitlist information by region for different years.


2.Structure
comp0034cw2/
│
├──coursework1                          # SQLite Database
├── coursework2_flask/                  # Main application package
│   ├── flask_app/                      # Application logic and views
│   │   ├── templates/                  # All HTML Jinja templates
│   │   │   ├── base.html               # Layout template
│   │   │   ├── area_chart.html         # Single chart template
│   │   │   ├── tables.html             # Table list page showing all database tables
│   │   │   ├── area.html               # Area list view with cards linking to details and charts
│   │   │   ├── data.html               # Generic table view with pagination and optional search
│   │   │   ├── chart.html              # Single chart template
│   │   │   ├── home.html               # Homepage of the dashboard
│   │   │   ├── chart_area_dual.html    # Dual chart for housing + waiting list
│   │   │   ├── area_detail.html        # Area-specific details (tables)
│   │   │   ├── news.html               # Hacker News feed
│   │   │   └── 404.html                # Custom not-found page
│   │   ├── routes.py                   # All route/view functions
│   │   └── __init__.py                 # Factory method to create app
│   │
│   ├── tests/                          # Pytest test cases
│   │   ├── test_routes.py              # Route functionality tests
│   │   └── conftest.py                 # Shared test fixtures
│   │
│   ├── requirements.txt                # Project dependencies
│   └── run.py                          # Entrypoint to run the Flask app
│
└── venv/                               # Virtual environment (excluded from version control)


3.
# Create a virtual environment 
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\Activate

# Install Python dependencies required for the project
pip install -r requirements.txt

# Run the application
python run.py

# Run the test
python -m pytest coursework2_flask/tests