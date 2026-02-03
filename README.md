# Chemical Equipment Parameter Visualizer

A hybrid **Web + Desktop** application for visualizing chemical equipment parameters from CSV data.

**🚀 Live Demo**: https://hakashikatake-equipment-visualizer.hf.space/api/docs/

## Architecture

- **Backend**: Django + Django REST Framework (shared by both clients)
- **Web Frontend**: React + Chart.js
- **Desktop Frontend**: PyQt5 + Matplotlib
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Hugging Face Spaces (backend) + Vercel (frontend)

## Key Features

✅ **Strict CSV Normalization** - Handles headers with spaces, case-insensitive matching, type normalization  
✅ **Server-Side Analytics** - All computations done in backend using pandas  
✅ **Token-Based Auth** - Secure authentication for both clients  
✅ **Dataset History** - Automatic maintenance of last 5 datasets per user  
✅ **Interactive Charts** - Histogram, scatter plots, type distributions  
✅ **PDF Reports** - Server-generated reports with charts and statistics  
✅ **Data Table** - Sortable, filterable equipment data  
✅ **OpenAPI Docs** - Auto-generated API documentation  
✅ **Health Check** - Monitoring endpoint for uptime services  
✅ **Production Ready** - Docker deployment with PostgreSQL support

## Project Structure

```
wba/
├── backend/                 # Django backend
│   ├── config/             # Django settings
│   ├── equipment/          # Main app
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── csv_normalizer.py  # CSV validation & normalization
│   │   ├── analytics.py    # Analytics engine
│   │   Dockerfile          # Docker configuration
│   ├── README.md           # HF Space metadata
│   ├── ├── reports.py      # PDF generation
│   │   └── serializers.py  # DRF serializers
│   ├── manage.py
│   └── requirements.txt
│
├── frontend-web/           # React web app
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── api.js          # API client
│   │   └── App.js
│   ├── public/
│   └── package.json
│
├── frontend-desktop/       # PyQt5 desktop app
│   ├── main.py            # Main application
│   ├── api_client.py      # API client
│   └── requirements.txt
├── DEPLOYMENT.md          # Detailed deployment guide
├── DEPLOYMENT_CHECKLIST.md # Quick deployment checklist
│
├── sample_equipment_data.csv  # Sample data
└── README.md              # This file
```

## Installation & Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
piCreate .env file (optional for development)
cat > config/.env << EOF
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
EOF

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

Backend will run at: `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs/`  
Health Check: `http://localhost:8000/api/v1/health

API Documentation: `http://localhost:8000/api/docs/`

### Web Frontend Setup

```bash
cd frontend-web

# Install dependencies
npm install

# Start development server
npm start
```

Web app will run at: `http://localhost:3000`

### Desktop Frontend Setup

```bash
cd frontend-desktop

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## CSV Format

The application expects CSV files with the following headers:

```
Equipment Name, Type, Flowrate, Pressure, Temperature
```

### Requirements

- Headers can have spaces and any casing
- Column order doesn't matter
- All fields are required
- Flowrate, Pressure, Temperature must be numeric

### Units (Documented in UI and Reports)

- **Flowrate**: m³/h
- **Pressure**: bar
- **Temperature**: °C

### Example

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120,5.2,110
Compressor-1,Compressor,95,8.4,95
Valve-1,Valve,60,4.1,105
```

A sample file `sample_equipment_data.csv` is provided.

## Normalization Rules

The backend implements a strict normalization layer:

### Header Normalization
- Case-insensitive matching
- Leading/trailing whitespace trimmed
- Maps external headers to internal field names:
  - `Equipment Name` → `equipment_name`
  - `Type` → `type`
  - `Flowrate` → `flowrate`
  - `Pressure` → `pressure`
  - `Temperature` → `temperature`

### Type Normalization
- Converted to lowercase
- Spaces replaced with underscores
- Example: `Heat Exchanger` → `heat_exchanger`

## API Endpoints


