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
