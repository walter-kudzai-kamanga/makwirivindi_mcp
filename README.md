Makwirivindi – AI Data Analytics MCP

Makwirivindi is a web-based platform that allows companies to upload datasets, analyze them using automated data processing, and visualize insights on a branded, dynamic dashboard. Each company can upload its logo, and the dashboard automatically adapts its color scheme to match the company’s branding.

Features

File Upload & Management

Upload multiple datasets at once.

Preview uploaded files in a table with rows, columns, numeric, and categorical columns.

Delete mistakenly uploaded files before analysis.

Dataset Analysis

Automatically analyzes datasets for structure, column types, and statistical summaries.

Displays a loading animation during analysis.

Dynamic Dashboard

Branded for each company using uploaded logo and dominant color extraction.

Displays:

Charts (bar, line, pie) with colors matching the company logo.

AI insights dynamically generated from dataset analysis.

Predictions or forecasts based on the dataset.

Table of analyzed dataset metrics (rows, columns, numeric/categorical columns).

Multi-Company Support

Each company has a separate dashboard.

Color scheme and styling automatically adapt to the company’s uploaded logo.

Frontend

Responsive and modern UI using Bootstrap.

Real-time updates with JavaScript for file table and analysis loader.

Project Structure
makwirivindi/
├── main.py                # FastAPI entry point
├── routers/
│   ├── upload_router.py   # Handles file uploads
│   ├── analyze_router.py  # Handles dataset analysis
│   └── dashboard_router.py# Serves dashboard pages
├── services/
│   └── analysis_service.py# Data analysis functions
├── templates/
│   ├── base.html
│   ├── upload.html        # File upload interface
│   └── dashboard.html     # Dashboard template
├── static/
│   ├── css/style.css
│   └── js/dashboard.js
├── uploads/               # Stores uploaded datasets and company logos
├── venv/                  # Python virtual environment
└── README.md
Installation & Setup

Clone the repository

git clone <repository_url>
cd makwirivindi

Create virtual environment & activate

python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

Run the server

uvicorn main:app --reload

Access the app

Upload page: http://127.0.0.1:8000/upload/

Dashboard page: http://127.0.0.1:8000/dashboard/

Usage

Upload Files

Enter your company name and upload the company logo.

Select one or more CSV datasets to upload.

View the table of files to analyze. Delete any file if needed.

Analyze

Click Analyze Files.

A loader will show while analysis is running.

After analysis, the dashboard will automatically open with charts, insights, and predictions.

Dashboard

Displays analysis results with charts and tables.

Color scheme and logo dynamically adapt to your company branding.

Folder Notes

uploads/: Stores all uploaded datasets and company logos.

static/css/: Contains custom CSS (style.css).

static/js/: Contains frontend logic (dashboard.js).

services/analysis_service.py: Contains dataset analysis logic.

templates/: Jinja2 HTML templates.

Dependencies

Python 3.11+

FastAPI

Uvicorn

Jinja2

Pillow (for logo color extraction)

Pandas (for dataset analysis)

Bootstrap 5 (for styling)

Chart.js (for charts)

Future Improvements

Support multiple file formats (Excel, JSON).

More advanced AI insights and predictions.

User authentication for multi-company security.

Export analysis reports as PDF or Excel.

License

This project is open-source and free to use under the MIT License.
