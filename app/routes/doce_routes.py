from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.doce_controller import DoceController

router = APIRouter(prefix='/api', tags=['doces'])
controller = DoceController()


class DoceRequest(BaseModel):
    nome: str
    categoria: str
    tipo: str          # 'unidade' ou 'peso'
    preco: float
    estoque: int


@router.get('/doces')
def listar():
    return controller.listar()


"""
===========|excedito o limite de rotas proposto pelo desafio.|=============
@router.get('/doces/categoria/{categoria}')
def listar_por_categoria(categoria: str):
    doces = controller.listar_por_categoria(categoria)
    if not doces:
        raise HTTPException(404, 'nenhum doce nessa categoria')
    return doces
"""

@router.post('/doces', status_code=201)
def cadastrar(dados: DoceRequest):
    if controller.existe_nome(dados.nome):
        raise HTTPException(409, 'já existe um doce com esse nome')
    try:
        return controller.cadastrar(dados.nome, dados.categoria, dados.tipo,
                                    dados.preco, dados.estoque)
    except ValueError as erro:
        raise HTTPException(422, str(erro))


@router.get('/estoque')
def consultar_estoque():
    return controller.consultar_estoque()
