from app.data.pedidos_mock import PEDIDOS


class Pedido:
    """Uma venda. Associacao: guarda os OBJETOS Doce (nao os ids), cada um
    com a quantidade vendida. Pedido -> Doce: 0..* para 1..*.
    """

    def __init__(self, id, itens, efetivado=False):
        self._id = id
        self._efetivado = False
        self._itens = []
        self.alterar_itens(itens)
        self._efetivado = efetivado

    # --- leitura ---
    def mostrar_id(self):
        return self._id

    def mostrar_itens(self):
        return list(self._itens)

    def esta_efetivado(self):
        return self._efetivado

    # --- alteracao, com regra ---
    def alterar_itens(self, itens):
        """itens: lista de (doce, quantidade). Doces repetidos sao somados."""
        if self._efetivado:
            raise ValueError('pedido já efetivado não pode ser alterado')
        if not itens:
            raise ValueError('pedido não pode ser vazio')
        somados = {}
        for doce, quantidade in itens:
            doce.validar_quantidade(quantidade)
            chave = doce.mostrar_id()
            anterior = somados[chave][1] if chave in somados else 0
            somados[chave] = (doce, anterior + quantidade)
        self._itens = list(somados.values())

    # --- comportamento ---
    def calcular_total(self):
        """Soma os subtotais. Cada doce sabe se cobrar: nenhum if de tipo."""
        return round(sum(doce.calcular_subtotal(quantidade)
                         for doce, quantidade in self._itens), 2)

    def efetivar(self):
        """Confirma a venda: verifica o estoque de TODOS os itens e so entao
        desconta. Se faltar um, nada e descontado."""
        if self._efetivado:
            raise ValueError('pedido já foi efetivado')
        for doce, quantidade in self._itens:
            doce.verificar_estoque(quantidade)
        for doce, quantidade in self._itens:
            doce.retirar_estoque(quantidade)
        self._efetivado = True

    def __repr__(self):
        return f'Pedido({self._id}, {len(self._itens)} itens)'


def carregar_pedidos(doces):
    """Liga os ids do mock aos objetos Doce que ja existem (como um JOIN).

    Recebe a lista de doces para que pedidos e estoque enxerguem os MESMOS
    objetos. Vendas do historico ja estao efetivadas: nao mexem no estoque.
    """
    por_id = {d.mostrar_id(): d for d in doces}
    return [Pedido(p['id'],
                   [(por_id[i['doce_id']], i['quantidade'])
                    for i in p['itens']],
                   efetivado=True)
            for p in PEDIDOS]
