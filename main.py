import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Tuple, Dict, List, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Distribox - Análise Estratégica",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 0. FUNÇÃO DE AJUDA (HELP) - DIDÁTICA E FÁCIL
# ============================================================================
def mostrar_ajuda():
    """
    Exibe um guia de uso interativo e didático dentro da aplicação.
    """
    with st.expander("❓ Como usar o sistema? (Guia Completo)", expanded=False):
        st.markdown("""
        ---
        # 📚 Guia de Uso - Distribox
        
        Olá! 👋 Este guia vai te ajudar a entender como usar cada parte do sistema.
        Vamos explorar juntos!
        
        ---
        
        ## 🏠 1. Dashboard Estratégico (O Painel de Controle)
        
        **O que é?** É a primeira tela que você vê. Mostra um resumo do negócio.
        
        **O que você vê?**
        - **💰 Faturamento Total**: Todo o dinheiro que a loja ganhou (R$)
        - **📋 Total de Vendas**: Quantas compras foram feitas
        - **📦 Itens Vendidos**: Quantas peças de roupa foram vendidas
        - **🎫 Ticket Médio**: Quanto cada cliente gasta em média
        
        **Gráficos:**
        - **Vendas por Loja**: Mostra qual loja vendeu mais (barras mais altas = mais vendas)
        - **Vendas por Tipo de Loja**: Mostra qual tipo (Prime, Outlet, Brands) vende mais
        
        💡 **Dica:** Quanto mais alta a barra, mais dinheiro a loja ganhou!
        
        ---
        
        ## 📦 2. Consulta de Produtos (O Catálogo)
        
        **O que é?** Permite pesquisar produtos no estoque do Centro de Distribuição.
        
        **Como usar?**
        1. Digite no campo **"🔍 Referência"** - ex: "CASACO" ou "19.907"
        2. Digite no campo **"📏 Tamanho"** - ex: "M", "G", "38", "40"
        3. Digite no campo **"🎨 Cor"** - ex: "PRETO", "AZUL", "CARAMELO"
        4. Clique em **"🔍 Consultar Produtos"**
        
        **O que aparece?**
        - **Referência**: Código único do produto (como um RG)
        - **Descrição**: Nome do produto
        - **Tamanho**: P, M, G, GG, ou números
        - **Cor**: A cor do produto
        - **Estoque Atual**: Quantos estão disponíveis
        - **Preço Custo**: Quanto custa para a loja
        
        💡 **Dica:** Você pode digitar APENAS UMA PARTE da palavra!
        Ex: "CASA" encontra "CASACO", "CASAQUETO", etc.
        
        📌 **Exemplo prático:**
        > Quer saber se tem um CASACO URUCUM na cor CARAMELO, tamanho M?
        > 1. Digite "CASACO" na Referência
        > 2. Digite "M" no Tamanho
        > 3. Digite "CARAMELO" na Cor
        > 4. Clique em Consultar!
        
        ---
        
        ## 🛒 3. Consulta de Vendas (O Histórico)
        
        **O que é?** Permite ver todas as vendas que aconteceram.
        
        **Como usar?**
        1. Escolha o **período**: Data Início e Data Fim
        2. Filtre por **Loja**: Digite o nome (ex: "15 - Metrô Outlet")
        3. Filtre por **Vendedor**: Digite o nome (ex: "LUCAS CAMPOS")
        4. Filtre por **Cliente**: Digite o código (ex: "15091")
        5. Clique em **"🔍 Consultar Vendas"**
        
        **O que aparece?**
        - **Data**: Quando a venda aconteceu
        - **Loja**: Onde foi vendido
        - **Vendedor**: Quem vendeu
        - **Cliente**: Quem comprou (código)
        - **Preço Unitário**: Quanto custou cada peça
        - **Quantidade**: Quantas peças foram compradas
        - **Valor Total**: Preço × Quantidade
        
        💡 **Dica:** Quer saber se uma loja está vendendo bem?
        Filtre por ela e veja quantas vendas aparecem!
        
        📌 **Exemplo prático:**
        > Quer ver todas as vendas do vendedor LUCAS CAMPOS PEREIRA?
        > 1. Deixe as datas como estão
        > 2. Digite "LUCAS" no Vendedor
        > 3. Clique em Consultar!
        
        ---
        
        ## 📈 4. Projeção de Vendas (A Bola de Cristal)
        
        **O que é?** Usa matemática para "adivinhar" como serão as vendas futuras.
        
        **Como usar?**
        1. Selecione a **loja** que quer analisar
        2. Escolha o **horizonte**: Quantos períodos (3 a 12)
        3. Escolha o **período de agregação**:
           - 📅 Diário: Projeção dia a dia
           - 📆 Semanal: Projeção semana a semana
           - 📅 Mensal: Projeção mês a mês
        4. Clique em **"📈 Gerar Projeção"**
        
        **O que aparece?**
        - **Linha azul**: O que já aconteceu (Histórico)
        - **Linha vermelha pontilhada**: O que achamos que vai acontecer (Projeção)
        - **R²**: O quanto confiamos (quanto mais perto de 1, melhor!)
        
        💡 **Dica:** R² = 0,85 significa que estamos 85% confiantes!
        
        📌 **Exemplo prático:**
        > Quer saber como serão as vendas da Loja 15 nos próximos 6 meses?
        > 1. Selecione a Loja 15
        > 2. Horizonte = 6
        > 3. Período = Mensal
        > 4. Clique em Gerar Projeção!
        
        ---
        
        ## 📋 5. Apresentação RAE (Relatório para os Chefões)
        
        **O que é?** Um relatório executivo com as informações mais importantes.
        
        **Como usar?**
        1. Leia o **Resumo Executivo**: Os números mais importantes
        2. Veja a **Análise de Performance**: Quem são os melhores
        3. Leia as **Recomendações**: O que fazer para melhorar
        4. **Baixe o Relatório**: Clique em "📄 Baixar Relatório RAE"
        
        **O que aparece?**
        - 💰 Faturamento Total
        - 📋 Total de Vendas
        - 🎫 Ticket Médio
        - 🏆 Top 3 Lojas
        - ⭐ Top 3 Vendedores
        - 💡 Recomendações Estratégicas
        
        💡 **Dica:** Use este relatório para mostrar aos chefões como a empresa está indo!
        
        ---
        
        ## 🎯 Glossário (Palavras importantes)
        
        | Palavra | O que significa |
        |---------|-----------------|
        | **Faturamento** | Todo o dinheiro que a loja ganhou |
        | **Estoque** | As roupas guardadas para vender |
        | **Ticket Médio** | Quanto cada cliente gasta em média |
        | **Projeção** | Uma "previsão" com matemática |
        | **RAE** | Reunião onde os chefões decidem o futuro |
        | **CD** | Centro de Distribuição - onde as roupas ficam |
        | **Referência** | O "RG" do produto (código único) |
        | **R²** | Medida de confiança (0 a 1, quanto maior melhor) |
        
        ---
        
        ## ❓ Perguntas Frequentes (FAQ)
        
        ### 1. Por que só aparece a loja 00-CD no estoque?
        > Porque o estoque é **centralizado** no Centro de Distribuição (CD).
        > As lojas recebem os produtos do CD.
        
        ### 2. O que significa "Ticket Médio"?
        > É o valor médio que cada cliente gasta por compra.
        > Ex: 10 clientes gastaram R$ 2.950,00 → Ticket Médio = R$ 295,00
        
        ### 3. Como sei se a projeção é confiável?
        > Veja o valor **R²**. Quanto mais perto de 1, mais confiável.
        > R² = 0,85 = 85% de confiança
        
        ### 4. Posso baixar os dados?
        > Sim! Na página "Apresentação RAE", clique em 
        > "📄 Baixar Relatório RAE" para baixar um relatório em TXT.
        
        ---
        
        ## 🎉 Parabéns!
        
        Agora você já sabe como usar o sistema da Distribox!
        
        Lembre-se: **dados são como pistas** - com as pistas certas,
        podemos descobrir histórias incríveis sobre a loja!
        
        🕵️‍♀️📊
        """)

