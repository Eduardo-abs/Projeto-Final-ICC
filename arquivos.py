import json
import os

# === VARIÁVEIS GLOBAIS === 
PRIORIDADES = ["Baixa", "Média", "Alta"]
SETORES = ["Trabalho", "Família", "Pessoal", "Saúde", "Estudos"]
DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
FINALIZADAS = 0

# Rotinas é um dicionário de listas, com a chave do dicionário sendo os dias da semana 
# Dentro das listas, cada tarefa é, por si só, um dicionário, facilitando a divisão entre as diferentes categorias, como horário, status, etc.
rotina = {dia: [] for dia in DIAS_SEMANA} 



# === FUNÇÕES DE SALVAMENTO ===
def salvar_rotina():
    #Sempre é usado a variável rotina como global, para o dicionário sempre ser atualizado corretamente
    global rotina 
    try:
        with open("rotina.json", "w", encoding="utf-8") as arq:
            json.dump(rotina, arq, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Erro ao salvar: {e}")

    # Backup de segurança
    try:
        with open("rotina_backup.json", "w", encoding="utf-8") as arq:
            json.dump(rotina, arq, ensure_ascii=False, indent=4)
    except:
        pass



def salvar_tarefas_recorrentes(rotina_atual):
    try:
        with open("rotina_recorrente.json", "w", encoding="utf-8") as arq:
            json.dump(rotina_atual, arq, ensure_ascii=False, indent=4)
    except:
        pass




# === FUNÇÃO DE CARREGAMENTO ===
def carregar_rotina():
    """
    Função utilizada para carregar o arquivo .json que contém as rotinas já criadas pelo 
    usuário
    """
    global rotina

    def carregar_recorrentes_ou_novo(): 
        """
        Uso de função aninhada que garante a inicialização de um arquivo .json ou de uma rotina vazia, caso nenhum seja encontrado
        """
        global rotina
        try:
            with open("rotina_recorrente.json", "r", encoding="utf-8") as arq:
                rotina = json.load(arq)
        except:
            rotina = {dia: [] for dia in DIAS_SEMANA}

    try:
        with open("rotina.json", "r", encoding="utf-8") as arq:
            dados = json.load(arq)
            rotina.clear()       
            rotina.update(dados)
    except FileNotFoundError:
        carregar_recorrentes_ou_novo()
    except json.JSONDecodeError:
        try:
            with open("rotina_backup.json", "r", encoding="utf-8") as arq:
                rotina = json.load(arq)
                print("⚠️ Backup restaurado.")
        except:
            carregar_recorrentes_ou_novo()




# === FUNÇÃO DE EXPORTAR RELATÓRIO ===
def exportar_relatorio_txt(): 
    """
    Função para a escrita do relatório em um arquivo .txt de maneira formatada e 
    organizada, com tratamento de erro
    """
    try:
        with open("relatorio.txt", "w", encoding="utf-8") as arq:
            arq.write("RELATÓRIO DE TAREFAS\n" + "=" * 20 + "\n")
            total = sum(len(lista) for lista in rotina.values())
            if total == 0:
                arq.write("\n(Banco de dados vazio)\n")

            for dia, lista in rotina.items():
                if lista:
                    arq.write(f"\n>> {dia.upper()}:\n")
                    for t in lista:
                        tempo = (
                            f"[{t.get('inicio')} - {t.get('fim')}]"
                            if t.get("fim")
                            else f"[Até {t.get('inicio')}]"
                        )
                        arq.write(f"   {tempo} {t['descrição']} \n")
                        for k, v in t.items():
                            if k not in ["descrição", "inicio", "fim", "data_completa", "prazo", "recorrente"]:
                                arq.write(f"      - {k.capitalize()}: {v}\n")
                        arq.write("-" * 20 + "\n")
        print("\n📄 Exportado para 'relatorio.txt'.")
    except Exception as e:
        print(f"Erro: {e}")




# === FUNÇÃO PARA ZERAR ARQUIVOS ===
def resetar_banco_dados():
    """
    Função auxiliar para zerar a rotina e salvar o estado vazio.
    Chamada pela interface quando o usuário confirma a limpeza.
    """
    # Limpa a variável rotina e salva esse arquivo vazio
    # Logo, todos os arquivos .json ficam em branco
    global rotina
    rotina = {dia: [] for dia in DIAS_SEMANA}
    salvar_rotina()
    try:
        salvar_tarefas_recorrentes(rotina)
    except:
        pass
