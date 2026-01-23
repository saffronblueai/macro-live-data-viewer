# 📁 Project Structure Guide

## Current vs. Recommended Structure

### ❌ Current Structure (Flat)
```
macro-live-data-viewer/
├── INDEX.md
├── ARCHITECTURE.md
├── DEPLOYMENT.md
├── GETTING_STARTED.md
├── QUICKSTART.md
├── SETUP_SUMMARY.md
├── PRE_DEPLOYMENT_CHECKLIST.md
├── DEPLOYMENT_STATUS.txt
├── index.html
├── data.js
├── fetch_data.py
├── fetch_sentiment.py
├── server.py
├── bond_yields_10y.csv
├── countries_tickers.csv
├── ... (more CSVs)
└── infrastructure/
```

### ✅ Recommended Structure (Organized)

```
macro-live-data-viewer/
├── docs/                          # 📚 All documentation
│   ├── INDEX.md
│   ├── GETTING_STARTED.md        # START HERE (5 min read)
│   ├── DEPLOYMENT.md             # Comprehensive guide
│   ├── QUICKSTART.md             # Command reference
│   ├── ARCHITECTURE.md           # System diagrams
│   ├── SETUP_SUMMARY.md          # Project overview
│   ├── PRE_DEPLOYMENT_CHECKLIST.md
│   └── DEPLOYMENT_STATUS.txt
│
├── src/                          # 🔧 Source code
│   ├── index.html                # Dashboard UI
│   ├── data.js                   # Generated data (not committed)
│   ├── fetch_data.py             # Market data fetcher
│   ├── fetch_sentiment.py        # Sentiment fetcher
│   └── server.py                 # Dev server
│
├── data/                         # 📊 Data files (CSV & logs)
│   ├── bond_yields_10y.csv
│   ├── countries_tickers.csv
│   ├── currencies.csv
│   ├── sentiment_data.csv
│   ├── sentiment_data_domestic.csv
│   ├── stock_indices.csv
│   └── *.log                     # Fetch operation logs
│
├── infrastructure/               # ☁️ Infrastructure as Code
│   ├── __main__.py               # Pulumi definitions
│   ├── Pulumi.yaml               # Project config
│   ├── Pulumi.dev.yaml           # Dev stack
│   ├── requirements.txt          # Dependencies
│   ├── deploy.py                 # Setup wizard
│   ├── deploy.sh                 # Setup helper
│   └── .gitignore
│
├── .github/workflows/            # CI/CD
│   ├── deploy.yml
│   └── nightly-data-update.yml
│
├── README.md                     # Main README
├── requirements.txt              # Project dependencies
└── .gitignore
```

## 🔄 How to Reorganize

### Option 1: Using Shell Commands

```bash
cd /home/air/projects/macro-live-data-viewer

# Create directories
mkdir -p docs src data

# Move documentation
mv INDEX.md ARCHITECTURE.md DEPLOYMENT.md DEPLOYMENT_STATUS.txt \
   GETTING_STARTED.md PRE_DEPLOYMENT_CHECKLIST.md QUICKSTART.md \
   SETUP_SUMMARY.md docs/

# Move source files
mv index.html data.js fetch_data.py fetch_sentiment.py server.py src/

# Move data files
mv *.csv data/
mv *.log data/ 2>/dev/null || true
```

### Option 2: Using Python Script

```python
import os
import shutil

files_to_reorganize = {
    "docs": [
        "INDEX.md", "ARCHITECTURE.md", "DEPLOYMENT.md", "DEPLOYMENT_STATUS.txt",
        "GETTING_STARTED.md", "PRE_DEPLOYMENT_CHECKLIST.md", "QUICKSTART.md", "SETUP_SUMMARY.md"
    ],
    "src": [
        "index.html", "data.js", "fetch_data.py", "fetch_sentiment.py", "server.py"
    ],
    "data": [
        "bond_yields_10y.csv", "countries_tickers.csv", "currencies.csv",
        "sentiment_data.csv", "sentiment_data_domestic.csv", "stock_indices.csv",
        "domestic_fetch.log", "domestic_fetch_err.log"
    ]
}

for target_dir, files in files_to_reorganize.items():
    os.makedirs(target_dir, exist_ok=True)
    for file in files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(target_dir, file))
```

### Option 3: Manual File Copy

Use VS Code's file explorer to:
1. Create folders: `docs/`, `src/`, `data/`
2. Drag and drop files into appropriate folders
3. Verify all files are in correct locations
4. Delete originals from root

## 📋 Files by Directory

