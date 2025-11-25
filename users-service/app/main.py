from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings

from app.routes import auth_routes, user_routes



app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount('/static', StaticFiles(directory=settings.static_dir), name='static')

app.include_router(auth_routes.router)
app.include_router(user_routes.router)



@app.get('/')
def root():
    return {
        'message': 'Welcome to fastapi shop API',
        'docs': '/api/docs',
    }

@app.get('/health')
def health_check():
    return {'status': 'healthy'}