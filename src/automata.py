def carrega_automato(nome_arquivo):
    """
    Lê os dados de um autômato finito a partir de um arquivo.
    A estsrutura do arquivo deve ser:
    <lista de símbolos do alfabeto, separados por espaço (' ')>
    <lista de nomes de estados>
    <lista de nomes de estados finais>
    <nome do estado inicial>
    <lista de regras de transição, com "origem símbolo destino">
    Um exemplo de arquivo válido é:
    ```
    a b
    q0 q1 q2 q3
    q0 q3
    q0
    q0 a q1
    q0 b q2
    q1 a q0
    q1 b q3
    q2 a q3
    q2 b q0
    q3 a q1
    q3 b q2
    ```
    Caso o arquivo seja inválido uma exceção Exception é gerada.
    """
    with open(nome_arquivo, "rt", encoding="utf-8") as arquivo:
        linhas = arquivo.readlines()
        
        # Lê e processa os dados do arquivo
        alfabeto = tuple(linhas[0].strip().split())
        estados = tuple(linhas[1].strip().split())
        estados_finais = tuple(linhas[2].strip().split())
        estado_inicial = linhas[3].strip()
        
        transicoes = []
        for linha in linhas[4:]:
            transicoes.append(tuple(linha.strip().split()))
    
    # Validação dos dados carregados
    if estado_inicial not in estados:
        raise ValueError("Estado inicial inválido")
    
    for estado in estados_finais:
        if estado not in estados:
            raise ValueError(f"Estado final inválido: {estado}")
    
    for transicao in transicoes:
        if len(transicao) != 3 or transicao[0] not in estados or (transicao[1] not in alfabeto and transicao[1] != '&') or transicao[2] not in estados:
            raise ValueError(f"Transição inválida: {transicao}")
    
    return estados, alfabeto, transicoes, estado_inicial, estados_finais

def processa_automato(automato, palavras):
    
    estados, alfabeto, transicoes, estado_inicial, estados_finais = automato
    resultados = {}
    
    for palavra in palavras:
        estado_atual = estado_inicial
        palavra_valida = True
        
        for simbolo in palavra:
            if simbolo not in alfabeto:
                resultados[palavra] = "INVALIDA"
                palavra_valida = False
                break
            
            transicao_encontrada = False
            for transicao in transicoes:
                if transicao[0] == estado_atual and (transicao[1] == simbolo or (transicao[1] == '&' and simbolo == '')):
                    estado_atual = transicao[2]
                    transicao_encontrada = True
                    break
            
            if not transicao_encontrada:
                resultados[palavra] = "INVALIDA"
                palavra_valida = False
                break
        
        if palavra_valida:
            if estado_atual in estados_finais:
                resultados[palavra] = "ACEITA"
            else:
                resultados[palavra] = "REJEITA"
    
    return resultados

def calcula_fecho(estado, delta):
    """Retorna o fecho de um estado em um NFA."""
    fecho = {estado}
    pilha = [estado]

    while pilha:
        atual = pilha.pop()
        for aresta in delta:
            if aresta[0] == atual and aresta[1] == '&' and aresta[2] not in fecho:
                fecho.add(aresta[2])
                pilha.append(aresta[2])

    return fecho

def converte_para_dfa(automato):
    """Converte um NFA em um DFA."""
    alfabeto = automato[1]
    delta = automato[2]
    estado_inicial = automato[3]
    estados_finais = automato[4]

    novos_estados = []
    novo_delta = []
    novos_estados_finais = []
    novo_estado_inicial = estado_inicial

    fecho_inicial = calcula_fecho(estado_inicial, delta)
    fila = [fecho_inicial]
    visitados = []
    while fila:
        atual = fila.pop()
        novos_estados.append(atual)

        for simbolo in alfabeto:
            novo_estado = set()
            for estado in atual:
                for aresta in delta:
                    if aresta[0] == estado and (aresta[1] == simbolo or (aresta[1] == '&' and simbolo == '')):
                        novo_estado = novo_estado.union(
                            calcula_fecho(aresta[2], delta)
                        )
            if novo_estado:
                novo_delta.append((atual, simbolo, novo_estado))
                if novo_estado not in visitados:
                    visitados.append(novo_estado)
                    fila.append(novo_estado)

    # Atualiza estados finais
    for novo_estado in novos_estados:
        for estado in novo_estado:
            if estado in estados_finais:
                novos_estados_finais.append(novo_estado)
                break

    # Atualiza estado inicial
    for novo_estado in novos_estados:
        if estado_inicial in novo_estado:
            novo_estado_inicial = novo_estado
            break

    # Formatação dos dados para representação simplificada
    novos_estados = ["".join(sorted(estado)) for estado in novos_estados]
    novo_delta = [("".join(sorted(origem)), simbolo, "".join(sorted(destino))) for origem, simbolo, destino in novo_delta]
    novos_estados_finais = ["".join(sorted(estado)) for estado in novos_estados_finais]
    novo_estado_inicial = "".join(sorted(novo_estado_inicial))

    return novos_estados, alfabeto, novo_delta, novo_estado_inicial, novos_estados_finais
