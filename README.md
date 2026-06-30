# 📊 DISTRIBOX - SISTEMA DE ANÁLISE ESTRATÉGICA
# ============================================================================
# Guia Completo para Entrevistadores
# ============================================================================


## 📋 ÍNDICE

1. SOBRE O PROJETO
2. ARQUITETURA DA SOLUÇÃO
3. FUNCIONALIDADES
4. ESTRUTURA DO CÓDIGO
5. COMO EXECUTAR
6. DECISÕES TÉCNICAS
7. ANÁLISE DOS RESULTADOS
8. MELHORIAS FUTURAS


# ============================================================================
# 1. SOBRE O PROJETO
# ============================================================================

## 1.1 Contexto do Negócio

A Distribox é uma rede de varejo de moda com 15 lojas físicas de diferentes perfis
(Prime, Brands, Outlet e Distrito) e um Centro de Distribuição (CD). A empresa
cresceu rapidamente e seus dados estão distribuídos em vários sistemas.

## 1.2 O Desafio

A diretoria precisa realizar uma RAE (Reunião de Alinhamento Estratégico) e
necessita de uma visão clara do negócio. Os dados foram exportados de diferentes
sistemas, em formatos variados, e não conversam entre si.

## 1.3 Objetivo do Projeto

Desenvolver uma aplicação que:
- Organize e trate dados brutos de múltiplas fontes
- Consolide as informações em um modelo confiável
- Forneça uma interface para consulta e análise
- Gere insights estratégicos para a diretoria


# ============================================================================
# 2. ARQUITETURA DA SOLUÇÃO
# ============================================================================

## 2.1 Stack Tecnológica

CAMADA DE APRESENTAÇÃO
  └── Streamlit (Interface Web Interativa)

CAMADA DE VISUALIZAÇÃO
  └── Plotly (Gráficos Interativos)

CAMADA DE ANÁLISE
  ├── Pandas (Manipulação de Dados)
  ├── NumPy (Processamento Matemático)
  └── Scikit-learn (Regressão Linear para Projeção)

CAMADA DE DADOS
  └── CSV Files (Vendas, Produtos, Clientes, Lojas, Estoque)

## 2.2 Modelo de Dados (Estrela)

TABELA FATO: VENDAS (Movimentações)
    │
    ├── DIMENSÃO: PRODUTOS
    ├── DIMENSÃO: CLIENTES
    ├── DIMENSÃO: VENDEDORES
    ├── DIMENSÃO: LOJAS
    └── DIMENSÃO: TEMPO

Vantagens do Modelo Estrela:
- Facilita consultas e agregações
- Reduz duplicidade de dados
- Melhora a performance
- Padroniza nomenclatura entre diferentes fontes


# ============================================================================
# 3. FUNCIONALIDADES
# ============================================================================

## 3.1 Dashboard Estratégico (🏠)

OBJETIVO: Visão geral do negócio para a diretoria

MÉTRICAS EXIBIDAS:
- 💰 Faturamento Total
- 📋 Total de Vendas
- 📦 Itens Vendidos
- 🎫 Ticket Médio

GRÁFICOS:
- Vendas por Loja (Barras)
- Vendas por Tipo de Loja (Pizza)

## 3.2 Consulta de Produtos (📦)

OBJETIVO: Pesquisar produtos no estoque do CD

FILTROS (com autocomplete):
- 🔍 Referência
- 📏 Tamanho
- 🎨 Cor

INFORMAÇÕES EXIBIDAS:
- Referência (código único)
- Descrição do produto
- Tamanho e Cor
- Estoque Atual e Mínimo
- Preço de Custo
- Grupo e Marca

## 3.3 Consulta de Vendas (🛒)

OBJETIVO: Analisar vendas com filtros combináveis

FILTROS (com autocomplete):
- 📅 Período (Data Início/Fim)
- 🏪 Loja
- 👤 Vendedor
- 👥 Cliente

