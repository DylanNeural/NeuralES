# ✅ Checklist Exam-Ready (Print this!)

Imprime cette page et checks au fur et à mesure!

---

## 📊 Critères d'Évaluation (sur 14)

### Page à tester pour chaque critère:

| # | Critère | Page Test | Status | Notes |
|---|---------|-----------|--------|-------|
| 1 | Organisation dossiers | Tous `/src/*` | ✅ | Structure scalable |
| 2 | Composants réutilisables | `/components/ui/*` | ✅ | AppButton, AppCard, AppAlert |
| 3 | Noms explicites | Code review | ✅ | fetchPatients, toggleElectrode... |
| 4 | Communication composants | DetailPages | ✅ | Props, Events, Pinia |
| 5 | Directives Vue (v-if, v-for, v-model...) | LoginPage, FormPages | ✅ | Visible dans templates |
| 6 | Formulaire fonctionnel | `/login`, `/patients/new` | 🔴 | **À VÉRIFIER** |
| 7 | Vue Router | Navigation sidebar | ✅ | 8 routes, guards |
| 8 | Pinia Store | F12 → VueDevTools | ✅ | 5 stores actifs |
| 9 | Appels API | Network tab F12 | ✅ | HTTP client typé |
| 10 | Gestion erreurs | Try/catch, v-if error | ⚠️ | **À TESTER** |
| 11 | UX fluide | User interactions | 🔴 | **À VÉRIFIER** |
| 12 | Pas de bugs | Full test | 🔴 | **À TESTER** |
| 13 | Explications | Préparé | ✅ | Script de démo |
| 14 | Tests (bonus) | unit/e2e (si présent) | ❌ | Non prioritaire |

---

## 🚀 Test Plan (30 min avant examen)

### **Phase 1: Setup** (5 min)
```bash
# Terminal 1
cd backend && python -m uvicorn app.main:app --reload

# Terminal 2  
cd neurales-web && npm run dev

# Terminal 3
# Ouvre Firefox/Chrome DevTools (F12)
```

### **Phase 2: Login Test** (2 min)
- [ ] Navigue à `http://localhost:5173`
- [ ] Page login affichée
- [ ] Email pré-rempli: `admin@neurales.com` ✓
- [ ] Password pré-rempli: `admin123` ✓
- [ ] Clique "Se connecter"
- [ ] Button dit "Connexion..." (loading state) ✓
- [ ] ⏳ Attend 2-3 secondes
- [ ] Redirection vers `/acquisition` ✓
- [ ] Console (F12) = zéro erreurs ✓

**Si échoue:** Voir [QUICK_FIXES.md](./QUICK_FIXES.md) section "Login échoue"

---

### **Phase 3: Navigation Test** (3 min)
- [ ] Clique "Patients" dans sidebar
- [ ] Page title change → "Patients" ✓
- [ ] Table des patients affichée ✓
- [ ] Clique "Dispositifs" → Title change ✓
- [ ] Clique "Résultats" → Title change ✓
- [ ] Clique "Acquisition" → Title change ✓
- [ ] Clique "Tableau de bord" → Title change ✓
- [ ] Console = zéro erreurs ✓

**À dire à l'examen:**
> "Navigation avec Vue Router + computed property pour titre dynamique"

---

### **Phase 4: Patient List Test** (2 min)
- [ ] Sur `/patients`
- [ ] Attend le chargement (spinner si visible)
- [ ] Table affichée avec patients
- [ ] Chaque ligne a:
  - [ ] Nom + Prénom
  - [ ] Bouton "Voir" (entité)
  - [ ] Bouton "Modifier" (edit)
  - [ ] Bouton "Supp" (delete)
- [ ] Console = zéro erreurs ✓

**À dire:**
> "v-for='patient in patients' + :key='patient.patient_id' pour la performance"

---

### **Phase 5: Create Patient Test** (5 min)
- [ ] Clique "Nouveau patient"
- [ ] Form s'affiche:
  - [ ] Input: Nom
  - [ ] Input: Prénom
  - [ ] Input: Date naissance
  - [ ] Input: SSN
  - [ ] Select: Service (si applicable)
  - [ ] Select: Médecin (si applicable)
  - [ ] Textarea: Remarques
- [ ] Remplis les champs:
  ```
  Nom: "TestPatient"
  Prénom: "TestFN"
  SSN: "1234567890123"
  Date: "1990-01-01"
  ```
- [ ] Clique "Créer"
- [ ] Button dit "Création..." (loading) ✓
- [ ] ⏳ Attend chargement
- [ ] Redirection vers `/patients` ✓
- [ ] Nouveau patient visible en haut de table ✓
- [ ] Console = zéro erreurs ✓

**À dire:**
> "v-model sur inputs + validation avant submit + gestion loading state"

---

### **Phase 6: Edit Patient Test** (3 min)
- [ ] Clique sur un patient dans la table (button "Voir")
- [ ] Page détail s'affiche:
  - [ ] Tous les champs affichés
  - [ ] Button "Modifier"
  - [ ] Button "Suppr" (danger)
- [ ] Clique "Modifier"
- [ ] Form s'affiche pré-remplie:
  - [ ] Nom = le nom du patient ✓
  - [ ] Prénom = prénom ✓
  - [ ] Autres champs pré-remplis ✓
