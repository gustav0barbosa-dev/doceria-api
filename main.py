from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.doce_routes import router as doce_router
from app.routes.pedido_routes import router as pedido_router

app = FastAPI(title='Doceria API', version='1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(doce_router)
app.include_router(pedido_router)
