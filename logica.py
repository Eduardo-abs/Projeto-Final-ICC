from datetime import datetime, timedelta

from arquivos import (
    DIAS_SEMANA,
    PRIORIDADES,
    SETORES,
    rotina,
    salvar_rotina,
    salvar_tarefas_recorrentes,
)
from interface import (
    coletar_dados_basicos,
    coletar_horario,
    ler_input,
    limpar_tela,
    visualizar_por_id,
)


# === FUNÇÃO QUE RESOLVE CONFLITOS DE HORÁRIOS ===
def verificar_conflito(
    dia_atual: str, inicio_novo: str, fim_novo: str, rotina_geral: dict
) -> bool:
    """
    Função que analisa a intersecção entre dois horários e permite o usuário escolher o que
    fazer
    """

    def converter_para_minutos(horario_str: str) -> int:
        """
        Função aninhada que converte o horário (string na forma hh:mm) em minutos para possibiltar a análise de intersecção
        """
        if not horario_str:
            return 0
        partes = horario_str.split(":")
        return (int(partes[0]) * 60) + int(partes[1])

    lista_tarefas = rotina_geral[dia_atual]

    # Transformar os horários em minutos
    min_inicio_novo = converter_para_minutos(inicio_novo)
    if fim_novo:
        min_fim_novo = converter_para_minutos(fim_novo)
    else:
        min_fim_novo = min_inicio_novo + 1

    conflitos = []

    # Percorre todas as tarefas do dia, lembrando que cada tarefa é um dicionário
    for i, tarefa in enumerate(lista_tarefas):
        ini_exist = tarefa.get("inicio")
        fim_exist = tarefa.get("fim")

        if not ini_exist:
            continue

        min_ini_velho = converter_para_minutos(ini_exist)
        if fim_exist:
            min_fim_velho = converter_para_minutos(fim_exist)
        else:
            min_fim_velho = min_ini_velho + 1
        # Essa condição analisa se há intersecção entre as tarefas,
        # Ela analisa isso verificando: se a nova tarefa começa antes da antiga terminar E a antiga começa antes da nova terminar, há uma intersecção.
        if (min_inicio_novo < min_fim_velho) and (min_ini_velho < min_fim_novo):
            conflitos.append((i, tarefa))

    if not conflitos:
        return True

    limpar_tela()
    print(f"\n⚠️  CONFLITO DE HORÁRIO EM {dia_atual.upper()}!")
    # Trata tarefas que tem apenas início ou definidas em um intervalo de tempo
    if fim_novo:
        print(f"Tentativa: {inicio_novo} até {fim_novo}")
    else:
        print(f"Tentativa: {inicio_novo}")

    print("\nCoincide com:")
    for _, tarefa in conflitos:
        if tarefa["fim"]:
            tempo = f"{tarefa['inicio']} - {tarefa['fim']}"
        else:
            tempo = tarefa["inicio"]

        print(f"   🚩 [{tempo}] {tarefa['descrição']}")

    print("\nComo resolver?")
    print("[1] Manter tudo (Criar sobreposição)")
    print("[2] Substituir (Apagar antigas e salvar esta)")
    print("[3] Cancelar")

    op = ler_input("Opção: ")

    if op == "1":
        print("Salvo duplicado.")
        return True
    elif op == "2":
        lista_de_indices = []
        for item in conflitos:
            # Salvando o índice de cada intersecção de horário
            lista_de_indices.append(item[0])

        # Agora, ordena-se os itens com reverse=True para poder remover os índices do dicionário sem haver erros, pois apagar elementos começando do índice 0 faz mudar todos os índices subsequentes
        indices_ordenados = sorted(lista_de_indices, reverse=True)

        for i in indices_ordenados:
            rotina_geral[dia_atual].pop(i)

        print("🗑️ Antigas removidas.")
        return True
    else:
        print("❌ Cancelado.")
        return False


