import json #Biblioteca necessária para salvar a rotina mesmo após o encerramento do programa
import os #Biblioteca utilizada para beleza do programa, limpando o terminal em ocasiões específicas
from datetime import datetime, timedelta #Biblioteca necessária para o uso correto e simplificado de dias no programa


from arquivos import (
    carregar_rotina, 
    salvar_rotina, 
    rotina, 
    FINALIZADAS
)

from interface import (
    limpar_tela, 
    visualizar_por_setor, 
    visualizar_por_data, 
    visualizar_por_prioridade, 
    menu_relatorios
)

from logica import (
    adicionar_rotina_unica, 
    tarefas_recorrentes, 
    excluir_tarefa, 
    editar_tarefa
)


# === MENU PRINCIPAL ===
def menu():
    global FINALIZADAS
    carregar_rotina()
    while True:
        limpar_tela()
        total = sum(len(lista) for lista in rotina.values())
        print(f"""
========================================
    GERENCIADOR DE ROTINAS (GRUPO 14)
    Total de Tarefas: {total} | Concluídas: {FINALIZADAS}
========================================
[GERENCIAR]
1. Adicionar Tarefa Única
2. Adicionar Tarefa Recorrente
3. Excluir Tarefa
4. Editar Tarefa (Modo Flexível)
5. Finalizar tarefa

[VISUALIZAR]
6. Visualizar por Setor
7. Visualizar por Data
8. Visualizar por Prioridade

[RELATÓRIOS]
9. Acessar Área de Relatórios

[SAÍDA]
0. Sair e Salvar
========================================""")
        try:
            op_str = input("Opção (ou 'E' para sair): ")
            if op_str.upper() == 'E' or op_str == '0':
                salvar_rotina()
                print("👋 Tchau!")
                break
            
            if not op_str.isdigit():
                print("Digite um número.")
                continue

            op = int(op_str)
            
            if op == 1: adicionar_rotina_unica()
            elif op == 2: tarefas_recorrentes()
            elif op == 3: excluir_tarefa()
            elif op == 4: editar_tarefa()
            elif op == 5:
                excluir_tarefa()
                FINALIZADAS += 1
            elif op == 6: visualizar_por_setor()
            elif op == 7: visualizar_por_data()
            elif op == 8: visualizar_por_prioridade()
            elif op == 9: menu_relatorios()
            else: input("Inválido!")
        except Exception as e:
            input(f"Erro inesperado: {e}")

if __name__ == "__main__":
    menu()



