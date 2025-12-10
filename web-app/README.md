# 🦎 Reptile Tracker Web App

Mobile-friendly web application for tracking reptile care, feeding schedules, and shed records.

## Features

- 📱 **Mobile-Responsive Design** - Works perfectly on phones, tablets, and desktops
- 🦎 **Reptile Management** - Track multiple reptiles with photos and detailed info
- 🍖 **Feeding Logs** - Record feeding schedules and success rates
- 🔄 **Shed Tracking** - Monitor shed cycles and completeness
- 📊 **Dashboard Stats** - View quick statistics at a glance
- 📷 **Photo Upload** - Add photos to each reptile's profile

## Quick Start

### Local Development

1. Install dependencies:
```bash
cd web-app
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser to `http://localhost:5000`

### Deploy to Railway (Free)

Railway offers free hosting for small projects:

1. Create account at [railway.app](https://railway.app)

2. Install Railway CLI:
```bash
npm install -g @railway/cli
```

3. Login and deploy:
```bash
cd web-app
railway login
railway init
railway up
```

4. Your app will be live at a Railway URL!

### Deploy to PythonAnywhere (Free)

PythonAnywhere offers free Python web hosting:

1. Create account at [pythonanywhere.com](https://www.pythonanywhere.com)

2. Upload your files via the Files tab

3. Create a new web app:
   - Choose Flask
   - Python 3.10
   - Point to your `app.py`

4. Install requirements in a Bash console:
```bash
pip install --user -r requirements.txt
```

5. Reload your web app

### Deploy to Render (Free)

Render offers free web service hosting:

1. Create account at [render.com](https://render.com)

2. Connect your GitHub repository

3. Create a new Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. Your app will be deployed automatically!

## Project Structure

```
web-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # For deployment
├── static/
│   ├── css/
│   │   └── style.css     # Mobile-responsive styles
│   └── uploads/          # User-uploaded images
└── templates/
    ├── base.html         # Base template
    ├── dashboard.html    # Main dashboard
    ├── reptile_form.html # Add/edit reptile
    ├── reptile_details.html
    ├── feeding_logs.html
    ├── feeding_form.html
    ├── shed_records.html
    └── shed_form.html
```

## Database

The app uses SQLite database (`reptile_tracker.db`) which is automatically created on first run. The database module is shared with the desktop version.

## Mobile Access

Once deployed, you can access your reptile tracker from any device:
- Add the web app to your phone's home screen for app-like experience
- All features work on mobile browsers
- Touch-friendly interface with large buttons
- Responsive design adapts to any screen size

## Security Notes

**Important**: This is a single-user application without authentication. For production use:

1. Change the `SECRET_KEY` in `app.py`
2. Consider adding user authentication
3. Use environment variables for sensitive data
4. Enable HTTPS on your hosting platform

## Support

For issues or questions, please open an issue on GitHub.