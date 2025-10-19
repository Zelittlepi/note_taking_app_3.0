# Installation Guide for Translation Feature

## Required Packages

To use the translation feature locally, you need to install:

```bash
pip install openai==1.45.0 python-dotenv==1.0.0
```

## If You Get "Module Not Found" Errors

If you see errors like "No module named 'openai'" when trying to use translation:

### Option 1: Install packages using conda (recommended)
```bash
conda install pip
pip install openai==1.45.0 python-dotenv==1.0.0
```

### Option 2: Install packages using pip directly
```bash
python -m pip install openai==1.45.0 python-dotenv==1.0.0
```

### Option 3: Install in your current conda environment
```bash
conda activate base
pip install openai==1.45.0 python-dotenv==1.0.0
```

## Testing the Translation

After installation, you can test the translation:

1. Run the debug script:
   ```bash
   python debug_translation.py
   ```

2. Start the Flask app:
   ```bash
   python src/main.py
   ```

3. Visit the debug endpoint:
   ```
   http://localhost:5001/api/debug/translation
   ```

## For Vercel Deployment

The packages are already included in `requirements.txt`, so they will be installed automatically when deploying to Vercel. Just make sure to set the `GITHUB_AI_TOKEN` environment variable in your Vercel dashboard.

## Troubleshooting

- If translation still doesn't work after installing packages, restart your terminal/IDE
- Make sure the `.env` file exists and contains your `GITHUB_AI_TOKEN`
- Check the Flask app logs for detailed error messages
- Use the `/api/debug/translation` endpoint to see what's not working