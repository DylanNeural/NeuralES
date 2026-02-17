from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.api import auth_router, organisations_router, eeg_router, health_router, acquisition_router

# Créer l'app FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NeuralES Backend</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 60px;
                text-align: center;
                max-width: 600px;
            }
            
            .logo {
                font-size: 60px;
                margin-bottom: 20px;
            }
            
            h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                color: #666;
                font-size: 1.1em;
                margin-bottom: 40px;
            }
            
            .links {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            a {
                display: inline-block;
                padding: 15px 30px;
                margin: 10px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }
            
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
                border: 2px solid #667eea;
            }
            
            .btn-secondary:hover {
                background: #667eea;
                color: white;
                transform: translateY(-2px);
            }
            
            .info {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 20px;
                margin-top: 40px;
                text-align: left;
                border-radius: 10px;
            }
            
            .info h3 {
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .info p {
                color: #666;
                line-height: 1.6;
                margin: 8px 0;
            }
            
            .version {
                color: #999;
                font-size: 0.9em;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🧠</div>
            <h1>NeuralES</h1>
            <p class="subtitle">Bienvenue sur le backend NeuralES</p>
            
            <div class="links">
                <a href="/docs" class="btn-primary">📖 Documentation API (Swagger)</a>
                <a href="/redoc" class="btn-secondary">📚 ReDoc Documentation</a>
            </div>
            
            <div class="info">
                <h3>🚀 Démarrage Rapide</h3>
                <p><strong>API Base:</strong> /api/v1</p>
                <p><strong>Status:</strong> <span style="color: #28a745;">✓ En ligne</span></p>
                <p><strong>Documentation:</strong> Consultez /docs pour explorer les endpoints</p>
            </div>
            
            <p class="version">Version """ + settings.app_version + """</p>
        </div>
    </body>
    </html>
    """

# Enregistrer les routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(organisations_router)
app.include_router(eeg_router)
app.include_router(acquisition_router)

