"""
============================================================================
 DISTRIBOX - SISTEMA DE ANÁLISE ESTRATÉGICA DE VAREJO DE MODA
============================================================================

O QUE ESTE PROGRAMA FAZ?
------------------------
Lê as planilhas (arquivos .csv) de uma rede de lojas de roupas e transforma
os dados "crus" em informações úteis para a tomada de decisão:
faturamento, lucro, melhores lojas, melhores vendedores, projeções de
vendas e recomendações automáticas para a diretoria.

COMO O PROGRAMA ESTÁ ORGANIZADO? (leia de cima para baixo)
----------------------------------------------------------
  1. CONFIGURAÇÕES   -> "números de regra de negócio" em um só lugar
  2. AJUDA           -> guia de uso que aparece dentro do site
  3. CARREGAMENTO    -> lê os arquivos .csv do disco
  4. LIMPEZA         -> arruma os dados (datas, números, textos)
  5. CONSOLIDAÇÃO    -> junta tudo e calcula valor, custo e lucro
  6. CONSULTAS       -> funções que respondem perguntas (produtos, vendas)
  7. PROJEÇÃO        -> usa estatística para prever vendas futuras
  8. GRÁFICOS        -> desenha os gráficos na tela
  9. ANÁLISE         -> gera conclusões e recomendações para os diretores
 10. INTERFACE (main)-> monta as 5 páginas que o usuário navega

COMO EXECUTAR?
--------------
No terminal, dentro desta pasta, rode:
    streamlit run main.py

DICA PARA QUEM ESTÁ APRENDENDO:
-------------------------------
"DataFrame" (abreviado como `df`) é simplesmente uma TABELA na memória do
computador, igual a uma planilha do Excel: tem linhas e colunas. A biblioteca
que cuida dessas tabelas se chama "pandas" (apelido: pd).
============================================================================
"""

# --- Bibliotecas que usamos (cada "import" traz uma "caixa de ferramentas") ---
import streamlit as st                       # Cria o site/dashboard na tela
import pandas as pd                          # Trabalha com tabelas (DataFrames)
import numpy as np                           # Cálculos numéricos rápidos
import plotly.express as px                  # Gráficos prontos e bonitos
import plotly.graph_objects as go            # Gráficos personalizados
from typing import Tuple, Dict, List, Optional  # Apenas "dicas" de tipo (didático)
from datetime import datetime, timedelta     # Trabalha com datas
from sklearn.linear_model import LinearRegression  # Modelo de previsão (IA simples)


# ============================================================================
# 0. CONFIGURAÇÕES DO NEGÓCIO (os "números mágicos" ficam todos aqui!)
# ============================================================================
# Por que isso é importante? Em vez de espalhar números soltos pelo código
# (o que confunde e dificulta a manutenção), nós damos um NOME a cada regra.
# Assim, se a diretoria mudar uma meta, você altera em UM lugar só.

# Metas e limiares de FATURAMENTO e TICKET (valor médio por venda)
META_FATURAMENTO_SAUDAVEL = 100_000   # Acima disso, o negócio vai bem (R$)
TICKET_MEDIO_OTIMO        = 300       # Ticket acima disso é considerado ótimo (R$)
TICKET_MEDIO_ACEITAVEL    = 150       # Entre aceitável e ótimo é "ok"; abaixo é baixo
TICKET_MEDIO_ALVO         = 200       # Abaixo disso, sugerimos ações de venda (R$)

# Limiares de MARGEM DE LUCRO (quanto sobra depois de pagar o custo do produto)
MARGEM_OTIMA   = 55   # Margem acima disso é excelente (%)
MARGEM_MINIMA  = 40   # Abaixo disso, acende um alerta de rentabilidade (%)

# Outros limiares de análise
VARIACAO_SAZONAL_ALERTA      = 30   # Variação entre melhor e pior mês acima disso = alerta (%)
CONCENTRACAO_VENDEDORES_ALERTA = 40 # Se top 3 vendedores fazem mais que isso = risco (%)
MIN_PERIODOS_PARA_PROJETAR   = 3    # Precisamos de pelo menos 3 pontos para prever

# Nomes de meses em português (índice 0 fica vazio para casar com mês 1 = Janeiro)
NOMES_MESES = ['', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
               'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']


# ============================================================================
# CONFIGURAÇÃO DA PÁGINA (título, ícone e layout da aba do navegador)
# ============================================================================
st.set_page_config(
    page_title="Distribox - Análise Estratégica",
    page_icon="👔",
    layout="wide",                      # Usa a largura toda da tela
    initial_sidebar_state="expanded"    # Já abre o menu lateral
)

