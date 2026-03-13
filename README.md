# Projeto-Final-ICC

---------------------------------------------------------
PROJETO FINAL - SSC0800 e SSC0801
TÍTULO: TaskPy
INTEGRANTES: Eduardo Affonso Boide Santos N°USP: 16862544
             Felipe Alírio Baruja N°USP: 15636442
             Nicolas Gonçalves Follone N°USP: 16827586
----------------------------------------------------------

[1] COMO EXECUTAR O PROJETO
----------------------------------------------------------
1. Certifique-se de que os 4 arquivos (.py) estão na mesma pasta:
   - main.py
   - arquivos.py
   - interface.py
   - logica.py

2. O programa utiliza apenas bibliotecas padrão do Python (json, os, datetime),
   portanto não é necessário instalar dependências externas.

3. Para iniciar, execute o arquivo 'main.py'.

----------------------------------------------------------
[2] ESTRUTURA DOS ARQUIVOS E FUNÇÕES
----------------------------------------------------------

Abaixo está a descrição da modularização do código e a localização 
de cada função:
Lembrando que cada função está devidamente comentada, explicando seu funcionamento quando este não é intuitivo.

A. ARQUIVO: main.py
   Responsabilidade: Ponto de entrada do programa.
   -------------------------------------------------------
   * menu(): Loop principal que gerencia a navegação do usuário e 
     integra os módulos.

B. ARQUIVO: arquivos.py
   Responsabilidade: Camada de dados, acesso a arquivos (I/O) e variáveis globais.
   -------------------------------------------------------
   * Variáveis Globais: rotina (dict), SETORES (list), PRIORIDADES (list), DIAS_SEMANA (list).
   * salvar_rotina(): Grava o estado atual no arquivo 'rotina.json'.
   * salvar_tarefas_recorrentes(): Grava o backup de tarefas recorrentes.
   * carregar_rotina(): Lê o JSON do disco ou inicia um banco vazio/backup.
   * exportar_relatorio_txt(): Gera o arquivo 'relatorio.txt' com os dados formatados.
   * resetar_banco_dados(): Zera o arquivo rotina e exclui todas as tarefas após salvar e sair do programa.

C. ARQUIVO: interface.py
   Responsabilidade: Interação com o usuário (Prints, Inputs e Menus Visuais).
   -------------------------------------------------------
   * limpar_tela(): Utilitário para limpar o terminal (Windows/Linux).
   * ler_input(): Wrapper de input que trata o comando de cancelamento ('E').
   * coletar_dados_basicos(): Pede descrição, setor e prioridade.
   * coletar_horario(): Pede e valida horários (vencimento ou intervalo).
   * visualizar_por_id(): Cria índice temporário para listagem simples.
   * visualizar_por_setor(): Filtra e exibe tarefas por categoria.
   * visualizar_por_data(): Ordena cronologicamente e exibe tarefas.
   * visualizar_por_prioridade(): Filtra e exibe tarefas por nível de urgência.
   * menu_relatorios(): Sub-menu para exportação e limpeza de dados.
   * limpar_todas_tarefas(): Função integral que solicita confirmação e reseta
     o banco de dados (acessando persistencia.rotina).

D. ARQUIVO: logica.py
   Responsabilidade: Regras de negócio, cálculos de data e manipulação de listas.
   -------------------------------------------------------
   * verificar_conflito(): Algoritmo que detecta sobreposição de horários.
   * adicionar_rotina_unica(): Monta e salva uma tarefa para data específica.
   * tarefas_recorrentes(): Calcula datas futuras baseadas em dias da semana
     (lógica de repetição semanal).
   * excluir_tarefa(): Localiza tarefa pelo ID visual e a remove do banco.
   * editar_tarefa(): Permite alteração de campos com suporte a rollback 
     (desfaz alterações em caso de conflito de horário).

----------------------------------------------------------
[3] OBSERVAÇÕES ADICIONAIS
----------------------------------------------------------
- O sistema gera automaticamente os arquivos .json na primeira execução.
- O backup de segurança é carregado automaticamente caso o arquivo principal
  esteja corrompido.
- A exclusão e edição utilizam índices temporários gerados em tempo de execução
  para facilitar a experiência do usuário.
