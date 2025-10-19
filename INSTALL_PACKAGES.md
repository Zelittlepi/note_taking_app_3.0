# Installation Commands for Translation Feature

## Try these commands in order until one works:

### Method 1: Direct pip install
```bash
pip install openai==1.45.0 python-dotenv==1.0.0
```

### Method 2: Using Python module
```bash
python -m pip install openai==1.45.0 python-dotenv==1.0.0
```

### Method 3: Using conda (if you're in a conda environment)
```bash
conda install pip -y
pip install openai==1.45.0 python-dotenv==1.0.0
```

### Method 4: Install in specific environment
```bash
conda activate base
pip install openai==1.45.0 python-dotenv==1.0.0
```

## After Installation:

1. Test the installation:
```bash
python -c "import openai; print('OpenAI installed successfully')"
```

2. Test the translation service:
```bash
python debug_translation.py
```

3. Start the Flask app:
```bash
python src/main.py
```

4. Test the translation button in the web interface

## If Installation Fails:

1. Check your internet connection
2. Try updating pip first: `python -m pip install --upgrade pip`
3. Use a different package index: `pip install --index-url https://pypi.org/simple/ openai==1.45.0`

## For Vercel Deployment:

The packages will be installed automatically from requirements.txt, so this is only needed for local development.