# ============================================================================
# DOCUMENTAÇÃO E AJUDA COMPLETA - INTERFACE EDUCATIVA
# ============================================================================
def mostrar_ajuda():
    """
    Exibe um guia de uso interativo e completo dentro da aplicação.
    Inclui explicações didáticas de cada funcionalidade.
    """
    with st.expander("❓ Como usar o sistema? (Guia Completo)", expanded=False):
        st.markdown("""
        ---
        # 📚 Guia de Uso Completo - Distribox

        ## 🎯 Sobre o Sistema

        O **Distribox** é uma plataforma de análise estratégica para a rede de varejo de moda.
        Ele consolida dados de 15 lojas físicas + 1 Centro de Distribuição, permitindo análises
        em tempo real de vendas, estoque e performance.

        **Dados disponíveis**: Janeiro a Junho de 2026

        ---

        ## 🏠 1. Dashboard Estratégico (Visão Geral do Negócio)

        **O que você encontra aqui?**
        É a primeira tela que todo diretor vê. Mostra um resumo executivo do negócio.

        **Métricas principais:**
        - 💰 **Faturamento Total**: Todo o dinheiro que a rede recebeu com vendas
        - 💵 **Lucro Bruto**: O que SOBRA depois de pagar o custo dos produtos (Faturamento − Custo)
        - 📊 **Margem de Lucro**: Quanto % do faturamento virou lucro (quanto maior, melhor!)
        - 🎫 **Ticket Médio**: Valor médio gasto por cliente por transação

        💡 **Diferença essencial**: Faturamento é o quanto VENDEMOS;
        Lucro é o quanto realmente GANHAMOS depois de pagar os custos.

        **Gráficos interativos:**
        - **Vendas por Loja**: Barra horizontal mostrando qual loja gera mais faturamento
        - **Distribuição por Tipo de Loja**: Pizza mostrando % de vendas (Prime, Brands, Outlet, Distrito)

        **Como interpretar:**
        > Lojas com barras mais altas = melhor performance
        > Lojas com % maiores no gráfico de pizza = maior participação nas vendas totais

        **💡 Dica executiva**: Use este dashboard para uma visão rápida da saúde do negócio
        antes de entrar em detalhes.

        ---

        ## 📦 2. Consulta de Produtos (Catálogo com Estoque)

        **Para que serve?**
        Pesquisar produtos disponíveis no **Centro de Distribuição (CD)** que abastece
        todas as 15 lojas físicas.

        **Como usar - 3 passos simples:**

        1. **Referência** (código do produto)
           - Ex: "CASACO", "19.907", "BOLSA"
           - Dica: Você pode digitar apenas PARTE do nome!

        2. **Tamanho** (P, M, G, GG ou números como 36, 38, 40, 42)
           - Ex: "M", "G", "38"
           - Se deixar em branco = todos os tamanhos

        3. **Cor** (nome da cor)
           - Ex: "PRETO", "BRANCO", "CARAMELO"
           - Se deixar em branco = todas as cores

        **O que aparece no resultado:**
        - Referência e Descrição (nome do produto)
        - Tamanho e Cor disponíveis
        - **Estoque Atual**: Quantidade disponível no CD
        - **Estoque Mínimo**: Quantidade recomendada para manter
        - **Preço Custo**: Quanto a rede pagou pelo produto
        - Grupo e Marca

        **Estatísticas automáticas:**
        - Total de peças disponíveis
        - Número de produtos diferentes (SKUs)
        - Preço médio dos produtos encontrados

        **📌 Exemplo prático:**
        ```
        Pergunta: Temos CASACO CARAMELO tamanho M no CD?

        Ação:
        1. Digite "CASACO" na Referência
        2. Digite "M" no Tamanho
        3. Digite "CARAMELO" na Cor
        4. Clique em "Consultar Produtos"

        Resultado: Mostra todos os CASACOS caramelo tamanho M com estoque
        ```

        ---

        ## 🛒 3. Consulta de Vendas (Histórico de Transações)

        **Para que serve?**
        Analisar vendas com filtros avançados (data, loja, vendedor, cliente).

        **Filtros disponíveis:**
        1. **Data Início e Data Fim**: Selecione o período
        2. **Loja**: Filtre por loja específica (ex: "15 - Metrô Outlet")
        3. **Vendedor**: Filtre por nome (ex: "LUCAS CAMPOS")
        4. **Cliente**: Filtre por código do cliente (ex: "15091")

        **Deixe os campos em branco para não filtrar!**

        **O que aparece:**
        Uma tabela com todas as vendas que atendem aos critérios, mostrando:
        - **Data**: Quando a venda aconteceu
        - **Loja**: Qual loja realizou a venda
        - **Vendedor**: Quem vendeu
        - **Cliente**: Código do cliente que comprou
        - **Preço Unitário**: Quanto custou cada peça
        - **Quantidade**: Quantas peças foram compradas
        - **Valor Total**: Preço × Quantidade (com descontos aplicados)

        **Métricas resumidas:**
        - Total de Vendas: Quantas transações
        - Itens Vendidos: Quantas peças
        - Faturamento: Valor total em R$
        - Ticket Médio: Valor médio por transação

        **📌 Exemplo de análise:**
        ```
        Pergunta: Como está a performance de LUCAS CAMPOS?

        Ação:
        1. Digite "LUCAS" no campo Vendedor
        2. Deixe os outros campos em branco
        3. Clique em "Consultar Vendas"

        Resultado: Todas as vendas de LUCAS no período, valor total e ticket médio
        ```

        ---

        ## 📈 4. Projeção de Vendas (Previsão Futura com IA)

        **Para que serve?**
        Usar histórico de vendas para **prever** como serão as vendas futuras.
        Ajuda no planejamento de estoque e recursos.

        **Como usar - 3 configurações:**

        1. **Selecione a Loja**
           - Escolha qual loja você quer analisar
           - Ou selecione "Todos" para análise consolidada

        2. **Horizonte de Projeção** (3 a 12 períodos)
           - Quantos períodos (dias/semanas/meses) você quer prever?
           - Padrão: 6 períodos

        3. **Período de Agregação**
           - 📅 **Diário**: Mostra previsão dia a dia (mais volátil)
           - 📆 **Semanal**: Mostra previsão por semana (mais estável)
           - 📊 **Mensal**: Mostra previsão por mês (visão estratégica)

        **O que aparece:**
        - **Gráfico com duas linhas:**
          - 🔵 Linha azul = Histórico de vendas (dados reais passados)
          - 🔴 Linha vermelha pontilhada = Projeção (previsão futura)

        - **Métrica R² (Qualidade da Projeção):**
          - Varia de 0 a 1
          - R² = 0,95 significa 95% de confiança
          - R² > 0,80 = Boa previsão
          - R² < 0,60 = Confiabilidade baixa (dados voláteis)

        - **Tendência Diária:**
          - Se positiva = vendas aumentando
          - Se negativa = vendas diminuindo
          - Se próxima a zero = vendas estáveis

        **⚠️ Importante:**
        A projeção assume uma tendência LINEAR. Se as vendas são sazonais
        (variam muito por mês/estação), a previsão será menos precisa.

        **📌 Exemplo:**
        ```
        Pergunta: Como será o faturamento da Loja 15 nos próximos 6 meses?

        Ação:
        1. Selecione "15 - Metrô Outlet"
        2. Horizonte = 6
        3. Período = Mensal
        4. Clique em "Gerar Projeção"

        Resultado: Gráfico mostrando histórico + projeção mensal de R$ de vendas
        ```

        ---

        ## 📋 5. Apresentação RAE (Relatório Executivo)

        **Para que serve?**
        Gerar um relatório executivo pronto para apresentar aos diretores
        com análises, conclusões e recomendações estratégicas.

        **Seções do relatório:**

        ### 🎯 Resumo Executivo
        - Faturamento Total do período
        - Quantidade total de vendas
        - Ticket Médio (valor por venda)

        ### 🏆 Análise de Performance
        - **Top 5 Lojas**: Quais lojas vendem mais (por faturamento)
        - **Top 5 Vendedores**: Melhores comerciantes
        - **💵 Ranking de Lojas por Margem**: Quais lojas mais LUCRAM (não só vendem!)
          - Uma loja pode faturar muito mas lucrar pouco se der descontos demais.
          - O gráfico vai do verde (rentável) ao vermelho (margem baixa).
          - Mostramos a loja mais e a menos rentável da rede.

        ### 📊 Análise Detalhada
        - **Sazonalidade**: Qual mês foi melhor/pior?
        - **Ticket Médio**: Está alto ou baixo?
        - **Cobertura**: Quantas lojas têm vendas registradas?
        - **Mix de Vendas**: Como está distribuído entre tipos de loja?

        ### 💡 Recomendações Estratégicas
        O sistema gera recomendações automáticas baseadas nos dados:
        - Se ticket é baixo → sugerir up-selling/cross-selling
        - Se tem sazonalidade → sugerir campanhas para baixa
        - Se cobertura é baixa → alertar sobre lojas inativas
        - Se performance é desigual → sugerir treinamento/revisão de operações

        ### 📥 Download do Relatório
        Botão para baixar o relatório em formato TXT para apresentar
        em reuniões de diretoria.

        ---

        ## 🎓 Glossário - Termos Importantes

        | Termo | Significado |
        |-------|------------|
        | **Faturamento** | Total de dinheiro arrecadado com vendas |
        | **Custo** | Quanto a rede pagou pelos produtos que foram vendidos |
        | **Lucro Bruto** | O que sobra: Faturamento − Custo |
        | **Margem de Lucro** | Lucro ÷ Faturamento, em % (ex: margem de 45% = de cada R$ 100 vendidos, R$ 45 são lucro) |
        | **Ticket Médio** | Valor médio de cada venda (Faturamento ÷ nº de vendas) |
        | **SKU** | Stock Keeping Unit = código único do produto |
        | **CD** | Centro de Distribuição (armazém que abastece as lojas) |
        | **SAIDA** | Quando um produto sai do CD para a loja (venda) |
        | **Estoque Mínimo** | Quantidade mínima recomendada para manter em CD |
        | **R²** | Coeficiente de determinação (qualidade da previsão: 0 a 1) |
        | **Sazonalidade** | Padrão de vendas que se repete em certas épocas |
        | **Prime** | Tipo de loja focado em produtos premium |
        | **Outlet** | Tipo de loja focado em liquidação/preços baixos |
        | **Brands** | Tipo de loja focado em marcas específicas |
        | **Distrito** | Tipo de loja em regiões de negócios |

        ---

        ## ❓ Perguntas Frequentes (FAQ)

        ### P: Por que só vejo "00 - CD" no estoque?
        > **R:** O estoque é centralizado no CD. As lojas recebem os produtos do CD
        > quando precisam. Esta visão mostra o que tem disponível para distribuir.

        ### P: Como é calculado o Ticket Médio?
        > **R:** Ticket Médio = Faturamento Total ÷ Número de Vendas
        > Exemplo: R$ 29.500 ÷ 100 vendas = R$ 295 de ticket médio

        ### P: A projeção é sempre precisa?
        > **R:** Não. A projeção é uma estimativa baseada em padrões passados.
        > Se as vendas forem sazonais ou houver mudanças no mercado, a projeção
        > pode não ser 100% precisa. Use como um guia, não como verdade absoluta.

        ### P: O que significa R² = 0,75?
        > **R:** Significa que a projeção tem 75% de confiança. É uma boa projeção,
        > mas há 25% de variabilidade que o modelo não explica.

        ### P: Posso baixar os dados?
        > **R:** Sim! Na página "Apresentação RAE", clique em
        > "📄 Baixar Relatório RAE" para baixar um relatório em TXT.

        ### P: Como filtrar por múltiplas lojas na Consulta de Vendas?
        > **R:** Atualmente, você pode filtrar uma loja por vez. Para múltiplas lojas,
        > faça consultas separadas ou deixe o filtro em branco para ver todas.

        ### P: Qual é o período de dados?
        > **R:** Os dados disponíveis são de **janeiro a junho de 2026**.
        > Períodos anteriores ou posteriores não têm dados.

        ---

        ## 🚀 Guia Rápido - Primeiros Passos

        **Para o gerente de loja:**
        1. Vá em "Dashboard Estratégico" para ver a saúde do negócio
        2. Vá em "Consulta de Vendas", filtre sua loja, veja a performance
        3. Vá em "Consulta de Produtos" para verificar estoque

        **Para o analista/BI:**
        1. Use "Consulta de Vendas" com filtros avançados
        2. Crie relatórios em "Apresentação RAE"
        3. Use "Projeção de Vendas" para planejamento

        **Para a diretoria:**
        1. Comece em "Dashboard Estratégico"
        2. Veja "Apresentação RAE" para conclusões
        3. Use "Projeção de Vendas" para planejamento estratégico

        ---

        ## ✅ Checklist de Dados

        Este sistema monitora a qualidade dos dados. Se você vir **alertas vermelhos**:
        - ⚠️ **Clientes com loja inválida**: Alguns clientes têm código de loja incorreto
        - ⚠️ **Vendedores inativos com vendas**: Há vendedores desligados com vendas registradas
        - ⚠️ **Produtos sem estoque**: Produtos no catálogo mas não disponíveis no CD

        **Impacto**: Essas inconsistências podem afetar a precisão das análises.
        Recomenda-se revisar os dados periodicamente.

        ---

        ## 🎉 Parabéns!

        Agora você domina o Distribox!

        Lembre-se: **dados são como pistas** - com as pistas certas,
        podemos descobrir histórias incríveis sobre a saúde do negócio! 📊

        Para dúvidas técnicas ou sugestões, consulte a equipe de BI.
        """)


# ============================================================================
# 1. FUNÇÕES DE CARREGAMENTO E VALIDAÇÃO
# ============================================================================
@st.cache_data
def carregar_dados() -> Dict[str, pd.DataFrame]:
    """
    Carrega todos os arquivos CSV do diretório com tratamento de erros.

    Trata múltiplos encodings (UTF-8, Latin1, ISO-8859-1) para
    compatibilidade com diferentes sistemas.

    Returns:
        Dict[str, pd.DataFrame]: Dicionário com todos os dados carregados
    """
    arquivos = {
        'vendedores': 'vendedores.csv',
        'clientes': 'clientes.csv',
        'lojas': 'lojas.csv',
        'produtos': 'produtos.csv',
        'variacoes_estoque': 'variacoes_estoque.csv',
        'vendas_p1': 'vendas_2026_p1.csv',
        'vendas_p2': 'vendas_2026_p2.csv'
    }

    dataframes = {}
    for nome, arquivo in arquivos.items():
        try:
            # Tentar múltiplos encodings
            for encoding in ['utf-8', 'latin1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(arquivo, sep=';', encoding=encoding, decimal=',')
                    break
                except UnicodeDecodeError:
                    continue
            dataframes[nome] = df
        except FileNotFoundError:
            st.warning(f"Arquivo '{arquivo}' não encontrado.")
            dataframes[nome] = pd.DataFrame()

    return dataframes


# ============================================================================
# 2. FUNÇÃO DE FORMATAÇÃO DE MOEDA
# ============================================================================
def formatar_moeda(valor: float) -> str:
    """
    Formata valor no padrão brasileiro (R$ 1.234,56).

    Args:
        valor: Número a ser formatado

    Returns:
        str: Valor formatado em moeda brasileira
    """
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    valor_formatado = f"{valor:,.2f}"
    # Converter formato americano (1,234.56) para brasileiro (1.234,56)
    valor_br = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_br}"


