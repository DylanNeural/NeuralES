# 🎬 Script Démo Examen (15 minutes)

## ⏱️ Timeline

```
0:00-1:00  - Intro + Architecture overview
1:00-3:00  - démo fonctionnelle (login → CRUD)
3:00-8:00  - Code walkthrough (store, API, components)
8:00-15:00 - Q&A + Explications téchniques
```

---

## 📋 Checklist avant examen

- [ ] `npm run dev` fonctionne ✓
- [ ] Console F12 sans erreurs
- [ ] Backend running sur `http://localhost:8000`
- [ ] Credentials de test: `admin@neurales.com` / `admin123`
- [ ] Avoir `.env` correctement configuré
- [ ] Screenshot des pages clés prêts

---

## 🚀 Démo Fonctionnelle (2 min)

### 1. **Login Page** (30s)
```
➊ Ouvrir http://localhost:5173
➋ Voir le formulaire de connexion
➌ Observer les champs pré-remplis (admin@neurales.com / admin123)
➍ Montrer v-model sur les inputs
➎ Cliquer "Se connecter"
➏ Voir le loading state (button disabled + spinner)
➐ Attendre redirection vers /acquisition
```

**À dire:**
> "Le formulaire utilise v-model pour la liaison bidirectionnelle, et j'ai une validation basic (required). Le token Bearer est sauvegardé automatiquement dans le store."

---

### 2. **Navigation Sidebar** (20s)
```
➊ Montrer le layout sidebar (8 liens de nav)
➋ Cliquer sur /patients
➊ Montrer le page title qui change dynamiquement
```

**À dire:**
> "La navigation change le titre dynamiquement avec un computed property. Les routes sont protégées - si t'es pas logged, tu reviens au login."

---

### 3. **Liste Patients (30s)**
```
➊ Voir la table des patients
➋ Montrer le v-for sur la ligne <tr>
➌ Cliquer "Nouveau patient"
➍ Voir form page
```

**À dire:**
> "J'utilise v-for pour récursive les patients depuis le store. Chaque ligne a un onClick qui navigue au détail."

---

### 4. **Formulaire Patient** (60s)
```
➊ Remplir le formulaire
   - Nom: "Dupont"
   - Prénom: "Jean"
   - SSN: "1234567890123"
   - Date naissance, etc.

➋ Montrer les validations en temps réel
➌ Submitter le formulaire

➍ Observer:
   - Button disabled + "Création..."
   - Les données envoyées via POST
   - Redirection vers /patients
   - Nouveau patient en top de liste
```

**À dire:**
> "Le formulaire utilise v-model pour binding et la validation est gérée dans utils/form-validation.ts. Après submit, les données sont envoyées à l'API via le store Pinia."

---

### 5. **Détail + Édition Patient** (20s)
```
➊ Cliquer sur patient dans liste
➋ Voir ses détails
➌ Cliquer "Modifier"
➍ Voir form pré-rempli
➎ Changer le nom
➏ Submit
➐ Redirection vers détail avec les nouvelles données
```

**À dire:**
> "L'édition utilise la même forme mais pré-remplie. Isomorphic pages (PatientCreatePage pour create ET edit)."

---

### 6. **Erreur Handling** (15s)
```
➊ Aller à /patients/99999 (ID qui existe pas)
➋ Voir l'erreur rouge affichée
➌ Montrer le message d'erreur explicite
```

**À dire:**
> "J'ai une gestion d'erreurs globale dans le HTTP interceptor et chaque store action capture et affiche les erreurs à l'utilisateur."

---

## 💻 Code Walkthrough (4 min)

### **1. Auth Store** (1 min) - CECI EST LE PLUS IMPORTANT !!

Ouvrir [src/stores/auth.store.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Fstores%2Fauth.store.ts)

```typescript
export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null as User | null,
    isReady: false,
    accessToken: null as string | null,
  }),
  getters: {
    isLogged: (state) => !!state.accessToken,
    displayName: (state) => (state.user ? `${state.user.prenom} ${state.user.nom}` : ""),
  },
  actions: {
    async login(email: string, password: string) {
      const res = await AuthAPI.login({ email, password });
      this.accessToken = res.access_token;
      setAccessToken(res.access_token);  // Ajoute le token au HTTP client
      await this.fetchMe();
      this.isReady = true;
    },
  }
});
```

**À dire:**
> "Je définis mon état global avec Pinia:
> - State: user, token, isReady
> - Getters: computed properties (isLogged, displayName)
> - Actions: async methods appelées depuis les composants
>
> Quand l'utilisateur se login, je:
> 1. Appelle l'API
> 2. Sauvegarde le token
> 3. L'ajoute automatiquement aux futurs requêtes (interceptor)
> 4. Cherche les infos utilisateur
> 5. Marque comme prêt"

---

### **2. HTTP Client** (1 min)

Ouvrir [src/api/http.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Fapi%2Fhttp.ts)

```typescript
export const http = axios.create({...});

// Intercepteur: ajoute token à chaque requête
http.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Intercepteur: gère erreurs globales
http.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
```

**À dire:**
> "J'utilise Axios avec 2 intercepteurs:
> 1. **Request**: ajoute automatiquement le Bearer token
> 2. **Response**: gère les erreurs 401 (redirection login)
>
> Cela centralise la gestion auth donc je dois pas la refaire partout."

---

### **3. Patients Store** (1 min)

Ouvrir [src/stores/patients.store.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Fstores%2Fpatients.store.ts)

