# Chemical Equipment Parameter Visualizer

A hybrid **Web + Desktop** application for visualizing chemical equipment parameters from CSV data.

## Architecture

- **Backend**: Django + Django REST Framework (shared by both clients)
- **Web Frontend**: React + Chart.js
- **Desktop Frontend**: PyQt5 + Matplotlib
- **Database**: SQLite

## Key Features

✅ **Strict CSV Normalization** - Handles headers with spaces, case-insensitive matching, type normalization  
✅ **Server-Side Analytics** - All computations done in backend using pandas  
✅ **Token-Based Auth** - Secure authentication for both clients  
✅ **Dataset History** - Automatic maintenance of last 5 datasets per user  
✅ **Interactive Charts** - Histogram, scatter plots, type distributions  
✅ **PDF Reports** - Server-generated reports with charts and statistics  
✅ **Data Table** - Sortable, filterable equipment data  
✅ **OpenAPI Docs** - Auto-generated API documentation

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
│   │   ├── reports.py      # PDF generation
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
pip install -r requirements.txt

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

### Manual Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Upload valid CSV
- [ ] Upload invalid CSV (missing column, empty field, non-numeric value)
- [ ] View dataset list (should show last 5)
- [ ] Select dataset and view analytics
- [ ] Check summary statistics
- [ ] View all three charts
- [ ] Sort and filter data table
- [ ] Download PDF report
- [ ] Upload 6th dataset (oldest should be auto-deleted)

## Database Management

### Dataset Limit
- System automatically maintains last 5 datasets per user
- Oldest dataset is deleted when 6th is uploaded
- Cascading delete removes associated equipment records

### Admin Interface

Access Django admin at: `http://localhost:8000/admin/`

- View all datasets
- View equipment records
- Manage users

## Production Deployment Notes

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

### Why Single Backend?
- Consistency across clients
- Single source of truth for analytics
- Easier maintenance
- Shared authentication & authorization

### Why Server-Side Analytics?
- Consistency in calculations
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
