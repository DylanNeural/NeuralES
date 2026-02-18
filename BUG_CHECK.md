# 🔍 Pre-Exam Bug Report & Verification

**Purpose:** Identify any last-minute issues before exam

---

## ✅ Verified Good

### 1. **Frontend Configuration** ✅
- [x] .env file exists: `VITE_API_BASE_URL=http://localhost:8000`
- [x] Tailwind configured in vite.config.ts
- [x] Path aliases set up (@/ → src/)
- [x] All key imports should work

### 2. **Backend Configuration** ✅
- [x] .env file exists with DATABASE_URL
- [x] CORS_ORIGINS includes localhost:5173
- [x] All EEG config present

### 3. **Router Setup** ✅
- [x] index.ts has 8+ routes
- [x] beforeEach guard checks auth
- [x] Layouts properly configured
- [x] 404 route included

### 4. **Pinia Stores** ✅
- [x] auth.store.ts with login/logout
- [x] patients.store.ts with CRUD
- [x] devices.store.ts with CRUD
- [x] results.store.ts with CRUD
- [x] acquisition.store.ts with WebSocket

### 5. **API Layer** ✅
- [x] http.ts with interceptors
- [x] Bearer token injection
- [x] 401 error handling
- [x] auth.api.ts implemented
- [x] patients.api.ts implemented
- [x] devices.api.ts implemented

### 6. **UI Components** ✅
- [x] AppButton.vue with props
- [x] AppCard.vue exists
- [x] AppAlert.vue exists
- [x] Layout components exist

### 7. **Pages** ✅
- [x] LoginPage.vue with form
- [x] PatientCreatePage.vue (create/edit)
- [x] PatientDetailPage.vue
- [x] DevicesPage similar
- [x] ResultsPage similar

---

## ⚠️ Items to Check at Runtime

### The Moment You Start `npm run dev`:

```bash
✓ No TypeScript compilation errors
✓ No module resolution errors  
✓ Dev server starts on localhost:5173
✓ Page loads without 404
✓ Console (F12) is clean
```

### After Opening Browser:

```bash
✓ Login page displays
✓ Form inputs visible
✓ CSS styling applied (not broken)
✓ No 503/504 errors
```

### After Logging In:

```bash
✓ Token received from API
✓ Redirected to /acquisition
✓ Sidebar navigation visible
✓ Can click between pages
✓ localStorage/sessionStorage has token
```

### After Navigating to /patients:

```bash
✓ Table loads
✓ Patients displayed (or empty state if no data)
✓ "Nouveau patient" button visible
✓ Console clean
```

### After Creating a Patient:

```bash
✓ Form submit works
✓ POST request goes to /patients
✓ Response 200-201
✓ Redirect to /patients
✓ New patient in table
```

---

## 🚨 Potential Issues & Quick Fixes

### Issue #1: "npm install" takes forever
**Fix:** Use `npm install --legacy-peer-deps` if dependency conflicts

### Issue #2: Port 5173 already in use
**Fix:** `npm run dev -- --port 3000` (use different port)

### Issue #3: Port 8000 (backend) already in use
**Fix:** `python -m uvicorn app.main:app --port 8001` (different port)
Then update .env: `VITE_API_BASE_URL=http://localhost:8001`

### Issue #4: "Cannot find module axios"
**Fix:** `npm install axios` in neurales-web folder

### Issue #5: TypeScript error "Property doesn't exist"
**Fix:** Ensure types are imported correctly:
```typescript
import type { Patient } from '@/types'  // or from store
```

### Issue #6: "API returns 404"
- Check backend is running
- Check endpoint spelling in api/ files
- `GET /patients` or `GET /api/patients`?

### Issue #7: "401 Unauthorized"
- Token not sent with request
- Check http.ts interceptor
- Check localhost dev not production API

### Issue #8: Form doesn't validate
- Check v-if error display exists
- Check validatePatientName() is called
- Check error state updates

### Issue #9: Loading spinner forever
- Check API response code
- Check in Network tab (F12)
- Maybe API is slow (add 5s timeout)

### Issue #10: Can't login with credentials
- Check backend seed ran: `python seed_db.py`
- Check email/password exactly: admin@neurales.com / admin123
- Check database connection

---

## 🧪 Quick Test Script

