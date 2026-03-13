import os
from datetime import datetime
from arquivos import rotina, SETORES, PRIORIDADES, DIAS_SEMANA
from arquivos import salvar_rotina, salvar_tarefas_recorrentes, carregar_rotina, exportar_relatorio_txt, resetar_banco_dados


# === FUNÇÕES DE UTILIDADE
def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def ler_input(mensagem: str) -> str:
    """
    Lê o input do usuário. Se ele digitar 'E' ou 'e', retorna um sinal de cancelamento. 
    Caso contrário, retorna o texto limpo. Útil para limpar o texto e cancelar operações facilmente.
    """
    valor = input(mensagem).strip()
    if valor.upper() == "E":
        print("\n🚫 Operação CANCELADA pelo usuário.")
        return "__CANCELAR__"
    return valor



def limpar_todas_tarefas():
    """
    Permite a exclusão definitiva de todas as tarefas e relatórios já criados pelo usuário
    """
    limpar_tela()
    print("⚠️  ZONA DE PERIGO  ⚠️")
    print("(Digite 'E' para sair)")
    print("Isso apagará TODAS as tarefas e zerará o relatório.")
    
    confirmacao = ler_input("Digite 'SIM' para confirmar: ")
    if confirmacao == "__CANCELAR__": return

    
    if confirmacao == "SIM":
        # Função que apaga os arquivos .json e os relatorios
        resetar_banco_dados()
        print("\n🗑️  Tudo limpo.")
    else:
        print("\n🛑 Cancelado.")
    input("Enter para voltar...")




# === MENU DE RELATÓRIOS ===
def menu_relatorios():
    """
    Cria o menu para a área de Relatórios, que possui ações específicas.
    """
    while True:
        limpar_tela()
        print("=== ÁREA DE RELATÓRIOS ===")
        print("(Digite 'E' para voltar)")
        print("1. Exportar (.txt)")
        print("2. Zerar Banco de Dados")
        print("0. Voltar")
        op = input("Escolha: ") 
        if op == "0" or op.upper() == "E":
            break
        elif op == "1":
            exportar_relatorio_txt()
            input("Enter...")
        elif op == "2":
            limpar_todas_tarefas()




# === FUNÇÕES DE COLETA DE INFORMAÇÕES ===
def coletar_dados_basicos() -> dict:
    """
    Coleta Descrição, Setor e Prioridade e adiciona ao dicionário da tarefa.
    Retorna None se o usuário cancelar com 'E'.
    """
    dados = {}
    
    # 1. Descrição
    while True:
        t = ler_input("Descrição da tarefa: ") #Uso da função de limpeza de input 
        if t == "__CANCELAR__": 
            return None 
        if t:
            dados["descrição"] = t
            break
        print("❌ Descrição vazia.")

    # 2. Setores
    print("\nSetores:")
    for indice_s, setor in enumerate(SETORES):
        print(f"{indice_s + 1}) {setor}")

    while True:
        try:
            op_str = ler_input("Setor (ID): ")
            if op_str == "__CANCELAR__": 
                return None
            
            op = int(op_str)
            # Verificando se o input está no alcance correto 
            # Corrigindo o índice na hora de adicionar ao dicionário da tarefa
            if 1 <= op <= len(SETORES):
                dados["setor"] = SETORES[op - 1]
                break
        except:
            pass
        print("❌ Opção inválida.")

    # 3. Prioridades
    print("\nPrioridades:")
    for indice_p, prioridade in enumerate(PRIORIDADES):
        print(f"{indice_p + 1}) {prioridade}")

    while True:
        try:
            op_str = ler_input("Prioridade (ID): ")
            if op_str == "__CANCELAR__": 
                return None
            
            op = int(op_str)
            # Verificando se o input está no alcance correto 
            # Corrigindo o índice na hora de adicionar ao dicionário da tarefa
            if 1 <= op <= len(PRIORIDADES): 
                dados["prioridade"] = PRIORIDADES[op - 1]
                break
        except:
            pass
        print("❌ Opção inválida.")

    return dados



def coletar_horario():
    """
    Coleta horários e adiciona ao dicionário da tarefa. 
    Retorna None se cancelar com 'E'.
    """
    print("\n🕒 HORÁRIO")
    print("1) Apenas Vencimento")
    print("2) Intervalo (Início e Fim)")
    
    while True:
        tipo = ler_input("Opção (1/2): ")
        if tipo == "__CANCELAR__": 
            return None
        
        if tipo == "1":
            while True:
                h = ler_input("Horário (HH:MM): ")
                if h == "__CANCELAR__": 
                    return None
                try:
                    # O método 'strptime' transforma strings em objetos de tempo.
                    # %H = hora (00-23) e %M = minutos (00-59).
                    datetime.strptime(h, "%H:%M") 
                    return {"inicio": h, "fim": ""}
                # Esse except capta erros de horário gerados pelo método 'strptime'
                # Como 25:80, por exemplo
                except: 
                    print("❌ Formato inválido.")
        elif tipo == "2":
            while True:
                i = ler_input("Início (HH:MM): ")
                if i == "__CANCELAR__": 
                    return None
                f = ler_input("Fim    (HH:MM): ")
                if f == "__CANCELAR__": 
                    return None
                try:
                    # Como os horários viraram objetos de tempo, o Python consegue compará-los matematicamente (<=).
                    # Isso impede que o fim seja "menor" (antes) que o início.
                    if datetime.strptime(f, "%H:%M") <= datetime.strptime(i, "%H:%M"): 
                        print("❌ Fim deve ser maior que início.")
                        continue
                    return {"inicio": i, "fim": f}
                except:
                    print("❌ Formato inválido.")




