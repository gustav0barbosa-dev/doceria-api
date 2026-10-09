# Vendas ja realizadas (historico). O estoque do mock de doces ja esta
# descontado delas. Cada item guarda o id do doce e a quantidade
# (un para doce por unidade, gramas para doce por peso).
PEDIDOS = [
    {'id': 1, 'itens': [{'doce_id': 1, 'quantidade': 10},
                        {'doce_id': 3, 'quantidade': 2}]},
    {'id': 2, 'itens': [{'doce_id': 6, 'quantidade': 250}]},
    {'id': 3, 'itens': [{'doce_id': 2, 'quantidade': 6},
                        {'doce_id': 5, 'quantidade': 3},
                        {'doce_id': 7, 'quantidade': 500}]},
    {'id': 4, 'itens': [{'doce_id': 4, 'quantidade': 4}]},
    {'id': 5, 'itens': [{'doce_id': 8, 'quantidade': 100},
                        {'doce_id': 1, 'quantidade': 5}]},
    {'id': 6, 'itens': [{'doce_id': 3, 'quantidade': 1},
                        {'doce_id': 4, 'quantidade': 1},
                        {'doce_id': 6, 'quantidade': 100}]},
]