Copy & paste into browser console (F12) to test:

```javascript
// Test 1: Check auth store
const auth = window.__VUE_DEVTOOLS_GLOBAL_HOOK__?.app?.config
console.log('✓ Vue DevTools found' || '✗ Vue DevTools NOT found')

// Test 2: Check Pinia stores
if (window.__PINIA__) {
  console.log('✓ Pinia working')
} else {
  console.log('✗ Pinia NOT loaded')
}

// Test 3: Check API client
if (window.__HTTP__) {
  console.log('✓ HTTP client found')
}

// Test 4: Check route params
console.log('Current route:', window.location.pathname)

// Test 5: Check token
const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
console.log('Token present:', !!token)
```

---

## 🎬 Quick Demo Test

**Before you start, test these 3 things (5 min total):**

**Test 1: Login** (2 min)
```
1. Go to http://localhost:5173
2. See login form
3. Click "Se connecter"
4. See loading state
5. Get redirected
✓ PASS if success
```

**Test 2: Navigate** (2 min)
```
1. Click "Patients" in sidebar
2. See table load
3. Click "Dispositifs"
4. Click "Résultats"
5. Click "Acquisition"
✓ PASS if no errors
```

**Test 3: Create** (1 min)
```
1. On /patients, click "Nouveau patient"
2. See form
3. Fill name: "Test"
4. Click "Créer"
5. See in table
✓ PASS if appears
```

---

## 📋 Final Pre-Exam Checks

### 1 Hour Before Exam
- [ ] Run `npm run dev` (check no errors)
- [ ] Run backend server
- [ ] Open http://localhost:5173
- [ ] Console (F12) clean?
  - [ ] No red errors
  - [ ] No security warnings
- [ ] Can login?
- [ ] Can create patient?

### 30 Min Before
- [ ] Stop and restart servers (fresh start)
- [ ] Do full test again
- [ ] Screenshot working app
- [ ] Open 5 key files in tabs

### 10 Min Before
- [ ] Take a screenshot of working app
- [ ] Do one more quick test of login
- [ ] Make sure you can navigate 3 pages
- [ ] Clean up terminal (no spam)

### Go Time!
- [ ] Start demo
- [ ] Be confident
- [ ] You've prepared! 💪

---

## 📊 Confidence Checklist

Rate these 1-5:

```
App starts without errors        [ ] 1  2  3  4  5
Login form works                 [ ] 1  2  3  4  5
Navigation between pages         [ ] 1  2  3  4  5
Patient creation works           [ ] 1  2  3  4  5
Error messages display           [ ] 1  2  3  4  5
Code is understandable           [ ] 1  2  3  4  5
Can explain architecture         [ ] 1  2  3  4  5
Vue/TypeScript concepts clear    [ ] 1  2  3  4  5
Store pattern understood         [ ] 1  2  3  4  5
Can show key files               [ ] 1  2  3  4  5

TARGET: 35+ for good confidence
```

---

## 🚨 "Help, something's broken!" 

### Systematic Debugging (10 min max)

**Step 1: Check Console (F12)**
```
- Read red error messages
- Google the error
- Or check QUICK_FIXES.md
```

**Step 2: Check Network Tab (F12)**
```
- Look for failed requests (red)
- Check response codes (500?)
- Read error response from API
```

**Step 3: Check Application Tab (F12)**
```
- Look in localStorage
- Is token there?
- What's the value?
```

**Step 4: Check Backend Terminal**
```
- Any error messages?
- Is it actually running?
- Port correct?
```

**Step 5: Format & Restart**
```bash
# If all else fails:
pkill -f uvicorn          # Kill backend
pkill -f "npm run dev"    # Kill frontend
npm run dev               # Restart
python -m uvicorn ...     # Restart
```

---

## ✨ You're Covered!

With these checklists, you should be able to:
1. ✓ Verify app works before exam
2. ✓ Quickly debug any issues
3. ✓ Keep calm if something breaks
4. ✓ Have backup explanation

**Remember:**
- Even if something breaks mid-demo, you can still:
  - Show your code
  - Explain what it does
  - Discuss the architecture
  - Answer questions

Your code is solid. The professor will recognize that.

---

**You've got this! 🎓✨**

Last Checked: February 18, 2026