- [ ] Change le Nom: "TestPatient2"
- [ ] Clique "Mettre à jour"
- [ ] Button dit "Mise à jour..." ✓
- [ ] Redirection vers détail ✓
- [ ] Nom mis à jour ✓
- [ ] Console = zéro erreurs ✓

**À dire:**
> "Édition utilise la même form, pré-remplie avec les données actuelles"

---

### **Phase 7: Error Handling Test** (2 min)

**Test: API error**
- [ ] Sur `/patients`
- [ ] Ouvre DevTools → Network tab
- [ ] Cherche une requête GET `/patients`
- [ ] Right-click → Block (simule erreur)
- [ ] Refresh la page
- [ ] Message d'erreur rouge affichée ✓
- [ ] Text explicite: "Erreur lors du chargement" ✓

**À dire:**
> "Try/catch dans store + error state affiché au user"

---

### **Phase 8: Devices Page Test** (2 min)
- [ ] Clique "Dispositifs"
- [ ] Similar flow à patients:
  - [ ] List affichée ✓
  - [ ] Boutons CRUD visibles ✓
  - [ ] Créer/Modifier/Supp fonctionne ✓

---

### **Phase 9: Results Page Test** (2 min)
- [ ] Clique "Résultats"
- [ ] Similar flow

---

### **Phase 10: Logout Test** (1 min)
- [ ] Regarde le sidebar (bas)
- [ ] Button "Déconnexion"
- [ ] Clique
- [ ] Redirection vers `/login` ✓
- [ ] Auth state réinitialisé ✓
- [ ] Console = zéro erreurs ✓

---

## 🎥 Code Show Points

Prépare ces fichiers à montrer:

- [ ] [src/stores/auth.store.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Fstores%2Fauth.store.ts) - **Main show!**
- [ ] [src/router/index.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Frouter%2Findex.ts) - Routes + guards
- [ ] [src/api/http.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Fapi%2Fhttp.ts) - HTTP client
- [ ] [src/pages/patients/PatientCreatePage.vue](..%2FneuralES%2Fneurales-web%2Fsrc%2Fpages%2Fpatients%2FPatientCreatePage.vue) - Form example
- [ ] [src/components/ui/AppButton.vue](..%2FneuralES%2Fneurales-web%2Fsrc%2Fcomponents%2Fui%2FAppButton.vue) - Reusable component

---

## 🔴 **PROBLÈMES À NE PAS LAISSER PASSER**

### ❌ Console errors
```
Uncaught TypeError: cannot read property 'xyz' of undefined
```
**Solution:** Trouve la ligne → ajoute undefined check

### ❌ API returns 500
```
Error: 500 Internal Server Error
```
**Solution:** Check backend terminal pour error message

### ❌ Form ne soumet pas
```
Button cliqué, rien happens, console silent
```
**Solution:** Vérifies `@submit.prevent` sur form + `handleSubmit` existe

### ❌ Router ne navigue pas
```
URL change dans address bar mais page pas mise à jour
```
**Solution:** Vérifies `<RouterView />` existe dans layout

### ❌ Erreurs typage TypeScript
```
Type 'Patient' does not have property 'xyz'
```
**Solution:** Vérifies que types matchent l'API response

---

## 📋 Checklist Finale (10 min avant examen)

```
PRÊT À PASSER L'EXAMEN?

☐ Backend running sans erreur
☐ Frontend running sur localhost:5173
☐ Console F12 = VIDE (zéro erreurs)
☐ Login fonctionne
☐ Navigation 5/5 pages fonctionne
☐ List patients affichée
☐ Créer patient fonctionne (visible en table)
☐ Éditer patient fonctionne
☐ Détail patient affichage OK
☐ Devices PAGE fonctionne
☐ Results PAGE fonctionne
☐ Logout fonctionne (redirect login)
☐ Code files ouverts et prêts à montrer
☐ Script de démo mémorisé / imprimé
```

**Si ☑️ tous = LET'S GO!** 🚀

---

## 🎬 Pour la Démo (Have ready!)

**Script court (2 min):**
1. Login avec admin@neurales.com / admin123 → Redirection /acquisition
2. Click Patients → Table affichée
3. Click "Nouveau patient" → Form
4. Remplir + Submit → Nouveau patient en table
5. Click patient → Détail
6. Click "Modifier" → Edit form pré-rempli
7. Changer + Submit → Détail mis à jour

**Code show (3 min):**
1. Ouvrir `auth.store.ts` → Montrer state/getters/actions
2. Montrer `LoginPage.vue` → v-model + @submit
3. Montrer `http.ts` → Intercepteurs
4. Montrer `router/index.ts` → beforeEach guard

---

## 💡 Quick Talking Points

> **"Mon app a une architecture de 3 couches:**
> - **UI Layer:** Pages + Reusable components (AppButton, AppCard)
> - **State Layer:** Pinia stores pour each ressource (patients, devices, auth)
> - **API Layer:** Axios client centralisé avec intercepteurs
>
> **Chaque action:**
> 1. Component appelle store action
> 2. Store fait try/catch sur API call
> 3. Store met à jour state + error
> 4. Component re-render automatiquement (Vue reactive)"

---

**VOUS ÊTES OFFICIELLEMENT PRÊT! 🎓**

(Imprimez cette page et garder pendant l'examen comme guide!)