# ============================================================================
# 3. FUNÇÕES DE LIMPEZA E VALIDAÇÃO DE DADOS
# ============================================================================
def limpar_dados(df: pd.DataFrame, nome: str) -> pd.DataFrame:
    """
    Aplica limpeza inteligente nos dados com validações por tipo.

    - Remove espaços em branco nas colunas
    - Padroniza valores booleanos
    - Converte datas
    - Remove duplicatas

    Args:
        df: DataFrame a limpar
        nome: Nome do dataset (para lógica específica)

    Returns:
        pd.DataFrame: DataFrame limpo
    """
    df_limpo = df.copy()
    df_limpo.columns = df_limpo.columns.str.strip()

    # Padronizar texto: remover espaços e valores nulos
    for col in df_limpo.select_dtypes(include=['object']).columns:
        df_limpo[col] = df_limpo[col].astype(str).str.strip()
        df_limpo[col] = df_limpo[col].replace('nan', pd.NA)
        df_limpo[col] = df_limpo[col].replace('None', pd.NA)

    # Tratamento específico por dataset
    if nome == 'clientes':
        if 'data_cadastro' in df_limpo.columns:
            df_limpo['data_cadastro'] = pd.to_datetime(df_limpo['data_cadastro'], errors='coerce', dayfirst=True)
        if 'ativo' in df_limpo.columns:
            df_limpo['ativo'] = df_limpo['ativo'].map({'sim': True, 'nao': False})

    elif nome == 'vendedores':
        if 'ativo' in df_limpo.columns:
            df_limpo['ativo'] = df_limpo['ativo'].map({'sim': True, 'nao': False})

    elif nome == 'produtos':
        for col in ['PRECO_CUSTO']:
            if col in df_limpo.columns:
                df_limpo[col] = df_limpo[col].astype(str).str.replace(',', '.').str.replace('"', '')
                df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')
        if 'DATA_CADASTRO' in df_limpo.columns:
            df_limpo['DATA_CADASTRO'] = pd.to_datetime(df_limpo['DATA_CADASTRO'], errors='coerce', dayfirst=True)
        if 'ATIVO' in df_limpo.columns:
            df_limpo['ATIVO'] = df_limpo['ATIVO'].map({'S': True, 'N': False})

    elif nome.startswith('vendas'):
        # Converter colunas numéricas
        colunas_numericas = [
            'MOVIMENTO_ITEM_QUANTIDADE', 'MOVIMENTO_ITEM_PRECO_UNITARIO',
            'MOVIMENTO_ITEM_ACRESCIMO', 'MOVIMENTO_ITEM_DESCONTO',
            'MOVIMENTO_ITEM_DESCONTO_PROMOCIONAL', 'MOVIMENTO_ITEM_RATEIO',
            'MOVIMENTO_FRETE', 'MOVIMENTO_ITEM_CUSTO_UNITARIO'
        ]
        for col in colunas_numericas:
            if col in df_limpo.columns:
                df_limpo[col] = df_limpo[col].astype(str).str.replace(',', '.').str.replace('"', '')
                df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')
        if 'MOVIMENTO_DATA' in df_limpo.columns:
            df_limpo['MOVIMENTO_DATA'] = pd.to_datetime(df_limpo['MOVIMENTO_DATA'], errors='coerce', dayfirst=True)

    elif nome == 'variacoes_estoque':
        colunas_numericas = ['QTDE_ESTOQUE_ATUAL', 'QTDE_ESTOQUE_MINIMO']
        for col in colunas_numericas:
            if col in df_limpo.columns:
                df_limpo[col] = df_limpo[col].astype(str).str.replace(',', '.')
                df_limpo[col] = pd.to_numeric(df_limpo[col], errors='coerce')

    # Remover duplicatas
    df_limpo = df_limpo.drop_duplicates()
    return df_limpo


