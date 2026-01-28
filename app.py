"""
Dom Creator Dashboard - Social Media Post Scheduler & Analytics
A personal Flask app to schedule and track content across multiple platforms.

Database Note: Currently using SQLite for simplicity. To swap to Postgres (Render):
  1. Install psycopg2: pip install psycopg2-binary
  2. Change DATABASE_URL in config.py to: postgresql://user:pass@localhost/dbname
  3. For Microsoft 365 integration (future): Replace with Azure SQL or Graph API calls.
     See comments marked [MS365_INTEGRATION] for integration points.
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# ============== DATABASE CONFIGURATION ==============
# For local dev: SQLite (app.db in root)
# For Render: Set DATABASE_URL env var to postgresql://...
# [MS365_INTEGRATION] Future: Could use Azure SQL by setting DATABASE_URL env var
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# Fix postgres:// to postgresql:// for newer SQLAlchemy
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ============== DATABASE MODELS ==============

class ScheduledPost(db.Model):
    """
    Model for scheduled social media posts.
    Each post can be scheduled for one platform at a time.
    [MS365_INTEGRATION] Future: Could add OneNote or SharePoint sync via Graph API.
    """
    __tablename__ = 'scheduled_posts'

    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(
        db.String(20),
        nullable=False,
        index=True,
        comment="Platform: tiktok, youtube, instagram, facebook, linkedin, threads"
    )
    caption = db.Column(db.Text, nullable=False, comment="Post caption/description")
    scheduled_datetime = db.Column(db.DateTime, nullable=False, index=True, comment="When to post")
    link_or_asset_note = db.Column(db.Text, nullable=True, comment="Optional link or file reference")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="Creation timestamp")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_posted = db.Column(db.Boolean, default=False, comment="True if successfully posted")

    def to_dict(self):
        """Convert model to dict for JSON responses."""
        return {
            'id': self.id,
            'platform': self.platform,
            'caption': self.caption,
            'scheduled_datetime': self.scheduled_datetime.isoformat(),
            'link_or_asset_note': self.link_or_asset_note,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_posted': self.is_posted
        }

    def __repr__(self):
        return f'<ScheduledPost {self.id} {self.platform} {self.scheduled_datetime}>'


# ============== ANALYTICS DATA (PLACEHOLDER) ==============
def get_analytics_data():
    """
    Fetch analytics for dashboard.
    [MS365_INTEGRATION] Future: Replace this function with:
      - Real TikTok API calls (using API key stored in env)
      - Real YouTube API calls
      - Real Instagram API calls (via Facebook Graph API)
      - Real Facebook API calls
      - Real LinkedIn API calls
      - Real Threads API calls (when available)
    
    Currently returns mocked data for UI development and testing.
    Each platform API should cache results to avoid rate limits.
    """
    PLATFORMS = {
        'tiktok': {'name': 'TikTok', 'color': '#000000'},
        'youtube': {'name': 'YouTube', 'color': '#FF0000'},
        'instagram': {'name': 'Instagram', 'color': '#E1306C'},
        'facebook': {'name': 'Facebook', 'color': '#1877F2'},
        'linkedin': {'name': 'LinkedIn', 'color': '#0A66C2'},
        'threads': {'name': 'Threads', 'color': '#333333'}
    }

    analytics = {}
    for platform_key, platform_info in PLATFORMS.items():
        # TODO: Replace with real API calls for each platform
        analytics[platform_key] = {
            'name': platform_info['name'],
            'color': platform_info['color'],
            'followers': {
                'tiktok': 15000,
                'youtube': 8500,
                'instagram': 12000,
                'facebook': 5000,
                'linkedin': 3200,
                'threads': 2100
            }.get(platform_key, 0),
            'views_7d': {
                'tiktok': 125000,
                'youtube': 45000,
                'instagram': 38000,
                'facebook': 12000,
                'linkedin': 5600,
                'threads': 8900
            }.get(platform_key, 0),
            'posts_scheduled': ScheduledPost.query.filter_by(platform=platform_key, is_posted=False).count(),
            'top_posts': [
                # Real API would fetch actual top posts
                {
                    'title': f'Top post #{i+1}',
                    'engagement': [450, 380, 290, 210, 150][i],
                    'date': '2024-01-20'
                } for i in range(3)
            ]
        }
    return analytics


# ============== ROUTES ==============

@app.route('/')
def index():
    """Home page - redirects to scheduler."""
    return redirect(url_for('scheduler'))


@app.route('/scheduler')
def scheduler():
    """Scheduler page - view and manage scheduled posts."""
    scheduled_posts = ScheduledPost.query.filter_by(is_posted=False).order_by(
        ScheduledPost.scheduled_datetime
    ).all()
    
    # Platform color mapping
    platform_colors = {
        'tiktok': '#000000',
        'youtube': '#FF0000',
        'instagram': '#E1306C',
        'facebook': '#1877F2',
        'linkedin': '#0A66C2',
        'threads': '#333333'
    }
    
    return render_template(
        'scheduler.html',
        posts=scheduled_posts,
        platform_colors=platform_colors,
        platforms=['tiktok', 'youtube', 'instagram', 'facebook', 'linkedin', 'threads']
    )


@app.route('/analytics')
def analytics():
    """Analytics dashboard page."""
    analytics_data = get_analytics_data()
    return render_template('analytics.html', analytics=analytics_data)


# ============== API ENDPOINTS (for AJAX requests) ==============

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Fetch all unposted scheduled posts as JSON."""
    posts = ScheduledPost.query.filter_by(is_posted=False).order_by(
        ScheduledPost.scheduled_datetime
    ).all()
    return jsonify([post.to_dict() for post in posts])


@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new scheduled post."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['platform', 'caption', 'scheduled_datetime']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Parse datetime
        try:
            scheduled_dt = datetime.fromisoformat(data['scheduled_datetime'])
        except ValueError:
            return jsonify({'error': 'Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:mm'}), 400
        
        # Create post
        post = ScheduledPost(
            platform=data['platform'].lower(),
            caption=data['caption'],
            scheduled_datetime=scheduled_dt,
            link_or_asset_note=data.get('link_or_asset_note', '')
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify(post.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a scheduled post."""
    try:
        post = ScheduledPost.query.get_or_404(post_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'platform' in data:
            post.platform = data['platform'].lower()
        if 'caption' in data:
            post.caption = data['caption']
        if 'scheduled_datetime' in data:
            try:
                post.scheduled_datetime = datetime.fromisoformat(data['scheduled_datetime'])
            except ValueError:
                return jsonify({'error': 'Invalid datetime format'}), 400
        if 'link_or_asset_note' in data:
            post.link_or_asset_note = data['link_or_asset_note']
        
        db.session.commit()
        return jsonify(post.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a scheduled post."""
    try:
        post = ScheduledPost.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return render_template('error.html', error='Server error'), 500


# ============== DEVELOPMENT ==============

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # In production (Render), Flask runs via Gunicorn with debug=False
    # This is only for local development
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER') == 'true'
    app.run(debug=not is_production, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