RESULTADOS:
- Totais (Vendas, Itens, Faturamento, Ticket Médio)
- Detalhamento (Data, Loja, Vendedor, Cliente, Preço, Quantidade)

## 3.4 Projeção de Vendas (📈)

OBJETIVO: Prever vendas futuras usando Regressão Linear

CONFIGURAÇÕES:
- 🏪 Loja (autocomplete)
- 📅 Horizonte (3 a 12 períodos)
- 📊 Período de Agregação (Diário/Semanal/Mensal)

RESULTADOS:
- Gráfico com Histórico (azul) e Projeção (vermelha)
- R² (qualidade da projeção)
- Tendência Diária

## 3.5 Apresentação RAE (📋)

OBJETIVO: Relatório executivo para a diretoria

CONTEÚDO:
- Resumo Executivo (métricas principais)
- Análise de Performance (Top 3 Lojas e Vendedores)
- Recomendações Estratégicas
- Download do Relatório (TXT)


# ============================================================================
# 4. ESTRUTURA DO CÓDIGO
# ============================================================================

## 4.1 Organização do Código (app.py)

A aplicação está organizada em 10 seções principais:

1. CONFIGURAÇÃO DA PÁGINA
   └── st.set_page_config(...)

2. FUNÇÃO DE AJUDA (HELP)
   └── mostrar_ajuda(): Exibe guia interativo com instruções didáticas

3. FUNÇÕES DE CARREGAMENTO
   └── carregar_dados(): Carrega todos os arquivos CSV

4. FUNÇÃO DE FORMATAÇÃO DE MOEDA
   └── formatar_moeda(): Formata valores no padrão brasileiro

5. FUNÇÕES DE LIMPEZA DE DADOS
   └── limpar_dados(): Aplica limpeza inteligente nos dados

6. CONSOLIDAÇÃO DE DADOS (Modelo Estrela)
   └── consolidar_dados(): Consolida dados em modelo dimensional

7. FUNÇÃO PARA CRIAR COMBOBOX COM DIGITAÇÃO
   └── filtro_autocomplete(): Cria filtro com autocomplete

8. CONSULTA DE PRODUTOS
   └── consultar_produtos(): Consulta produtos com estoque no CD

9. CONSULTA DE VENDAS
   └── consultar_vendas(): Consulta vendas com filtros

10. PROJEÇÃO DE VENDAS
    └── projetar_vendas(): Projeta vendas usando Regressão Linear

11. VISUALIZAÇÕES ESTRATÉGICAS
    └── criar_dashboard_estrategico(): Cria visualizações para RAE

12. INTERFACE PRINCIPAL
    └── main(): Função principal da aplicação

## 4.2 Fluxo de Dados

1. CARREGAMENTO
   └── CSV Files (vendas_p1, vendas_p2, produtos, clientes, etc.)

2. LIMPEZA (limpar_dados)
   ├── Remove espaços extras
   ├── Padroniza textos
   ├── Converte tipos de dados
   ├── Trata valores nulos
   └── Remove duplicatas

3. CONSOLIDAÇÃO (consolidar_dados)
   ├── Concatena vendas (p1 + p2)
   ├── Calcula valor_total
   ├── Filtra apenas o CD para estoque
   └── Cria modelo estrela

4. ANÁLISE E VISUALIZAÇÃO
   ├── Dashboard Estratégico
   ├── Consulta de Produtos
   ├── Consulta de Vendas
   ├── Projeção de Vendas
   └── Apresentação RAE


# ============================================================================
# 5. COMO EXECUTAR
# ============================================================================

## 5.1 Pré-requisitos

- Python 3.9 ou superior
- Pip (gerenciador de pacotes Python)

## 5.2 Instalação

1. Clone o repositório:
   git clone https://github.com/seu-usuario/distribox-analise.git
   cd distribox-analise

2. Instale as dependências:
   pip install streamlit pandas numpy plotly scikit-learn

3. Verifique os arquivos necessários:
   - app.py
   - vendedores.csv
   - clientes.csv
   - lojas.csv
   - produtos.csv
   - variacoes_estoque.csv
   - vendas_2026_p1.csv
   - vendas_2026_p2.csv

