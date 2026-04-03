# 🔧 Fixes Rapides Avant Examen

Des problèmes possibles et **solutions en 2 minutes**:

---

## 1. ❌ "npm run dev" ne marche pas

**Solution:**
```bash
cd neurales-web
npm install  # Réinstalle les dépendances
npm run dev
```

**Si ça freeze:** (Ctrl+C en terminal, puis):
```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 2. ❌ "Connection refused" au backend

**Vérifies que:**
- [ ] Backend running: `http://localhost:8000` (terminal séparé)
- [ ] Terminal backend dit `Uvicorn running on http://0.0.0.0:8000`
- [ ] Base de données accessible (SSH tunnel si nécessaire)

**Solution:**
```bash
# Terminal 2 - Backend
cd backend
pip install -r requirements.txt  # si besoin
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. ❌ "L'API retourne 500"

**Vérifies:**
```bash
# Terminal backend - regarde les erreurs
# Cherche: "ERROR", "Traceback", "Exception"
```

**Solutions classiques:**
- [ ] Database not running: SSH tunnel status
- [ ] Migration pas faite: `python seed_db.py`
- [ ] Requirements pas installés: `pip install -r requirements.txt`

---

## 4. ❌ Erreurs console (F12)

### Problème: "CORS error"
```
Access to XMLHttpRequest... CORS policy
```

**Solution:** Vérifies que backend a `http://localhost:5173` dans CORS_ORIGINS:
```python
# backend/.env
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Problème: "Module not found"
```
Cannot find module '@/stores/auth.store'
```

**Solution:** Vérifies tsconfig.json:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## 5. ❌ "Login échoue"

**Vérifies:**
- [ ] Email exact: `admin@neurales.com`
- [ ] Password exact: `admin123`
- [ ] Backend running
- [ ] Database seed a créé le user: 
```bash
python seed_db.py  # dans backend/
```

**Test manuellement:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@neurales.com","password":"admin123"}'
```

Devrait retourner:
```json
{"access_token": "eyJ....", "token_type": "bearer"}
```

---

## 6. ❌ "Les patients ne s'affichent pas"

1. Vérifies la console (F12) pour erreurs API
2. Test l'endpoint:
```bash
curl http://localhost:8000/patients \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. Si 501 "Not Implemented": l'endpoint existe pas
4. Si 500: bug backend (regarde terminal backend)

---

## 7. ❌ "Le formulaire ne remonte pas erreurs"

Vérifie qu'il y a bien `v-if="error"` dans le template:
```vue
<div v-if="error" class="text-red-600">
  {{ error }}
</div>
```

Si manquant → ajoute-le!

---

## 8. ❌ "Les données se rafraîchissent pas"

Le store oublie peut-être d'appeler la fetch:
```vue
<script setup>
const patients = usePatientsStore()

onMounted(() => {
  patients.fetchPatients()  // ← IMPORTANT!
})
</script>
```

---

## 9. ❌ "Débug modes" pour l'examen

### Désactiver les validations pour rapidement tester:
Cherche la validation et comment-la:
```typescript
// export const validatePatientName = (name: string) => {
//   if (!name) return ["Nom requis"];
// }
```

### Utiliser localStorage pour simuler token:
```javascript
// Dans console (F12)
localStorage.setItem('access_token', 'test-token')
```

### Désactiver animations si c'est lent:
```css
/* Ajoute dans App.vue */
* {
  animation-duration: 0s !important;
  transition-duration: 0s !important;
}
```

---

## 10. ✅ Commande Finale Before Exam

Lanc **ceci 30 minutes avant l'examen:**

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend (dans un nouveau terminal)
cd neurales-web
npm run dev

# Terminal 3: Ouvre le navigateur
# Navigue à http://localhost:5173
```

**Vérifies:**
- [ ] Console F12 = zéro erreurs 
- [ ] Login fonctionne
- [ ] Patients liste se charge
- [ ] Créer un patient fonctionne
- [ ] Page se rafraîchit - données persistent

**Si tout = ✓, tu es prêt!**

---

## 🚨 DERNIER RECOURS (2min avant examen)

Si ça marche TOUJOURS pas:

```bash
# Force reload
npm run build  # Build statique
npm run preview  # Serve le build

# Ou démonstration offline:
# Prépare des screenshots des pages
# Explique le code même sans exécution
```

---

## Checklist Technique (15 min)

- [ ] Backend running `http://localhost:8000`
- [ ] Frontend running `http://localhost:5173`
- [ ] Console vide d'erreurs
- [ ] Login fonctionne
- [ ] Peut créer un patient
- [ ] Peut éditer un patient
- [ ] Peut voir les détails
- [ ] Navigation fonctionne
- [ ] Logout fonctionne

---

**DEVRAIT TOUT MARCHER! 💪**
