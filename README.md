# 🎬 Dom Creator Dashboard

A personal "mini-Metricool" web app for scheduling social media posts and tracking analytics across multiple platforms. Built with Flask, designed for mobile, and ready to deploy on Render.

## Features

### ✅ Post Scheduler
- Schedule posts for TikTok, YouTube, Instagram, Facebook, LinkedIn, and Threads
- Color-coded by platform throughout the UI
- List and calendar views for easy planning
- Simple form to add posts with caption, datetime, and optional link/asset notes

### 📊 Analytics Dashboard
- Platform-specific metrics (followers, 7-day views, top posts)
- Currently mocked for UI development
- Easy to plug in real API calls (see code comments for integration points)
- References to official platform APIs

### 📱 Responsive Mobile Design
- Mobile-first CSS
- Touch-friendly buttons and forms
- Works on all devices (phones, tablets, desktops)
- Platform legend for easy visual scanning

### 🔧 Tech Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (local) / PostgreSQL (Render)
- **Frontend**: HTML, CSS, JavaScript (vanilla, no heavy frameworks)
- **Deployment**: Render (free tier compatible)

---

## Project Structure

```
Dom_Creator_Dashboard/
├── app.py                    # Main Flask app + database models
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment config
├── render.yaml               # Render service definition
├── .env.example              # Environment variable template
├── README.md                 # This file
│
├── templates/
│   ├── base.html             # Base template with navbar
│   ├── scheduler.html        # Post scheduler page
│   ├── analytics.html        # Analytics dashboard
│   └── error.html            # Error page
│
└── static/
    ├── css/
    │   └── style.css         # Main stylesheet (mobile-first)
    └── js/
        └── (future custom JS)
```

---

## Installation & Local Setup

### Prerequisites
- Python 3.9+ installed
- pip package manager

### 1. Clone or Create Project
```bash
cd Dom_Creator_Dashboard
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and set:
# - FLASK_ENV=development
# - FLASK_DEBUG=True
# - SECRET_KEY=any-random-string-for-dev
```

### 5. Initialize Database
```bash
# Create database and tables
flask db init    # (if migrations/ doesn't exist)
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Run Locally
```bash
python app.py
```

Visit **http://localhost:5000** in your browser.

---

## Deploying to Render

### Prerequisites
- GitHub account
- Render account (free tier available)

### Step-by-Step Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Mini-Metricool dashboard"
   git remote add origin https://github.com/YOUR_USERNAME/Dom_Creator_Dashboard.git
   git push -u origin main
   ```

