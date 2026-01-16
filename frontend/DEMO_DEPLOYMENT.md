# Demo Deployment Guide - Portfolio Version

This guide explains how to deploy the frontend as a standalone demo for your portfolio.

## ✨ Features in Demo Mode

- ✅ Fully interactive UI with mock data
- ✅ Beautiful credentials display on login page
- ✅ Click-to-fill demo credentials
- ✅ Three role-based accounts (Admin, Teacher, Student)
- ✅ Secure login - only demo credentials work
- ✅ View students, attendance, and analytics
- ✅ Manage users and suspicious activities
- ✅ All CRUD operations work (simulated)
- ✅ No backend required
- ✅ Professional, clean interface

## 🚀 Quick Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard

1. **Go to [vercel.com](https://vercel.com)** and sign in

2. **Import Project:**
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Select the repository

3. **Configure Build Settings:**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

4. **Environment Variables:**
   ```
   VITE_DEMO_MODE=true
   ```

5. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Get your live URL: `https://your-app.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: your-project-name
# - Directory: ./
# - Override settings? Yes
#   - Build Command: npm run build
#   - Output Directory: dist
#   - Development Command: npm run dev

# Add environment variable
vercel env add VITE_DEMO_MODE
# Enter: true
# Select: Production

# Deploy to production
vercel --prod
```

## 🎨 Deploy to Netlify

### Via Netlify Dashboard

1. **Go to [netlify.com](https://netlify.com)** and sign in

2. **Import Project:**
   - Click "Add new site" → "Import an existing project"
   - Connect to GitHub
   - Select your repository

3. **Configure Build Settings:**
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: frontend/dist
   ```

4. **Environment Variables:**
   - Go to Site settings → Environment variables
   - Add: `VITE_DEMO_MODE` = `true`

5. **Deploy!**

### Via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Navigate to frontend
cd frontend

# Build
npm run build

# Deploy
netlify deploy --prod --dir=dist
```

## 📱 What Users Will See

### Demo Banner
A yellow banner at the top: "🎨 Portfolio Demo - This is a frontend prototype. Backend features are not available."

### Login Page
- Beautiful credentials card displayed next to login form
- Click any credential card to auto-fill the login form
- Copy buttons for easy credential copying
- Only these specific credentials work:
  - **Admin:** `admin@classroom.com` / `admin123`
  - **Teacher:** `teacher@classroom.com` / `teacher123`
  - **Student:** `student@classroom.com` / `student123`
- Other credentials will be rejected with an error message

### Dashboard
- Shows mock attendance data
- 5 sample students
- 4 present today
- 2 suspicious activities

### Features That Work
- ✅ View all students
- ✅ View attendance records
- ✅ View analytics and stats
- ✅ View suspicious activities
- ✅ User management interface
- ✅ All navigation and UI interactions

### Features That Are Simulated
- Camera feed (shows message about demo mode)
- Photo uploads (accepted but not stored)
- Real-time WebSocket updates
- Actual data persistence

## 🎯 Portfolio Presentation

### On Your Portfolio Website

**Project Title:** Smart Classroom Attendance System

**Description:**
```
AI-powered attendance system with facial recognition and anti-spoofing detection.
Built with React, TypeScript, Tailwind CSS, and shadcn/ui components.
```

**Links:**
- 🌐 Live Demo: `https://your-app.vercel.app`
- 💻 GitHub: `https://github.com/yourusername/your-repo`

**Tech Stack:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Query
- React Router

**Features:**
- Modern, responsive UI
- Role-based access control (Admin/Teacher/Student)
- Dashboard with analytics
- Student management
- Attendance tracking
- Suspicious activity monitoring

**Note:** This is a frontend prototype with mock data for demonstration purposes.

## 🔧 Local Testing

Test demo mode locally:

```bash
cd frontend

# Create .env.local
echo "VITE_DEMO_MODE=true" > .env.local

# Install and run
npm install
npm run dev
```

Visit `http://localhost:8080` and login with any credentials.

## 📊 Mock Data Included

- **5 Students** with varying attendance rates
- **4 Attendance records** for today
- **2 Suspicious activities** (spoofing attempt, unknown person)
- **3 Users** (admin, teacher, student)
- **Statistics** showing 92.6% average attendance

## 🎨 Customization

### Change Demo Banner

Edit `frontend/src/components/DemoBanner.tsx`:

```tsx
export function DemoBanner() {
  return (
    <div className="bg-blue-500 text-white px-4 py-2 text-center text-sm font-medium">
      🚀 Your custom message here
    </div>
  );
}
```

### Add More Mock Data

Edit `frontend/src/services/mockApi.ts` to add more students, attendance records, etc.

### Remove Demo Banner

In `frontend/src/App.tsx`, remove:
```tsx
{isDemoMode && <DemoBanner />}
```

## 🐛 Troubleshooting

**Build fails:**
- Check Node.js version (need 18+)
- Run `npm install` in frontend directory
- Check for TypeScript errors: `npm run build`

**Demo mode not activating:**
- Verify `VITE_DEMO_MODE=true` is set
- Check browser console for errors
- Clear browser cache and localStorage

**Styling issues:**
- Ensure Tailwind CSS is configured
- Check `tailwind.config.ts` and `postcss.config.js`

## 💡 Tips

1. **Test locally first** before deploying
2. **Use production build** to test: `npm run build && npm run preview`
3. **Check browser console** for any errors
4. **Mobile responsive** - test on different screen sizes
5. **Add screenshots** to your portfolio

## 📞 Support

If you encounter issues:
- Check Vercel/Netlify deployment logs
- Verify environment variables are set
- Test the production build locally
- Check browser console for errors

---

**Ready to impress recruiters!** 🎉

Your demo will show:
- Clean, modern UI design
- Professional code structure
- TypeScript proficiency
- React best practices
- Responsive design skills
