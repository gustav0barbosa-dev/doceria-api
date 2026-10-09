"""Testa as 8 rotas, com os codigos 200, 201, 404, 409 e 422.
Precisa de: pip install httpx
"""
from fastapi.testclient import TestClient
from main import app

c = TestClient(app)
falhas = 0


def t(desc, resp, esperado, verif=None):
    global falhas
    ok = resp.status_code == esperado
    extra = ''
    if ok and verif:
        try:
            ok = verif(resp.json())
        except Exception as e:
            ok = False
            extra = f' ({e})'
    print(('  ok      ' if ok else '  FALHOU  ') + f'{desc} -> {resp.status_code}{extra}')
    if not ok:
        falhas += 1


print('\nDOCES')
t('GET  /api/doces', c.get('/api/doces'), 200, lambda j: len(j) == 8)
t('GET  /api/doces/categoria/bolos', c.get('/api/doces/categoria/Bolos'), 200,
  lambda j: len(j) == 2)
t('GET  /api/doces/categoria/xyz', c.get('/api/doces/categoria/xyz'), 404)
novo = {'nome': 'Cupcake', 'categoria': 'Bolos', 'tipo': 'unidade',
        'preco': 7.5, 'estoque': 12}
t('POST /api/doces (cria)', c.post('/api/doces', json=novo), 201,
  lambda j: j['id'] == 9 and j['tipo'] == 'unidade')
t('POST /api/doces (nome repetido)', c.post('/api/doces', json=novo), 409)
t('POST /api/doces (preco zero)',
  c.post('/api/doces', json={**novo, 'nome': 'Outro', 'preco': 0}), 422)
t('POST /api/doces (tipo invalido)',
  c.post('/api/doces', json={**novo, 'nome': 'Outro', 'tipo': 'xyz'}), 422)

print('\nESTOQUE')
t('GET  /api/estoque', c.get('/api/estoque'), 200, lambda j: len(j) == 9)

print('\nPEDIDOS')
t('GET  /api/pedidos', c.get('/api/pedidos'), 200, lambda j: len(j) == 6)
t('GET  /api/pedidos/1', c.get('/api/pedidos/1'), 200, lambda j: j['total'] == 51.0)
t('GET  /api/pedidos/99', c.get('/api/pedidos/99'), 404)
venda = {'itens': [{'doce_id': 1, 'quantidade': 2},
                   {'doce_id': 6, 'quantidade': 250}]}
t('POST /api/pedidos (venda)', c.post('/api/pedidos', json=venda), 201,
  lambda j: j['id'] == 7 and j['total'] == 29.5)
t('estoque do doce 1 baixou', c.get('/api/estoque'), 200,
  lambda j: j[0]['estoque'] == 118)
t('POST /api/pedidos (vazio)', c.post('/api/pedidos', json={'itens': []}), 422)
t('POST /api/pedidos (peso fora do multiplo)',
  c.post('/api/pedidos', json={'itens': [{'doce_id': 6, 'quantidade': 75}]}), 422)
t('POST /api/pedidos (sem estoque)',
  c.post('/api/pedidos', json={'itens': [{'doce_id': 1, 'quantidade': 9999}]}), 409)
t('POST /api/pedidos (doce inexistente)',
  c.post('/api/pedidos', json={'itens': [{'doce_id': 99, 'quantidade': 1}]}), 404)

print('\nRELATORIO')
t('GET  /api/relatorio/ticket-medio', c.get('/api/relatorio/ticket-medio'), 200,
  lambda j: j['pedidos'] == 7 and j['ticket_medio'] == 37.43)

print()
print('TUDO CERTO.' if falhas == 0 else f'{falhas} teste(s) falharam.')
