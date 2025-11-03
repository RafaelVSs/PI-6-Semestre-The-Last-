from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.config import settings

router = APIRouter(tags=["Home"])


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Endpoint raiz com informações sobre a API e links clicáveis para documentação"""
    base_url = str(request.base_url).rstrip('/')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.PROJECT_NAME}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #007bff;
                padding-bottom: 10px;
            }}
            .info {{
                margin: 20px 0;
                color: #666;
            }}
            .links {{
                margin-top: 30px;
            }}
            .link-button {{
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s;
            }}
            .link-button:hover {{
                background-color: #0056b3;
            }}
            .version {{
                color: #999;
                font-size: 0.9em;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 {settings.PROJECT_NAME}</h1>
            <div class="info">
                <p><strong>Descrição:</strong> API para controle de abastecimento de frotas de caminhões</p>
                <p class="version">Versão: {settings.PROJECT_VERSION}</p>
            </div>
            
            <div class="links">
                <h2>📚 Links Úteis</h2>
                <a href="{base_url}/docs" class="link-button">📖 Documentação Interativa (Swagger)</a>
                <a href="{base_url}/redoc" class="link-button">📘 Documentação (ReDoc)</a>
                <a href="{base_url}/healthcheck" class="link-button">💚 Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/healthcheck")
async def health_check():
    """Endpoint de health check para monitoramento"""
    return {"status": "ok"}
