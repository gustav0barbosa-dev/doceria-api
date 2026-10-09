from app.data.doces_mock import DOCES


class EstoqueInsuficiente(ValueError):
    """E um ValueError (regra violada), mas com nome proprio para que a
    rota consiga separar 'conflito com o estado atual' (409) de 'regra de
    negocio violada' (422). Nao e uma classe de dominio."""


class Doce:
    """Classe base. As filhas mudam apenas a unidade e a forma de cobrar.

    Constantes de classe (valor diferente em cada filha):
      UNIDADE_ESTOQUE    em que o estoque e a venda sao medidos
      UNIDADE_PRECO      em que o preco cadastrado e cobrado
      DIVISOR_PRECO      quantos UNIDADE_ESTOQUE cabem em 1 UNIDADE_PRECO
      QUANTIDADE_MINIMA  menor quantidade que pode ser vendida
    """

    TIPO = 'generico'
    UNIDADE_ESTOQUE = 'un'
    UNIDADE_PRECO = 'un'
    DIVISOR_PRECO = 1
    QUANTIDADE_MINIMA = 1

    def __init__(self, id, nome, categoria, preco, estoque):
        self._id = id
        self.alterar_nome(nome)
        self.alterar_categoria(categoria)
        self.alterar_preco(preco)
        self.alterar_estoque(estoque)

    # --- leitura ---
    def mostrar_id(self):
        return self._id

    def mostrar_nome(self):
        return self._nome

    def mostrar_categoria(self):
        return self._categoria

    def mostrar_preco(self):
        return self._preco

    def mostrar_estoque(self):
        return self._estoque

    def mostrar_tipo(self):
        return self.TIPO

    def mostrar_unidade_estoque(self):
        return self.UNIDADE_ESTOQUE

    def mostrar_unidade_preco(self):
        return self.UNIDADE_PRECO

    def mostrar_descricao(self):
        return f'{self._nome} (R$ {self._preco:.2f}/{self.UNIDADE_PRECO})'

    # --- alteracao, com regra (nao existe alterar_id) ---
    def alterar_nome(self, novo_nome):
        if novo_nome.strip() == '':
            raise ValueError('nome não pode ser vazio')
        self._nome = novo_nome.strip()

    def alterar_categoria(self, nova_categoria):
        if nova_categoria.strip() == '':
            raise ValueError('categoria não pode ser vazia')
        self._categoria = nova_categoria.strip()

    def alterar_preco(self, novo_preco):
        if novo_preco <= 0:
            raise ValueError('preço precisa ser maior que zero')
        self._preco = novo_preco

    def alterar_estoque(self, novo_estoque):
        if novo_estoque < 0:
            raise ValueError('estoque não pode ficar negativo')
        self._estoque = novo_estoque

    # --- comportamento ---
    def tem_nome(self, nome):
        return self._nome.lower() == nome.strip().lower()

    def e_da_categoria(self, categoria):
        return self._categoria.lower() == categoria.strip().lower()

    def esta_esgotado(self):
        return self._estoque == 0

    def validar_quantidade(self, quantidade):
        if quantidade < self.QUANTIDADE_MINIMA:
            raise ValueError(
                f'quantidade mínima de {self._nome} é '
                f'{self.QUANTIDADE_MINIMA} {self.UNIDADE_ESTOQUE}')

    def verificar_estoque(self, quantidade):
        self.validar_quantidade(quantidade)
        if quantidade > self._estoque:
            raise EstoqueInsuficiente(
                f'estoque insuficiente de {self._nome}: pediu '
                f'{quantidade} {self.UNIDADE_ESTOQUE}, restam '
                f'{self._estoque} {self.UNIDADE_ESTOQUE}')

    def retirar_estoque(self, quantidade):
        self.verificar_estoque(quantidade)
        self.alterar_estoque(self._estoque - quantidade)

    def calcular_subtotal(self, quantidade):
        """Mesma conta para todos: so as constantes mudam. Nenhum if de tipo."""
        self.validar_quantidade(quantidade)
        return round(self._preco * quantidade / self.DIVISOR_PRECO, 2)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._nome})'


class DoceUnidade(Doce):
    """Vendido por unidade: brigadeiro, fatia de bolo, pao de mel."""

    TIPO = 'unidade'
 


class DocePorPeso(Doce):
    """Vendido a granel: preco por kg, estoque e venda em gramas."""

    TIPO = 'peso'
    UNIDADE_ESTOQUE = 'g'
    UNIDADE_PRECO = 'kg'
    DIVISOR_PRECO = 1000
    QUANTIDADE_MINIMA = 50

    def validar_quantidade(self, quantidade):
        super().validar_quantidade(quantidade)
        if quantidade % self.QUANTIDADE_MINIMA != 0:
            raise ValueError(
                f'{self._nome} é vendido em múltiplos de '
                f'{self.QUANTIDADE_MINIMA} {self.UNIDADE_ESTOQUE}')

    def mostrar_descricao(self):
        return (super().mostrar_descricao()
                + f' — porções de {self.QUANTIDADE_MINIMA} g')


# o valor do dicionario e a propria CLASSE, nao um texto
PERFIS = {
    'unidade': DoceUnidade,
    'peso': DocePorPeso,
}


def criar_doce(dados):
    """Transforma um dicionario (do mock ou do POST) em um objeto."""
    if dados['tipo'] not in PERFIS:
        raise ValueError('tipo de doce inválido: use "unidade" ou "peso"')
    return PERFIS[dados['tipo']](dados['id'], dados['nome'],
                                 dados['categoria'], dados['preco'],
                                 dados['estoque'])


def carregar_doces():
    return [criar_doce(d) for d in DOCES]