# ============================================================================
# 1. FUNÇÕES DE CARREGAMENTO
# ============================================================================
@st.cache_data
def carregar_dados() -> Dict[str, pd.DataFrame]:
    """Carrega todos os arquivos CSV do diretório."""
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
    """Formata valor no padrão brasileiro."""
    if pd.isna(valor) or valor == 0:
        return "R$ 0,00"
    valor_formatado = f"{valor:,.2f}"
    valor_br = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_br}"

# ============================================================================
# 3. FUNÇÕES DE LIMPEZA DE DADOS
# ============================================================================
def limpar_dados(df: pd.DataFrame, nome: str) -> pd.DataFrame:
    """Aplica limpeza inteligente nos dados."""
    df_limpo = df.copy()
    df_limpo.columns = df_limpo.columns.str.strip()
    
    # Padronizar texto
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
    
    df_limpo = df_limpo.drop_duplicates()
    return df_limpo

# ============================================================================
# 4. CONSOLIDAÇÃO DE DADOS (MODELO ESTRELA)
# ============================================================================
@st.cache_data
def consolidar_dados(dados: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Consolida todos os dados em um modelo dimensional (estrela).
    
    Returns:
        Dict com as tabelas: vendas, produtos, clientes, lojas, vendedores, estoque
    """
    # Limpar todos os datasets
    df_vendas_p1 = limpar_dados(dados['vendas_p1'], 'vendas_p1') if not dados['vendas_p1'].empty else pd.DataFrame()
    df_vendas_p2 = limpar_dados(dados['vendas_p2'], 'vendas_p2') if not dados['vendas_p2'].empty else pd.DataFrame()
    df_produtos = limpar_dados(dados['produtos'], 'produtos') if not dados['produtos'].empty else pd.DataFrame()
    df_clientes = limpar_dados(dados['clientes'], 'clientes') if not dados['clientes'].empty else pd.DataFrame()
    df_vendedores = limpar_dados(dados['vendedores'], 'vendedores') if not dados['vendedores'].empty else pd.DataFrame()
    df_lojas = limpar_dados(dados['lojas'], 'lojas') if not dados['lojas'].empty else pd.DataFrame()
    df_estoque = limpar_dados(dados['variacoes_estoque'], 'variacoes_estoque') if not dados['variacoes_estoque'].empty else pd.DataFrame()
    
    # Concatenar vendas
    df_vendas = pd.concat([df_vendas_p1, df_vendas_p2], ignore_index=True)
    
    # Filtrar apenas vendas (não devoluções)
    df_vendas = df_vendas[df_vendas['MOVIMENTO_TIPO'] == 'SAIDA']
    
    # Calcular valor total
    if not df_vendas.empty:
        df_vendas['MOVIMENTO_ITEM_QUANTIDADE'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_QUANTIDADE'], errors='coerce').fillna(1)
        df_vendas['MOVIMENTO_ITEM_PRECO_UNITARIO'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_PRECO_UNITARIO'], errors='coerce').fillna(0)
        df_vendas['MOVIMENTO_ITEM_DESCONTO'] = pd.to_numeric(df_vendas['MOVIMENTO_ITEM_DESCONTO'], errors='coerce').fillna(0)
        
        df_vendas['valor_total'] = (
            df_vendas['MOVIMENTO_ITEM_QUANTIDADE'] * 
            df_vendas['MOVIMENTO_ITEM_PRECO_UNITARIO'] * 
            (1 - df_vendas['MOVIMENTO_ITEM_DESCONTO'] / 100)
        )
        
        # Extrair código do produto do código de barras
        df_vendas['produto_codigo'] = df_vendas['MOVIMENTO_ITEM_CODIGO_DE_BARRAS'].astype(str).str[:12]
    
    # ========================================================================
    # ESTOQUE: Manter apenas o CD (estoque centralizado)
    # ========================================================================
    # Filtrar apenas o Centro de Distribuição
    df_estoque_cd = df_estoque[df_estoque['IDENTIFICACAO'] == '00 - CD'].copy()
    
    # Se não houver registros do CD, usar todos
    if df_estoque_cd.empty:
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
# 5. FUNÇÃO PARA CRIAR COMBOBOX COM DIGITAÇÃO
# ============================================================================
def filtro_autocomplete(
    label: str,
    options: List,
    placeholder: str = "Digite para filtrar...",
    allow_all: bool = True
) -> Optional[str]:
    """
    Cria um filtro com autocomplete usando selectbox.
    
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
    cor: Optional[str] = None,
    loja: Optional[str] = None  # Mantido para compatibilidade, mas ignorado
) -> pd.DataFrame:
    """
    Consulta produtos com estoque disponível no CD.
    """
    # Unir produtos com estoque do CD
    df_consulta = df_produtos.merge(
        df_estoque,
        left_on='REFERENCIA',
        right_on='PRODUTO_REFERENCIA',
        how='inner'
    )
    
    # Aplicar filtros
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
# 7. CONSULTA DE VENDAS COM FILTROS (COM LOJA)
# ============================================================================
def consultar_vendas(
    df_vendas: pd.DataFrame,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    loja: Optional[str] = None,
    categoria: Optional[str] = None,
    cliente: Optional[int] = None,
    vendedor: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict]:
    """
    Consulta vendas com filtros combináveis.
    
    Returns:
        Tuple: (DataFrame filtrado, dicionário com totais)
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
    
    # Calcular totais
    totais = {
        'total_vendas': len(df),
        'total_itens': df['MOVIMENTO_ITEM_QUANTIDADE'].sum() if not df.empty else 0,
        'faturamento': df['valor_total'].sum() if not df.empty else 0,
        'ticket_medio': df['valor_total'].mean() if not df.empty and len(df) > 0 else 0,
        'valor_medio_item': df['MOVIMENTO_ITEM_PRECO_UNITARIO'].mean() if not df.empty else 0
    }
    
    return df, totais

# ============================================================================
# 8. PROJEÇÃO DE VENDAS (CORRIGIDA)
# ============================================================================
def projetar_vendas(
    df_vendas: pd.DataFrame,
    periodo: str = 'D',
    horizonte: int = 30,
    loja: Optional[str] = None
) -> Dict:
    """
    Projeta vendas futuras usando regressão linear.
    
    Args:
        df_vendas: DataFrame com vendas
        periodo: Período de agregação ('D' para diário, 'W' para semanal, 'ME' para mensal)
        horizonte: Número de períodos para projeção
        loja: Nome da loja para filtrar (opcional)
    
    Returns:
        Dict com histórico e projeção
    """
    df = df_vendas.copy()
    
    if loja:
        df = df[df['MOVIMENTO_NOME_LOJA'] == loja]
    
    # Mapeamento de períodos (corrigido)
    # 'M' foi substituído por 'ME' (MEnsal)
    mapeamento_periodos = {
        'D': 'D',      # Diário
        'W': 'W',      # Semanal
        'ME': 'ME'     # Mensal (era 'M' antes)
    }
    
    freq = mapeamento_periodos.get(periodo, 'D')
    
    # Agregar por período
    df['data'] = pd.to_datetime(df['MOVIMENTO_DATA'])
    df_agregado = df.groupby(pd.Grouper(key='data', freq=freq)).agg({
        'valor_total': 'sum'
    }).reset_index()
    df_agregado = df_agregado.dropna()
    
    # Verificar se há dados suficientes
    if len(df_agregado) < 3:
        return {
            'historico': df_agregado, 
            'projecao': pd.DataFrame(), 
            'mensagem': 'Dados insuficientes para projeção (mínimo 3 períodos)'
        }
    
    # Preparar dados para regressão
    df_agregado['dias'] = (df_agregado['data'] - df_agregado['data'].min()).dt.days
    
    X = df_agregado['dias'].values.reshape(-1, 1)
    y = df_agregado['valor_total'].values
    
    # Treinar modelo
    model = LinearRegression()
    model.fit(X, y)
    
    # Projetar futuro
    ultimo_dia = df_agregado['dias'].max()
    
    # Para períodos mensais, o horizonte é em meses
    if periodo == 'ME':
        # Para mensal, usamos dias (30 dias por mês)
        dias_por_periodo = 30
    elif periodo == 'W':
        dias_por_periodo = 7
    else:
        dias_por_periodo = 1
    
    dias_futuros = np.arange(
        ultimo_dia + 1, 
        ultimo_dia + horizonte * dias_por_periodo + 1,
        dias_por_periodo
    ).reshape(-1, 1)
    
    projecao_valores = model.predict(dias_futuros)
    
    # Criar DataFrame de projeção
    datas_futuras = []
    for i in range(horizonte):
        if periodo == 'ME':
            # Para mensal, adicionar meses
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
    
    # Combinar
    df_completo = pd.concat([df_historico, df_projecao], ignore_index=True)
    
    return {
        'historico': df_historico,
        'projecao': df_projecao,
        'completo': df_completo,
        'modelo': model,
        'r2': model.score(X, y),
        'tendencia_diaria': model.coef_[0],
        'mensagem': f'Projeção gerada com R² = {model.score(X, y):.2f}'
    }

# ============================================================================
# 9. VISUALIZAÇÕES ESTRATÉGICAS
# ============================================================================
def criar_dashboard_estrategico(df_vendas: pd.DataFrame, df_lojas: pd.DataFrame) -> None:
    """
    Cria visualizações estratégicas para a RAE.
    """
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        faturamento = df_vendas['valor_total'].sum() if not df_vendas.empty else 0
        st.metric("💰 Faturamento Total", formatar_moeda(faturamento))
    
    with col2:
        total_vendas = len(df_vendas) if not df_vendas.empty else 0
        st.metric("📋 Total de Vendas", f"{total_vendas:,}")
    
    with col3:
        itens_vendidos = df_vendas['MOVIMENTO_ITEM_QUANTIDADE'].sum() if not df_vendas.empty else 0
        st.metric("📦 Itens Vendidos", f"{itens_vendidos:,.0f}")
    
    with col4:
        ticket_medio = df_vendas['valor_total'].mean() if not df_vendas.empty else 0
        st.metric("🎫 Ticket Médio", formatar_moeda(ticket_medio))
    
    # Gráfico 1: Vendas por Loja
    if not df_vendas.empty and 'MOVIMENTO_NOME_LOJA' in df_vendas.columns:
        vendas_loja = df_vendas.groupby('MOVIMENTO_NOME_LOJA')['valor_total'].sum().sort_values(ascending=False).reset_index()
        vendas_loja.columns = ['loja', 'valor_total']
        
        fig = px.bar(
            vendas_loja,
            x='loja',
            y='valor_total',
            title='🏪 Vendas por Loja',
            labels={'loja': 'Loja', 'valor_total': 'Faturamento'},
            color='valor_total',
            color_continuous_scale='Viridis',
            text=vendas_loja['valor_total'].apply(formatar_moeda)
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico 2: Vendas por Tipo de Loja
    if not df_lojas.empty and not df_vendas.empty:
        df_lojas['identificacao_limpa'] = df_lojas['identificacao'].str.split(' - ').str[0]
        df_vendas['loja_codigo'] = df_vendas['MOVIMENTO_NOME_LOJA'].str.split(' - ').str[0]
        
        vendas_tipo = df_vendas.merge(
            df_lojas[['identificacao_limpa', 'tipo']],
            left_on='loja_codigo',
            right_on='identificacao_limpa',
            how='left'
        )
        
        if not vendas_tipo.empty:
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
    Cria gráfico de projeção de vendas.
    """
    if 'completo' not in projecao or projecao['completo'].empty:
        st.warning(projecao.get('mensagem', 'Dados insuficientes para projeção'))
        return
    
    df = projecao['completo']
    
    fig = go.Figure()
    
    # Separar histórico e projeção
    df_historico = df[df['tipo'] == 'Histórico']
    df_projecao = df[df['tipo'] == 'Projeção']
    
    # Adicionar histórico
    fig.add_trace(go.Scatter(
        x=df_historico['data'],
        y=df_historico['valor_total'],
        name='Histórico',
        line=dict(color='blue', width=2),
        mode='lines+markers'
    ))
    
    # Adicionar projeção
    fig.add_trace(go.Scatter(
        x=df_projecao['data'],
        y=df_projecao['valor_total'],
        name='Projeção',
        line=dict(color='red', width=2, dash='dash'),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title='📈 Projeção de Vendas',
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
            st.metric("📊 Qualidade da Projeção", f"R² = {projecao['r2']:.2f}")
        with col2:
            tendencia = projecao['tendencia_diaria']
            st.metric(
                "📈 Tendência Diária", 
                formatar_moeda(tendencia),
                delta=f"{tendencia/100:.1f}%" if abs(tendencia) > 0 else "Estável"
            )

# ============================================================================
# 10. INTERFACE PRINCIPAL
# ============================================================================
def main():
    """Função principal da aplicação."""
    
    # Título e botão de ajuda no topo
    col_title, col_help = st.columns([4, 1])
    with col_title:
        st.title("👔 Distribox - Análise Estratégica")
        st.caption("RAE - Reunião de Alinhamento Estratégico")
    with col_help:
        # Botão de ajuda bem visível
        if st.button("❓ Ajuda", use_container_width=True):
            mostrar_ajuda()
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📌 Navegação")
        pagina = st.radio(
            "Selecione:",
            [
                "🏠 Dashboard Estratégico",
                "📦 Consulta de Produtos",
                "🛒 Consulta de Vendas",
                "📈 Projeção de Vendas",
                "📋 Apresentação RAE"
            ]
        )
        
        st.markdown("---")
        st.info("""
        **Distribox - Varejo de Moda**
        15 lojas físicas | Centro de Distribuição
        Dados 2026
        """)
        
        # Botão de ajuda na sidebar
        st.markdown("---")
        if st.button("❓ Como usar o sistema?", use_container_width=True):
            mostrar_ajuda()
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
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
        st.markdown("Visão geral do negócio para a diretoria.")
        
        if not df_vendas.empty:
            criar_dashboard_estrategico(df_vendas, df_lojas)
        else:
            st.warning("Dados de vendas não disponíveis.")
    
    # ========================================================================
    # PÁGINA 2: CONSULTA DE PRODUTOS (ESTOQUE DO CD)
    # ========================================================================
    elif pagina == "📦 Consulta de Produtos":
        st.header("📦 Consulta de Produtos com Estoque")
        st.markdown("""
        Consulte produtos e verifique o estoque disponível no **Centro de Distribuição**.
        O estoque é centralizado e abastece todas as lojas físicas.
        """)
        st.caption("💡 Digite no campo para filtrar as opções disponíveis")
        
        # Preparar listas para autocomplete
        lista_referencias = df_produtos['REFERENCIA'].unique().tolist() if not df_produtos.empty else []
        lista_tamanhos = df_estoque['TAMANHO'].unique().tolist() if not df_estoque.empty else []
        lista_cores = df_estoque['COR'].unique().tolist() if not df_estoque.empty else []
        
        col1, col2 = st.columns(2)
        with col1:
            referencia = filtro_autocomplete(
                "🔍 Referência",
                lista_referencias,
                "Digite a referência do produto..."
            )
            tamanho = filtro_autocomplete(
                "📏 Tamanho",
                lista_tamanhos,
                "Digite o tamanho (M, G, 38, 40)..."
            )
        with col2:
            cor = filtro_autocomplete(
                "🎨 Cor",
                lista_cores,
                "Digite a cor (PRETO, AZUL, CARAMELO)..."
            )
        
        if st.button("🔍 Consultar Produtos", type="primary"):
            with st.spinner("Consultando..."):
                resultado = consultar_produtos(
                    df_produtos, df_estoque,
                    referencia=referencia if referencia else None,
                    tamanho=tamanho if tamanho else None,
                    cor=cor if cor else None
                )
                
                if not resultado.empty:
                    st.success(f"✅ Encontrados {len(resultado)} registros de estoque no CD")
                    
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
                        st.metric("📦 Estoque Total", f"{total_estoque:,.0f}")
                    with col2:
                        produtos_unicos = resultado['REFERENCIA'].nunique() if 'REFERENCIA' in resultado.columns else 0
                        st.metric("📋 Produtos Únicos", produtos_unicos)
                    with col3:
                        if 'PRECO_CUSTO' in resultado.columns:
                            valor_medio = resultado['PRECO_CUSTO'].mean() if pd.notna(resultado['PRECO_CUSTO']).any() else 0
                            st.metric("💰 Preço Médio", formatar_moeda(valor_medio))
                else:
                    st.warning("⚠️ Nenhum produto encontrado com os filtros informados.")
    
    # ========================================================================
    # PÁGINA 3: CONSULTA DE VENDAS (COM FILTRO POR LOJA)
    # ========================================================================
    elif pagina == "🛒 Consulta de Vendas":
        st.header("🛒 Consulta de Vendas")
        st.markdown("Consulte vendas com filtros combináveis, incluindo filtro por loja.")
        st.caption("💡 Digite no campo para filtrar as opções disponíveis")
        
        # Preparar listas para autocomplete
        lista_lojas = df_vendas['MOVIMENTO_NOME_LOJA'].unique().tolist() if not df_vendas.empty else []
        lista_vendedores = df_vendas['MOVIMENTO_ITEM_VENDEDOR'].unique().tolist() if not df_vendas.empty else []
        lista_clientes = df_vendas['CODIGO_CLIENTE'].unique().tolist() if not df_vendas.empty else []
        
        # Remover valores nulos e vazios
        lista_lojas = [l for l in lista_lojas if pd.notna(l) and str(l) != 'nan' and str(l) != '']
        lista_vendedores = [v for v in lista_vendedores if pd.notna(v) and str(v) != 'nan' and str(v) != '']
        lista_clientes = [c for c in lista_clientes if pd.notna(c) and str(c) != 'nan' and str(c) != '']
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input("📅 Data Início", value=pd.to_datetime('2026-01-01'))
            data_fim = st.date_input("📅 Data Fim", value=pd.to_datetime('2026-06-30'))
            
            loja_selecionada = filtro_autocomplete(
                "🏪 Loja",
                lista_lojas,
                "Digite o nome da loja..."
            )
        
        with col2:
            vendedor_selecionado = filtro_autocomplete(
                "👤 Vendedor",
                lista_vendedores,
                "Digite o nome do vendedor..."
            )
            
            cliente_selecionado = filtro_autocomplete(
                "👥 Cliente",
                lista_clientes,
                "Digite o código do cliente..."
            )
        
        if st.button("🔍 Consultar Vendas", type="primary"):
            with st.spinner("Consultando..."):
                # Converter cliente para int se selecionado
                cliente_filtro = None
                if cliente_selecionado and cliente_selecionado.isdigit():
                    cliente_filtro = int(cliente_selecionado)
                
                df_filtrado, totais = consultar_vendas(
                    df_vendas,
                    data_inicio=pd.to_datetime(data_inicio),
                    data_fim=pd.to_datetime(data_fim),
                    loja=loja_selecionada,
                    cliente=cliente_filtro,
                    vendedor=vendedor_selecionado
                )
                
                # Exibir totais
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📋 Total de Vendas", totais['total_vendas'])
                with col2:
                    st.metric("📦 Itens Vendidos", f"{totais['total_itens']:,.0f}")
                with col3:
                    st.metric("💰 Faturamento", formatar_moeda(totais['faturamento']))
                with col4:
                    st.metric("🎫 Ticket Médio", formatar_moeda(totais['ticket_medio']))
                
                # Exibir dados
                if not df_filtrado.empty:
                    st.subheader("📋 Detalhamento")
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
    # PÁGINA 4: PROJEÇÃO DE VENDAS (CORRIGIDA)
    # ========================================================================
    elif pagina == "📈 Projeção de Vendas":
        st.header("📈 Projeção de Vendas")
        st.markdown("Projeção de vendas futuras baseada em dados históricos.")
        
        if not df_vendas.empty:
            # Preparar lista de lojas para autocomplete
            lista_lojas = df_vendas['MOVIMENTO_NOME_LOJA'].unique().tolist()
            lista_lojas = [l for l in lista_lojas if pd.notna(l) and str(l) != 'nan' and str(l) != '']
            
            col1, col2 = st.columns(2)
            with col1:
                loja_selecionada = filtro_autocomplete(
                    "🏪 Selecione a loja",
                    lista_lojas,
                    "Digite o nome da loja..."
                )
            
            with col2:
                horizonte = st.slider("📅 Horizonte de projeção", 3, 12, 6, 
                                     help="Número de períodos para projetar")
                
                # CORREÇÃO: Usar 'ME' em vez de 'M' para mensal
                periodo = st.selectbox(
                    "📊 Período de agregação",
                    options=['D', 'W', 'ME'],
                    format_func={
                        'D': '📅 Diário', 
                        'W': '📆 Semanal', 
                        'ME': '📅 Mensal'
                    }.get
                )
                
                # Mostrar explicação sobre o período
                if periodo == 'ME':
                    st.info("📌 **Mensal:** A projeção mostrará valores agregados por mês.")
                elif periodo == 'W':
                    st.info("📌 **Semanal:** A projeção mostrará valores agregados por semana.")
                else:
                    st.info("📌 **Diário:** A projeção mostrará valores agregados por dia.")
            
            if st.button("📈 Gerar Projeção", type="primary"):
                with st.spinner("Gerando projeção..."):
                    projecao = projetar_vendas(
                        df_vendas, 
                        periodo=periodo, 
                        horizonte=horizonte, 
                        loja=loja_selecionada
                    )
                    
                    criar_projecao_vendas(projecao)
        else:
            st.warning("Dados de vendas não disponíveis para projeção.")
    
    # ========================================================================
    # PÁGINA 5: APRESENTAÇÃO RAE
    # ========================================================================
    elif pagina == "📋 Apresentação RAE":
        st.header("📋 Apresentação RAE")
        st.markdown("Reunião de Alinhamento Estratégico - Distribox")
        
        if not df_vendas.empty:
            # Resumo Executivo
            st.subheader("🎯 Resumo Executivo")
            
            faturamento_total = df_vendas['valor_total'].sum()
            total_vendas = len(df_vendas)
            ticket_medio = df_vendas['valor_total'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Faturamento Total", formatar_moeda(faturamento_total))
            with col2:
                st.metric("📋 Total de Vendas", f"{total_vendas:,}")
            with col3:
                st.metric("🎫 Ticket Médio", formatar_moeda(ticket_medio))
            
            # Análise de Performance
            st.subheader("🏆 Análise de Performance")
            
            # Top Lojas
            if 'MOVIMENTO_NOME_LOJA' in df_vendas.columns:
                top_lojas = df_vendas.groupby('MOVIMENTO_NOME_LOJA')['valor_total'].sum().sort_values(ascending=False).head(3)
                st.write("**Top 3 Lojas por Faturamento:**")
                for i, (loja, valor) in enumerate(top_lojas.items(), 1):
                    st.write(f"{i}. {loja}: {formatar_moeda(valor)}")
            
            # Top Vendedores
            if 'MOVIMENTO_ITEM_VENDEDOR' in df_vendas.columns:
                top_vendedores = df_vendas.groupby('MOVIMENTO_ITEM_VENDEDOR')['valor_total'].sum().sort_values(ascending=False).head(3)
                st.write("**Top 3 Vendedores por Faturamento:**")
                for i, (vendedor, valor) in enumerate(top_vendedores.items(), 1):
                    st.write(f"{i}. {vendedor}: {formatar_moeda(valor)}")
            
            # Recomendações Estratégicas
            st.subheader("💡 Recomendações Estratégicas")
            
            recomendacoes = []
            
            # Análise de sazonalidade
            if not df_vendas.empty and 'MOVIMENTO_DATA' in df_vendas.columns:
                df_vendas['mes'] = df_vendas['MOVIMENTO_DATA'].dt.month
                vendas_por_mes = df_vendas.groupby('mes')['valor_total'].sum()
                melhor_mes = vendas_por_mes.idxmax() if not vendas_por_mes.empty else None
                pior_mes = vendas_por_mes.idxmin() if not vendas_por_mes.empty else None
                
                if melhor_mes and pior_mes:
                    recomendacoes.append(f"📊 **Sazonalidade identificada:** Melhor mês = {melhor_mes}, Pior mês = {pior_mes}. Recomenda-se campanhas específicas para o período de baixa.")
            
            # Análise de ticket médio
            if ticket_medio < 100:
                recomendacoes.append("💰 **Ticket médio baixo:** Considere estratégias de up-selling e cross-selling para aumentar o valor das vendas.")
            
            # Análise de lojas
            if 'MOVIMENTO_NOME_LOJA' in df_vendas.columns:
                lojas_com_vendas = df_vendas['MOVIMENTO_NOME_LOJA'].nunique()
                if lojas_com_vendas < 10:
                    recomendacoes.append(f"🏪 **Apenas {lojas_com_vendas} lojas com vendas registradas:** Verifique a operação das demais unidades.")
            
            for i, rec in enumerate(recomendacoes, 1):
                st.write(f"{i}. {rec}")
            
            if not recomendacoes:
                st.success("✅ Todas as métricas estão dentro dos parâmetros esperados.")
            
            # Download do Relatório
            st.markdown("---")
            st.subheader("📥 Download do Relatório")
            
            relatorio = []
            relatorio.append("=" * 60)
            relatorio.append("RELATÓRIO RAE - DISTRIBOX")
            relatorio.append("=" * 60)
            relatorio.append("")
            relatorio.append(f"Faturamento Total: {formatar_moeda(faturamento_total)}")
            relatorio.append(f"Total de Vendas: {total_vendas:,}")
            relatorio.append(f"Ticket Médio: {formatar_moeda(ticket_medio)}")
            relatorio.append("")
            relatorio.append("RECOMENDAÇÕES ESTRATÉGICAS:")
            for rec in recomendacoes:
                relatorio.append(f"- {rec}")
            
            relatorio_text = "\n".join(relatorio)
            
            st.download_button(
                label="📄 Baixar Relatório RAE (TXT)",
                data=relatorio_text,
                file_name="relatorio_rae_distribox.txt",
                mime="text/plain"
            )
        else:
            st.warning("Dados não disponíveis para a apresentação.")

# ============================================================================
# EXECUÇÃO
# ============================================================================
if __name__ == "__main__":
    main()