# === FUNÇÕES DE VISUALIZAÇÃO ===
def visualizar_por_id():
    """"
    Importante para funções como excluir/editar tarefas, pois cria um índice numérico
    temporário para cada tarefa, facilitando essa busca
    """
    contador = 1
    for tarefas in rotina.values():
        for tarefa in tarefas:
            descricao = tarefa.get("descrição", "")
            prazo = tarefa.get("prazo", "Sem prazo")
            setor = tarefa.get("setor", "")
            prioridade = tarefa.get("prioridade", "")
            print(f"{contador}. {descricao}   | Setor: {setor} | Prioridade: {prioridade} | Prazo: {prazo}")
            contador += 1
    if contador == 1:
        print("Nenhuma tarefa cadastrada.")



def visualizar_por_setor():
    """
    Permite a visualização de todas as tarefas de um mesmo setor escolhido pelo usuário
    """
    limpar_tela()
    print("=== VISUALIZAR POR SETOR ===")
    print("(Digite 'E' para cancelar)\n")
    print("Setores:")
    # Visualização para o usuário escolher qual setor quer visualizar
    for i, s in enumerate(SETORES, 1):
        print(f"{i}) {s}")
    
    escolha = ler_input("Escolha setor (número): ")
    if escolha == "__CANCELAR__": 
        return

    if not escolha.isdigit():
        print("Entrada inválida.")
        return
    escolha = int(escolha)
    if escolha < 1 or escolha > len(SETORES):
        print("Setor inválido.")
        return

    setor = SETORES[escolha - 1]
    print(f"\nTarefas no setor: {setor}\n")

    achou = False
    # Analisa cada tarefa da rotina em busca da chave 'setor'
    # Se encontrar, seta a variável achou como True e printa os valores da tarefa
    # Usa o método 'get' para garantir a existência de um valor
    for tarefas in rotina.values():
        for t in tarefas:
            if t.get("setor") == setor:
                achou = True
                desc = t.get("descrição", "(sem descrição)")
                data = t.get("data_completa", "")
                horario = f"{t.get('inicio')} - {t.get('fim')}" if t.get("fim") else t.get("inicio")
                print(f"- {desc} | {data} {horario}")

    if not achou:
        print("Nenhuma tarefa encontrada para esse setor.")
    input("\nEnter para voltar...")



def visualizar_por_data():
    """
    Ordena as tarefas pelas suas datas
    """
    limpar_tela()
    print("=== TAREFAS ORDENADAS POR DATA ===\n")
    lista = []
    for tarefas in rotina.values():
        for t in tarefas:
            data_str = t.get("data_completa")
            inicio_str = t.get("inicio")
            # Transforma-se as strings de dias em objetos de tempo para possibilitar uma ordenação
            # Caso não encontre o dia, coloca como uma data praticamente impossível 
            # Adiciona à uma lista vazia a tupla (data, tarefa)
            try:
                dt = datetime.strptime(f"{data_str} {inicio_str}", "%d/%m/%Y %H:%M")
            except:
                dt = datetime(9999, 1, 1)
            lista.append((dt, t))

    if not lista:
        print("Nenhuma tarefa cadastrada.")
        input("\nEnter para voltar...")
        return

    # Aqui, usa-se uma ordenação especial com o uso de função lambda
    # Isso permite organizar pelo primeiro valor da tupla, ou seja, a data
    # Como essa data é um objeto de tempo, o python consegue ordená-la corretamente
    lista.sort(key=lambda x: x[0])

    # Por causa do uso do método 'sort', a lista está ordenada definitivamente
    for dt, t in lista:
        desc = t.get("descrição", "(sem descrição)")
        data = t.get("data_completa", "")
        horario = f"{t.get('inicio')} - {t.get('fim')}" if t.get("fim") else t.get("inicio")
        print(f"- {desc}")
        print(f"  Data: {data} | Horário: {horario}")
        print(f"  Setor: {t.get('setor')} | Prioridade: {t.get('prioridade')}\n")

    input("\nEnter para voltar...")



def visualizar_por_prioridade():
    """
    Funciona da mesma forma que a função visualizar_por_setor
    """
    limpar_tela()
    print("=== VISUALIZAR POR PRIORIDADE ===\n")
    print("(Digite 'E' para cancelar)\n")
    print("Prioridades:")
    for i, p in enumerate(PRIORIDADES, 1):
        print(f"{i}) {p}")

    escolha = ler_input("\nPrioridade (ID): ")
    if escolha == "__CANCELAR__": 
        return

    if not escolha.isdigit():
        print("Entrada inválida.")
        input("Enter...")
        return

    escolha = int(escolha)
    if escolha < 1 or escolha > len(PRIORIDADES):
        print("Prioridade inválida.")
        return

    prioridade = PRIORIDADES[escolha - 1]
    achou = False
    print(f"\nTarefas com prioridade: {prioridade}\n")

    for tarefas in rotina.values():
        for t in tarefas:
            if t.get("prioridade") == prioridade:
                achou = True
                desc = t.get("descrição", "")
                data = t.get("data_completa", "")
                horario = f"{t.get('inicio')} - {t.get('fim')}" if t.get("fim") else t.get("inicio")
                print(f"- {desc} | {data} {horario} | {t.get('setor')}")

    if not achou:
        print("Nenhuma tarefa com essa prioridade.")
    input("\nEnter para voltar...")
