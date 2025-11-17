# Quick Start Testing Guide
**For Green Sea Map Application**
**Created:** 2025-11-14

---

## 🚀 Prerequisites Check

Before testing, ensure you have:

- [x] Python 3.9+ installed
- [x] PostgreSQL with PostGIS extension running
- [x] Database credentials in `.env` file
- [ ] Python dependencies installed (see below)

---

## 📦 Step 1: Install Dependencies

If you haven't already installed the required packages:

```bash
cd /home/user/GreenSea_Map

# Option A: Using pip directly
pip install -r requirements.txt

# Option B: Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Installation time:** ~5-10 minutes depending on your connection

---

## 🗄️ Step 2: Verify Database Connection

Check that your database is accessible:

```bash
# Test database connection
python3 -c "from database.db_manager import db_manager; db_manager.initialize(); print('✅ Database connected!' if db_manager.test_connection() else '❌ Connection failed')"
```

**Expected output:** `✅ Database connected!`

If you see an error:
1. Check `.env` file has correct credentials
2. Ensure PostgreSQL is running
3. Verify PostGIS extension is installed

---

## 🎯 Step 3: Launch the Application

Start the Streamlit app:

```bash
streamlit run app/main.py
```

**Expected behavior:**
- Console shows: `You can now view your Streamlit app in your browser.`
- Browser automatically opens to: `http://localhost:8501`
- App redirects to Home page
- Dark glassmorphism theme is visible

**If the app doesn't start:**
- Check for error messages in console
- Verify all dependencies are installed
- Check that port 8501 is not in use

---

## ✅ Step 4: Quick Smoke Test (5 minutes)

Perform these quick checks to ensure everything works:

### Test 1: Home Page
- [ ] Page loads with dark background
- [ ] Glass effects visible on cards
- [ ] Statistics display (may show zeros if no data)
- [ ] Navigation buttons visible

### Test 2: Map Viewer
- [ ] Page loads without errors
- [ ] City selector dropdown appears
- [ ] If you have data: Select a city and verify map generates
- [ ] If no data: Verify helpful error message appears

### Test 3: Upload Data
- [ ] Page loads with step indicator
- [ ] Step 1 form displays
- [ ] Can type in text fields
- [ ] "Next Step" button works

### Test 4: Settings
- [ ] Page loads without errors
- [ ] Database statistics show counts
- [ ] If you have cities: City selector appears
- [ ] Import history section displays

### Test 5: Navigation
- [ ] Can navigate between all 4 pages
- [ ] Theme remains consistent on all pages
- [ ] No JavaScript errors in browser console (F12)

---

## 🧪 Step 5: Full Testing (Use TESTING_CHECKLIST.md)

Once the smoke test passes, proceed to comprehensive testing:

```bash
# Open the full testing checklist
cat Documents/TESTING_CHECKLIST.md
```

Work through all sections:
1. **Visual Testing** (~15 minutes)
2. **Functional Testing** (~30-45 minutes)
3. **Performance Testing** (~20 minutes)
4. **Polish Testing** (~15 minutes)
5. **Integration Testing** (~30 minutes with data import)

**Total testing time:** ~2-2.5 hours for complete testing

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: "Database connection failed"
**Solution:**
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify `.env` file exists and has correct credentials
3. Test connection manually: `psql -h localhost -U your_user -d your_db`

### Issue: "Map not loading / stuck on 'Generating map'"
**Solution:**
- This is a known issue we're working on
- Try:
  1. Clear Streamlit cache (Settings page → will add button)
  2. Restart the application
  3. Check browser console for JavaScript errors
  4. Verify you have parcel data with geometries

### Issue: "Import fails with file upload error"
**Solution:**
- Check file size < 500MB (configured in .streamlit/config.toml)
- Verify CSV has required columns
- Ensure shapefile ZIP contains all components (.shp, .shx, .dbf, .prj)

### Issue: "Page is blank or styles not loading"
**Solution:**
1. Check browser console (F12) for CSS errors
2. Verify `ui/styles/glass_theme.css` exists
3. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
4. Check that each page has `load_css()` function call

---

## 📊 Testing Checklist Progress

As you test, keep track of your progress:

- [ ] **Smoke test complete** (all 5 quick tests pass)
- [ ] **Visual testing complete** (9 items from TESTING_CHECKLIST.md)
- [ ] **Functional testing complete** (30+ items)
- [ ] **Performance testing complete** (15+ items)
- [ ] **Polish testing complete** (20+ items)
- [ ] **Integration testing complete** (35+ items)

---

## 📝 Documenting Issues

When you find issues, document them in this format:

### Issue Template

**Issue #:** ___
**Page:** [Home / Map Viewer / Upload Data / Settings]
**Severity:** [Critical / High / Medium / Low]
**Description:**

**Steps to reproduce:**
1.
2.
3.

**Expected behavior:**

**Actual behavior:**

**Screenshot/Error message:**

**Browser:** [Chrome / Firefox / Safari / Edge]
**Browser console errors:** [Yes / No - if yes, paste errors]

---

## 🎯 Success Criteria

Testing is complete when:

- ✅ All smoke tests pass
- ✅ 90%+ of visual tests pass
- ✅ 100% of critical functional tests pass
- ✅ Performance targets met (or documented issues)
- ✅ All issues documented with severity levels
- ✅ Critical and high-severity bugs fixed or workarounds found

---

## 🔄 After Testing

Once testing is complete:

1. **Compile results** - Summarize what works and what needs attention
2. **Prioritize fixes** - Critical > High > Medium > Low
3. **Create action plan** - What needs to be fixed immediately vs. later
4. **Document wins** - What works well and is production-ready

---

## 📞 Getting Help

If you encounter issues during testing:

1. **Check this guide** - Common issues section above
2. **Check logs** - Streamlit console output usually has helpful errors
3. **Browser console** - Press F12, check Console and Network tabs
4. **Database logs** - If database-related issues
5. **Ask for help** - Provide: error message, steps to reproduce, browser info

---

## ✨ Quick Commands Reference

```bash
# Start app
streamlit run app/main.py

# Start app on different port
streamlit run app/main.py --server.port 8502

# Start app with debug mode
streamlit run app/main.py --logger.level=debug

# Clear Streamlit cache
streamlit cache clear

# Check database connection
python3 database/verify_setup.py

# Run Python syntax check on all pages
python3 -m py_compile app/pages/*.py

# View recent git changes
git log --oneline -10

# Check current branch
git branch --show-current
```

---

**Ready to test?** Start with Step 1 above! 🚀

**Questions?** Document them in your testing notes and we can address them together.

**Found bugs?** Use the issue template above to document them clearly.

Good luck with testing!
