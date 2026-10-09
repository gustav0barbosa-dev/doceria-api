"""Verificacao da Doceria API.

Roda sem subir a API: testa as models e os controllers.
"""
import os

from app.models.doce import (Doce, DoceUnidade, DocePorPeso, PERFIS,
                             EstoqueInsuficiente, carregar_doces, criar_doce)
from app.models.pedido import Pedido, carregar_pedidos
from app.controllers.doce_controller import DoceController
from app.controllers.pedido_controller import PedidoController

falhas = 0


def checar(ok, descricao):
    global falhas
    if ok:
        print(f'  ok      {descricao}')
    else:
        print(f'  FALHOU  {descricao}')
        falhas += 1


def recusa(funcao, descricao):
    """Checa que a chamada levanta ValueError."""
    try:
        funcao()
        checar(False, 'deveria recusar: ' + descricao)
    except ValueError:
        checar(True, descricao)


print('\n1. Encapsulamento: o objeto nasce valido')
recusa(lambda: DoceUnidade(99, '   ', 'Teste', 5, 10),
       'construtor recusa nome vazio')
recusa(lambda: DoceUnidade(99, 'Teste', '  ', 5, 10),
       'construtor recusa categoria vazia')
recusa(lambda: DoceUnidade(99, 'Teste', 'Teste', 0, 10),
       'construtor recusa preco zero')
recusa(lambda: DoceUnidade(99, 'Teste', 'Teste', 5, -1),
       'construtor recusa estoque negativo')
checar(not hasattr(Doce, 'alterar_id'), 'nao existe alterar_id')

print('\n2. Heranca: a hierarquia esta correta')
checar(issubclass(DoceUnidade, Doce), 'DoceUnidade herda de Doce')
checar(issubclass(DocePorPeso, Doce), 'DocePorPeso herda de Doce')
checar('validar_quantidade' in DocePorPeso.__dict__,
       'DocePorPeso sobrescreve validar_quantidade')
checar('calcular_subtotal' not in DocePorPeso.__dict__
       and 'calcular_subtotal' not in DoceUnidade.__dict__,
       'as filhas NAO reescrevem calcular_subtotal: herdam')

print('\n3. Heranca: constante de classe com valor diferente')
checar(DoceUnidade.UNIDADE_ESTOQUE == 'un'
       and DocePorPeso.UNIDADE_ESTOQUE == 'g', 'UNIDADE_ESTOQUE difere')
checar(DoceUnidade.QUANTIDADE_MINIMA == 1
       and DocePorPeso.QUANTIDADE_MINIMA == 50, 'QUANTIDADE_MINIMA difere')

print('\n4. Heranca: super() estende o metodo da base')
brigadeiro = DoceUnidade(90, 'Brigadeiro', 'Teste', 3.5, 10)
bombom = DocePorPeso(91, 'Bombom', 'Teste', 90, 1000)
recusa(lambda: bombom.validar_quantidade(0),
       'super() ainda aplica a regra da base (minimo)')
recusa(lambda: bombom.validar_quantidade(75),
       'a filha acrescenta a sua regra (multiplos de 50 g)')
checar('porções de 50 g' in bombom.mostrar_descricao()
       and 'Bombom' in bombom.mostrar_descricao(),
       'descricao da filha contem a da base + o acrescimo')

print('\n5. Polimorfismo: o mock vira classes diferentes')
doces = carregar_doces()
nomes = {type(d).__name__ for d in doces}
checar(nomes == {'DoceUnidade', 'DocePorPeso'},
       'o mock virou objetos das duas filhas')
checar(set(PERFIS) == {'unidade', 'peso'}, 'PERFIS mapeia texto -> classe')
checar(PERFIS['peso'] is DocePorPeso, 'o valor de PERFIS e a propria classe')
recusa(lambda: criar_doce({'id': 1, 'nome': 'X', 'categoria': 'Y',
                           'tipo': 'inexistente', 'preco': 1, 'estoque': 1}),
       'tipo desconhecido e recusado')

print('\n6. Polimorfismo: a mesma chamada, cobrancas diferentes')
checar(brigadeiro.calcular_subtotal(4) == 14.0, '4 brigadeiros = R$ 14,00')
checar(bombom.calcular_subtotal(250) == 22.5,
       '250 g a R$ 90/kg = R$ 22,50')

print('\n7. Estoque: nunca fica negativo')
brigadeiro.retirar_estoque(4)
checar(brigadeiro.mostrar_estoque() == 6, 'retirar 4 de 10 deixa 6')
try:
    brigadeiro.retirar_estoque(7)
    checar(False, 'deveria recusar retirar mais do que ha')
