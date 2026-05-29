# Crop Disease Detection - Deployment Guide

This guide explains how to deploy the entire project (frontend + backend) using GitHub and Docker.

## Project Structure

```
crop-disease-detection/
├── src/                    # React frontend source
├── public/                 # Static assets
├── server/                 # Python backend
├── package.json            # Frontend dependencies
├── Dockerfile              # Backend Docker image
├── Dockerfile.frontend     # Frontend Docker image
├── docker-compose.yml      # Local development setup
└── .github/workflows/      # CI/CD pipelines
```

## Deployment Options

### Option 1: GitHub Pages (Frontend Only)

The frontend is automatically deployed to GitHub Pages on every push to `main` branch.

**Access your frontend:**
```
https://mulesarthak.github.io/crop-disease-detecction/
```

### Option 2: Docker Deployment (Recommended for Full Stack)

#### Prerequisites
- Docker installed
- Docker Hub account

#### Local Development with Docker Compose

```bash
# Build and run both frontend and backend
docker-compose up --build

# Frontend: http://localhost:5173
# Backend: http://localhost:5000
```

#### Deploy Backend to Docker Hub

1. Set GitHub Secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password/token

2. Push to main branch - automatic deployment triggers:
   ```bash
   git add .
   git commit -m "Deploy"
   git push origin main
   ```

3. Image available at:
   ```
   docker.io/YOUR_USERNAME/crop-disease-detection:latest
   ```

### Option 3: Deploy to Cloud Platforms

#### Railway (Recommended - Free Tier)

**Backend Deployment:**
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Set root directory: `/server`
4. Deploy automatically

**Frontend Deployment:**
1. Deploy as separate Railway project
2. Set root directory: `/`

#### Heroku (Legacy - Requires Credit Card)

```bash
# Login to Heroku
heroku login

# Create app
heroku create crop-disease-detection

# Deploy
git push heroku main
```

#### Vercel (Best for Frontend)

```bash
npm install -g vercel
vercel
```

### Option 4: Traditional VPS/Server

#### Deployment Steps:

**Backend:**
```bash
# SSH into your server
ssh user@your-server.com

# Clone repository
git clone https://github.com/mulesarthak/crop-disease-detecction.git
cd crop-disease-detecction/server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

**Frontend:**
```bash
cd crop-disease-detecction

# Build
npm run build

# Serve with nginx or copy dist/ to your web server
cp -r dist/* /var/www/html/
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On every push to main:**
   - Installs dependencies
   - Builds frontend (React + Vite)
   - Deploys to GitHub Pages
   - Tests backend
   - Builds Docker image
   - Pushes to Docker Hub (if secrets configured)

**View status:** Go to **Actions** tab in GitHub

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=https://your-backend-api.com
VITE_APP_NAME=Crop Disease Detection
```

### Backend (server/.env)
```
FLASK_ENV=production
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

## Monitoring Deployment

### GitHub Pages
- Frontend automatically deployed to: `https://mulesarthak.github.io/crop-disease-detecction/`
- View deployment status in repository **Deployments** tab

### Docker Hub
- Image: `docker.io/YOUR_USERNAME/crop-disease-detection:latest`
- Pull: `docker pull YOUR_USERNAME/crop-disease-detection:latest`

### GitHub Actions
- View build logs: Repository → **Actions** tab
- Check workflow runs for any failures

## Troubleshooting

### Frontend not deploying?
- Ensure `vite.config.js` has correct `base` path
- Check GitHub Actions workflow logs

### Backend Docker build fails?
- Verify `server/requirements.txt` exists
- Check Dockerfile paths are correct

### API calls failing?
- Update `VITE_API_URL` in frontend
- Ensure backend CORS is configured correctly

## Next Steps

1. **Configure Secrets:**
   - Go to Settings → Secrets → Add:
     - `DOCKER_USERNAME`
     - `DOCKER_PASSWORD`

2. **Test Deployment:**
   ```bash
   git add .
   git commit -m "Initial deployment setup"
   git push origin main
   ```

3. **Monitor:**
   - Check GitHub Actions for build status
   - Verify GitHub Pages deployment
   - Test API connectivity

4. **Update Environment Variables:**
   - Configure production URLs in `.env` files
   - Add database connections if needed

## Support

For issues, check:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- Project Issues tab