## 5.3 Execução

Para iniciar a aplicação:
   streamlit run app.py

A aplicação abrirá automaticamente no navegador:
   http://localhost:8501

## 5.4 Estrutura de Arquivos

projeto_distribox/
├── app.py                    # Código principal da aplicação
├── vendedores.csv            # Cadastro de vendedores
├── clientes.csv              # Cadastro de clientes
├── lojas.csv                 # Cadastro de lojas
├── produtos.csv              # Catálogo de produtos
├── variacoes_estoque.csv     # Estoque por tamanho/cor
├── vendas_2026_p1.csv        # Vendas - Parte 1
├── vendas_2026_p2.csv        # Vendas - Parte 2
└── README.md                 # Documentação


# ============================================================================
# 6. DECISÕES TÉCNICAS
# ============================================================================

## 6.1 Modelagem de Dados (Modelo Estrela)

DECISÃO: Consolidar os dados em um modelo estrela

JUSTIFICATIVA:
- Facilita consultas e agregações
- Reduz duplicidade de dados
- Melhora a performance das consultas
- Padroniza a nomenclatura entre diferentes fontes

IMPLEMENTAÇÃO:
- Fato: Vendas
- Dimensões: Produtos, Clientes, Lojas, Vendedores, Tempo

## 6.2 Estoque Centralizado

DECISÃO: Considerar o CD como única fonte de estoque

JUSTIFICATIVA:
- O arquivo variacoes_estoque.csv contém apenas o CD (00 - CD)
- O estoque é centralizado e abastece todas as lojas físicas
- Simplifica a lógica de consulta de produtos
- Evita inconsistências de estoque entre lojas

IMPLEMENTAÇÃO:
df_estoque_cd = df_estoque[df_estoque['IDENTIFICACAO'] == '00 - CD']

## 6.3 Limpeza Robusta de Dados

DECISÃO: Função de limpeza específica para cada tipo de dado

JUSTIFICATIVA:
- Dados vêm de sistemas diferentes com formatos variados
- Colunas têm separadores decimais diferentes (vírgula vs ponto)
- Datas estão em formatos diversos
- Valores nulos e duplicatas precisam ser tratados

TRATAMENTOS:
- Padronização de texto (strip, replace)
- Conversão de tipos (numéricos, datas, booleanos)
- Tratamento de separadores decimais
- Remoção de duplicatas

## 6.4 Combobox com Autocomplete

DECISÃO: Usar st.selectbox com suporte a digitação para todos os filtros

JUSTIFICATIVA:
- Listas longas (produtos, clientes) dificultam a navegação
- Melhora a experiência do usuário
- Reduz erros de digitação
- Agiliza a pesquisa

IMPLEMENTAÇÃO:
def filtro_autocomplete(label, options, placeholder, allow_all):
    options_with_all = ['Todos'] + sorted(set(options_clean))
    return st.selectbox(label, options_with_all, index=0, placeholder=placeholder)

## 6.5 Formatação no Padrão Brasileiro

DECISÃO: Exibir valores monetários no formato brasileiro

JUSTIFICATIVA:
- A empresa é brasileira
- Facilita a interpretação pela diretoria
- Padrão do mercado local

IMPLEMENTAÇÃO:
def formatar_moeda(valor):
    valor_formatado = f"{valor:,.2f}"
    valor_br = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_br}"

Exemplo: 35169447.94 -> R$ 35.169.447,94

## 6.6 Projeção com Regressão Linear

DECISÃO: Utilizar Regressão Linear para projeções de vendas

JUSTIFICATIVA:
- Simples e interpretável
- Funciona bem com dados com tendência
- Fornece métrica de qualidade (R²)
- Baixo custo computacional

LIMITAÇÕES:
- Não captura sazonalidade complexa
- Assume tendência linear
- Sensível a outliers