except EstoqueInsuficiente:
    checar(True, 'recusa retirar mais do que ha (EstoqueInsuficiente)')
checar(brigadeiro.mostrar_estoque() == 6, 'a tentativa falha nao mexe no estoque')
checar(issubclass(EstoqueInsuficiente, ValueError),
       'EstoqueInsuficiente e um ValueError')

print('\n8. Pedido: associacao e regras')
doces = carregar_doces()
pedidos = carregar_pedidos(doces)
checar(len(pedidos) >= 5 and len(doces) >= 5, 'mocks com pelo menos 5 registros')
primeiro = pedidos[0]
checar(all(hasattr(d, 'mostrar_nome') for d, _ in primeiro.mostrar_itens()),
       'o pedido guarda objetos Doce, nao ids')
checar(primeiro.calcular_total() == 51.0, 'total do pedido 1 = R$ 51,00')
recusa(lambda: Pedido(99, []), 'pedido vazio e recusado')
recusa(lambda: Pedido(99, [(brigadeiro, 0)]), 'quantidade zero e recusada')
soma = Pedido(99, [(brigadeiro, 1), (brigadeiro, 2)])
checar(len(soma.mostrar_itens()) == 1 and soma.mostrar_itens()[0][1] == 3,
       'o mesmo doce repetido e somado')

print('\n9. Venda: verifica e atualiza o estoque')
dc = DoceController()
pc = PedidoController(dc)
antes = dc.buscar_objeto(1).mostrar_estoque()
venda = pc.criar([{'doce_id': 1, 'quantidade': 10},
                  {'doce_id': 6, 'quantidade': 500}])
checar(dc.buscar_objeto(1).mostrar_estoque() == antes - 10,
       'a venda descontou o estoque do doce por unidade')
checar(dc.buscar_objeto(6).mostrar_estoque() == 2500,
       'a venda descontou o estoque do doce por peso (g)')
checar(venda['total'] == 80.0, 'total da venda = R$ 80,00')

print('\n10. Venda: tudo ou nada')
estoque_6 = dc.buscar_objeto(6).mostrar_estoque()
estoque_1 = dc.buscar_objeto(1).mostrar_estoque()
try:
    pc.criar([{'doce_id': 6, 'quantidade': 100},
              {'doce_id': 1, 'quantidade': 99999}])
    checar(False, 'deveria recusar venda sem estoque')
except EstoqueInsuficiente:
    checar(True, 'venda sem estoque e recusada')
checar(dc.buscar_objeto(6).mostrar_estoque() == estoque_6
       and dc.buscar_objeto(1).mostrar_estoque() == estoque_1,
       'nenhum item foi descontado quando um falhou')

print('\n11. Colecoes: filtro e relatorio')
checar(len(dc.listar_por_categoria('bolos')) == 2,
       'filtro por categoria ignora maiusculas')
checar(dc.listar_por_categoria('xyz') == [], 'categoria inexistente: lista vazia')
checar(pc.buscar(99) is None, 'pedido inexistente devolve None')
checar(dc.existe_nome('  beijinho '), 'existe_nome ignora caixa e espacos')
relatorio = PedidoController(DoceController()).ticket_medio()
checar(relatorio['ticket_medio'] == 38.75, 'ticket medio do historico = R$ 38,75')

print('\n12. Camadas: a model nao conhece o FastAPI')
import app.models.doce as md
import app.models.pedido as mp
for modulo in (md, mp):
    conteudo = open(modulo.__file__, encoding='utf-8').read()
    checar('fastapi' not in conteudo.lower(),
           f'{modulo.__name__.split(".")[-1]}.py nao importa fastapi')

print('\n13. Camadas: o controller nao devolve codigo HTTP')
import app.controllers.doce_controller as cd
import app.controllers.pedido_controller as cp
for modulo in (cd, cp):
    conteudo = open(modulo.__file__, encoding='utf-8').read()
    checar('HTTPException' not in conteudo and 'fastapi' not in conteudo.lower(),
           f'{modulo.__name__.split(".")[-1]}.py nao usa HTTP')

print('\n14. Nenhum if comparando tipo ou nome de classe')
achou = []
for pasta, _, arquivos in os.walk('app'):
    for nome in arquivos:
        if nome.endswith('.py'):
            for linha in open(os.path.join(pasta, nome), encoding='utf-8'):
                if linha.strip().startswith(('if ', 'elif ')) and (
                        'isinstance' in linha or 'type(' in linha
                        or '__name__' in linha):
                    achou.append(linha.strip())
checar(achou == [], 'nenhum if de tipo em app/')

print()
if falhas == 0:
    print('TUDO CERTO. Agora suba a API e teste no /docs.')
else:
    print(f'{falhas} verificacao(oes) falharam.')