# ============================================================================
# 4. CONSOLIDAÇÃO E VALIDAÇÃO (MODELO ESTRELA)
# ============================================================================
@st.cache_data
def consolidar_dados(dados: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Consolida todos os dados em um modelo dimensional (estrela).

    - Limpa cada dataset
    - Concatena vendas P1 e P2
    - Filtra apenas vendas (SAIDA)
    - Valida integridade de dados
    - Trata inconsistências

    Returns:
        Dict com tabelas: vendas, produtos, clientes, lojas, vendedores, estoque
    """
    # Limpar todos os datasets
    df_vendas_p1 = limpar_dados(dados['vendas_p1'], 'vendas_p1') if not dados['vendas_p1'].empty else pd.DataFrame()
    df_vendas_p2 = limpar_dados(dados['vendas_p2'], 'vendas_p2') if not dados['vendas_p2'].empty else pd.DataFrame()
    df_produtos = limpar_dados(dados['produtos'], 'produtos') if not dados['produtos'].empty else pd.DataFrame()
    df_clientes = limpar_dados(dados['clientes'], 'clientes') if not dados['clientes'].empty else pd.DataFrame()
    df_vendedores = limpar_dados(dados['vendedores'], 'vendedores') if not dados['vendedores'].empty else pd.DataFrame()
    df_lojas = limpar_dados(dados['lojas'], 'lojas') if not dados['lojas'].empty else pd.DataFrame()
    df_estoque = limpar_dados(dados['variacoes_estoque'], 'variacoes_estoque') if not dados['variacoes_estoque'].empty else pd.DataFrame()

    # Concatenar vendas de ambos os períodos
    df_vendas = pd.concat([df_vendas_p1, df_vendas_p2], ignore_index=True)

    # ========================================================================
    # FILTRAGEM DE VENDAS: Apenas SAIDA (não devoluções)
    # ========================================================================
    df_vendas = df_vendas[df_vendas['MOVIMENTO_TIPO'] == 'SAIDA']

    # ------------------------------------------------------------------------
    # CÁLCULOS FINANCEIROS: receita, custo e lucro de cada item vendido
    # ------------------------------------------------------------------------
    if not df_vendas.empty:
        # Garantir que as colunas usadas nas contas são números (e não texto).
        # Se algum valor estiver vazio/inválido, usamos um padrão seguro (fillna).
        df_vendas['MOVIMENTO_ITEM_QUANTIDADE'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_QUANTIDADE'], errors='coerce').fillna(1)
        df_vendas['MOVIMENTO_ITEM_PRECO_UNITARIO'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_PRECO_UNITARIO'], errors='coerce').fillna(0)
        df_vendas['MOVIMENTO_ITEM_DESCONTO'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_DESCONTO'], errors='coerce').fillna(0)
        df_vendas['MOVIMENTO_ITEM_CUSTO_UNITARIO'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_CUSTO_UNITARIO'], errors='coerce').fillna(0)

        # 1) RECEITA (valor_total): o quanto a loja recebeu pela venda.
        #    Fórmula: Quantidade × Preço unitário × (1 - % de desconto)
        df_vendas['valor_total'] = (
            df_vendas['MOVIMENTO_ITEM_QUANTIDADE'] *
            df_vendas['MOVIMENTO_ITEM_PRECO_UNITARIO'] *
            (1 - df_vendas['MOVIMENTO_ITEM_DESCONTO'] / 100)
        )

        # 2) CUSTO (custo_total): o quanto a loja pagou pelos produtos vendidos.
        #    Fórmula: Quantidade × Custo unitário
        df_vendas['custo_total'] = (
            df_vendas['MOVIMENTO_ITEM_QUANTIDADE'] *
            df_vendas['MOVIMENTO_ITEM_CUSTO_UNITARIO']
        )

        # 3) LUCRO BRUTO (lucro_bruto): o que sobra = Receita - Custo.
        #    É o número que mais interessa à diretoria!
        df_vendas['lucro_bruto'] = df_vendas['valor_total'] - df_vendas['custo_total']

        # Extrair código do produto (primeiros 12 caracteres do código de barras)
        df_vendas['produto_codigo'] = df_vendas['MOVIMENTO_ITEM_CODIGO_DE_BARRAS'].astype(str).str[:12]

    # ========================================================================
    # VALIDAÇÃO 1: Filtrar apenas lojas válidas
    # ========================================================================
    lojas_validas = df_lojas['identificacao'].unique().tolist() if not df_lojas.empty else []
    if df_clientes is not None and not df_clientes.empty:
        df_clientes_antes = len(df_clientes)
        df_clientes = df_clientes[df_clientes['loja'].isin(lojas_validas) | df_clientes['loja'].isna()]
        df_clientes_depois = len(df_clientes)
        # if df_clientes_antes > df_clientes_depois:
        #     st.warning(f"⚠️ {df_clientes_antes - df_clientes_depois} clientes com loja inválida foram removidos")

    # ========================================================================
    # VALIDAÇÃO 2: Filtrar apenas vendedores ATIVOS nas análises de vendas
    # ========================================================================
    if not df_vendedores.empty and 'ativo' in df_vendedores.columns:
        vendedores_ativos = df_vendedores[df_vendedores['ativo'] == True]['nome_vendedor'].unique()
        if not df_vendas.empty and 'MOVIMENTO_ITEM_VENDEDOR' in df_vendas.columns:
            df_vendas = df_vendas[df_vendas['MOVIMENTO_ITEM_VENDEDOR'].isin(vendedores_ativos)]

    # ========================================================================
    # VALIDAÇÃO 3: Remover vendas sem cliente válido (opcional, mantém para flexibilidade)
    # ========================================================================
    # Dados com CODIGO_CLIENTE vazio são mantidos (algumas vendas sem cliente registrado)

    # ========================================================================
    # ESTOQUE: Manter apenas o CD (estoque centralizado)
    # ========================================================================
    df_estoque_cd = df_estoque[df_estoque['IDENTIFICACAO'] == '00 - CD'].copy() if not df_estoque.empty else pd.DataFrame()

    # Se não houver registros do CD, usar todos (fallback)
    if df_estoque_cd.empty and not df_estoque.empty:
        df_estoque_cd = df_estoque

    return {
        'vendas': df_vendas,
        'produtos': df_produtos,
        'clientes': df_clientes,
        'vendedores': df_vendedores,
        'lojas': df_lojas,
        'estoque': df_estoque_cd  # Apenas CD
    }


# ============================================================================
# 5. FUNÇÃO PARA CRIAR COMBOBOX COM AUTOCOMPLETE
# ============================================================================
def filtro_autocomplete(
    label: str,
    options: List,
    placeholder: str = "Digite para filtrar...",
    allow_all: bool = True
) -> Optional[str]:
    """
    Cria um filtro com autocomplete usando selectbox.
    Limpa automaticamente valores nulos e duplicatas.

    Args:
        label: Rótulo do campo
        options: Lista de opções
        placeholder: Texto do placeholder
        allow_all: Se True, inclui opção "Todos"

    Returns:
        Optional[str]: Opção selecionada ou None
    """
    # Filtrar valores nulos e converter para string
    options_clean = [str(opt) for opt in options if pd.notna(opt) and str(opt) != 'nan' and str(opt) != '']

    # Ordenar e remover duplicatas
    options_sorted = sorted(set(options_clean))

    # Adicionar opção "Todos"
    if allow_all:
        options_with_all = ['Todos'] + options_sorted
    else:
        options_with_all = options_sorted

    # Se não houver opções, retornar None
    if not options_with_all:
        return None

    # Selectbox com suporte a digitação
    selected = st.selectbox(
        label=label,
        options=options_with_all,
        index=0,
        placeholder=placeholder
    )

    return None if (allow_all and selected == 'Todos') else selected


# ============================================================================
# 6. CONSULTA DE PRODUTOS COM ESTOQUE (CD)
# ============================================================================
def consultar_produtos(
    df_produtos: pd.DataFrame,
    df_estoque: pd.DataFrame,
    referencia: Optional[str] = None,
    tamanho: Optional[str] = None,
    cor: Optional[str] = None
) -> pd.DataFrame:
    """
    Consulta produtos com estoque disponível no CD.
    Permite filtros por referência, tamanho e cor.

    Args:
        df_produtos: DataFrame de produtos
        df_estoque: DataFrame de estoque do CD
        referencia: Filtro por referência (parcial)
        tamanho: Filtro por tamanho (parcial)
        cor: Filtro por cor (parcial)

    Returns:
        pd.DataFrame: Produtos encontrados com estoque
    """
    # Unir produtos com estoque do CD
    df_consulta = df_produtos.merge(
        df_estoque,
        left_on='REFERENCIA',
        right_on='PRODUTO_REFERENCIA',
        how='inner'
    )

    # Aplicar filtros (case-insensitive, busca parcial)
    if referencia:
        df_consulta = df_consulta[df_consulta['REFERENCIA'].str.contains(referencia, case=False, na=False)]
    if tamanho:
        df_consulta = df_consulta[df_consulta['TAMANHO'].str.contains(tamanho, case=False, na=False)]
    if cor:
        df_consulta = df_consulta[df_consulta['COR'].str.contains(cor, case=False, na=False)]

    # Selecionar colunas relevantes
    colunas = ['REFERENCIA', 'DESCRICAO', 'TAMANHO', 'COR',
               'QTDE_ESTOQUE_ATUAL', 'QTDE_ESTOQUE_MINIMO', 'PRECO_CUSTO', 'GRUPO', 'MARCA']
    colunas_existentes = [c for c in colunas if c in df_consulta.columns]

    return df_consulta[colunas_existentes]


# ============================================================================
# 7. CONSULTA DE VENDAS COM FILTROS AVANÇADOS
# ============================================================================
def consultar_vendas(
    df_vendas: pd.DataFrame,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    loja: Optional[str] = None,
    cliente: Optional[int] = None,
    vendedor: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Consulta vendas com filtros combináveis.
    Retorna dados filtrados + totals calculados.

    Args:
        df_vendas: DataFrame de vendas
        data_inicio: Data inicial do filtro
        data_fim: Data final do filtro
        loja: Nome da loja a filtrar
        cliente: Código do cliente a filtrar
        vendedor: Nome do vendedor a filtrar

    Returns:
        Tuple: (DataFrame filtrado, Dict com totals)
    """
    df = df_vendas.copy()

    # Aplicar filtros
    if data_inicio:
        df = df[df['MOVIMENTO_DATA'] >= data_inicio]
    if data_fim:
        df = df[df['MOVIMENTO_DATA'] <= data_fim]
    if loja:
        df = df[df['MOVIMENTO_NOME_LOJA'] == loja]
    if cliente:
        df = df[df['CODIGO_CLIENTE'] == cliente]
    if vendedor:
        df = df[df['MOVIMENTO_ITEM_VENDEDOR'] == vendedor]

    # Calcular totals
    totais = {
        'total_vendas': len(df),
        'total_itens': df['MOVIMENTO_ITEM_QUANTIDADE'].sum() if not df.empty else 0,
        'faturamento': df['valor_total'].sum() if not df.empty else 0,
        'ticket_medio': df['valor_total'].mean() if not df.empty and len(df) > 0 else 0,
        'valor_medio_item': df['MOVIMENTO_ITEM_PRECO_UNITARIO'].mean() if not df.empty else 0
    }

    return df, totais


# ============================================================================
# 8. PROJEÇÃO DE VENDAS COM REGRESSÃO LINEAR
# ============================================================================
def projetar_vendas(
    df_vendas: pd.DataFrame,
    periodo: str = 'D',
    horizonte: int = 30,
    loja: Optional[str] = None
) -> Dict:
    """
    Projeta vendas futuras usando regressão linear.

    Usa o histórico de vendas para criar uma tendência linear
    e projeta para os próximos N períodos.

    Args:
        df_vendas: DataFrame com vendas
        periodo: Período de agregação ('D'=diário, 'W'=semanal, 'ME'=mensal)
        horizonte: Número de períodos para projetar
        loja: Nome da loja para filtrar (opcional)

    Returns:
        Dict com:
        - historico: dados históricos agregados
        - projecao: dados projetados
        - completo: histórico + projeção
        - modelo: modelo de regressão linear
        - r2: qualidade da projeção (0 a 1)
        - tendencia_diaria: inclinação da tendência
        - mensagem: mensagem com resultado
    """
    df = df_vendas.copy()

    # Filtrar por loja se especificada
    if loja:
        df = df[df['MOVIMENTO_NOME_LOJA'] == loja]

    # Mapear períodos para pandas (corrigido para versões >= 2.0)
    mapeamento_periodos = {
        'D': 'D',      # Diário
        'W': 'W',      # Semanal
        'ME': 'ME'     # Mensal (use 'ME' em vez de 'M' em pandas >= 2.0)
    }

    freq = mapeamento_periodos.get(periodo, 'D')

    # Agregar por período
    df['data'] = pd.to_datetime(df['MOVIMENTO_DATA'])
    df_agregado = df.groupby(pd.Grouper(key='data', freq=freq)).agg({
        'valor_total': 'sum'
    }).reset_index()
    df_agregado = df_agregado.dropna()

    # Verificar se há dados suficientes (mínimo 3 períodos)
    if len(df_agregado) < 3:
        return {
            'historico': df_agregado,
            'projecao': pd.DataFrame(),
            'mensagem': f'⚠️ Dados insuficientes para projeção (encontrados {len(df_agregado)} períodos, mínimo 3 necessários)'
        }

    # Preparar dados para regressão linear
    df_agregado['dias'] = (df_agregado['data'] - df_agregado['data'].min()).dt.days

    X = df_agregado['dias'].values.reshape(-1, 1)
    y = df_agregado['valor_total'].values

    # Treinar modelo de regressão linear
    model = LinearRegression()
    model.fit(X, y)

    # Projetar futuro
    ultimo_dia = df_agregado['dias'].max()

    # Calcular dias para cada período
    if periodo == 'ME':
        dias_por_periodo = 30  # Aproximação: 30 dias por mês
    elif periodo == 'W':
        dias_por_periodo = 7   # 7 dias por semana
    else:
        dias_por_periodo = 1   # 1 dia por dia

    # Gerar dias futuros para predição
    dias_futuros = np.arange(
        ultimo_dia + 1,
        ultimo_dia + horizonte * dias_por_periodo + 1,
        dias_por_periodo
    ).reshape(-1, 1)

    projecao_valores = model.predict(dias_futuros)

    # Criar DataFrame de projeção com datas correspondentes
    datas_futuras = []
    for i in range(horizonte):
        if periodo == 'ME':
            data_futura = df_agregado['data'].max() + pd.DateOffset(months=i+1)
        elif periodo == 'W':
            data_futura = df_agregado['data'].max() + timedelta(weeks=i+1)
        else:
            data_futura = df_agregado['data'].max() + timedelta(days=i+1)
        datas_futuras.append(data_futura)

    df_projecao = pd.DataFrame({
        'data': datas_futuras,
        'valor_total': projecao_valores,
        'tipo': 'Projeção'
    })

    # Criar DataFrame histórico com marcação
    df_historico = df_agregado.copy()
    df_historico['tipo'] = 'Histórico'
    df_historico = df_historico[['data', 'valor_total', 'tipo']]

    # Combinar histórico + projeção
    df_completo = pd.concat([df_historico, df_projecao], ignore_index=True)

    r2_score = model.score(X, y)

    return {
        'historico': df_historico,
        'projecao': df_projecao,
        'completo': df_completo,
        'modelo': model,
        'r2': r2_score,
        'tendencia_diaria': model.coef_[0],
        'mensagem': f'✅ Projeção gerada com R² = {r2_score:.2f} ({r2_score*100:.0f}% de confiança)'
    }


# ============================================================================
# 9. VISUALIZAÇÕES ESTRATÉGICAS PARA DASHBOARD
# ============================================================================
def criar_dashboard_estrategico(df_vendas: pd.DataFrame, df_lojas: pd.DataFrame) -> None:
    """
    Cria visualizações estratégicas para a RAE.
    Mostra métricas principais + gráficos interativos.
    """
    # Pega todos os indicadores de uma vez (mesma fonte usada na RAE).
    kpi = calcular_indicadores(df_vendas)

    # --- Primeira linha de métricas: o "resumo do dinheiro" ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Faturamento Total", formatar_moeda(kpi['faturamento']))
    with col2:
        # O 'delta' mostra a margem logo abaixo do lucro, em verde/vermelho.
        st.metric("💵 Lucro Bruto", formatar_moeda(kpi['lucro']),
                  delta=f"Margem de {kpi['margem']:.1f}%")
    with col3:
        st.metric("📋 Total de Vendas", f"{kpi['total_vendas']:,}")
    with col4:
        st.metric("🎫 Ticket Médio", formatar_moeda(kpi['ticket_medio']))

    # Gráfico 1: Vendas por Loja (barras)
    if not df_vendas.empty and 'MOVIMENTO_NOME_LOJA' in df_vendas.columns:
        vendas_loja = df_vendas.groupby('MOVIMENTO_NOME_LOJA')['valor_total'].sum().sort_values(ascending=False).reset_index()
        vendas_loja.columns = ['loja', 'valor_total']

        fig = px.bar(
            vendas_loja,
            x='loja',
            y='valor_total',
            title='🏪 Vendas por Loja',
            labels={'loja': 'Loja', 'valor_total': 'Faturamento (R$)'},
            color='valor_total',
            color_continuous_scale='Viridis',
            text=vendas_loja['valor_total'].apply(formatar_moeda)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    # Gráfico 2: Distribuição por Tipo de Loja (pizza)
    if not df_lojas.empty and not df_vendas.empty:
        df_lojas['identificacao_limpa'] = df_lojas['identificacao'].str.split(' - ').str[0]
        df_vendas['loja_codigo'] = df_vendas['MOVIMENTO_NOME_LOJA'].str.split(' - ').str[0]

        vendas_tipo = df_vendas.merge(
            df_lojas[['identificacao_limpa', 'tipo']],
            left_on='loja_codigo',
            right_on='identificacao_limpa',
            how='left'
        )

        if not vendas_tipo.empty and 'tipo' in vendas_tipo.columns:
            vendas_por_tipo = vendas_tipo.groupby('tipo')['valor_total'].sum().reset_index()

            fig = px.pie(
                vendas_por_tipo,
                values='valor_total',
                names='tipo',
                title='📊 Distribuição de Vendas por Tipo de Loja',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=400)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)


def criar_projecao_vendas(projecao: Dict) -> None:
    """
    Cria gráfico de projeção de vendas com histórico.
    Mostra linha azul (histórico) e vermelha (projeção).
    """
    if 'completo' not in projecao or projecao['completo'].empty:
        st.warning(projecao.get('mensagem', 'Dados insuficientes para projeção'))
        return

    df = projecao['completo']

    fig = go.Figure()

    # Separar histórico e projeção
    df_historico = df[df['tipo'] == 'Histórico']
    df_projecao = df[df['tipo'] == 'Projeção']

    # Adicionar histórico (linha azul)
    fig.add_trace(go.Scatter(
        x=df_historico['data'],
        y=df_historico['valor_total'],
        name='Histórico',
        line=dict(color='blue', width=3),
        mode='lines+markers'
    ))

    # Adicionar projeção (linha vermelha pontilhada)
    fig.add_trace(go.Scatter(
        x=df_projecao['data'],
        y=df_projecao['valor_total'],
        name='Projeção',
        line=dict(color='red', width=3, dash='dash'),
        mode='lines+markers'
    ))

    fig.update_layout(
        title='📈 Projeção de Vendas (Histórico vs Previsão)',
        xaxis_title='Data',
        yaxis_title='Faturamento (R$)',
        height=450,
        hovermode='x unified'
    )

    fig.update_yaxes(tickprefix='R$ ')

    st.plotly_chart(fig, use_container_width=True)

    # Métricas da projeção
    if 'r2' in projecao and 'tendencia_diaria' in projecao:
        col1, col2 = st.columns(2)
        with col1:
            r2_percent = projecao['r2'] * 100
            st.metric("📊 Qualidade da Projeção (R²)", f"{projecao['r2']:.2f}",
                     f"{r2_percent:.0f}% confiança")
        with col2:
            tendencia = projecao['tendencia_diaria']
            if abs(tendencia) < 1:
                delta_text = "Estável"
            else:
                delta_text = f"{'+' if tendencia > 0 else ''}{tendencia/100:.1f}% ao dia"
            st.metric(
                "📈 Tendência",
                formatar_moeda(tendencia),
                delta_text
            )


# ============================================================================
# 10. ANÁLISE EXECUTIVA E RECOMENDAÇÕES
# ============================================================================
def calcular_indicadores(df_vendas: pd.DataFrame) -> Dict:
    """
    Calcula os principais NÚMEROS (KPIs) do negócio a partir das vendas.

    Centralizamos as contas aqui para que o Dashboard, a RAE e o relatório
    em TXT usem EXATAMENTE os mesmos valores (sem risco de divergência).

    Args:
        df_vendas: tabela de vendas já consolidada

    Returns:
        Dict com faturamento, lucro, margem, ticket médio, etc.
    """
    if df_vendas.empty:
        return {
            'faturamento': 0, 'custo': 0, 'lucro': 0, 'margem': 0,
            'total_vendas': 0, 'total_itens': 0, 'ticket_medio': 0
        }

    faturamento = df_vendas['valor_total'].sum()
    # As colunas de custo/lucro podem não existir em dados muito antigos; por isso o "if".
    custo = df_vendas['custo_total'].sum() if 'custo_total' in df_vendas.columns else 0
    lucro = df_vendas['lucro_bruto'].sum() if 'lucro_bruto' in df_vendas.columns else 0
    total_vendas = len(df_vendas)

    return {
        'faturamento': faturamento,
        'custo': custo,
        'lucro': lucro,
        # Margem (%) = quanto do faturamento virou lucro. Evitamos dividir por zero.
        'margem': (lucro / faturamento * 100) if faturamento > 0 else 0,
        'total_vendas': total_vendas,
        'total_itens': df_vendas['MOVIMENTO_ITEM_QUANTIDADE'].sum(),
        # Ticket médio = faturamento dividido pelo número de vendas
        'ticket_medio': df_vendas['valor_total'].mean() if total_vendas > 0 else 0
    }


def ranking_lojas_por_margem(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """
    Monta um RANKING das lojas pela MARGEM DE LUCRO (do maior % para o menor).

    Por que isso é importante? Uma loja pode VENDER muito (alto faturamento)
    mas LUCRAR pouco (margem baixa) — por exemplo, se dá descontos demais.
    Este ranking revela quais lojas realmente dão lucro e quais "puxam a
    rentabilidade para baixo".

    Como é feito (passo a passo):
      1. Agrupamos as vendas por loja.
      2. Para cada loja, somamos o faturamento e o lucro.
      3. Calculamos a margem de cada loja = lucro ÷ faturamento × 100.
      4. Ordenamos da maior margem para a menor.

    Args:
        df_vendas: tabela de vendas já consolidada (com 'lucro_bruto')

    Returns:
        DataFrame com as colunas: Loja, Faturamento, Lucro, Margem (%)
    """
    # Sem dados ou sem a coluna de lucro, devolvemos uma tabela vazia.
    if df_vendas.empty or 'lucro_bruto' not in df_vendas.columns:
        return pd.DataFrame()

    # O "00 - CD" é o Centro de Distribuição (armazém), não uma loja de venda.
    # Por isso, ele fica de fora do ranking de lojas.
    df_lojas_venda = df_vendas[df_vendas['MOVIMENTO_NOME_LOJA'] != '00 - CD']

    # Passo 1 e 2: agrupar por loja e somar faturamento e lucro.
    #   .agg() permite calcular várias somas de uma vez.
    ranking = df_lojas_venda.groupby('MOVIMENTO_NOME_LOJA').agg(
        Faturamento=('valor_total', 'sum'),
        Lucro=('lucro_bruto', 'sum')
    ).reset_index()

    # Renomear a coluna da loja para um nome mais amigável.
    ranking = ranking.rename(columns={'MOVIMENTO_NOME_LOJA': 'Loja'})

    # Passo 3: calcular a margem (%) de cada loja, com proteção contra divisão por zero.
    ranking['Margem (%)'] = ranking.apply(
        lambda linha: (linha['Lucro'] / linha['Faturamento'] * 100) if linha['Faturamento'] > 0 else 0,
        axis=1  # axis=1 significa "aplicar linha por linha"
    )

    # Passo 4: ordenar da MAIOR margem para a MENOR.
    ranking = ranking.sort_values('Margem (%)', ascending=False).reset_index(drop=True)

    return ranking


def gerar_analise_executiva(df_vendas: pd.DataFrame, df_lojas: pd.DataFrame, df_vendedores: pd.DataFrame) -> Dict:
    """
    O "cérebro" do sistema: transforma números em CONCLUSÕES e RECOMENDAÇÕES.

    Como funciona (bem simples!):
      1. Calculamos os indicadores do negócio (faturamento, lucro, margem...).
      2. Comparamos cada indicador com as metas definidas em CONFIGURAÇÕES.
      3. Para cada comparação, escrevemos uma frase pronta para a diretoria.

    Returns:
        Dict com duas listas:
        - 'conclusoes':   o que os dados ESTÃO dizendo (diagnóstico)
        - 'recomendacoes': o que a diretoria PODE fazer (plano de ação)
    """
    analise = {'conclusoes': [], 'recomendacoes': []}

    # Sem dados não há o que analisar — devolvemos as listas vazias.
    if df_vendas.empty:
        return analise

    # Pega todos os números de uma vez (ver função acima).
    kpi = calcular_indicadores(df_vendas)

    # ========================================================================
    # PARTE 1 - CONCLUSÕES (o diagnóstico: "como estamos?")
    # ========================================================================

    # Conclusão 1: Saúde geral (faturamento + lucro)
    analise['conclusoes'].append({
        'titulo': '🎯 Saúde Geral do Negócio',
        'dados': (f"Faturamento de {formatar_moeda(kpi['faturamento'])} e lucro bruto de "
                  f"{formatar_moeda(kpi['lucro'])} em {kpi['total_vendas']:,} vendas "
                  f"({kpi['total_itens']:,.0f} peças)."),
        'status': 'positivo' if kpi['faturamento'] > META_FATURAMENTO_SAUDAVEL else 'neutro'
    })

    # Conclusão 2: Rentabilidade (margem de lucro) - o que mais interessa à diretoria!
    if kpi['margem'] >= MARGEM_OTIMA:
        status_margem, comentario = 'positivo', 'rentabilidade excelente'
    elif kpi['margem'] >= MARGEM_MINIMA:
        status_margem, comentario = 'positivo', 'rentabilidade saudável'
    else:
        status_margem, comentario = 'alerta', 'rentabilidade abaixo do ideal'
    analise['conclusoes'].append({
        'titulo': '💵 Margem de Lucro',
        'dados': f"Margem bruta de {kpi['margem']:.1f}% — {comentario}.",
        'status': status_margem
    })

    # Conclusão 3: Tipo de loja com melhor performance (Prime, Outlet, Brands...)
    if not df_lojas.empty and 'tipo' in df_lojas.columns:
        # Extrai só o número da loja ("01 - Aurora Prime" -> "01") para casar as tabelas.
        df_lojas = df_lojas.copy()
        df_vendas_copia = df_vendas.copy()
        df_lojas['identificacao_limpa'] = df_lojas['identificacao'].str.split(' - ').str[0]
        df_vendas_copia['loja_codigo'] = df_vendas_copia['MOVIMENTO_NOME_LOJA'].str.split(' - ').str[0]

        vendas_tipo = df_vendas_copia.merge(
            df_lojas[['identificacao_limpa', 'tipo']],
            left_on='loja_codigo', right_on='identificacao_limpa', how='left'
        )
        if not vendas_tipo.empty and 'tipo' in vendas_tipo.columns:
            vendas_por_tipo = vendas_tipo.groupby('tipo')['valor_total'].sum().sort_values(ascending=False)
            if len(vendas_por_tipo) > 0:
                top_tipo = str(vendas_por_tipo.index[0])
                top_valor = float(vendas_por_tipo.iloc[0])
                analise['conclusoes'].append({
                    'titulo': '📊 Tipo de Loja com Melhor Performance',
                    'dados': f"Lojas do tipo '{top_tipo}' lideram com {formatar_moeda(top_valor)} em vendas.",
                    'status': 'positivo'
                })

    # Conclusão 4: Ticket médio (valor médio por venda)
    if kpi['ticket_medio'] >= TICKET_MEDIO_OTIMO:
        status_ticket = 'positivo'
    elif kpi['ticket_medio'] >= TICKET_MEDIO_ACEITAVEL:
        status_ticket = 'alerta'
    else:
        status_ticket = 'negativo'
    analise['conclusoes'].append({
        'titulo': '🎫 Ticket Médio',
        'dados': f"Cada cliente gasta em média {formatar_moeda(kpi['ticket_medio'])} por compra.",
        'status': status_ticket
    })

    # Conclusão 5: Sazonalidade (em que mês vendemos mais e menos?)
    variacao_sazonal = 0  # guardamos para reutilizar nas recomendações
    if 'MOVIMENTO_DATA' in df_vendas.columns:
        df_vendas = df_vendas.copy()
        df_vendas['mes'] = df_vendas['MOVIMENTO_DATA'].dt.month
        vendas_por_mes = df_vendas.groupby('mes')['valor_total'].sum()
        if len(vendas_por_mes) > 1:
            melhor_mes = int(vendas_por_mes.idxmax())  # int() evita erro de índice numpy
            pior_mes = int(vendas_por_mes.idxmin())
            variacao_sazonal = ((vendas_por_mes.max() - vendas_por_mes.min()) / vendas_por_mes.mean()) * 100
            analise['conclusoes'].append({
                'titulo': '📅 Sazonalidade Detectada',
                'dados': (f"Melhor mês: {NOMES_MESES[melhor_mes]} | Pior mês: {NOMES_MESES[pior_mes]} | "
                          f"Variação de {variacao_sazonal:.0f}% entre eles."),
                'status': 'alerta' if variacao_sazonal > VARIACAO_SAZONAL_ALERTA else 'positivo'
            })

    # ========================================================================
    # PARTE 2 - RECOMENDAÇÕES (o plano de ação: "o que fazer?")
    # ========================================================================

    # Recomendação 1: Margem baixa -> revisar preços e custos
    if kpi['margem'] < MARGEM_MINIMA:
        analise['recomendacoes'].append({
            'titulo': '💵 Recuperar a Margem de Lucro',
            'descricao': f"A margem atual ({kpi['margem']:.1f}%) está abaixo da meta de {MARGEM_MINIMA}%.",
            'prioridade': 'alta',
            'acao': 'Renegociar custos com fornecedores e revisar a política de descontos.'
        })

    # Recomendação 2: Ticket médio baixo -> vender mais por cliente
    if kpi['ticket_medio'] < TICKET_MEDIO_ALVO:
        analise['recomendacoes'].append({
            'titulo': '💰 Aumentar o Ticket Médio',
            'descricao': (f"O ticket atual ({formatar_moeda(kpi['ticket_medio'])}) está abaixo do alvo "
                          f"de {formatar_moeda(TICKET_MEDIO_ALVO)}."),
            'prioridade': 'alta',
            'acao': 'Treinar vendedores em up-selling/cross-selling e criar kits/combos de produtos.'
        })

    # Recomendação 3: Sazonalidade forte -> campanhas no período fraco
    if variacao_sazonal > VARIACAO_SAZONAL_ALERTA:
        analise['recomendacoes'].append({
            'titulo': '📅 Suavizar a Sazonalidade',
            'descricao': f"Detectamos forte variação de {variacao_sazonal:.0f}% entre o melhor e o pior mês.",
            'prioridade': 'média',
            'acao': 'Planejar promoções e ações de marketing direcionadas aos meses de baixa.'
        })

    # Recomendação 4: Lojas paradas -> verificar operação
    if 'MOVIMENTO_NOME_LOJA' in df_vendas.columns and not df_lojas.empty:
        lojas_com_vendas = df_vendas['MOVIMENTO_NOME_LOJA'].nunique()
        # Total de lojas físicas = todas menos o Centro de Distribuição (CD).
        total_lojas = df_lojas[df_lojas['tipo'] != 'CD'].shape[0] if 'tipo' in df_lojas.columns else 0
        if total_lojas > 0 and lojas_com_vendas < total_lojas:
            analise['recomendacoes'].append({
                'titulo': '🏪 Lojas sem Vendas Registradas',
                'descricao': f"Apenas {lojas_com_vendas} de {total_lojas} lojas físicas registraram vendas.",
                'prioridade': 'alta',
                'acao': 'Verificar se as demais lojas estão operando e enviando dados corretamente.'
            })

    # Recomendação 5: Vendas concentradas em poucos vendedores -> risco
    if 'MOVIMENTO_ITEM_VENDEDOR' in df_vendas.columns:
        ranking_vendedores = df_vendas.groupby('MOVIMENTO_ITEM_VENDEDOR')['valor_total'].sum().sort_values(ascending=False)
        if len(ranking_vendedores) > 3 and ranking_vendedores.sum() > 0:
            concentracao = (ranking_vendedores.head(3).sum() / ranking_vendedores.sum()) * 100
            if concentracao > CONCENTRACAO_VENDEDORES_ALERTA:
                analise['recomendacoes'].append({
                    'titulo': '👥 Vendas Concentradas em Poucos Vendedores',
                    'descricao': f"Os 3 melhores vendedores respondem por {concentracao:.0f}% de todo o faturamento.",
                    'prioridade': 'média',
                    'acao': 'Mapear as boas práticas dos campeões e treinar o restante da equipe.'
                })

    # Recomendação 6: Loja com a PIOR margem -> aponta exatamente onde agir
    ranking_margem = ranking_lojas_por_margem(df_vendas)
    if not ranking_margem.empty and len(ranking_margem) > 1:
        # A última linha do ranking é a loja com a menor margem (já ordenado).
        pior_loja = ranking_margem.iloc[-1]
        # Só vale recomendar se a margem dessa loja estiver abaixo da meta mínima.
        if pior_loja['Margem (%)'] < MARGEM_MINIMA:
            analise['recomendacoes'].append({
                'titulo': '🏪 Loja com Margem Crítica',
                'descricao': (f"A loja '{pior_loja['Loja']}' tem a pior margem da rede: "
                              f"{pior_loja['Margem (%)']:.1f}% (faturou {formatar_moeda(pior_loja['Faturamento'])})."),
                'prioridade': 'alta',
                'acao': 'Investigar descontos excessivos, mix de produtos e custos específicos dessa loja.'
            })

    return analise


# ============================================================================
# 11. INTERFACE PRINCIPAL
# ============================================================================
def main():
    """Função principal da aplicação - Orquestra toda a interface."""

    # Título e botão de ajuda no topo
    col_title, col_help = st.columns([4, 1])
    with col_title:
        st.title("👔 Distribox - Análise Estratégica")
        st.caption("Plataforma de Inteligência de Negócios para Varejo de Moda | RAE - Reunião de Alinhamento Estratégico")
    with col_help:
        if st.button("❓ Ajuda", use_container_width=True, key="help_main"):
            mostrar_ajuda()

    st.markdown("---")

    # Sidebar com navegação
    with st.sidebar:
        st.header("📌 Navegação Principal")
        pagina = st.radio(
            "Selecione a página:",
            [
                "🏠 Dashboard Estratégico",
                "📦 Consulta de Produtos",
                "🛒 Consulta de Vendas",
                "📈 Projeção de Vendas",
                "📋 Apresentação RAE"
            ],
            key="navigation"
        )

        st.markdown("---")
        st.info("""
        **📊 Distribox Analytics**

        Varejo de Moda em Tempo Real
        - 15 lojas físicas
        - 1 Centro de Distribuição
        - Dados: Jan-Jun 2026

        **Última atualização**: 30/06/2026
        """)

        # Botão de ajuda na sidebar
        st.markdown("---")
        if st.button("❓ Como usar?", use_container_width=True, key="help_sidebar"):
            mostrar_ajuda()

    # Carregar e consolidar dados
    with st.spinner("⏳ Carregando dados..."):
        dados = carregar_dados()
        dados_consolidados = consolidar_dados(dados)

    df_vendas = dados_consolidados['vendas']
    df_produtos = dados_consolidados['produtos']
    df_clientes = dados_consolidados['clientes']
    df_vendedores = dados_consolidados['vendedores']
    df_lojas = dados_consolidados['lojas']
    df_estoque = dados_consolidados['estoque']

    # ========================================================================
    # PÁGINA 1: DASHBOARD ESTRATÉGICO
    # ========================================================================
    if pagina == "🏠 Dashboard Estratégico":
        st.header("📊 Dashboard Estratégico")
        st.markdown("Visão executiva em tempo real do negócio para análise rápida de performance.")
        st.markdown("---")

        if not df_vendas.empty:
            criar_dashboard_estrategico(df_vendas, df_lojas)

            # Informações adicionais
            with st.expander("📋 Detalhes Adicionais", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📅 Período de Dados", "Jan - Jun 2026")
                    st.metric("🏪 Lojas Ativas", df_vendas['MOVIMENTO_NOME_LOJA'].nunique())
                with col2:
                    st.metric("👥 Vendedores Ativos", df_vendas['MOVIMENTO_ITEM_VENDEDOR'].nunique())
                    st.metric("👤 Clientes Ativos", df_vendas['CODIGO_CLIENTE'].nunique())
        else:
            st.warning("⚠️ Dados de vendas não disponíveis.")

    # ========================================================================
    # PÁGINA 2: CONSULTA DE PRODUTOS (ESTOQUE DO CD)
    # ========================================================================
    elif pagina == "📦 Consulta de Produtos":
        st.header("📦 Consulta de Produtos com Estoque")
        st.markdown("""
        Consulte produtos e verifique a disponibilidade no **Centro de Distribuição**.

        ℹ️ **Importante**: O estoque é centralizado no CD. As lojas recebem os produtos
        conforme suas necessidades. Esta consulta mostra o que está disponível para distribuição.
        """)
        st.caption("💡 **Dica**: Digite parte do nome para filtrar! Exemplo: 'CASA' encontra 'CASACO'")
        st.markdown("---")

        # Preparar listas para autocomplete
        lista_referencias = df_produtos['REFERENCIA'].unique().tolist() if not df_produtos.empty else []
        lista_tamanhos = df_estoque['TAMANHO'].unique().tolist() if not df_estoque.empty else []
        lista_cores = df_estoque['COR'].unique().tolist() if not df_estoque.empty else []

        col1, col2 = st.columns(2)
        with col1:
            referencia = filtro_autocomplete(
                "🔍 Referência (código do produto)",
                lista_referencias,
                "Digite a referência ou parte do nome...",
                allow_all=True
            )
            tamanho = filtro_autocomplete(
                "📏 Tamanho",
                lista_tamanhos,
                "Digite: P, M, G, GG ou números (36, 38, 40)...",
                allow_all=True
            )
        with col2:
            cor = filtro_autocomplete(
                "🎨 Cor",
                lista_cores,
                "Digite a cor (PRETO, BRANCO, CARAMELO)...",
                allow_all=True
            )

        if st.button("🔍 Consultar Produtos", type="primary", key="btn_produtos"):
            with st.spinner("Consultando produtos..."):
                resultado = consultar_produtos(
                    df_produtos, df_estoque,
                    referencia=referencia if referencia else None,
                    tamanho=tamanho if tamanho else None,
                    cor=cor if cor else None
                )

                if not resultado.empty:
                    st.success(f"✅ Encontrados {len(resultado)} registros de estoque no CD")
                    st.markdown("---")

                    # Exibir resultado formatado
                    df_display = resultado.copy()
                    if 'PRECO_CUSTO' in df_display.columns:
                        df_display['PRECO_CUSTO'] = df_display['PRECO_CUSTO'].apply(
                            lambda x: formatar_moeda(x) if pd.notna(x) else 'R$ 0,00'
                        )

                    # Renomear colunas para exibição
                    df_display.columns = ['Referência', 'Descrição', 'Tamanho', 'Cor',
                                         'Estoque Atual', 'Estoque Mínimo', 'Preço Custo',
                                         'Grupo', 'Marca']

                    st.dataframe(df_display, use_container_width=True)

                    # Estatísticas rápidas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_estoque = resultado['QTDE_ESTOQUE_ATUAL'].sum() if 'QTDE_ESTOQUE_ATUAL' in resultado.columns else 0
                        st.metric("📦 Estoque Total", f"{total_estoque:,.0f} peças")
                    with col2:
                        produtos_unicos = resultado['REFERENCIA'].nunique() if 'REFERENCIA' in resultado.columns else 0
                        st.metric("📋 SKUs Únicos", produtos_unicos)
                    with col3:
                        if 'PRECO_CUSTO' in resultado.columns:
                            valor_medio = resultado['PRECO_CUSTO'].mean() if pd.notna(resultado['PRECO_CUSTO']).any() else 0
                            st.metric("💰 Preço Médio", formatar_moeda(valor_medio))
                else:
                    st.warning("⚠️ Nenhum produto encontrado com os filtros informados.")

    # ========================================================================
    # PÁGINA 3: CONSULTA DE VENDAS
    # ========================================================================
    elif pagina == "🛒 Consulta de Vendas":
        st.header("🛒 Consulta de Vendas")
        st.markdown("""
        Análise detalhada de vendas com filtros avançados.
        Deixe os campos em branco para não filtrar.
        """)
        st.caption("💡 **Dica**: Use os filtros para análises específicas (por loja, vendedor, período, etc)")
        st.markdown("---")

        # Preparar listas para autocomplete
        lista_lojas = df_vendas['MOVIMENTO_NOME_LOJA'].unique().tolist() if not df_vendas.empty else []
        lista_vendedores = df_vendas['MOVIMENTO_ITEM_VENDEDOR'].unique().tolist() if not df_vendas.empty else []

        # Criar mapeamento de clientes: Nome (Código) -> Código
        cliente_mapeamento = {}
        if not df_vendas.empty and not df_clientes.empty:
            # Merge para obter nomes dos clientes
            df_vendas_clientes = df_vendas.merge(
                df_clientes[['codigo', 'nome_cliente']],
                left_on='CODIGO_CLIENTE',
                right_on='codigo',
                how='left'
            )

            # Criar lista com nomes (código)
            for codigo, nome in zip(df_vendas_clientes['CODIGO_CLIENTE'].unique(),
                                    df_vendas_clientes['nome_cliente'].unique()):
                if pd.notna(codigo) and pd.notna(nome) and str(codigo) != 'nan':
                    chave = f"{nome} ({int(codigo)})"
                    cliente_mapeamento[chave] = int(codigo)

        # Se não conseguir fazer merge, usar apenas códigos
        if not cliente_mapeamento:
            lista_clientes_codigos = df_vendas['CODIGO_CLIENTE'].unique().tolist() if not df_vendas.empty else []
            for codigo in lista_clientes_codigos:
                if pd.notna(codigo) and str(codigo) != 'nan':
                    cliente_mapeamento[f"Cliente {int(codigo)}"] = int(codigo)

        # Limpar valores nulos e vazios
        lista_lojas = [l for l in lista_lojas if pd.notna(l) and str(l) != 'nan' and str(l) != '']
        lista_vendedores = [v for v in lista_vendedores if pd.notna(v) and str(v) != 'nan' and str(v) != '']
        lista_clientes_display = sorted(cliente_mapeamento.keys())

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("📅 Data Início", value=pd.to_datetime('2026-01-01'), key="data_inicio")
            data_fim = st.date_input("📅 Data Fim", value=pd.to_datetime('2026-06-30'), key="data_fim")

            loja_selecionada = filtro_autocomplete(
                "🏪 Loja",
                lista_lojas,
                "Digite o nome da loja...",
                allow_all=True
            )

        with col2:
            vendedor_selecionado = filtro_autocomplete(
                "👤 Vendedor",
                lista_vendedores,
                "Digite o nome do vendedor...",
                allow_all=True
            )

            # Filtro de cliente mostrando nome
            cliente_selecionado_display = filtro_autocomplete(
                "👥 Cliente",
                lista_clientes_display,
                "Digite o nome ou código do cliente...",
                allow_all=True
            )

            # Converter a seleção para código
            cliente_selecionado = cliente_mapeamento.get(cliente_selecionado_display) if cliente_selecionado_display else None

        if st.button("🔍 Consultar Vendas", type="primary", key="btn_vendas"):
            with st.spinner("Consultando vendas..."):
                df_filtrado, totais = consultar_vendas(
                    df_vendas,
                    data_inicio=pd.to_datetime(data_inicio),
                    data_fim=pd.to_datetime(data_fim),
                    loja=loja_selecionada,
                    cliente=cliente_selecionado,
                    vendedor=vendedor_selecionado
                )

                # Exibir totals
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📋 Total de Vendas", f"{totais['total_vendas']:,}")
                with col2:
                    st.metric("📦 Itens Vendidos", f"{totais['total_itens']:,.0f}")
                with col3:
                    st.metric("💰 Faturamento", formatar_moeda(totais['faturamento']))
                with col4:
                    st.metric("🎫 Ticket Médio", formatar_moeda(totais['ticket_medio']))

                st.markdown("---")

                # Exibir dados
                if not df_filtrado.empty:
                    st.subheader("📋 Detalhamento das Vendas")
                    colunas_exibir = ['MOVIMENTO_DATA', 'MOVIMENTO_NOME_LOJA', 'MOVIMENTO_ITEM_VENDEDOR',
                                     'CODIGO_CLIENTE', 'MOVIMENTO_ITEM_PRECO_UNITARIO',
                                     'MOVIMENTO_ITEM_QUANTIDADE', 'valor_total']
                    colunas_existentes = [c for c in colunas_exibir if c in df_filtrado.columns]

                    df_display = df_filtrado[colunas_existentes].copy()
                    df_display['valor_total'] = df_display['valor_total'].apply(formatar_moeda)
                    df_display['MOVIMENTO_ITEM_PRECO_UNITARIO'] = df_display['MOVIMENTO_ITEM_PRECO_UNITARIO'].apply(formatar_moeda)

                    # Renomear colunas
                    df_display.columns = ['Data', 'Loja', 'Vendedor', 'Cliente',
                                         'Preço Unitário', 'Quantidade', 'Valor Total']

                    st.dataframe(df_display, use_container_width=True)
                else:
                    st.warning("⚠️ Nenhuma venda encontrada com os filtros informados.")

    # ========================================================================
    # PÁGINA 4: PROJEÇÃO DE VENDAS
    # ========================================================================
    elif pagina == "📈 Projeção de Vendas":
        st.header("📈 Projeção de Vendas")
        st.markdown("""
        Use regressão linear para prever vendas futuras baseado no histórico.

        ⚠️ **Importante**: A projeção assume uma tendência LINEAR. Se as vendas forem sazonais
        ou cíclicas, a precisão pode ser reduzida. Use como guia, não como verdade absoluta.
        """)
        st.markdown("---")

        if not df_vendas.empty:
            # Preparar lista de lojas
            lista_lojas = df_vendas['MOVIMENTO_NOME_LOJA'].unique().tolist()
            lista_lojas = [l for l in lista_lojas if pd.notna(l) and str(l) != 'nan' and str(l) != '']

            col1, col2 = st.columns(2)
            with col1:
                loja_selecionada = filtro_autocomplete(
                    "🏪 Selecione a loja para projetar",
                    lista_lojas,
                    "Digite o nome da loja...",
                    allow_all=True
                )

            with col2:
                horizonte = st.slider("📅 Horizonte de projeção", 3, 12, 6,
                                     help="Número de períodos (dias, semanas ou meses) para projetar")

                # Usar 'ME' para mensal em pandas >= 2.0
                periodo = st.selectbox(
                    "📊 Período de agregação",
                    options=['D', 'W', 'ME'],
                    format_func={
                        'D': '📅 Diário (dia a dia)',
                        'W': '📆 Semanal (semana a semana)',
                        'ME': '📊 Mensal (mês a mês)'
                    }.get,
                    help="Escolha o nível de agregação dos dados"
                )

            # Mostrar explicação sobre o período
            if periodo == 'ME':
                st.info("📌 **Mensal**: Projeção mostrará valores agregados por mês. Melhor para visão estratégica de longo prazo.")
            elif periodo == 'W':
                st.info("📌 **Semanal**: Projeção mostrará valores agregados por semana. Bom balanço entre detalhe e visão macro.")
            else:
                st.info("📌 **Diário**: Projeção mostrará valores dia a dia. Melhor para análise tática de curto prazo.")

            if st.button("📈 Gerar Projeção", type="primary", key="btn_projecao"):
                with st.spinner("Gerando projeção com machine learning..."):
                    projecao = projetar_vendas(
                        df_vendas,
                        periodo=periodo,
                        horizonte=horizonte,
                        loja=loja_selecionada
                    )

                    criar_projecao_vendas(projecao)

                    # Aviso sobre dados insuficientes
                    if 'mensagem' in projecao and '⚠️' in projecao['mensagem']:
                        st.warning(projecao['mensagem'])
        else:
            st.warning("⚠️ Dados de vendas não disponíveis para projeção.")

    # ========================================================================
    # PÁGINA 5: APRESENTAÇÃO RAE (RELATÓRIO EXECUTIVO)
    # ========================================================================
    elif pagina == "📋 Apresentação RAE":
        st.header("📋 Apresentação RAE - Reunião de Alinhamento Estratégico")
        st.markdown("""
        Relatório executivo com análise completa, conclusões e recomendações estratégicas
        para apresentação à diretoria.
        """)
        st.markdown("---")

        if not df_vendas.empty:
            # Gerar análise
            analise = gerar_analise_executiva(df_vendas, df_lojas, df_vendedores)

            # ====================================================================
            # SEÇÃO 1: RESUMO EXECUTIVO
            # ====================================================================
            st.subheader("🎯 Resumo Executivo")

            # Calcula todos os números uma única vez (mesma fonte do Dashboard).
            kpi = calcular_indicadores(df_vendas)
            faturamento_total = kpi['faturamento']
            total_vendas = kpi['total_vendas']
            ticket_medio = kpi['ticket_medio']
            total_itens = kpi['total_itens']

            # Primeira linha: faturamento, lucro, margem
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Faturamento Total", formatar_moeda(faturamento_total))
            with col2:
                st.metric("💵 Lucro Bruto", formatar_moeda(kpi['lucro']))
            with col3:
                st.metric("📊 Margem de Lucro", f"{kpi['margem']:.1f}%")

            # Segunda linha: volume e ticket
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📋 Total de Vendas", f"{total_vendas:,}")
            with col2:
                st.metric("📦 Itens Vendidos", f"{total_itens:,.0f}")
            with col3:
                st.metric("🎫 Ticket Médio", formatar_moeda(ticket_medio))

            st.markdown("---")

            # ====================================================================
            # SEÇÃO 2: ANÁLISE DE PERFORMANCE
            # ====================================================================
            st.subheader("🏆 Análise de Performance")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Top 5 Lojas por Faturamento:**")
                if 'MOVIMENTO_NOME_LOJA' in df_vendas.columns:
                    top_lojas = df_vendas.groupby('MOVIMENTO_NOME_LOJA')['valor_total'].sum().sort_values(ascending=False).head(5)
                    for i, (loja, valor) in enumerate(top_lojas.items(), 1):
                        pct = (valor / faturamento_total) * 100
                        st.write(f"**{i}.** {loja}")
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{formatar_moeda(valor)} ({pct:.1f}% do total)")

            with col2:
                st.write("**Top 5 Vendedores por Faturamento:**")
                if 'MOVIMENTO_ITEM_VENDEDOR' in df_vendas.columns:
                    top_vendedores = df_vendas.groupby('MOVIMENTO_ITEM_VENDEDOR')['valor_total'].sum().sort_values(ascending=False).head(5)
                    for i, (vendedor, valor) in enumerate(top_vendedores.items(), 1):
                        pct = (valor / faturamento_total) * 100
                        st.write(f"**{i}.** {vendedor}")
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;{formatar_moeda(valor)} ({pct:.1f}% do total)")

            st.markdown("---")

            # ====================================================================
            # SEÇÃO 2B: RANKING DE LOJAS POR MARGEM DE LUCRO
            # ====================================================================
            # Faturar muito não é o mesmo que lucrar muito! Este ranking mostra
            # quais lojas são mais RENTÁVEIS (maior margem) e quais menos.
            st.subheader("💵 Ranking de Lojas por Margem de Lucro")
            st.caption("Faturar muito ≠ lucrar muito. Aqui vemos quais lojas realmente dão lucro.")

            ranking_margem = ranking_lojas_por_margem(df_vendas)

            if not ranking_margem.empty:
                # --- Gráfico de barras: margem (%) de cada loja ---
                # A cor acompanha a margem: barras mais escuras = mais rentáveis.
                fig_margem = px.bar(
                    ranking_margem,
                    x='Margem (%)',
                    y='Loja',
                    orientation='h',  # barras na horizontal (mais fácil de ler nomes)
                    title='Margem de Lucro por Loja (maior → menor)',
                    color='Margem (%)',
                    color_continuous_scale='RdYlGn',  # vermelho (ruim) → verde (bom)
                    text=ranking_margem['Margem (%)'].apply(lambda m: f"{m:.1f}%")
                )
                # Linha tracejada mostrando a meta mínima de margem.
                fig_margem.add_vline(
                    x=MARGEM_MINIMA, line_dash='dash', line_color='gray',
                    annotation_text=f"Meta mínima: {MARGEM_MINIMA}%"
                )
                fig_margem.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_margem, use_container_width=True)

                # --- Destaques: a melhor e a pior loja em rentabilidade ---
                melhor = ranking_margem.iloc[0]   # primeira linha = maior margem
                pior = ranking_margem.iloc[-1]     # última linha = menor margem
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"🥇 **Mais rentável:** {melhor['Loja']}\n\n"
                               f"Margem de {melhor['Margem (%)']:.1f}%")
                with col2:
                    st.error(f"⚠️ **Menos rentável:** {pior['Loja']}\n\n"
                             f"Margem de {pior['Margem (%)']:.1f}%")

                # --- Tabela completa, formatada em moeda e porcentagem ---
                with st.expander("📋 Ver tabela completa de margens por loja", expanded=False):
                    tabela = ranking_margem.copy()
                    tabela['Faturamento'] = tabela['Faturamento'].apply(formatar_moeda)
                    tabela['Lucro'] = tabela['Lucro'].apply(formatar_moeda)
                    tabela['Margem (%)'] = tabela['Margem (%)'].apply(lambda m: f"{m:.1f}%")
                    st.dataframe(tabela, use_container_width=True, hide_index=True)
            else:
                st.info("Sem dados de lucro suficientes para montar o ranking de margem.")

            st.markdown("---")

            # ====================================================================
            # SEÇÃO 3: CONCLUSÕES
            # ====================================================================
            st.subheader("📊 Conclusões Estratégicas")

            if analise['conclusoes']:
                for i, conclusao in enumerate(analise['conclusoes'], 1):
                    if conclusao['status'] == 'positivo':
                        st.success(f"✅ **{conclusao['titulo']}**\n{conclusao['dados']}")
                    elif conclusao['status'] == 'alerta':
                        st.warning(f"⚠️ **{conclusao['titulo']}**\n{conclusao['dados']}")
                    else:
                        st.info(f"ℹ️ **{conclusao['titulo']}**\n{conclusao['dados']}")

            st.markdown("---")

            # ====================================================================
            # SEÇÃO 4: RECOMENDAÇÕES ESTRATÉGICAS
            # ====================================================================
            st.subheader("💡 Recomendações Estratégicas")

            if analise['recomendacoes']:
                for idx, rec in enumerate(analise['recomendacoes'], 1):
                    i = int(idx)  # Converter para int nativo em caso de numpy.int64
                    prioridade_emoji = '🔴' if rec['prioridade'] == 'alta' else '🟡' if rec['prioridade'] == 'média' else '🟢'
                    with st.expander(f"{prioridade_emoji} {rec['titulo']} ({rec['prioridade'].upper()})", expanded=(i==1)):
                        st.write(f"**Descrição:** {rec['descricao']}")
                        st.write(f"**Ação recomendada:** {rec['acao']}")
            else:
                st.success("✅ Nenhuma recomendação crítica - Métricas dentro dos parâmetros esperados!")

            st.markdown("---")

            # ====================================================================
            # SEÇÃO 5: DOWNLOAD DO RELATÓRIO
            # ====================================================================
            st.subheader("📥 Download do Relatório")

            relatorio = []
            relatorio.append("=" * 80)
            relatorio.append("DISTRIBOX - APRESENTAÇÃO RAE")
            relatorio.append("Reunião de Alinhamento Estratégico")
            relatorio.append("=" * 80)
            relatorio.append("")
            relatorio.append(f"Data do relatório: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
            relatorio.append(f"Período analisado: Janeiro a Junho de 2026")
            relatorio.append("")

            relatorio.append("=" * 80)
            relatorio.append("RESUMO EXECUTIVO")
            relatorio.append("=" * 80)
            relatorio.append(f"Faturamento Total:        {formatar_moeda(faturamento_total)}")
            relatorio.append(f"Lucro Bruto:              {formatar_moeda(kpi['lucro'])}")
            relatorio.append(f"Margem de Lucro:          {kpi['margem']:.1f}%")
            relatorio.append(f"Total de Transações:      {total_vendas:,}")
            relatorio.append(f"Itens Vendidos:           {total_itens:,.0f}")
            relatorio.append(f"Ticket Médio:             {formatar_moeda(ticket_medio)}")
            relatorio.append("")

            relatorio.append("=" * 80)
            relatorio.append("TOP 5 LOJAS")
            relatorio.append("=" * 80)
            if 'MOVIMENTO_NOME_LOJA' in df_vendas.columns:
                top_lojas = df_vendas.groupby('MOVIMENTO_NOME_LOJA')['valor_total'].sum().sort_values(ascending=False).head(5)
                for i, (loja, valor) in enumerate(top_lojas.items(), 1):
                    pct = (valor / faturamento_total) * 100
                    relatorio.append(f"{i}. {loja:40} {formatar_moeda(valor):>15} ({pct:>5.1f}%)")
            relatorio.append("")

            relatorio.append("=" * 80)
            relatorio.append("TOP 5 VENDEDORES")
            relatorio.append("=" * 80)
            if 'MOVIMENTO_ITEM_VENDEDOR' in df_vendas.columns:
                top_vendedores = df_vendas.groupby('MOVIMENTO_ITEM_VENDEDOR')['valor_total'].sum().sort_values(ascending=False).head(5)
                for i, (vendedor, valor) in enumerate(top_vendedores.items(), 1):
                    pct = (valor / faturamento_total) * 100
                    relatorio.append(f"{i}. {vendedor:40} {formatar_moeda(valor):>15} ({pct:>5.1f}%)")
            relatorio.append("")

            relatorio.append("=" * 80)
            relatorio.append("RANKING DE LOJAS POR MARGEM DE LUCRO")
            relatorio.append("=" * 80)
            ranking_margem_txt = ranking_lojas_por_margem(df_vendas)
            if not ranking_margem_txt.empty:
                # Percorremos o ranking linha por linha, pegando cada coluna pelo nome.
                posicao = 1
                for _, linha in ranking_margem_txt.iterrows():
                    nome_loja = linha['Loja']
                    margem = linha['Margem (%)']
                    lucro = linha['Lucro']
                    relatorio.append(f"{posicao:>2}. {nome_loja:40} margem {margem:>6.1f}%  "
                                     f"(lucro {formatar_moeda(lucro)})")
                    posicao += 1
            relatorio.append("")

            relatorio.append("=" * 80)
            relatorio.append("CONCLUSÕES")
            relatorio.append("=" * 80)
            if analise['conclusoes']:
                for conclusao in analise['conclusoes']:
                    relatorio.append(f"\n{conclusao['titulo']}")
                    relatorio.append(f"{conclusao['dados']}\n")
            relatorio.append("")

            relatorio.append("=" * 80)
            relatorio.append("RECOMENDAÇÕES ESTRATÉGICAS")
            relatorio.append("=" * 80)
            if analise['recomendacoes']:
                for i, rec in enumerate(analise['recomendacoes'], 1):
                    relatorio.append(f"\n{i}. [{rec['prioridade'].upper()}] {rec['titulo']}")
                    relatorio.append(f"   Descrição: {rec['descricao']}")
                    relatorio.append(f"   Ação: {rec['acao']}")
            else:
                relatorio.append("✅ Todas as métricas estão dentro dos parâmetros esperados.")

            relatorio.append("\n" + "=" * 80)
            relatorio.append("FIM DO RELATÓRIO")
            relatorio.append("=" * 80)

            relatorio_text = "\n".join(relatorio)

            st.download_button(
                label="📄 Baixar Relatório RAE (TXT)",
                data=relatorio_text,
                file_name=f"relatorio_rae_distribox_{datetime.now().strftime('%d%m%Y')}.txt",
                mime="text/plain",
                key="download_rae"
            )
        else:
            st.warning("⚠️ Dados não disponíveis para a apresentação RAE.")


# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================
if __name__ == "__main__":
    main()
