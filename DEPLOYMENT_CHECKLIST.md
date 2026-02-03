# Quick Deployment Checklist

## Pre-Deployment

### 1. Create Neon Database
- [ ] Sign up at https://console.neon.tech/
- [ ] Create new project: `equipment-visualizer`
- [ ] Copy connection string
- [ ] Test connection (optional)

### 2. Prepare Backend for Hugging Face
- [x] Install production dependencies (psycopg2-binary, gunicorn, whitenoise, dj-database-url)
- [x] Update requirements.txt
- [x] Create Dockerfile
- [x] Create README.md for HF Space
- [x] Update settings.py for production

### 3. Prepare Frontend for Vercel
- [x] Create vercel.json
- [x] Create .env.production
- [x] Update api.js to use environment variable

## Deployment Steps

### Backend to Hugging Face

1. **Generate Secret Key**
```bash
cd backend
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output.

2. **Create Hugging Face Space**
- Go to https://huggingface.co/spaces
- Click "Create new Space"
- Name: `equipment-visualizer-api`
- SDK: Docker
- Visibility: Public

3. **Add Environment Variables in Space Settings**
```
SECRET_KEY=<your-generated-key>
DATABASE_URL=<your-neon-connection-string>
DEBUG=False
ALLOWED_HOSTS=.hf.space,.vercel.app
CORS_ALLOWED_ORIGINS=https://your-app-name.vercel.app
```

4. **Push Backend Code to Hugging Face**

**Important**: Deploy only the backend folder contents to your Hugging Face Space.

**Option A: Using git subtree (Recommended)**
```bash
# From the root wba directory
git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/equipment-visualizer-api
git subtree push --prefix backend hf main
```

**Option B: Manually copy and push**
```bash
# Clone your HF Space
git clone https://huggingface.co/spaces/YOUR-USERNAME/equipment-visualizer-api
cd equipment-visualizer-api

# Copy backend files
cp -r ../wba/backend/* .

# Push
git add .
git commit -m "Initial deployment"
git push
```

5. **Wait for Build** (check Space logs)

6. **Run Initial Migration** (in Space terminal)
```bash
python manage.py createsuperuser
```

7. **Test API**
Visit: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/docs/`

### Frontend to Vercel

1. **Update .env.production**
Replace `YOUR-USERNAME` with your actual Hugging Face username:
```env
REACT_APP_API_URL=https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/v1
```

2. **Deploy to Vercel**

**Option A: Using Vercel CLI**
```bash
cd frontend-web
npm install -g vercel
vercel login
vercel --prod
```

**Option B: Using Vercel Dashboard**
- Go to https://vercel.com
- Click "Add New Project"
- Import Git repository
- Root Directory: `frontend-web`
- Framework: Create React App
- Add environment variable:
  - Key: `REACT_APP_API_URL`
  - Value: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/v1`
- Click "Deploy"

3. **Get Vercel Domain**
Copy your Vercel URL (e.g., `https://your-app-name.vercel.app`)

4. **Update Backend CORS**
Go back to Hugging Face Space settings and update:
```
CORS_ALLOWED_ORIGINS=https://your-app-name.vercel.app
```

## Post-Deployment

### Keep Hugging Face Space Alive

Hugging Face Spaces go to sleep after inactivity. Set up a cron job to keep it alive:

1. **Go to https://cron-job.org/en/**
2. **Sign up / Log in**
3. **Create New Cron Job**:
   - **Title**: `Keep Equipment Visualizer Alive`
   - **URL**: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/v1/health/`
   - **Schedule**: Every 10 minutes (or as preferred)
     - Pattern: `*/10 * * * *`
   - **Request Method**: GET
   - **Enable**: ✓
4. **Save**

The health endpoint will respond with:
```json
{
  "status": "ok",
  "message": "Equipment Visualizer API is running"
}
```

This keeps your Space active 24/7 by pinging it regularly.

### Testing
- [ ] Test backend API endpoints at `/api/docs/`
- [ ] Test health check at `/api/v1/health/`
- [ ] Test frontend at Vercel URL
- [ ] Test user registration
- [ ] Test login
- [ ] Test CSV upload
- [ ] Test analytics display
- [ ] Test PDF download
- [ ] Test on mobile device

### Optional Improvements
- [ ] Set up custom domain on Vercel
- [ ] Enable automatic backups on Neon
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Set up cron job at cron-job.org to keep Space alive
- [ ] Add rate limiting
- [ ] Set up CI/CD pipeline
- [ ] Add Google Analytics

## Troubleshooting

### CORS Errors
1. Verify `CORS_ALLOWED_ORIGINS` in HF Space includes your Vercel domain
2. No trailing slash in URLs
3. Check browser console for exact error

### Database Connection Failed
1. Verify `DATABASE_URL` is correct
2. Check Neon project is active
3. Ensure `?sslmode=require` is in connection string

### Static Files Not Loading
1. Check Hugging Face build logs
2. Verify `collectstatic` ran successfully
3. Check WhiteNoise is in MIDDLEWARE

### 502 Bad Gateway on Hugging Face
1. Check Space logs for errors
2. Verify Dockerfile is correct
3. Check port 7860 is exposed and used

## URLs to Save

- **Backend API**: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space`
- **Backend Admin**: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space/admin`
- **API Docs**: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/docs/`
- **Health Check**: `https://YOUR-USERNAME-equipment-visualizer-api.hf.space/api/v1/health/`
- **Frontend**: `https://your-app-name.vercel.app`
- **Neon Console**: `https://console.neon.tech/`
- **Cron Job Dashboard**: `https://cron-job.org/en/members/jobs/`

## Support

- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
- Hugging Face Forums: https://discuss.huggingface.co/
- Vercel Support: https://vercel.com/support
- Neon Discord: https://neon.tech/discord