IMPLEMENTAÇÃO:
model = LinearRegression()
model.fit(X, y)
projecao = model.predict(X_futuro)
r2 = model.score(X, y)  # Qualidade da projeção

## 6.7 Cache de Dados

DECISÃO: Utilizar @st.cache_data para otimizar performance

JUSTIFICATIVA:
- Carregamento de dados é custoso
- Os dados não mudam durante a sessão
- Melhora a experiência do usuário
- Reduz tempo de carregamento

IMPLEMENTAÇÃO:
@st.cache_data
def carregar_dados():
    # Código de carregamento


# ============================================================================
# 7. ANÁLISE DOS RESULTADOS
# ============================================================================

## 7.1 Exemplo de Dashboard

MÉTRICAS PRINCIPAIS:
- 💰 Faturamento Total: R$ 3.516.944,79
- 📋 Total de Vendas: 43
- 📦 Itens Vendidos: 127
- 🎫 Ticket Médio: R$ 295,00

## 7.2 Interpretação do R²

R² = 0,53 (Regular)

O QUE SIGNIFICA:
- 53% de confiança na projeção
- 47% de chance de erro
- É como jogar uma moeda (cara ou coroa)

POR QUE ESTÁ BAIXO:
- Poucos dados históricos (apenas 6 meses)
- Vendas irregulares (picos e quedas)
- Sazonalidade não capturada
- Eventos especiais (promoções, liquidações)

RECOMENDAÇÕES:
- Use a projeção apenas para tendência geral
- Não confie nos valores exatos
- Combine com conhecimento de negócio
- Agregue por mês em vez de dia (suaviza variações)

## 7.3 Insights Gerados

1. Loja com melhor desempenho: 15 - Metrô Outlet
   - Faturamento: R$ 800.000,00
   - Vendeu o dobro da segunda colocada

2. Melhor vendedor: LUCAS CAMPOS PEREIRA
   - Faturamento: R$ 10.000,00
   - Pode servir como mentor para outros vendedores

3. Sazonalidade identificada
   - Melhor mês: Junho (inverno - casacos)
   - Pior mês: Janeiro (verão - poucos casacos)
   - Recomendação: Campanhas específicas para período de baixa

4. Ticket Médio: R$ 295,00
   - Acima de R$ 100,00 -> Considere up-selling e cross-selling


# ============================================================================
# 8. MELHORIAS FUTURAS
# ============================================================================

## 8.1 Planejadas

- Adicionar mais métodos de projeção:
  - ARIMA (sazonalidade)
  - Prophet (Facebook)
  - Média Móvel (simples)

- Incluir análise de sazonalidade:
  - Identificar padrões mensais
  - Ajustar projeções com base na sazonalidade

- Dashboard de KPIs por vendedor:
  - Meta vs realizado
  - Comissões
  - Performance histórica

- Exportação para PowerPoint/PDF:
  - Relatórios automáticos
  - Apresentações prontas para RAE

- Alertas automáticos:
  - Estoque baixo
  - Metas não atingidas
  - Queda brusca nas vendas

- Integração com banco de dados SQL:
  - Dados em tempo real
  - Maior escalabilidade

## 8.2 Próximos Passos

1. Coletar mais dados históricos (2024 e 2025)
2. Implementar modelo ARIMA para capturar sazonalidade
3. Criar dashboard de metas por vendedor
4. Adicionar filtro por categoria de produto
5. Implementar alertas de estoque baixo


# ============================================================================
# 9. CONTATO
# ============================================================================

DESENVOLVEDOR
- Nome: Carlos Alberto
- Email: carloshouser@gmail.com
- GitHub: [github.com/seu-usuario]
- LinkedIn: https://www.linkedin.com/in/carlos-alberto-sistemas/


# ============================================================================
# 10. LICENÇA
# ============================================================================

Uso interno - Distribox

Este projeto foi desenvolvido como parte do processo seletivo para a posição de
Cientista de Dados Sênior.


# ============================================================================
# FIM DO DOCUMENTO
# ============================================================================