# === FUNÇÕES PARA ADICIONAR TAREFA À ROTINA (ÚNICAS E RECORRENTES) ===
def adicionar_rotina_unica():
    """
    Adiciona uma tarefa única na rotina do usuário.
    """
    limpar_tela()
    print("=== NOVA TAREFA ÚNICA ===")
    print("(Digite 'E' para cancelar a qualquer momento)\n")

    # Utiliza a mesma função para coletar Descrição, Setor e Prioridade
    tarefa = coletar_dados_basicos()
    # Esse if detecta se a função coletar_dados_basicos retornou 'None'
    if tarefa is None:
        input("Enter para voltar...")
        return

    while True:
        data_str = ler_input("\nData (DD/MM/AAAA): ")
        if data_str == "__CANCELAR__":
            input("Enter para voltar...")
            return

        try:
            # Lógica do método 'strptime' é a mesma, apenas com o uso, agora, de dia, mês e ano
            dt = datetime.strptime(data_str, "%d/%m/%Y")
            # O método .now().date() extraí a dia que está setado no computador, utilizando datas atuais
            # Utiliza a mesma lógica de comparação entre objetos de tempo
            if dt.date() < datetime.now().date():
                print("Data passada.")
                continue
            tarefa["data_completa"] = data_str
            break
        except:
            print("❌ Inválido.")

    horarios = coletar_horario()

    # Se a data escolhida for hoje, o trecho adiante garante que o horário de início é posterior ao de agora
    data_obj = datetime.strptime(tarefa["data_completa"], "%d/%m/%Y").date()
    if data_obj == datetime.now().date():
        while True:
            inicio_dt = datetime.strptime(
                f"{tarefa['data_completa']} {horarios['inicio']}", "%d/%m/%Y %H:%M"
            )
            now = datetime.now()

            if inicio_dt < now:
                print("Horário já passou. Escolha outro horário.")
                horarios = coletar_horario()
                if horarios is None:
                    input("Enter para voltar...")
                    return
                # volta para checar o novo horário
                continue
            break

    if horarios is None:
        input("Enter para voltar...")
        return

    # Adiciona o horário ao dicionário tarefa criado anteriormente
    tarefa.update(horarios)
    tarefa["status"] = "pendente"
    tarefa["prazo"] = f"{data_str} {horarios['inicio']}"

    # O método 'weekday' é do próprio Python e retorna 0 para segunda e 6 para domingo
    # Antes de usá-lo é necessário usar o método 'strptime' para transformar a string em um objeto de tempo
    # Logo, idx é um número entre 0 e 6, os mesmos números dos índices da lista 'DIAS_SEMANA'
    # Com esse número, é possível coletar qual o dia de qualquer data
    idx = datetime.strptime(tarefa["prazo"], "%d/%m/%Y %H:%M").weekday()
    dia_chave = DIAS_SEMANA[idx]

    if verificar_conflito(dia_chave, horarios["inicio"], horarios["fim"], rotina):
        rotina[dia_chave].append(tarefa)
        # A tarefa já é salva automaticamente em rotina.json
        salvar_rotina()
        print(f"\n✅ Agendado para {dia_chave.capitalize()}!")
    else:
        print("\n🚫 Agendamento cancelado.")
    input("Enter para voltar...")


