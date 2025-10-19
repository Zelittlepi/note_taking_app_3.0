# Vercel Translation Debug Guide

## 🚀 Testing Steps After Deployment

### 1. **First, check if the app is running:**
```
GET https://your-app.vercel.app/api/health
```

Expected response should include:
```json
{
  "status": "ok",
  "github_token_available": true,
  "environment": {
    "VERCEL": "1",
    "FLASK_ENV": "production"
  }
}
```

### 2. **Check translation service status:**
```
GET https://your-app.vercel.app/api/debug/translation
```

This will show:
- Whether OpenAI package is available
- Whether GitHub token is configured
- Any import or initialization errors

### 3. **Test the Vercel-specific translation handler:**
```
POST https://your-app.vercel.app/api/notes/test/vercel-translation/1
Content-Type: application/json

{
  "translate_title": true,
  "translate_content": true
}
```

This uses a specialized handler designed for Vercel's serverless environment.

### 4. **Test the main translation endpoint:**
```
POST https://your-app.vercel.app/api/notes/1/translate
Content-Type: application/json

{
  "translate_title": true,
  "translate_content": true
}
```

## 🔍 Common Vercel Issues and Solutions

### **Issue 1: Environment Variables Not Set**
- **Symptom**: `github_token_available: false`
- **Solution**: Set `GITHUB_AI_TOKEN` in Vercel dashboard

### **Issue 2: Timeout Errors**
- **Symptom**: 504 Gateway Timeout
- **Solution**: Increased timeout to 60 seconds in vercel.json

### **Issue 3: Cold Start Issues**
- **Symptom**: First request fails, subsequent requests work
- **Solution**: Vercel-optimized handler bypasses service initialization

### **Issue 4: Import Failures**
- **Symptom**: OpenAI import errors
- **Solution**: Check package installation in deployment logs

## 🛠 Debugging Checklist

1. ✅ **Environment Variables Set in Vercel:**
   - `GITHUB_AI_TOKEN`
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `FLASK_ENV=production`

2. ✅ **Packages in requirements.txt:**
   - `openai==1.45.0`
   - `python-dotenv==1.0.0`

3. ✅ **Vercel Configuration:**
   - Timeout set to 60 seconds
   - Lambda size increased to 50MB

4. ✅ **Test Endpoints Available:**
   - `/api/health` - General health check
   - `/api/debug/translation` - Translation service status
   - `/api/notes/test/vercel-translation/1` - Vercel-specific test

## 📱 Expected Behavior

- **Local Development**: May not work due to missing packages (expected)
- **Vercel Deployment**: Should work with proper environment variables
- **Error Handling**: Clear error messages with debug information

## 🚨 If Still Getting 500 Errors

1. Check Vercel function logs
2. Test the debug endpoints
3. Verify environment variables are set correctly
4. Try the Vercel-specific test endpoint first