# Deployment Guide - Smart Classroom Attendance System

## 🚀 Quick Deployment (Railway - Recommended)

### Step 1: Deploy Backend

1. **Go to [Railway.app](https://railway.app)** and sign up/login

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose this repository
   - Select `backend` as the root directory

3. **Add MongoDB Database:**
   - In your project, click "+ New"
   - Select "Database" → "MongoDB"
   - Railway will automatically create `MONGODB_URI` variable

4. **Configure Environment Variables:**
   - Go to your backend service → "Variables"
   - Add these variables:
   ```
   JWT_SECRET_KEY=your-random-secret-key-min-32-chars-long
   PORT=${{PORT}}
   ```
   - `MONGODB_URI` should already be set automatically

5. **Configure Build Settings:**
   - Root Directory: `backend`
   - Build Command: (leave default)
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Deploy:**
   - Railway will auto-deploy
   - Wait for deployment to complete (~3-5 minutes)
   - Copy your backend URL (e.g., `https://your-app.up.railway.app`)

### Step 2: Deploy Frontend

1. **Go to [Vercel](https://vercel.com)** or **[Netlify](https://netlify.com)**

2. **Import Project:**
   - Connect your GitHub repository
   - Select the repository

3. **Configure Build Settings:**
   - Framework Preset: **Other** (or Vite)
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variables:**
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api
   VITE_WS_URL=wss://your-backend-url.railway.app
   ```
   Replace `your-backend-url.railway.app` with your actual Railway backend URL

5. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)
   - Your app is live!

### Step 3: Update Backend CORS

After frontend is deployed, update the backend CORS settings:

1. Go to Railway → Your Backend Service → Variables
2. Add:
   ```
   FRONTEND_URL=https://your-frontend-url.vercel.app
   ```

3. Update `backend/main.py` CORS settings (optional for production):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[os.getenv("FRONTEND_URL", "*")],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## 🔧 Alternative Deployment Options

### Option 2: Render (Free Tier Available)

**Backend:**
1. Go to [Render.com](https://render.com)
2. New → Web Service
3. Connect repository, select `backend` folder
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add MongoDB Atlas connection string as environment variable

**Frontend:**
1. New → Static Site
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Publish Directory: `dist`

### Option 3: Docker + DigitalOcean/AWS

```bash
# Build and push Docker image
cd backend
docker build -t classroom-backend .
docker push your-registry/classroom-backend

# Deploy using docker-compose
docker-compose up -d
```

### Option 4: Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy backend
cd backend
fly launch
fly deploy

# Deploy frontend
cd ../frontend
npm run build
# Upload dist folder to any static hosting
```

---

## 📋 Pre-Deployment Checklist

### Backend:
- [ ] MongoDB connection string configured
- [ ] JWT secret key set (min 32 characters)
- [ ] Environment variables configured
- [ ] CORS origins updated for production
- [ ] Port configuration supports dynamic PORT variable

### Frontend:
- [ ] API URL environment variable set
- [ ] WebSocket URL environment variable set
- [ ] Build command tested locally (`npm run build`)
- [ ] Environment variables use production backend URL

---

## 🔐 Security Recommendations

1. **JWT Secret:** Generate a strong random key:
   ```bash
   openssl rand -hex 32
   ```

2. **MongoDB:** Use MongoDB Atlas with:
   - Strong password
   - IP whitelist (or allow all for cloud deployments)
   - Database user with limited permissions

3. **CORS:** In production, replace `allow_origins=["*"]` with specific frontend URL

4. **HTTPS:** Ensure both frontend and backend use HTTPS in production

---

## 🧪 Testing Deployment

1. **Test Backend:**
   ```bash
   curl https://your-backend-url.railway.app/
   # Should return: {"message": "Smart Classroom Attendance API", ...}
   ```

2. **Test Frontend:**
   - Open your frontend URL
   - Try logging in
   - Check browser console for any CORS or API errors

3. **Test WebSocket:**
   - Go to camera/attendance page
   - Check if live feed connects

---

## 🐛 Troubleshooting

**Backend won't start:**
- Check logs in Railway/Render dashboard
- Verify MongoDB connection string
- Ensure all dependencies in requirements.txt

**Frontend can't connect to backend:**
- Verify VITE_API_URL is correct (include `/api`)
- Check CORS settings in backend
- Ensure backend is running (check Railway dashboard)

**WebSocket connection fails:**
- Use `wss://` (not `ws://`) for HTTPS deployments
- Check firewall/security group settings
- Verify WebSocket support on hosting platform

**MongoDB connection error:**
- Whitelist IP: 0.0.0.0/0 in MongoDB Atlas
- Check connection string format
- Verify database user permissions

---

## 💰 Cost Estimate

**Free Tier Options:**
- Railway: $5 credit/month (enough for small apps)
- Render: Free tier available (with limitations)
- MongoDB Atlas: 512MB free forever
- Vercel/Netlify: Free for personal projects

**Paid Options (if needed):**
- Railway: ~$5-10/month
- Render: ~$7/month
- MongoDB Atlas: ~$9/month (shared cluster)

---

## 📞 Support

If you encounter issues:
1. Check platform-specific documentation
2. Review deployment logs
3. Test locally first with production environment variables
4. Check CORS and network settings
