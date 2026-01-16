# Netlify Deployment Guide

## Quick Deploy

### Option 1: Deploy via Netlify CLI (Recommended)

1. **Install Netlify CLI** (if not already installed):
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**:
   ```bash
   netlify login
   ```

3. **Deploy from the project root**:
   ```bash
   netlify deploy --prod
   ```

   Or for a draft deployment first:
   ```bash
   netlify deploy
   ```

### Option 2: Deploy via Netlify Dashboard

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for Netlify deployment"
   git push origin main
   ```

2. **Go to [Netlify](https://app.netlify.com/)**
   - Click "Add new site" → "Import an existing project"
   - Connect to your GitHub repository
   - Netlify will auto-detect the settings from `netlify.toml`

3. **Deploy settings** (auto-configured via netlify.toml):
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
   - Environment variables: `VITE_DEMO_MODE=true`

4. **Click "Deploy site"**

### Option 3: Drag & Drop Deploy

1. **Build the project locally**:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Go to [Netlify Drop](https://app.netlify.com/drop)**
   - Drag and drop the `frontend/dist` folder
   - Your site will be deployed instantly!

## Demo Mode Features

Your deployment includes:
- ✅ No backend required - fully functional demo
- ✅ Mock data for all features
- ✅ Demo credentials displayed on login page:
  - **Admin**: admin@demo.com / admin123
  - **Teacher**: teacher@demo.com / teacher123
  - **Student**: student@demo.com / student123
- ✅ Interactive DotGrid background with glassmorphism design
- ✅ All dashboard features working with mock data

## Post-Deployment

After deployment, you'll get a URL like: `https://your-site-name.netlify.app`

### Custom Domain (Optional)
1. Go to Site settings → Domain management
2. Add your custom domain
3. Follow Netlify's DNS configuration instructions

### Environment Variables
The demo mode is already configured via `netlify.toml`, but you can also set it in:
- Site settings → Environment variables → Add `VITE_DEMO_MODE=true`

## Troubleshooting

### Build fails
- Check that Node version is 18+ in build settings
- Verify all dependencies are in `package.json`
- Check build logs for specific errors

### Routes not working (404 errors)
- The `netlify.toml` includes redirect rules for SPA routing
- If issues persist, check Site settings → Build & deploy → Post processing

### Demo mode not working
- Verify `VITE_DEMO_MODE=true` is set in environment variables
- Check browser console for any errors
- Clear browser cache and reload

## Build Optimization

The production build is optimized with:
- Code splitting
- Tree shaking
- Minification
- Asset optimization

Typical build size: ~500KB (gzipped)
Build time: ~1-2 minutes

## Support

For issues:
1. Check Netlify build logs
2. Review browser console errors
3. Verify environment variables are set correctly