### Health & Monitoring
- `GET /api/v1/health/` - Health check endpoint (no auth required)
### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/register/` - Register

### Datasets
- `GET /api/v1/datasets/` - List user's datasets
- `POST /api/v1/datasets/upload/` - Upload CSV
- `GET /api/v1/datasets/{id}/` - Get dataset details
- `GET /api/v1/datasets/{id}/analytics/` - Get analytics
- `GET /api/v1/datasets/{id}/report/` - Download PDF report

## Analytics

All analytics are computed server-side:

### Global Summary
- Total equipment count
- Average flowrate, pressure, temperature
- Min/max values for each parameter

### Distributions
- Equipment count by type
- Histogram bins for flowrate
- Scatter data (pressure vs temperature)

### Chart-Ready Payloads
Frontend receives pre-computed data for visualization - no client-side computation needed.

## UI/UX Guidelines

Both web and desktop UIs follow these principles:

- **Flat design** - No gradients
- **Solid colors** - Clear, accessible color scheme
- **Minimal shadows** - Subtle depth where needed
- **Clear typography** - Readable text hierarchy
- **Responsive** - Web app adapts to screen sizes

## Validation & Error Handling

### CSV Upload Validation

Rejects uploads if:
- Required column is missing
- Any field is empty
- Numeric field cannot be parsed as float
- File size exceeds limit (10 MB)

### Error Response Format

```json
{
  "errors": [
    {
      "row": 6,
      "column": "pressure",
      "error": "Expected numeric value"
    }
  ]
}
```

## Testing

### Backend Tests

```bash
cd backend
python manage.py test equipment
```

## Database Management

### Dataset Limit

This application is production-ready and can be deployed to:
- **Backend**: Hugging Face Spaces (Docker)
- **Frontend**: Vercel
- **Database**: Neon PostgreSQL

### Quick Deployment

**Backend to Hugging Face:**
```bash
# Add HF Space as remote
git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/equipment-visualizer-api

# Deploy backend folder only
git subtree split --prefix backend -b backend-deploy
git push hf backend-deploy:main --force
git branch -D backend-deploy
```

**Frontend to Vercel:**
```bash
cd frontend-web

# Update .env.production with your backend URL
echo "REACT_APP_API_URL=https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/v1" > .env.production

# Deploy
npm install .7
- Django REST Framework 3.14.0
- pandas 2.1.3
- matplotlib 3.8.2
- reportlab 4.0.7
- drf-spectacular 0.27.0 (OpenAPI)
- gunicorn 25.0.1 (production)
- whitenoise 6.11.0 (static files)
- psycopg2-binary 2.9.11 (PostgreSQL)
- dj-database-url 3.1.0

### Web Frontend
- React 18
- Chart.js 4
- axios
- react-router-dom

### Desktop Frontend
- PyQt5 5.15.10
- matplotlib 3.10.8
- requests 2.32.5

### Infrastructure
- Docker (containerization)
- Hugging Face Spaces (backend hosting)
- Vercel (frontend hosting)
- Neon (PostgreSQL hosting)
- cron-job.org (uptime monitoring)
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Keep Backend Alive (Important!)

Hugging Face Spaces sleep after inactivity. Use **cron-job.org** to keep it alive:

1. Go to https for Development?
- Simple setup for development
- Zero configuration
- Adequate for moderate usage
- Easy to switch to PostgreSQL for production

### Why PostgreSQL for Production?
- Better concurrency handling
- Robust backup and recovery
- Scalable for large datasets
- Industry standard for web applications

### Why Hugging Face Spaces?
- Free hosting for open-source projects
- Docker support for full-stack apps
- Easy deployment with git
- Built-in SSL and CDN

### Why Docker?
- Consistent environment across dev/prod
- Easy dependency management
- Simplified deployment
- Container isolation and security

### Detailed Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:
- Neon PostgreSQL setup

### Production deployment issues
- **HF Space not responding**: Check build logs in Space dashboard
- **404 on all endpoints**: Verify `app_port: 7860` in backend/README.md
- **Database connection failed**: Check DATABASE_URL environment variable
- **CORS errors**: Update CORS_ALLOWED_ORIGINS with actual frontend URL
- **Space goes to sleep**: Set up cron-job.org health check pings

### Health check not working
- Ensure backend is deployed with latest code
- Visit `/api/v1/health/` (not `/health/`)
- Check Space logs for errors
- Verify endpoint returns: `{"status": "ok", "message": "Equipment Visualizer API is running"}`
- Docker configuration
- CI/CD pipeline setup
- Troubleshooting guide

Quick reference: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

Before deploying to production:

1. **Change SECRET_KEY** in `config/settings.py`
2. **Set DEBUG = False**
3. **Configure ALLOWED_HOSTS**
4. **Use PostgreSQL** instead of SQLite
5. **Set up static file serving** (WhiteNoise or CDN)
6. **Configure CORS** properly (remove CORS_ALLOW_ALL_ORIGINS)
7. **Use environment variables** for sensitive settings
8. **Set up HTTPS**
9. **Configure file upload limits** based on needs
10. **Set up logging** and monitoring

## Technology Stack

### Backend
- Django 4.2
- Django REST Framework 3.14
- pandas 2.1
- matplotlib 3.8
- reportlab 4.0
- drf-spectacular (OpenAPI)

### Web Frontend
- React 18
- Chart.js 4
- axios
- react-router-dom

### Desktop Frontend
- PyQt5
- matplotlib
- requests

## Design Decisions
Useful Links

### Development
- Local API: `http://localhost:8000/api/v1/`
- API Documentation: `http://localhost:8000/api/docs/`
- Django Admin: `http://localhost:8000/admin/`
- Health Check: `http://localhost:8000/api/v1/health/`
- Web App: `http://localhost:3000`