```typescript
export const usePatientsStore = defineStore("patients", () => {
  const items = ref<Patient[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  
  const fetchPatients = async (limit = 50, offset = 0) => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await api.get("/patients", { params: { limit, offset } });
      items.value = response.data || [];
    } catch (err: any) {
      error.value = err.response?.data?.detail || "Erreur de chargement";
    } finally {
      isLoading.value = false;
    }
  };
  
  return { items, isLoading, error, fetchPatients };
});
```

**À dire:**
> "Chaque ressource (patients, devices, results) a un store Pinia dédié.
> Je gère:
> - **items**: le listage
> - **isLoading**: pour le UI feedback
> - **error**: pour afficher les erreurs
>
> Chaque action a un try/catch et marque isLoading pour que le UI peur afficher un spinner."

---

### **4. Router avec Guards** (1 min)

Ouvrir [src/router/index.ts](..%2FneuralES%2Fneurales-web%2Fsrc%2Frouter%2Findex.ts)

```typescript
router.beforeEach(async (to) => {
  const auth = useAuthStore();
  
  if (!auth.isReady) {
    await auth.initialize();
  }
  
  if (!to.meta.public && !auth.isLogged) {
    return "/login";
  }
});
```

**À dire:**
> "Je vérify l'auth avant chaque navigation:
> 1. Si pas prêt, j'initialise (refresh token)
> 2. Si route protégée ET pas logged → redirection /login
> 3. Routes publiques (login) ont `meta: { public: true }`"

---

### **5. Component Props** (1 min - si temps)

Ouvrir [src/components/ui/AppButton.vue](..%2FneuralES%2Fneurales-web%2Fsrc%2Fcomponents%2Fui%2FAppButton.vue)

```vue
<script setup lang="ts">
const props = defineProps({
  type: { type: String, default: 'button' },
  variant: { type: String, default: 'primary' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
});
</script>
```

**À dire:**
> "Les composants réutilisables comme AppButton ont des props typées.
> - type: HTML button type
> - variant: primary/secondary/danger (différents styles)
> - loading: affiche loader et désactive le button
>
> Ça permet de réutiliser le composant dans les formulaires avec juste `<AppButton :loading='isLoading'>Créer</AppButton>`"

---

## 🎯 Questions Probables et Réponses

### **Q: Pourquoi TypeScript?**
A: Typage statique = moins de bugs, meilleure auto-complétion, et facilite la maintenance. Avec TypeScript, je type mes API responses et state, donc j'ai de garanties côté compile-time.

### **Q: Comment gères les erreurs réseau?**
A: Try/catch dans chaque action store. Je capture le message d'erreur sur `error.response?.data?.detail` et j'affiche à l'utilisateur. Si c'est 401, l'interceptor HTTP me redirige au login.

### **Q: Pourquoi Pinia et pas Vuex?**
A: Pinia est plus moderne et plus simple. Pas de mutations, juste actions et etats. Plus facile à tester aussi.

### **Q: Comment communiques les données entre composants?**
A: 
- **Parents → Enfants**: Props
- **Enfants → Parents**: Events ($emit)
- **Global state**: Pinia stores
- **Layout components**: Provide/Inject (si besoin)

### **Q: Comment protèges l'authentification?**
A: 
- Routes guards vérifient `auth.isLogged` avant navigation
- 401 responses redirigent au login automatiquement
- Token en HTTP-only cookies (idéal) ou localStorage
- Bearer token dans Authorization header pour requêtes

### **Q: Pourquoi v-model sur les inputs?**
A: Binding bidirectionnel. Quand l'utilisateur tape, la variable ref se met à jour. Quand je change la variable programmatiquement, l'input se met à jour. Beaucoup plus simple que des event listeners.

### **Q: Comment gères les listes avec v-for?**
A: 
```vue
<tr v-for="patient in patients" :key="patient.patient_id">
```
La clé `:key` est importante pour la performance et les transitions.

### **Q: C'est quoi le computed property pour le titre?**
A: 
```typescript
const pageTitle = computed(() => {
  if (route.path.startsWith("/patients")) return "Patients";
  return "Dashboard";
});
```
Le computed recalcul automatiquement quand `route.path` change (reactive).

---

## ⚠️ Choses à NE PAS dire

- ❌ "Je sais pas comment ça marche"
- ❌ "j'ai copié du code from le web sans comprendre"
- ❌ "mon projet est pas fini"
- ❌ "Je vais tester ça pour la première fois pendant l'examen" 😱

---

## ✅ Choses À dire

- ✅ "J'utilise le pattern [X] parce que..."
- ✅ "Je peux vous montrer le code qui fait..."
- ✅ "Les points forts de mon architecture son..."
- ✅ "Si j'avais plus de temps, j'ajouterais des tests"
- ✅ "En production, j'utiliserais [X]"

---

## 🎬 Commandes pour la démo

```bash
# Terminal 1: Frontend
cd neurales-web
npm install  # si besoin
npm run dev

# Terminal 2: Backend (si le backend est pas déjà running)
cd backend
python3 -m venv venv
source venv/bin/activate  # ou `venv\Scripts\activate` sur Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

---

## 📸 Screenshots à préparer

Faire des screenshots de:
- [ ] Login page (formulaire)
- [ ] Patients list + table
- [ ] Patient create form
- [ ] Patient detail
- [ ] Router navigation
- [ ] Console (F12) - pas d'erreurs
- [ ] Auth store dans Vue DevTools

---

## ⏰ Timing

- **2 min**: Démo de la démo (login → CRUD)
- **5 min**: Code show (stores, API, components)
- **3 min**: Explications techniques
- **5 min**: Q&A

**Total: 15 minutes** ✓

---

Generated: 2026-02-18 (la veille de l'examen!)

**BON COURAGE! 💪**