def tarefas_recorrentes():
    """ "
    Permite a criação de tarefas recorrentes durante uma semana, que serão armazenadas em um
    arquivo .json separado mas que será carregado junto do programa, permitindo a
    coexistência de tarefas únicas e recorrentes
    """
    

    while True:
        limpar_tela()
        print("=== NOVA TAREFA RECORRENTE ===")
        print("(Digite 'E' para cancelar a qualquer momento)\n")

        tarefa_base = coletar_dados_basicos()
        if tarefa_base is None:
            break

        horarios = coletar_horario()
        if horarios is None:
            break

        tarefa_base.update(horarios)
        tarefa_base["status"] = "pendente"

        print("\n📅 REPETIÇÃO (Ex: 'segunda quarta')")
        while True:
            dias_input = ler_input("Dias: ")
            if dias_input == "__CANCELAR__":
                break

            # Como o usuário informará os dias da semana, é melhor mapeá-los usando os mesmos índices do método 'weekday'
            dias_input = dias_input.lower()
            partes = dias_input.split()
            mapa = {
                "segunda": 0,
                "terça": 1,
                "terca": 1,
                "quarta": 2,
                "quinta": 3,
                "sexta": 4,
                "sábado": 5,
                "sabado": 5,
                "domingo": 6,
            }

            if not partes:
                continue

            dias_salvos = []
            dias_invalidos = []  # Lista para capturar palavras inválidas

            for nome in partes:
                nome = nome.replace(",", "")
                if nome in mapa:
                    dia_alvo = mapa[nome]
                    nome_dia_chave = DIAS_SEMANA[dia_alvo]

                    # Pelo método 'now' e 'weekday', é descoberto o índice do dia atual
                    # É feito a diferença entre entre o dia desejado e o dia atual e armazenado na variável dias_add
                    # O método 'timedelta' representa uma duração entre dois momentos, nesse caso, essa duração sempre será dias, mostrada pelo kwarg days
                    # Logo, na variável data_calc será adicionado a quantidade de dia até a próxima repetição
                    # A variável prazo é um objeto de tempo que contém o dia, mês, ano e o horário de início
                    if verificar_conflito(
                        nome_dia_chave, horarios["inicio"], horarios["fim"], rotina
                    ):
                        agora = datetime.now()
                        dias_add = (dia_alvo - agora.weekday()) % 7
                        data_calc = agora + timedelta(days=dias_add)
                        prazo = datetime.strptime(
                            f"{data_calc.strftime('%d/%m/%Y')} {horarios['inicio']}",
                            "%d/%m/%Y %H:%M",
                        )

                        # Aqui, como prazo é um objeto que contém dia e horário, pode-se comparar se o horário já passou no dia atual
                        # Se sim, a tarefa é jogada para a semana seguinte
                        if prazo < agora:
                            data_calc += timedelta(days=7)
                            prazo += timedelta(days=7)

                        # O método 'copy' é necessário para não afetar os outros dias da semana do loop
                        # Sem o copy, apenas a última iteração seria armazenada
                        nova = tarefa_base.copy()
                        # O método 'strftime' transforma um objeto de tempo em uma string
                        nova["data_completa"] = data_calc.strftime("%d/%m/%Y")
                        nova["prazo"] = prazo.strftime("%d/%m/%Y %H:%M")
                        # Deixa-se esse marcador para que haja uma distinção entre tarefas únicas e recorrentes
                        nova["recorrente"] = True

                        # Armazena-se no dicionário rotina para que se mantenha a lógica do programa de salvar o dicionário atual
                        rotina[nome_dia_chave].append(nova)
                        dias_salvos.append(nome_dia_chave.capitalize())
                    else:
                        pass
                else:
                    # Adiciona à lista de inválidos se o nome não estiver no mapa
                    dias_invalidos.append(nome)

            if dias_salvos:
                print(f"\n✅ Salvo em: {', '.join(dias_salvos)}!")
                salvar_rotina()
                salvar_tarefas_recorrentes(rotina)
                # Avisa se algo foi ignorado junto com o sucesso
                if dias_invalidos:
                    print(
                        f"⚠️ Ignorado(s): {', '.join(dias_invalidos)}. (Não são dias da semana válidos)"
                    )
                break
            else:
                if dias_invalidos:
                    # Caso onde só haviam palavras inválidas
                    print(f"❌ Nenhum dia válido encontrado para salvar.")
                    print(f"⚠️ Palavra(s) inválida(s): {', '.join(dias_invalidos)}.")
                else:
                    # Caso onde o único problema foi o conflito
                    print("❌ Nenhum dia salvo (conflito ou entrada vazia).")
                break

        if ler_input("\nCadastrar outra recorrente? [S/N]: ").upper() != "S":
            break


# === FUNÇÕES PARA ALTERAR TAREFAS JÁ CRIADAS (EXCLUSÃO E EDIÇÃO) ===
def excluir_tarefa():
    """
    Permite a exclusão permanente de uma tarefa por meio de um ID temporário criado
    pela função visualizar_por_id
    """
    contador = 1
    limpar_tela()
    visualizar_por_id()

    print("\n(Digite 'E' para cancelar)")
    alvo_str = ler_input("Digite o ID da tarefa que deseja excluir: ")
    if alvo_str == "__CANCELAR__":
        return

    try:
        alvo = int(alvo_str)
    except:
        print("ID inválido.")
        return
    # Cada tarefa é analisada individualmente, aumentando o contador nesse processo
    # Quando o contador se iguala ao ID, a tarefa é excluída de rotinas pelo método 'pop' e isso é salvo logo em sequência
    for tarefas in rotina.values():
        for i, _ in enumerate(tarefas):
            if contador == alvo:
                tarefas.pop(i)
                salvar_rotina()
                salvar_tarefas_recorrentes(rotina)
                print("Tarefa excluída com sucesso!")
                return
            contador += 1
    print("ID não encontrado.")


