# Deployment Guide - Luminous Dashboard

This guide covers deploying the Luminous Dashboard to various hosting platforms.

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Access to your Supabase project credentials
- (Optional) CI/CD pipeline access

## Build Process

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file with your production values:

```bash
cp .env.example .env
```

Edit `.env` with your production Supabase credentials:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_production_anon_key
```

### 3. Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

### 4. Preview Build Locally

```bash
npm run preview
```

Visit `http://localhost:4173` to verify the build.

## Build Optimizations

The production build includes:

- **Code Splitting**: Vendor chunks for React, Framer Motion, VisX, Supabase, and Radix UI
- **Tree Shaking**: Unused code is removed
- **Minification**: JavaScript and CSS are minified
- **Source Maps**: Enabled for production debugging
- **Asset Optimization**: Images and fonts are optimized

### Bundle Analysis

To analyze bundle size:

```bash
npm run build -- --report
```

## Deployment Platforms

### Vercel (Recommended)

1. Connect your repository to Vercel
2. Set the root directory to `frontend`
3. Configure environment variables in Vercel dashboard
4. Deploy

**vercel.json** (optional, place in frontend/):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite"
}
```

### Netlify

1. Connect your repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `frontend/dist`
4. Configure environment variables in Netlify dashboard

**netlify.toml** (place in frontend/):
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### AWS S3 + CloudFront

1. Build the application:
   ```bash
   npm run build
   ```

2. Create S3 bucket with static website hosting enabled

3. Upload `dist/` contents to S3:
   ```bash
   aws s3 sync dist/ s3://your-bucket-name --delete
   ```

4. Configure CloudFront distribution:
   - Origin: S3 bucket
   - Default root object: `index.html`
   - Error pages: Redirect 404 to `/index.html` with 200 status

### Docker

**Dockerfile** (place in frontend/):
```dockerfile
# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf** (place in frontend/):
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Build and run:
```bash
docker build -t luminous-dashboard .
docker run -p 80:80 luminous-dashboard
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `/api` |
| `VITE_DEBUG_MODE` | Enable debug logging | `false` |

## CI/CD Pipeline

### GitHub Actions Example

**.github/workflows/deploy.yml**:
```yaml
name: Deploy Luminous Dashboard

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Run tests
        working-directory: frontend
        run: npm test
      
      - name: Build
        working-directory: frontend
        run: npm run build
        env:
          VITE_SUPABASE_URL: ${{ secrets.VITE_SUPABASE_URL }}
          VITE_SUPABASE_ANON_KEY: ${{ secrets.VITE_SUPABASE_ANON_KEY }}
      
      # Add deployment step for your platform
      # - name: Deploy to Vercel/Netlify/S3
```

## Post-Deployment Checklist

- [ ] Verify environment variables are set correctly
- [ ] Test Supabase connection (check connection pulse indicator)
- [ ] Test real-time updates (submit a generation request)
- [ ] Verify all assets load correctly (images, fonts)
- [ ] Test responsive layout on mobile devices
- [ ] Run accessibility audit
- [ ] Monitor error tracking (if configured)
- [ ] Set up uptime monitoring

## Troubleshooting

### Build Fails with TypeScript Errors

If the build fails with TypeScript errors in legacy components (outside `src/luminous/`), you may need to:

1. Fix the legacy component errors, or
2. Exclude legacy components from the build by updating `tsconfig.json`:
   ```json
   {
     "exclude": [
       "src/components/monitoring/**",
       "src/design-system/**"
     ]
   }
   ```

The Luminous design system components (`src/luminous/`) are TypeScript-clean and should build without errors.

### Build Fails

1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check Node.js version (requires 18+):
   ```bash
   node --version
   ```

### Assets Not Loading

- Verify `base` path in vite.config.ts matches your deployment path
- Check browser console for 404 errors
- Ensure CDN/hosting serves correct MIME types

### Supabase Connection Issues

- Verify VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are set
- Check Supabase project is active and not paused
- Verify CORS settings in Supabase dashboard

### Performance Issues

- Enable gzip compression on your hosting platform
- Configure proper cache headers for static assets
- Consider using a CDN for global distribution