### Production
- Backend API: `https://hakashikatake-equipment-visualizer.hf.space`
- API Documentation: `https://hakashikatake-equipment-visualizer.hf.space/api/docs/`
- Health Check: `https://hakashikatake-equipment-visualizer.hf.space/api/v1/health/`
- Hugging Face Space: `https://huggingface.co/spaces/HakashiKatake/equipment-visualizer`

### External Services
- Neon Console: `https://console.neon.tech/`
- Vercel Dashboard: `https://vercel.com/dashboard`
- Cron Job Dashboard: `https://cron-job.org/en/members/jobs/`

## Documentation

- **README.md** (this file) - Overview and quick start
- **DEPLOYMENT.md** - Comprehensive deployment guide
- **DEPLOYMENT_CHECKLIST.md** - Quick deployment reference
- **prompt.md** - Original project requirements

## Support & Resources

- **API Schema**: Interactive API documentation at `/api/docs/`
- **OpenAPI Spec**: Raw OpenAPI schema at `/api/schema/`
- **Django Admin**: Database management at `/admin/`
- **Health Status**: Service health at `/api/v1/health/`

## License

This project is created for educational/evaluation purposes.

---

**Built with ❤️ using Django, React, and PyQt5**
- Better performance for large datasets
- Reduced client complexity
- Easier to update algorithms

### Why SQLite?
- Simple setup for development
- Zero configuration
- Adequate for moderate usage
- Easy to switch to PostgreSQL for production

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Ensure migrations are applied
- Verify virtual environment is activated

### Web app can't connect to backend
- Ensure backend is running at `http://localhost:8000`
- Check CORS settings in Django
- Verify proxy setting in `package.json`

### Desktop app login fails
- Ensure backend is running
- Check API_BASE_URL in `api_client.py`
- Verify firewall settings

### CSV upload fails
- Check file format matches specification
- Verify all required columns present
- Ensure numeric fields contain valid numbers
- Check file size (must be under 10 MB)

## License

This project is created for educational/evaluation purposes.

## Contact & Support

For questions or issues, please check:
- API Documentation: `http://localhost:8000/api/docs/`
- Django Admin: `http://localhost:8000/admin/`
