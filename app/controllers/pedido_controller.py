# a rota so conhece o controller: por isso o erro e reexportado daqui
from app.models.doce import EstoqueInsuficiente  # noqa: F401
from app.models.pedido import Pedido, carregar_pedidos


class PedidoController:
    def __init__(self, doce_controller):
        # os pedidos precisam enxergar os MESMOS objetos Doce do estoque
        self._doces = doce_controller
        self._pedidos = carregar_pedidos(doce_controller.listar_objetos())

    def listar(self):
        return [self._para_dicionario(p) for p in self._pedidos]

    def buscar(self, id):
        for pedido in self._pedidos:
            if pedido.mostrar_id() == id:
                return self._para_dicionario(pedido)
        return None

    def ids_inexistentes(self, itens):
        """Ids de doce pedidos que nao existem (lista vazia: todos existem)."""
        return [i['doce_id'] for i in itens
                if self._doces.buscar_objeto(i['doce_id']) is None]

    def criar(self, itens):
        """itens: [{'doce_id', 'quantidade'}]. Antes, use ids_inexistentes.
        Pode levantar ValueError / EstoqueInsuficiente (regras da model)."""
        resolvidos = [(self._doces.buscar_objeto(i['doce_id']), i['quantidade'])
                      for i in itens]
        pedido = Pedido(self._proximo_id(), resolvidos)
        pedido.efetivar()
        self._pedidos.append(pedido)
        return self._para_dicionario(pedido)

    def ticket_medio(self):
        if not self._pedidos:
            return None
        totais = [p.calcular_total() for p in self._pedidos]
        return {
            'pedidos': len(totais),
            'faturamento': round(sum(totais), 2),
            'ticket_medio': round(sum(totais) / len(totais), 2),
        }

    def _proximo_id(self):
        return max((p.mostrar_id() for p in self._pedidos), default=0) + 1

    def _para_dicionario(self, pedido):
        return {
            'id': pedido.mostrar_id(),
            'itens': [{
                'doce': doce.mostrar_nome(),
                'quantidade': quantidade,
                'unidade': doce.mostrar_unidade_estoque(),
                'subtotal': doce.calcular_subtotal(quantidade),
            } for doce, quantidade in pedido.mostrar_itens()],
            'total': pedido.calcular_total(),
        }