2. **Create PostgreSQL Database on Render**
   - Go to [render.com](https://render.com)
   - Sign up / Log in
   - Click "New +" → "PostgreSQL"
   - Name: `dom-creator-db`
   - Region: Pick closest to you
   - PostgreSQL Version: Latest
   - Click "Create Database"
   - Copy the connection string (DATABASE_URL)

3. **Deploy Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `dom-creator-dashboard`
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt && flask db upgrade`
   - Start command: `gunicorn app:app`
   - Region: Same as database
   - Plan: Free

4. **Set Environment Variables**
   - In Render dashboard, go to your web service
   - Click "Environment"
   - Add:
     ```
     FLASK_ENV = production
     SECRET_KEY = <generate via: python -c "import secrets; print(secrets.token_hex(32))">
     DATABASE_URL = <paste from PostgreSQL database>
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (check logs)
   - Your app is live! URL shown in Render dashboard

### Notes on Render Free Tier
- Web service spins down after 15 minutes of inactivity (will restart on request)
- PostgreSQL database has storage limits (~100MB free)
- Suitable for personal use or low-traffic projects
- Upgrade to paid if you need always-on service

---

## Database & Data Storage

### Current Setup
- **Local Development**: SQLite (`app.db`)
- **Production (Render)**: PostgreSQL

### To Swap Database Later

#### Option 1: Azure SQL (Microsoft 365 Integration)
1. Create Azure SQL Database
2. Update `DATABASE_URL` env var:
   ```
   DATABASE_URL=mssql+pyodbc://<user>:<password>@<server>.database.windows.net/<database>?driver=ODBC+Driver+17+for+SQL+Server
   ```
3. Install: `pip install pyodbc`

#### Option 2: SharePoint/Dataverse (Microsoft 365 Sync)
- See comments in `app.py` marked `[MS365_INTEGRATION]`
- Would require Azure AD authentication
- Replace database queries with Microsoft Graph API calls
- Dataverse integration guide: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/

### Code Integration Points for DB Swaps
Search `app.py` for `[MS365_INTEGRATION]` comments to see where database calls can be replaced.

---

## API Integration (Analytics & Real Data)

Currently, all analytics data is **mocked** for UI development.

### To Add Real API Calls

See the `get_analytics_data()` function in `app.py` for comments on each platform.

#### Platform APIs
- **TikTok**: https://developers.tiktok.com
- **YouTube**: https://developers.google.com/youtube/v3
- **Instagram/Facebook**: https://developers.facebook.com (Meta Graph API)
- **LinkedIn**: https://www.linkedin.com/developers
- **Threads**: API availability pending

#### Implementation Steps
1. Get API keys from each platform
2. Store keys in `.env` file (never commit!)
3. Replace mock data calls in `get_analytics_data()` with real API requests
4. Add caching (e.g., Redis) to avoid rate limits
5. Add error handling and retry logic

#### Example (YouTube API)
```python
# In get_analytics_data()
import requests

def get_youtube_metrics():
    api_key = os.getenv('YOUTUBE_API_KEY')
    # Call YouTube Data API v3
    response = requests.get(
        'https://www.googleapis.com/youtube/v3/channels',
        params={
            'part': 'statistics',
            'mine': True,
            'key': api_key
        }
    )
    return response.json()
```

---

## Color Scheme (Platform Branding)

Used consistently throughout the UI:

| Platform  | Color       | Hex Code  | Usage |
|-----------|-------------|-----------|-------|
| TikTok    | Black       | #000000   | Posts, badges, accents |
| YouTube   | Red         | #FF0000   | Posts, badges, accents |
| Instagram | Pink        | #E1306C   | Posts, badges, accents |
| Facebook  | Blue        | #1877F2   | Posts, badges, accents |
| LinkedIn  | Prof. Blue  | #0A66C2   | Posts, badges, accents |
| Threads   | Dark Gray   | #333333   | Posts, badges, accents |

View the **platform legend** on the right side of the dashboard (mobile: bottom section).

---

## Troubleshooting

### Issue: Database locked (SQLite)
**Solution**: If using SQLite locally, close other connections. Switch to PostgreSQL in production.

### Issue: "No module named 'flask'"
**Solution**: Activate virtual environment and run `pip install -r requirements.txt`

### Issue: Port 5000 already in use
**Solution**: Change port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Issue: Render deployment fails
**Check**:
1. `requirements.txt` installed successfully?
2. `Procfile` and `render.yaml` correct?
3. Environment variables set in Render dashboard?
4. Database connection string valid?

View build logs in Render dashboard for detailed errors.

---

## Future Enhancements

- [ ] User authentication (for multi-user support)
- [ ] Real API integrations for each platform
- [ ] Post scheduling/auto-publish integration
- [ ] Advanced analytics (charts, trends)
- [ ] Content calendar view (month/week)
- [ ] Draft/approved post workflow
- [ ] Asset upload and management
- [ ] Hashtag and mention suggestions
- [ ] Team collaboration features

---

## License

Personal project. Use as needed.

---

## Support & Questions

- **Flask Docs**: https://flask.palletsprojects.com
- **Flask-SQLAlchemy**: https://flask-sqlalchemy.palletsprojects.com
- **Render Docs**: https://render.com/docs
- **Mobile-first CSS**: https://www.w3schools.com/css/css_rwd_intro.asp

---

**Built with ❤️ for content creators.**
