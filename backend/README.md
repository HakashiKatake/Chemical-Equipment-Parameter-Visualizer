---
title: Equipment Visualizer API
emoji: 🔧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Chemical Equipment Parameter Visualizer API

Django REST API for chemical equipment data analysis and visualization.

## Features

- CSV file upload and validation
- Equipment data analytics (statistics, histograms, scatter plots)
- PDF report generation
- User authentication with JWT tokens
- Auto-cleanup of old datasets (keeps last 5 per user)

## API Documentation

Visit `/api/schema/swagger-ui/` for interactive API documentation.

## Environment Variables

Required environment variables:
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