### docs/ (8 files)
These are all reference and setup documentation
```
documentation → docs/
├── INDEX.md                       # Overview of everything
├── GETTING_STARTED.md            # Quick start (read first)
├── DEPLOYMENT.md                 # Step-by-step guide
├── QUICKSTART.md                 # Command reference
├── ARCHITECTURE.md               # System design
├── SETUP_SUMMARY.md              # What was built
├── PRE_DEPLOYMENT_CHECKLIST.md   # Pre-deployment checks
└── DEPLOYMENT_STATUS.txt         # Status tracker
```

### src/ (5 files)
Application source code and UI
```
application → src/
├── index.html                    # Web dashboard (main UI)
├── data.js                       # Generated market data (*.gitignore)
├── fetch_data.py                 # Fetches market/macro data
├── fetch_sentiment.py            # Fetches sentiment data
└── server.py                     # Local dev server
```

### data/ (8+ files)
Data files and operation logs
```
data files → data/
├── bond_yields_10y.csv           # 10-year bond yields
├── countries_tickers.csv         # Country/ticker mapping
├── currencies.csv                # Currency data
├── sentiment_data.csv            # Global sentiment data
├── sentiment_data_domestic.csv   # Domestic sentiment data
├── stock_indices.csv             # Stock index data
├── domestic_fetch.log            # Fetch operation log
└── domestic_fetch_err.log        # Fetch error log
```

## 🔧 After Reorganization

Update file paths in these locations:

### 1. GitHub Actions Workflows
File: `.github/workflows/deploy.yml`

```yaml
# Before
- run: |
    aws s3 sync . s3://macro-live-data-viewer-bucket \
      --exclude "*" \
      --include "index.html" \
      --include "data.js" \
      --include "*.csv"

# After
- run: |
    aws s3 sync . s3://macro-live-data-viewer-bucket \
      --exclude "*" \
      --include "src/index.html" \
      --include "src/data.js" \
      --include "data/*.csv"
```

### 2. Nightly Data Update Workflow
File: `.github/workflows/nightly-data-update.yml`

```yaml
# Update paths for CSV uploads
aws s3 cp data/*.csv s3://macro-live-data-viewer-bucket/data/
```

### 3. Pulumi Infrastructure
File: `infrastructure/__main__.py`

Update any file paths if they reference root directory files

### 4. GitHub Actions Outputs
File: `.github/workflows/deploy.yml`

Paths in sync command should reference new locations

## 📝 Updated .gitignore

After reorganization, consider:

```gitignore
# Generated data (regenerated nightly)
data/*.csv
data/*.log
src/data.js

# Or keep if you want to track initial data
# data/bond_yields_10y.csv
# data/countries_tickers.csv
# etc...

# Build artifacts
infrastructure/.pulumi/
.venv/
__pycache__/
*.pyc
```

## ✅ Verification Checklist

After reorganization:

- [ ] All 8 `.md` files are in `docs/`
- [ ] All 5 source files (`*.py`, `*.html`, `*.js`) are in `src/`
- [ ] All CSV files are in `data/`
- [ ] `infrastructure/` folder remains unchanged
- [ ] `.github/` folder remains unchanged
- [ ] `README.md` stays in root
- [ ] `requirements.txt` stays in root
- [ ] `.gitignore` stays in root
- [ ] `README.md` and documentation still reference correct files

## 🚀 After Moving Files

1. **Test local deployment:**
   ```bash
   cd infrastructure
   pulumi preview
   ```

2. **Commit changes:**
   ```bash
   git add .
   git commit -m "chore: reorganize project into structured directories"
   git push origin main
   ```

3. **Verify GitHub Actions:**
   - Trigger manual deploy workflow
   - Confirm it still works with new paths
   - Check nightly update workflow

4. **Update documentation:**
   - Any internal links in docs may need updating
   - Update README if it references file locations

## 📚 Documentation Access After Reorganization

After moving files to `docs/`, access them via:

| Document | Purpose | Time |
|----------|---------|------|
| `docs/INDEX.md` | Complete overview | 10 min |
| `docs/GETTING_STARTED.md` | Quick start | 5 min |
| `docs/DEPLOYMENT.md` | Step-by-step | 20-30 min |
| `docs/QUICKSTART.md` | Command reference | 5 min |
| `docs/ARCHITECTURE.md` | System design | 10 min |

## 🎯 Benefits

✅ **Cleaner Repository**
- Root directory only has essential files
- Easy to navigate

✅ **Better Organization**
- Documentation grouped together
- Source code isolated
- Data separate from code

✅ **CI/CD Simplification**
- Clear path specifications in workflows
- Easier to exclude/include files

✅ **Easier Collaboration**
- New team members understand structure
- Logical file organization
- Standard project layout

✅ **Future Scalability**
- Easy to add more source files
- Room for tests/, scripts/, build/ directories
- Professional repository structure