def editar_tarefa():
    """
    Função que permite a edição de tarefas previamente criadas, podendo ser alteradas
    quaisquer especificidades
    """
    limpar_tela()
    print("=== EDITAR TAREFA (MODO FLEXÍVEL) ===\n")
    print("(Digite 'E' para cancelar a qualquer momento)\n")

    # Listar tarefas com ID, facilita o acesso futuro
    todas = []
    n = 1
    for dia, tarefas in rotina.items():
        for i, t in enumerate(tarefas):
            print(f"{n}. {t['descrição']} | {t['data_completa']} {t['inicio']}")
            todas.append((dia, i, t))
            n += 1

    if not todas:
        input("\nNenhuma tarefa cadastrada. Enter para voltar...")
        return

    escolha_str = ler_input("\nID da tarefa para editar: ")
    if escolha_str == "__CANCELAR__":
        return

    try:
        escolha = int(escolha_str)
        if escolha < 1 or escolha > len(todas):
            raise ValueError
    except:
        print("ID inválido.")
        input("Enter para voltar...")
        return

    dia_antigo, idx_antigo, tarefa_antiga = todas[escolha - 1]

    # Aqui começa a edição flexível
    print("\n--- Pressione ENTER para manter o valor atual ---")

    nova = tarefa_antiga.copy()  # Começa com os dados antigos

    # 1. Descrição
    # Se o usuário apenas apertar enter, será mantida o valor atual. Isso vale para todas as próximas seções
    print(f"\nDescrição atual: {tarefa_antiga['descrição']}")
    novo_desc = ler_input("Nova descrição: ")
    if novo_desc == "__CANCELAR__":
        return
    if novo_desc != "":
        nova["descrição"] = novo_desc

    # 2. Setor
    print(f"\nSetor atual: {tarefa_antiga['setor']}")
    print("Setores:")
    for indice_s, setor in enumerate(SETORES):
        print(f"{indice_s + 1}) {setor}")

    novo_setor = ler_input("Novo setor (ID): ")
    if novo_setor == "__CANCELAR__":
        return
    if novo_setor != "":
        if novo_setor.isdigit() and 1 <= int(novo_setor) <= len(SETORES):
            nova["setor"] = SETORES[int(novo_setor) - 1]
        else:
            print("⚠️ Setor inválido, mantendo o anterior.")

    # 3. Prioridade
    print(f"\nPrioridade atual: {tarefa_antiga['prioridade']}")
    print("Prioridades:")
    for indice_p, prioridade in enumerate(PRIORIDADES):
        print(f"{indice_p + 1}) {prioridade}")

    nova_prio = ler_input("Nova prioridade (ID): ")
    if nova_prio == "__CANCELAR__":
        return
    if nova_prio != "":
        if nova_prio.isdigit() and 1 <= int(nova_prio) <= len(PRIORIDADES):
            nova["prioridade"] = PRIORIDADES[int(nova_prio) - 1]
        else:
            print("⚠️ Prioridade inválida, mantendo anterior.")

    # 4. Data
    # São usados os mesmos conceitos que os anteriores para a inserção de datas
    print(f"\nData atual: {tarefa_antiga['data_completa']}")
    nova_data = ler_input("Nova data (DD/MM/AAAA): ")
    if nova_data == "__CANCELAR__":
        return
    if nova_data != "":
        try:
            datetime.strptime(nova_data, "%d/%m/%Y")
            nova["data_completa"] = nova_data
        except:
            print("⚠️ Data inválida, mantendo a anterior.")

    # 5. Horário
    # Apenas usa a função de coletar horário
    print(f"\nHorário atual: {tarefa_antiga['inicio']} - {tarefa_antiga['fim']}")
    mudar_hora = ler_input("Deseja mudar o horário? [S/N] (ENTER = N): ")
    if mudar_hora == "__CANCELAR__":
        return

    if mudar_hora.upper() == "S":
        novos_horarios = coletar_horario()
        if novos_horarios is None:
            return
        nova.update(novos_horarios)

    # Recalcular Prazo e Dia da Semana
    # É salvo na chave prazo uma nova data e horário
    # A data é convertida, usando 'strptime' e 'weekday' em um dia da semana, para ser colocado na chave correta de rotina
    nova["prazo"] = f"{nova['data_completa']} {nova['inicio']}"
    novo_idx = datetime.strptime(nova["prazo"], "%d/%m/%Y %H:%M").weekday()
    novo_dia = DIAS_SEMANA[novo_idx]

    # Validação final antes de trocar
    rotina[dia_antigo].pop(idx_antigo)

    if verificar_conflito(novo_dia, nova["inicio"], nova["fim"], rotina):
        rotina[novo_dia].append(nova)
        salvar_rotina()
        try:
            salvar_tarefas_recorrentes(rotina)
        except:
            pass
        print("\n✔ Tarefa atualizada com sucesso!")
    else:
        rotina[dia_antigo].insert(idx_antigo, tarefa_antiga)
        print("\n🚫 Edição cancelada (conflito). Restaurando original.")

    input("Enter para voltar...")
