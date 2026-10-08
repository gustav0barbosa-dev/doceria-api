from app.models.doce import carregar_doces, criar_doce


class DoceController:
    def __init__(self):
        self._doces = carregar_doces()

    def listar(self):
        return [self._para_dicionario(d) for d in self._doces]

    def listar_por_categoria(self, categoria):
        da_categoria = [d for d in self._doces if d.e_da_categoria(categoria)]
        return [self._para_dicionario(d) for d in da_categoria]

    def existe_nome(self, nome):
        return any(d.tem_nome(nome) for d in self._doces)

    def cadastrar(self, nome, categoria, tipo, preco, estoque):
        """Pode levantar ValueError (regra da model). A rota traduz."""
        doce = criar_doce({
            'id': self._proximo_id(),
            'nome': nome,
            'categoria': categoria,
            'tipo': tipo,
            'preco': preco,
            'estoque': estoque,
        })
        self._doces.append(doce)
        return self._para_dicionario(doce)

    def consultar_estoque(self):
        return [{
            'id': d.mostrar_id(),
            'nome': d.mostrar_nome(),
            'estoque': d.mostrar_estoque(),
            'unidade': d.mostrar_unidade_estoque(),
            'esgotado': d.esta_esgotado(),
        } for d in self._doces]

    # usados pelo PedidoController: devolvem OBJETOS, nao dicionarios
    def listar_objetos(self):
        return list(self._doces)

    def buscar_objeto(self, id):
        for doce in self._doces:
            if doce.mostrar_id() == id:
                return doce
        return None

    def _proximo_id(self):
        return max((d.mostrar_id() for d in self._doces), default=0) + 1

    def _para_dicionario(self, doce):
        return {
            'id': doce.mostrar_id(),
            'nome': doce.mostrar_nome(),
            'categoria': doce.mostrar_categoria(),
            'tipo': doce.mostrar_tipo(),
            'preco': doce.mostrar_preco(),
            'cobrado_por': doce.mostrar_unidade_preco(),
            'estoque': doce.mostrar_estoque(),
            'unidade_estoque': doce.mostrar_unidade_estoque(),
            'descricao': doce.mostrar_descricao(),
        }
