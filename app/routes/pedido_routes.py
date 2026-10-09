from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.controllers.pedido_controller import (EstoqueInsuficiente,
                                               PedidoController)
# o mesmo DoceController das rotas de doce: estoque compartilhado
from app.routes.doce_routes import controller as doce_controller

router = APIRouter(prefix='/api', tags=['pedidos'])
controller = PedidoController(doce_controller)


class ItemRequest(BaseModel):
    doce_id: int
    quantidade: int    # un (doce por unidade) ou gramas (doce por peso)


class PedidoRequest(BaseModel):
    itens: list[ItemRequest]


@router.get('/pedidos')
def listar():
    return controller.listar()


@router.get('/pedidos/{id}')
def buscar(id: int):
    pedido = controller.buscar(id)
    if pedido is None:
        raise HTTPException(404, 'pedido não encontrado')
    return pedido


@router.post('/pedidos', status_code=201)
def registrar_venda(dados: PedidoRequest):
    itens = [i.model_dump() for i in dados.itens]
    inexistentes = controller.ids_inexistentes(itens)
    if inexistentes:
        raise HTTPException(404, f'doce(s) não encontrado(s): {inexistentes}')
    try:
        return controller.criar(itens)
    except EstoqueInsuficiente as erro:   # antes de ValueError: e filha dele
        raise HTTPException(409, str(erro))
    except ValueError as erro:
        raise HTTPException(422, str(erro))


@router.get('/relatorio/ticket-medio')
def ticket_medio():
    relatorio = controller.ticket_medio()
    if relatorio is None:
        raise HTTPException(404, 'nenhuma venda registrada')
    return relatorio
