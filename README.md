# Data Pilot

O Data Pilot é um painel de vendas desenvolvido em Python. Ele organiza dados de pedidos, calcula indicadores e permite consultar esses resultados em português por meio de um assistente conectado a um modelo de linguagem. As respostas usam métricas calculadas pelo projeto.

## O que o projeto faz

- Inspeciona e prepara os dados de vendas com pandas.
- Calcula receita, pedidos concluídos, unidades vendidas, clientes únicos, ticket médio, cancelamentos e receita mensal.
- Exibe indicadores e evolução mensal em um painel interativo.
- Permite fazer perguntas sobre as métricas em linguagem natural.

## Tecnologias

- Python e pandas: preparação e análise dos dados.
- Streamlit: interface do painel, filtros e chat.
- Plotly Express: gráfico interativo de receita mensal.
- OpenRouter: acesso ao modelo de IA configurado pelo projeto.
- Jupyter Notebook: documentação do processo de análise e ETL.

## Estrutura do projeto

    .
    ├── data/
    │   └── sales.csv                 # Dados originais
    ├── data_processed/
    │   └── sales_clean.csv           # Dados tratados para o painel
    ├── src/
    │   ├── app.py                    # Interface Streamlit e visualizações
    │   ├── llm.py                    # Integração com OpenRouter e contexto do chat
    │   ├── metrics.py                # Cálculo das métricas de vendas
    │   └── preprocess.py             # Extração, limpeza e carga (ETL)
    ├── main.ipynb                    # Análise exploratória, ETL e visão dos módulos
    ├── main.py                       # Ponto de entrada alternativo
    ├── .streamlit/config.toml                   # Tema visual do Streamlit
    ├── .env.example                  # Exemplo de configuração da IA
    ├── requirements.txt              # Dependências para instalação com pip
    └── pyproject.toml                # Metadados e dependências do projeto

## Como executar

Requer Python 3.11 ou superior.

1. Crie e ative um ambiente virtual.
2. Instale as dependências:

       pip install -r requirements.txt

3. Copie .env.example para .env e configure OPENROUTER_API_KEY. O arquivo .env é ignorado pelo Git.
4. Prepare o CSV tratado, executando a partir da pasta raiz do projeto:

       python src/preprocess.py

5. Inicie o painel:

       streamlit run src/app.py

Também é possível iniciar com python main.py.

## Configuração da IA

O projeto usa o serviço OpenRouter. A chave é lida da variável OPENROUTER_API_KEY. O modelo pode ser escolhido em OPENROUTER_MODEL; se essa variável não estiver definida, src/llm.py usa ~openai/gpt-mini-latest como padrão. O valor definido no .env tem precedência sobre esse padrão.

A função build_data_context prepara as métricas e os dados mensais. A função ask_openrouter envia esse contexto junto da pergunta. Há também em src/llm.py uma implementação de chamadas de ferramentas (run_agent), que executa métricas do próprio projeto.

## Notebook

Abra main.ipynb na raiz para acompanhar a inspeção dos dados originais, a distribuição de variáveis, comparações entre grupos e as etapas Extract, Transform e Load. O encerramento do notebook resume os principais módulos usados pelo painel e pelo assistente.
