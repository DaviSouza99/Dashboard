import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import concurrent.futures

# ===============================================================
# CÓDIGO DE VERIFICAÇÃO DE SENHA - COLE ISSO NO TOPO
# ===============================================================

def check_password():

    """Retorna `True` se o usuário inseriu a senha correta."""
 
    def password_entered():

        """Verifica se a senha inserida pelo usuário está correta."""

        if st.session_state["password"] == st.secrets["PASSWORD"]:

            st.session_state["password_correct"] = True

            del st.session_state["password"]

        else:

            st.session_state["password_correct"] = False
 
    if st.session_state.get("password_correct", False):

        return True
 
    st.text_input(

        "Type your password to continue", type="password", on_change=password_entered, key="password"

    )

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:

        st.error("😕 Incorrect Password")

    return False
 
if not check_password():

    st.stop()

# ==========================================
# CONFIGURAÇÃO DA PÁGINA E UI
# ==========================================
st.set_page_config(page_title="Dashboard de Risco - Loan Tape", layout="wide")

# Injeção de CSS customizado para melhorar a usabilidade das Abas
st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# GESTÃO DE IDIOMAS (INTERNACIONALIZAÇÃO)
# ==========================================
idioma = st.sidebar.radio("🌐 Idioma / Language", ["Português", "English"], horizontal=True)

DICIONARIO_EN = {
    # Alertas e Títulos Gerais
    "Dashboard de Risco - Loan Tape": "Risk Dashboard - Loan Tape",
    "⚠️ Biblioteca 'holidays' não instalada. O cálculo de dias úteis ignorará feriados. Execute `pip install holidays` no terminal para máxima precisão.": "⚠️ 'holidays' library not installed. Business days calculation will ignore holidays. Run `pip install holidays` in the terminal for maximum precision.",
    "📊 Upload de Dados": "📊 Data Upload",
    "Faça o upload do arquivo 'Loan Tape'": "Upload the 'Loan Tape' file",
    "📅 Configurações Globais": "📅 Global Settings",
    "Data de Referência (Snapshot)": "Reference Date (Snapshot)",
    "Corte Fotográfico: Pagamentos ocorridos APÓS esta data não existirão na simulação.": "Snapshot Cut: Payments occurred AFTER this date will not exist in the simulation.",
    "Tolerância FPD/SPD/TDP (Dias)": "FPD/SPD/TDP Tolerance (Days)",
    "Tolerância Perda / PAR (Dias)": "Loss / PAR Tolerance (Days)",
    "🔍 Filtros de Análise": "🔍 Analysis Filters",
    "Tipo de Produto": "Product Type",
    "Safra": "Vintage",
    "📈 Análise de Risco e Rentabilidade - Institucional": "📈 Risk and Profitability Analysis - Institutional",
    "**Volume Total Originado Filtrado (Desembolso Real por Contrato):** R$ ": "**Filtered Total Originated Volume (Real Disbursement by Contract):** R$ ",
    
    # Nomes das Abas
    "Originação": "Origination",
    "Análise de TIR": "IRR Analysis",
    "TIR (Ajustada PDD)": "IRR (PDD Adjusted)",
    "FPD, SPD e TDP": "FPD, SPD and TDP",
    "Perda Over {}": "Loss Over {}",
    "Collection": "Collection",
    "PAR (Vintage)": "PAR (Vintage)",
    "Aging": "Aging",
    "Ciclo de Pag. (Waterfall)": "Payment Cycle (Waterfall)",
    "Roll Rate": "Roll Rate",
    "Perfil e Concentração": "Profile and Concentration",
    
    # Aba Originação
    "Originação por Safra": "Origination by Vintage",
    "Comparativo da Soma das Parcelas Esperadas vs Valor Total Desembolsado. Taxa e Prazo são ponderados pela Exposição do Contrato.": "Comparison of Expected Installments Sum vs Total Disbursed Value. Rate and Term are weighted by Contract Exposure.",
    "Soma Face Parcela (Esperado)": "Face Installment Sum (Expected)",
    "Valor Desembolsado (VP)": "Disbursed Value (PV)",
    "Taxa Média Ponderada": "Weighted Average Rate",
    "Prazo Médio Ponderado (Meses)": "Weighted Average Term (Months)",
    "Ticket Médio Simples": "Simple Average Ticket",
    "Comparativo de Originação, Taxa e Prazo Médio": "Comparison of Origination, Average Rate and Term",
    "Volume (R$)": "Volume (R$)",
    "Taxa (%)": "Rate (%)",
    "Prazo (Meses)": "Term (Months)",
    "Evolução do Ticket Médio por Safra (R$)": "Average Ticket Evolution by Vintage (R$)",
    "Valor (R$)": "Value (R$)",
    "Total Face (Esperado)": "Total Face (Expected)",
    "Total Desembolso (VP)": "Total Disbursement (PV)",
    "Taxa Média (%)": "Average Rate (%)",
    
    # Aba TIR
    "Análise de TIR Anualizada (XIRR) por Safra": "Annualized IRR (XIRR) Analysis by Vintage",
    "**Novo Motor de Precisão Diária e Financeira:**\n* **D0 a Dn (Originação):** Saídas de caixa alocadas no dia exato da `DATA_ORIGINACAO`. Considera o `VALOR_DESEMBOLSO` único por contrato.\n* **Fluxos de Entrada:** Utiliza o `VALOR_PAGO` integral (inclui os ágios de multas e juros, aumentando a rentabilidade real).\n* **Fluxo Terminal:** `SALDO_REMANESCENTE` futuro descontado a Valor Presente na data da foto.": "**New Daily and Financial Precision Engine:**\n* **D0 to Dn (Origination):** Cash outflows allocated on the exact `DATA_ORIGINACAO` date. Considers the unique `VALOR_DESEMBOLSO` per contract.\n* **Cash Inflows:** Uses the full `VALOR_PAGO` (includes penalty and interest premiums, increasing real profitability).\n* **Terminal Flow:** Future `SALDO_REMANESCENTE` discounted to Present Value on the snapshot date.",
    "Haircut de Perda Projetada (%)": "Projected Loss Haircut (%)",
    "Haircut (%)": "Haircut (%)",
    "TIR Anualizada (%)": "Annualized IRR (%)",
    "TIR Anualizada Real (Ref: {})": "Real Annualized IRR (Ref: {})",
    "Ver Matriz de Fluxo de Caixa Diário por Safra (Offset Real)": "View Daily Cash Flow Matrix by Vintage (Real Offset)",
    "💡 **Nota Explicativa:** A matriz distribui as saídas de caixa nos dias exatos das averbações. O marco zero de cada coluna é a primeira data de originação daquela Safra. A última linha exibe o Valor Terminal aplicado.": "💡 **Explanatory Note:** The matrix distributes cash outflows on the exact averbation dates. The zero mark of each column is the first origination date of that Vintage. The last row displays the applied Terminal Value.",
    "➔ Saldo Terminal Aplicado": "➔ Applied Terminal Balance",
    
    # Aba TIR PDD
    "Análise de TIR com Provisão Granular (PDD por Efeito Vagão)": "IRR Analysis with Granular Provision (PDD by Wagon Effect)",
    "**Rigor de Risco:** Nesta visão, o provisionamento do \"Valor Terminal\" não é linear por Safra. \n            Aplicamos o conceito de **Efeito Vagão**: se um contrato tem qualquer parcela em atraso, a sua pior faixa contamina o saldo total do contrato (vencido e futuro).": "**Risk Rigor:** In this view, the \"Terminal Value\" provisioning is not linear per Vintage. \n            We apply the **Wagon Effect** concept: if a contract has any overdue installment, its worst bucket contaminates the entire contract balance (overdue and future).",
    "Configuração de PDD por Faixa de Atraso do Contrato (%)": "PDD Configuration by Contract Delay Bucket (%)",
    "Faixa de Atraso (Pior do Contrato)": "Delay Bucket (Worst of Contract)",
    "Provisão (%)": "Provision (%)",
    "TIR (Ajustada PDD) %": "IRR (PDD Adjusted) %",
    "TIR Anualizada Pós-PDD (Efeito Vagão)": "Post-PDD Annualized IRR (Wagon Effect)",
    "Auditabilidade de Valor Terminal": "Terminal Value Auditability",
    "💡 Este valor representa o montante que o fundo espera recuperar do saldo devedor atual, já descontando as perdas estimadas por atraso (PDD).": "💡 This value represents the amount the fund expects to recover from the current outstanding balance, already discounting the estimated losses due to delay (PDD).",
    "Valor de Recuperação Esperada (R$)": "Expected Recovery Value (R$)",
    "Ver Matriz de Fluxos de Caixa (Provisão Vagão)": "View Cash Flow Matrix (Wagon Provision)",
    "➔ Valor Final Ajustado (PDD)": "➔ Final Adjusted Value (PDD)",
    
    # Aba FPD, SPD, TDP
    "Análise de FPD, SPD e TDP por Safra": "FPD, SPD and TDP Analysis by Vintage",
    "Selecione a Visão:": "Select View:",
    "Parcela (Visão de Fluxo/Caixa)": "Installment (Cash/Flow View)",
    "Contrato (Efeito Vagão / Visão de Exposição)": "Contract (Wagon Effect / Exposure View)",
    "Evolução Default - {}": "Default Evolution - {}",
    "#### Detalhamento FPD ({})": "#### FPD Breakdown ({})",
    "Inadimplência (Num)": "Default (Num)",
    "Exposição (Denom)": "Exposure (Denom)",
    "FPD (%)": "FPD (%)",
    "SPD (%)": "SPD (%)",
    "TDP (%)": "TDP (%)",
    
    # Aba Perda Over
    "FPD vs Perda (Over {})": "FPD vs Loss (Over {})",
    "Over {} (Maturada)": "Over {} (Matured)",
    "Over {} (Diluída)": "Over {} (Diluted)",
    "Over {} (%)": "Over {} (%)",
    "Over {} (Diluído) (%)": "Over {} (Diluted) (%)",
    "#### Detalhamento: FPD vs Perda (Over {})": "#### Breakdown: FPD vs Loss (Over {})",
    "Perda {} Maturada (%)": "Loss {} Matured (%)",
    "Inadimplência Maturada (Num)": "Matured Default (Num)",
    "Exposição Maturada (Denom)": "Matured Exposure (Denom)",
    "Perda {} Diluída (%)": "Loss {} Diluted (%)",
    "Inadimplência Total (Num)": "Total Default (Num)",
    "Exposição Total (Denom)": "Total Exposure (Denom)",
    
    # Aba Collection
    "Curvas de Collection por Safra": "Collection Curves by Vintage",
    "💡 Utiliza o **VALOR_PAGO** no Numerador (Caixa Real). Denominador soma o que venceu + pré-pagamentos aprovados na curva.": "💡 Uses **PAID_VALUE** in the Numerator (Real Cash). Denominator sums what has matured + approved prepayments on the curve.",
    "Collection (%)": "Collection (%)",
    
    # Aba PAR
    "Curvas de Portfolio at Risk (PAR > {} Dias)": "Portfolio at Risk Curves (PAR > {} Days)",
    "O PAR (Portfolio at Risk) responde à pergunta: ***De todo o valor nominal (Face) esperado numa Safra, qual é a proporção do Saldo Devedor que está comprometida por contratos em atraso?***": "PAR (Portfolio at Risk) answers the question: ***Of the total nominal value (Face) expected in a Vintage, what proportion of the Outstanding Balance is compromised by overdue contracts?***",
    "💡 **Regra do Cálculo (Consistência Nominal):** O denominador agora é a soma de todas as Face_Parcelas da safra. Se naquela foto específica o contrato tinha ao menos uma parcela com mais de **{} dias de atraso**, todo o saldo devedor restante é contabilizado como 'Em Risco'.": "💡 **Calculation Rule (Nominal Consistency):** The denominator is now the sum of all Face_Installments of the vintage. If in that specific snapshot the contract had at least one installment more than **{} days overdue**, all remaining outstanding balance is accounted as 'At Risk'.",
    "⚠️ **Atenção:** O cálculo do PAR Vintage constrói matrizes cruzadas mensais e exige um processamento pesado do computador. Clique no botão abaixo apenas quando quiser calcular os resultados após aplicar seus filtros.": "⚠️ **Attention:** The Vintage PAR calculation builds monthly cross matrices and requires heavy computer processing. Click the button below only when you want to calculate the results after applying your filters.",
    "🚀 Calcular PAR (Vintage)": "🚀 Calculate PAR (Vintage)",
    "Construindo matrizes mensais de vintage... Isso pode levar alguns segundos dependendo do tamanho da base.": "Building monthly vintage matrices... This may take a few seconds depending on the database size.",
    "Evolução do PAR > {} Dias por Safra (Soma Face)": "Evolution of PAR > {} Days by Vintage (Sum Face)",
    "Month on Book (MOB)": "Month on Book (MOB)",
    "PAR (%)": "PAR (%)",
    "#### Tabela de Evolução: PAR (%) vs Month on Book (MOB)": "#### Evolution Table: PAR (%) vs Month on Book (MOB)",
    "Não foi possível gerar a análise de PAR. Certifique-se de ter os IDs de contrato, Valores de Parcela e Datas preenchidos na base.": "Could not generate PAR analysis. Make sure you have Contract IDs, Installment Values, and Dates filled in the database.",
    
    # Aba Aging
    "Análise de Aging da Carteira": "Portfolio Aging Analysis",
    "Distribuição do **Saldo Devedor** por faixa de atraso na fotografia da Data de Referência.": "Distribution of **Outstanding Balance** by delay bucket in the Reference Date snapshot.",
    "Selecione a Visão do Aging:": "Select Aging View:",
    "Contrato (Efeito Vagão / Risco)": "Contract (Wagon Effect / Risk)",
    "Formato do Gráfico:": "Chart Format:",
    "Percentual (100%)": "Percentage (100%)",
    "Absoluto (R$)": "Absolute (R$)",
    "Composição de Aging por Safra - {}": "Aging Composition by Vintage - {}",
    "Saldo Devedor": "Outstanding Balance",
    "Faixa de Atraso": "Delay Bucket",
    "Proporção (%)": "Proportion (%)",
    "#### Detalhamento Financeiro (R$)": "#### Financial Breakdown (R$)",
    "#### Concentração Percentual (%)": "#### Percentage Concentration (%)",
    "Colunas de Faixa de Atraso ou Safra não encontradas.": "Delay Bucket or Vintage columns not found.",
    
    # Aba Waterfall
    "Ciclo de Vida do Pagamento (Waterfall de Originação)": "Payment Lifecycle (Origination Waterfall)",
    "Análise de **100% da carteira gerada**: rastreia o destino final de cada Real (R$) originado na Safra, separando em fatias de antecipação, pontualidade, atrasos recuperados e inadimplência em aberto.": "Analysis of **100% of the generated portfolio**: tracks the final destination of each Real (R$) originated in the Vintage, separating into slices of anticipation, punctuality, recovered delays, and open default.",
    "⚠️ **Atenção:** O cálculo do Waterfall de Originação processa a carteira inteira (linha a linha) e exige um processamento pesado do computador. Clique no botão abaixo apenas quando quiser calcular os resultados após aplicar seus filtros.": "⚠️ **Attention:** The Origination Waterfall calculation processes the entire portfolio (line by line) and requires heavy computer processing. Click the button below only when you want to calculate the results after applying your filters.",
    "🚀 Calcular Waterfall": "🚀 Calculate Waterfall",
    "Processando o ciclo de vida e fatiamento dos pagamentos... Isso pode levar alguns segundos.": "Processing lifecycle and payment slicing... This may take a few seconds.",
    "Comportamento de Pagamento (Fatiamento Total da Safra)": "Payment Behavior (Total Vintage Slicing)",
    "Status do Componente": "Component Status",
    "Composição da Safra (%)": "Vintage Composition (%)",
    "Volume Alocado (R$)": "Allocated Volume (R$)",
    "#### Matriz do Ciclo de Liquidação (R$)": "#### Liquidation Cycle Matrix (R$)",
    "➔ TOTAL GERAL": "➔ GRAND TOTAL",
    "Volume Total Alocado": "Total Allocated Volume",
    "Volume Nominal Original (Referência)": "Original Nominal Volume (Reference)",
    "Dados de Vencimento e Safra ausentes para gerar o Waterfall.": "Due Date and Vintage data missing to generate the Waterfall.",
    
    # Aba Roll Rate
    "Análise de Roll Rate (Rolagem de Atraso)": "Roll Rate Analysis (Delay Rollover)",
    "Avalia a migração do saldo devedor (Efeito Vagão) entre as faixas de atraso de um mês para o outro.": "Evaluates the migration of outstanding balance (Wagon Effect) between delay buckets from one month to the next.",
    "⚠️ **Atenção:** O cálculo histórico de Roll Rate constrói fotos retroativas dinâmicas. Clique no botão abaixo para executar.": "⚠️ **Attention:** The historical Roll Rate calculation builds dynamic retroactive snapshots. Click the button below to run.",
    "Meses de Histórico para Tendência:": "Historical Months for Trend:",
    "🚀 Calcular Roll Rate Híbrido": "🚀 Calculate Hybrid Roll Rate",
    "Construindo a máquina do tempo para os últimos {} meses...": "Building the time machine for the last {} months...",
    "Tipo de Rolagem": "Rollover Type",
    "Mês de Destino da Rolagem": "Destination Rollover Month",
    "Matriz de Transição Exata (Último Fechamento)": "Exact Transition Matrix (Last Closing)",
    "Não há dados de histórico suficientes.": "Not enough historical data.",
    
    # Aba Concentração
    "Análise de Perfil e Concentração da Carteira": "Portfolio Profile and Concentration Analysis",
    "Exposição Total (Saldo Devedor)": "Total Exposure (Outstanding Balance)",
    "Ticket Médio por Cliente": "Average Ticket per Client",
    "Concentração Top 10 Clientes": "Top 10 Clients Concentration",
    "Concentração por Setor": "Concentration by Sector",
    "Qualidade de Crédito (Rating)": "Credit Quality (Rating)",
    "Distribuição Geográfica": "Geographic Distribution",
    "Top 10 Maiores Devedores": "Top 10 Largest Debtors",
    "%_Carteira": "%_Portfolio",
    "Erro ao carregar dados. Verifique o arquivo.": "Error loading data. Check the file.",
    "Erro ao processar o arquivo: {}": "Error processing file: {}",
    
    # Buckets & Categorias 
    "A Vencer / Em Dia": "Current / Up to Date",
    "1-30 Dias": "1-30 Days",
    "31-60 Dias": "31-60 Days",
    "61-90 Dias": "61-90 Days",
    "91-120 Dias": "91-120 Days",
    "121-150 Dias": "121-150 Days",
    "151-180 Dias": "151-180 Days",
    "181-360 Dias": "181-360 Days",
    "> 360 Dias": "> 360 Days",
    "Liquidado": "Settled",
    "Novo Atraso (Em Dia ➔ 1-30)": "New Delay (Current ➔ 1-30)",
    "Roll 30 ➔ 60 Dias": "Roll 30 ➔ 60 Days",
    "Roll 60 ➔ 90 Dias": "Roll 60 ➔ 90 Days",
    "Roll 90 ➔ 120 Dias": "Roll 90 ➔ 120 Days",
    "2. Pré-Pago": "2. Pre-Paid",
    "3. Pago no Vencimento": "3. Paid on Due Date",
    "4. Pago com Atraso": "4. Paid with Delay",
    "5. Vencido / Em Aberto": "5. Overdue / Open",
    "1. A Vencer": "1. To Mature",
    "Antecipado > 60 Dias": "Anticipated > 60 Days",
    "Antecipado 31-60 Dias": "Anticipated 31-60 Days",
    "Antecipado 1-30 Dias": "Anticipated 1-30 Days",
    "No Vencimento": "On Due Date",
    "Atraso 1-30 Dias": "Delay 1-30 Days",
    "Atraso 31-60 Dias": "Delay 31-60 Days",
    "Atraso 61-90 Dias": "Delay 61-90 Days",
    "Atraso 91-120 Dias": "Delay 91-120 Days",
    "Atraso 121-150 Dias": "Delay 121-150 Days",
    "Atraso 151-180 Dias": "Delay 151-180 Days",
    "Atraso 181-360 Dias": "Delay 181-360 Days",
    "Atraso > 360 Dias": "Delay > 360 Days",
    "Aberto 1-30 Dias": "Open 1-30 Days",
    "Aberto 31-60 Dias": "Open 31-60 Days",
    "Aberto 61-90 Dias": "Open 61-90 Days",
    "Aberto 91-120 Dias": "Open 91-120 Days",
    "Aberto 121-150 Dias": "Open 121-150 Days",
    "Aberto 151-180 Dias": "Open 151-180 Days",
    "Aberto 181-360 Dias": "Open 181-360 Days",
    "Aberto > 360 Dias": "Open > 360 Days",
    "A Vencer": "To Mature"
}

def t(texto):
    """Função de tradução dinâmica com base no idioma selecionado"""
    if idioma == "English":
        return DICIONARIO_EN.get(texto, texto)
    return texto

# Tenta importar a biblioteca de feriados
try:
    import holidays
    br_holidays = holidays.Brazil(years=range(2010, 2035))
    feriados_br = np.array(list(br_holidays.keys()), dtype='datetime64[D]')
except ImportError:
    feriados_br = []
    st.warning(t("⚠️ Biblioteca 'holidays' não instalada. O cálculo de dias úteis ignorará feriados. Execute `pip install holidays` no terminal para máxima precisão."))


# ==========================================
# FUNÇÕES MATEMÁTICAS E TRATAMENTO
# ==========================================
def calc_xirr(cashflows, days):
    """ Função matemática blindada para calcular a TIR Anualizada (XIRR). """
    cf_days = [(c, d) for c, d in zip(cashflows, days) if c != 0]
    if not cf_days: return 0.0
    
    has_pos = any(c > 0 for c, d in cf_days)
    has_neg = any(c < 0 for c, d in cf_days)
    
    if not has_pos: return -1.0 
    if not has_neg: return 0.0  
    
    def xnpv(rate):
        if rate <= -1.0: return float('inf')
        try:
            return sum([c / (1.0 + rate)**(d / 365.0) for c, d in cf_days])
        except:
            return float('inf')

    left, right = -0.999, 1000.0
    for _ in range(100):
        mid = (left + right) / 2.0
        val_mid = xnpv(mid)
        if abs(val_mid) < 1e-5: break
        if xnpv(left) > 0:
            if val_mid > 0: left = mid
            else: right = mid
        else:
            if val_mid > 0: right = mid
            else: left = mid
    return mid

@st.cache_data
def calcular_vintage_par_otimizado(df_base, data_ref_global, dias_par=90):
    """
    Realiza uma análise de PAR (Portfolio at Risk) Vintage com Efeito Vagão.
    Refatorado com Otimização 4 (Lazy Loading), Otimização 2 (Vetorial) e Otimização 1 (Paralelismo).
    """
    # Opção 4: Filtro Agressivo - Elimina a gordura da memória mantendo só o essencial
    cols_necessarias = ['ID_CONTRATO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO', 'FACE_PARCELA', 'VALOR_PAGO', 'VALOR_CURVA_PAGAMENTO', 'SAFRA']
    cols_presentes = [c for c in cols_necessarias if c in df_base.columns]
    
    df = df_base[cols_presentes].dropna(subset=['DATA_VENCIMENTO', 'FACE_PARCELA', 'SAFRA']).copy()
    id_col = 'ID_CONTRATO'
    
    df['mes_safra'] = pd.to_datetime(df['SAFRA']).dt.to_period('M')
    data_final_analise = pd.to_datetime(data_ref_global)
    
    # Denominador: Soma de toda a FACE_PARCELA original da safra (Total Nominal Esperado)
    map_valor_originado_safra = df.groupby('mes_safra')['FACE_PARCELA'].sum()
    
    lista_safras = sorted(df['mes_safra'].unique())
    
    # Função encapsulada para processar uma safra individualmente
    def processar_safra(safra_atual):
        df_safra = df[df['mes_safra'] == safra_atual].copy()
        
        meses_analise_safra = pd.period_range(start=safra_atual, end=data_final_analise.to_period('M'), freq='M')
        if len(meses_analise_safra) == 0: 
            return pd.DataFrame()
            
        total_originado = map_valor_originado_safra.get(safra_atual, 0)
        resultados_meses = []
        
        # Opção 2: Lógica Vetorial temporal (Substitui o Produto Cartesiano pesado)
        for mes_analise in meses_analise_safra:
            data_corte_snapshot = min(mes_analise.to_timestamp(how='end'), data_final_analise)
            
            # Simula o status exato na foto daquele mês com matrizes NumPy
            pago_ate_foto = df_safra['DATA_PAGAMENTO'].notna() & (df_safra['DATA_PAGAMENTO'] <= data_corte_snapshot)
            valor_pago_foto = np.where(pago_ate_foto, df_safra['VALOR_PAGO'], 0)
            
            curva = df_safra['VALOR_CURVA_PAGAMENTO'] if 'VALOR_CURVA_PAGAMENTO' in df_safra.columns else df_safra['FACE_PARCELA']
            quitada_foto = pago_ate_foto & (valor_pago_foto >= (curva - 0.05))
            
            saldo_rem = np.where(quitada_foto, 0, np.clip(df_safra['FACE_PARCELA'] - valor_pago_foto, 0, None))
            dias_atraso = np.where(quitada_foto, 0, (data_corte_snapshot - df_safra['DATA_VENCIMENTO']).dt.days)
            
            # Gatilho de Risco
            gatilho_parcela = (saldo_rem > 0.01) & (df_safra['DATA_VENCIMENTO'] <= data_corte_snapshot) & (dias_atraso > dias_par)
            
            # Atribui temporariamente ao Dataframe para fazer Groupby agregador
            df_safra['temp_gatilho'] = gatilho_parcela
            df_safra['temp_saldo_rem'] = saldo_rem
            
            # Aplica o Efeito Vagão matematicamente consolidando o contrato
            agg_contratos = df_safra.groupby(id_col).agg(
                inadimplente=('temp_gatilho', 'any'),
                saldo_total=('temp_saldo_rem', 'sum')
            )
            
            # Soma apenas o Saldo Total dos contratos que ativaram o gatilho da inadimplência
            valor_atrasado_final = agg_contratos.loc[agg_contratos['inadimplente'], 'saldo_total'].sum()
            
            par_pct = (valor_atrasado_final / total_originado * 100) if total_originado > 0 else 0.0
            
            resultados_meses.append({
                'mes_safra': safra_atual,
                'mes_analise': mes_analise,
                'valor_atrasado_final': valor_atrasado_final,
                'Total_Originado': total_originado,
                'PAR (%)': par_pct,
                'MOB': (mes_analise - safra_atual).n
            })
            
        return pd.DataFrame(resultados_meses)

    # Opção 1: Processamento Paralelo (Distribui as Safras pelos núcleos do CPU)
    resultados_por_safra = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Mapeia e executa todas as safras simultaneamente
        resultados = executor.map(processar_safra, lista_safras)
        
        for df_res in resultados:
            if not df_res.empty:
                resultados_por_safra.append(df_res)
                
    if resultados_por_safra:
        return pd.concat(resultados_por_safra, ignore_index=True)
    return pd.DataFrame()

def get_snapshot_interno(df, dt_ref):
    """ Função auxiliar para calcular o Aging de Exposição (Contrato) em uma data histórica arbitrária """
    df_snap = df.dropna(subset=['DATA_VENCIMENTO']).copy()
    if df_snap.empty: return pd.DataFrame(columns=['ID_CONTRATO', 'MAX_ATRASO', 'SALDO_TOTAL', 'FAIXA'])
    
    pago_ate_foto = df_snap['DATA_PAGAMENTO'].notna() & (df_snap['DATA_PAGAMENTO'] <= dt_ref)
    valor_pago_foto = np.where(pago_ate_foto, df_snap['VALOR_PAGO'], 0)
    
    curva = df_snap['VALOR_CURVA_PAGAMENTO'] if 'VALOR_CURVA_PAGAMENTO' in df_snap.columns else df_snap['FACE_PARCELA']
    quitada_foto = pago_ate_foto & (valor_pago_foto >= (curva - 0.05))
    
    saldo_rem = np.where(quitada_foto, 0, np.clip(df_snap['FACE_PARCELA'] - valor_pago_foto, 0, None))
    dt_ref_ts = pd.to_datetime(dt_ref)
    dias_atraso = np.where(quitada_foto, 0, (dt_ref_ts - df_snap['DATA_VENCIMENTO']).dt.days)
    
    df_snap['SALDO_REF'] = saldo_rem
    df_snap['ATRASO_REF'] = dias_atraso
    
    # Filtra apenas o que está em aberto para o Efeito Vagão
    df_aberto = df_snap[df_snap['SALDO_REF'] > 0.01]
    if df_aberto.empty: return pd.DataFrame(columns=['ID_CONTRATO', 'MAX_ATRASO', 'SALDO_TOTAL', 'FAIXA'])
        
    agg = df_aberto.groupby('ID_CONTRATO').agg(
        MAX_ATRASO=('ATRASO_REF', 'max'),
        SALDO_TOTAL=('SALDO_REF', 'sum')
    ).reset_index()
    
    bins_aging = [-float('inf'), 0, 30, 60, 90, 120, 150, 180, 360, float('inf')]
    labels_aging = ['A Vencer / Em Dia', '1-30 Dias', '31-60 Dias', '61-90 Dias', '91-120 Dias', '121-150 Dias', '151-180 Dias', '181-360 Dias', '> 360 Dias']
    agg['FAIXA'] = pd.cut(agg['MAX_ATRASO'], bins=bins_aging, labels=labels_aging, right=True).astype(str)
    
    return agg

@st.cache_data
def calcular_roll_rate(df_base, data_ref_global, meses=6):
    """ Calcula a matriz de transição e o histórico de Rolagem. """
    dates = []
    curr_dt = pd.to_datetime(data_ref_global)
    dates.append(curr_dt)
    
    # Voltar no tempo criando o último dia dos meses anteriores
    for i in range(meses):
        curr_dt = curr_dt.replace(day=1) - pd.Timedelta(days=1)
        dates.append(curr_dt)
    dates = sorted(dates)
    
    snapshots = {}
    for d in dates:
        snapshots[d] = get_snapshot_interno(df_base, d)
        
    transitions = []
    trend_data = []
    
    for i in range(len(dates) - 1):
        dt_from = dates[i]
        dt_to = dates[i+1]
        df_from = snapshots[dt_from]
        df_to = snapshots[dt_to]
        
        if df_from.empty: continue
        
        # Merge de T0 para T1
        df_merged = pd.merge(df_from, df_to, on='ID_CONTRATO', how='left', suffixes=('_T0', '_T1'))
        
        # Se estava aberto em T0 e desapareceu em T1, foi liquidado
        df_merged['FAIXA_T1'] = df_merged['FAIXA_T1'].fillna('Liquidado')
        df_merged['SALDO_TOTAL_T1'] = df_merged['SALDO_TOTAL_T1'].fillna(0)
        
        matriz = df_merged.groupby(['FAIXA_T0', 'FAIXA_T1'])['SALDO_TOTAL_T0'].sum().reset_index()
        matriz['Periodo'] = f"{dt_from.strftime('%m/%Y')} ➔ {dt_to.strftime('%m/%Y')}"
        
        totais_t0 = matriz.groupby('FAIXA_T0')['SALDO_TOTAL_T0'].transform('sum')
        matriz['Roll_Pct'] = np.where(totais_t0 > 0, (matriz['SALDO_TOTAL_T0'] / totais_t0) * 100, 0)
        
        transitions.append(matriz)
        
        def get_rate(f_from, f_to):
            val = matriz[(matriz['FAIXA_T0'] == f_from) & (matriz['FAIXA_T1'] == f_to)]['Roll_Pct'].sum()
            return val
            
        trend_data.append({
            'Periodo_Destino': dt_to.strftime('%m/%Y'),
            'Novo Atraso (Em Dia ➔ 1-30)': get_rate('A Vencer / Em Dia', '1-30 Dias'),
            'Roll 30 ➔ 60 Dias': get_rate('1-30 Dias', '31-60 Dias'),
            'Roll 60 ➔ 90 Dias': get_rate('31-60 Dias', '61-90 Dias'),
            'Roll 90 ➔ 120 Dias': get_rate('61-90 Dias', '91-120 Dias')
        })
        
    df_trans = pd.concat(transitions, ignore_index=True) if transitions else pd.DataFrame()
    df_trend = pd.DataFrame(trend_data) if trend_data else pd.DataFrame()
    
    return df_trans, df_trend

@st.cache_data
def load_data(uploaded_file):
    """
    Módulo de Engenharia de Dados. 
    Lê o CSV ou Parquet, padroniza as colunas e aplica as regras de negócio de Curva e Feriados.
    """
    try:
        if uploaded_file.name.lower().endswith('.parquet'):
            df = pd.read_parquet(uploaded_file)
        else:
            try:
                df = pd.read_csv(uploaded_file, sep=';', low_memory=False, on_bad_lines='skip')
                if len(df.columns) == 1: raise ValueError("Separador incorreto")
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=',', low_memory=False, on_bad_lines='skip')
        
        # Padroniza todas as colunas para maiúsculo e sem espaços
        df.columns = [str(c).upper().strip() for c in df.columns]
        
        # Mapeamento Flexível e Universal
        col_map = {
            # ID Contrato
            'CCB_NUMEROCCB': 'ID_CONTRATO', 
            'PROPOSTA_ID': 'ID_CONTRATO',
            'CONTRACT_ID': 'ID_CONTRATO',
            'ID': 'ID_CONTRATO',
            
            # ID Cliente
            'CLIENT_ID': 'ID_CLIENTE',
            
            # Datas
            'DATA_AVERBACAO': 'DATA_ORIGINACAO',
            'PURCHASE_DATE': 'DATA_ORIGINACAO',
            'DATA ORIGINAÇÃO': 'DATA_ORIGINACAO',
            'DUE_DATE': 'DATA_VENCIMENTO',
            'DATA VENCIMENTO': 'DATA_VENCIMENTO',
            'PAYMENT_DATE': 'DATA_PAGAMENTO',
            'DATA PAGAMENTO': 'DATA_PAGAMENTO',
            
            # Valores e Taxas
            'VALOR_DA_PARCELA': 'FACE_PARCELA',
            'INSTALLMENT_VALUE': 'FACE_PARCELA',
            'VALOR NOMINAL PARCELA': 'FACE_PARCELA',
            'PAID_VALUE': 'VALOR_PAGO',
            'VALOR PAGO': 'VALOR_PAGO',
            'TX_JUROS_MES': 'TAXA_CONTRATO',
            'INTEREST_RATE': 'TAXA_CONTRATO',
            'TAXA CONTRATO': 'TAXA_CONTRATO',
            'PRINCIPAL_CONTRATO': 'VALOR_DESEMBOLSO',
            'TOTAL_FINANCED_VALUE': 'VALOR_DESEMBOLSO',
            'VALOR PRINCIPAL PARCELA': 'PRINCIPAL_PARCELA',
            
            # Outros
            'INSTALLMENT_ORDER': 'NUMERO_PARCELA',
            'N°PARCELA': 'NUMERO_PARCELA',
            'TIPO DE PRODUTO/ESTRATEGIA': 'TIPO_PRODUTO',
            'UF CEDENTE': 'UF_ORIGINACAO'
        }
        df.rename(columns=col_map, inplace=True)
        
        # REMOVE DUPLICADOS CRÍTICOS (Ex: se a base tinha VALOR_DESEMBOLSO e PRINCIPAL_CONTRATO juntos)
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        # Parse de Datas
        for col in ['DATA_ORIGINACAO', 'DATA_VENCIMENTO', 'DATA_PAGAMENTO']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                
        # Parse Seguro de Moedas e Taxas
        cols_financeiras = ['FACE_PARCELA', 'VALOR_PAGO', 'TAXA_CONTRATO', 'VALOR_DESEMBOLSO', 'PRINCIPAL_PARCELA']
        for col in cols_financeiras:
            if col in df.columns:
                # O "Guarda de Segurança" atualizado: se não for número nativo, limpa obrigatoriamente!
                if not pd.api.types.is_numeric_dtype(df[col]):
                    def safe_float_convert(val):
                        try:
                            if pd.isna(val): return 0.0
                            val_str = str(val).strip().replace(' ', '')
                            if not val_str: return 0.0
                            
                            # Tratamento explícito para o símbolo de porcentagem (Ex: "2%" -> 0.02)
                            is_percent = False
                            if '%' in val_str:
                                is_percent = True
                                val_str = val_str.replace('%', '')
                            
                            last_comma = val_str.rfind(',')
                            last_dot = val_str.rfind('.')
                            if last_comma > -1 and last_dot > -1:
                                if last_comma > last_dot: val_str = val_str.replace('.', '').replace(',', '.')
                                else: val_str = val_str.replace(',', '')
                            elif last_comma > -1:
                                if val_str.count(',') > 1: val_str = val_str.replace(',', '')
                                else: val_str = val_str.replace(',', '.')
                            elif last_dot > -1:
                                if val_str.count('.') > 1: val_str = val_str.replace('.', '')
                            
                            final_val = float(val_str)
                            
                            # Se encontrou o %, divide por 100 instantaneamente
                            if is_percent:
                                final_val = final_val / 100.0
                                
                            return final_val
                        except: return 0.0
                    df[col] = df[col].apply(safe_float_convert)
                df[col] = df[col].fillna(0)
            else:
                df[col] = 0.0 # Cria com zero se não existir no tape
                
        # Garante a existência do NUMERO_PARCELA limpo
        if 'NUMERO_PARCELA' in df.columns:
            if df['NUMERO_PARCELA'].dtype == object:
                df['NUMERO_PARCELA'] = df['NUMERO_PARCELA'].astype(str).str.extract(r'(\d+)', expand=False)
            df['NUMERO_PARCELA'] = pd.to_numeric(df['NUMERO_PARCELA'], errors='coerce')
            
        # ========================================================
        # SOMA SINTÉTICA DO DESEMBOLSO (Opção 2 - Otimizada)
        # ========================================================
        # Executa APENAS se a coluna estiver vazia (ausente no tape) para economizar processamento
        if 'ID_CONTRATO' in df.columns:
            if (df['VALOR_DESEMBOLSO'] == 0).all():
                if df['PRINCIPAL_PARCELA'].sum() > 0:
                    map_desembolso = df.groupby('ID_CONTRATO')['PRINCIPAL_PARCELA'].sum()
                else:
                    map_desembolso = df.groupby('ID_CONTRATO')['FACE_PARCELA'].sum()
                df['VALOR_DESEMBOLSO'] = df['ID_CONTRATO'].map(map_desembolso)
            
        # ========================================================
        # REGRAS DE NEGÓCIO E CRIAÇÃO DE CURVAS
        # ========================================================
        if 'DATA_ORIGINACAO' in df.columns:
            # 1. Safra Sintética (Ano-Mês da Originação)
            df['SAFRA'] = df['DATA_ORIGINACAO'].dt.to_period('M').dt.to_timestamp().dt.date
            
            valid_dates = df['DATA_VENCIMENTO'].notna() & df['DATA_ORIGINACAO'].notna()
            if valid_dates.any():
                orig_dates = df.loc[valid_dates, 'DATA_ORIGINACAO'].values.astype('datetime64[D]')
                venc_dates = df.loc[valid_dates, 'DATA_VENCIMENTO'].values.astype('datetime64[D]')
                
                # 2. Contagem de Dias Úteis EXATOS (Com Feriados Nacionais)
                prazo_du = np.busday_count(orig_dates, venc_dates, holidays=feriados_br)
                df['PRAZO_DU'] = np.nan
                df.loc[valid_dates, 'PRAZO_DU'] = np.clip(prazo_du, 0, None)
                
                # 3. Fallback do Valor de Aquisição da Parcela (Se a coluna vier nula/vazia)
                vp_calculado = df['FACE_PARCELA'] / ((1 + df['TAXA_CONTRATO']) ** (df['PRAZO_DU'] / 21.0))
                df['VALOR_AQUISICAO_PARCELA'] = np.where(df['PRINCIPAL_PARCELA'] > 0, df['PRINCIPAL_PARCELA'], vp_calculado)
                df['VALOR_AQUISICAO_PARCELA'] = df['VALOR_AQUISICAO_PARCELA'].fillna(0)
            else:
                df['PRAZO_DU'] = 0
                df['VALOR_AQUISICAO_PARCELA'] = 0.0
                
            # 4. Curva de Pré-Pagamento (Descapitaliza a Face_Parcela até a Data do Pagamento)
            df['VALOR_CURVA_PAGAMENTO'] = df['FACE_PARCELA']
            valid_payment = df['DATA_PAGAMENTO'].notna() & (df['DATA_PAGAMENTO'] < df['DATA_VENCIMENTO'])
            if valid_payment.any():
                pag_dates = df.loc[valid_payment, 'DATA_PAGAMENTO'].values.astype('datetime64[D]')
                venc_dates2 = df.loc[valid_payment, 'DATA_VENCIMENTO'].values.astype('datetime64[D]')
                
                du_antecipado = np.busday_count(pag_dates, venc_dates2, holidays=feriados_br)
                du_antecipado = np.clip(du_antecipado, 0, None)
                
                tx = df.loc[valid_payment, 'TAXA_CONTRATO']
                df.loc[valid_payment, 'VALOR_CURVA_PAGAMENTO'] = df.loc[valid_payment, 'FACE_PARCELA'] / ((1 + tx) ** (du_antecipado / 21.0))

        return df
    except Exception as e:
        st.error(t("Erro ao processar o arquivo: {}").format(e))
        return None

# ==========================================
# INTERFACE DO USUÁRIO (SIDEBAR)
# ==========================================
st.sidebar.title(t("📊 Upload de Dados"))
uploaded_file = st.sidebar.file_uploader(t("Faça o upload do arquivo 'Loan Tape'"), type=['csv', 'parquet'])

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None and not df.empty:
        # ------------------------------------------
        # CONFIGURAÇÃO GERAL E DA DATA DE REFERÊNCIA
        # ------------------------------------------
        st.sidebar.markdown("---")
        st.sidebar.title(t("📅 Configurações Globais"))
        
        # Padrão agora é a data de hoje (Data de acesso do usuário)
        default_date = datetime.today().date()
        
        data_input = st.sidebar.date_input(
            t("Data de Referência (Snapshot)"), 
            value=default_date,
            help=t("Corte Fotográfico: Pagamentos ocorridos APÓS esta data não existirão na simulação.")
        )
        data_referencia = pd.to_datetime(data_input)

        dias_atraso_tolerancia = st.sidebar.number_input(
            t("Tolerância FPD/SPD/TDP (Dias)"),
            min_value=0, max_value=365, value=15, step=1
        )
        
        dias_over = st.sidebar.number_input(
            t("Tolerância Perda / PAR (Dias)"),
            min_value=0, max_value=3650, value=90, step=1
        )
        
        # ---------------------------------------------------------
        # MOTOR SNAPSHOT (Aplica a foto da Data de Referência)
        # ---------------------------------------------------------
        if 'DATA_VENCIMENTO' in df.columns and 'DATA_PAGAMENTO' in df.columns:
            # Regra 1: O pagamento aconteceu até a data da foto?
            df['PAGO_ATE_REF'] = df['DATA_PAGAMENTO'].notna() & (df['DATA_PAGAMENTO'] <= data_referencia)
            
            # Regra 2: Valor efetivamente pago até a foto (se pagou depois, na foto é R$ 0)
            df['VALOR_PAGO_REF'] = np.where(df['PAGO_ATE_REF'], df['VALOR_PAGO'], 0)
            
            # Regra 3: A Parcela está Quitado na foto? (Valor pago >= Valor da curva no dia do pagamento)
            df['QUITADA_REF'] = df['PAGO_ATE_REF'] & (df['VALOR_PAGO_REF'] >= (df['VALOR_CURVA_PAGAMENTO'] - 0.05))
            
            # Regra 4: Saldo Remanescente com Piso Zero (Evita saldo negativo por multas)
            df['SALDO_REMANESCENTE_REF'] = np.where(df['QUITADA_REF'], 0, np.clip(df['FACE_PARCELA'] - df['VALOR_PAGO_REF'], 0, None))
            
            # Regra 5: Dias de Atraso Exatos na Foto
            df['DIAS_ATRASO'] = np.where(df['QUITADA_REF'], 0, (data_referencia - df['DATA_VENCIMENTO']).dt.days)
            
            # Regra 6: Indicadores Individuais de Default
            df['PARCELA_OVER'] = (df['DIAS_ATRASO'] > dias_over) & (df['SALDO_REMANESCENTE_REF'] > 0.01)
            df['IS_DEFAULT'] = (df['DIAS_ATRASO'] > dias_atraso_tolerancia) & (df['SALDO_REMANESCENTE_REF'] > 0.01)
            
            # Regra 7: Efeito Vagão (Contrato Inteiro)
            if 'ID_CONTRATO' in df.columns:
                contratos_over = df[df['PARCELA_OVER']]['ID_CONTRATO'].unique()
                df['CONTRATO_OVER'] = df['ID_CONTRATO'].isin(contratos_over)
                df['IS_OVER'] = df['CONTRATO_OVER'] & (~df['QUITADA_REF'])
            else:
                df['IS_OVER'] = df['PARCELA_OVER']
                
            df['VALOR_OVER'] = np.where(df['IS_OVER'], df['SALDO_REMANESCENTE_REF'], 0)
            
            # Regra 8: Categorização de Aging (Visão Parcela)
            bins_aging = [-float('inf'), 0, 30, 60, 90, 120, 150, 180, 360, float('inf')]
            labels_aging = ['A Vencer / Em Dia', '1-30 Dias', '31-60 Dias', '61-90 Dias', '91-120 Dias', '121-150 Dias', '151-180 Dias', '181-360 Dias', '> 360 Dias']
            df['FAIXA_AGING_PARCELA'] = pd.cut(df['DIAS_ATRASO'], bins=bins_aging, labels=labels_aging, right=True).astype(str)
            
            # Regra 9: Categorização de Aging (Visão Contrato - Efeito Vagão)
            if 'ID_CONTRATO' in df.columns:
                df['PIOR_ATRASO_CONTRATO'] = df.groupby('ID_CONTRATO')['DIAS_ATRASO'].transform('max')
                df['FAIXA_AGING_CONTRATO'] = pd.cut(df['PIOR_ATRASO_CONTRATO'], bins=bins_aging, labels=labels_aging, right=True).astype(str)
            else:
                df['FAIXA_AGING_CONTRATO'] = df['FAIXA_AGING_PARCELA']

        else:
            df['VALOR_PAGO_REF'] = 0
            df['SALDO_REMANESCENTE_REF'] = df['FACE_PARCELA']
            df['VALOR_OVER'] = 0
            df['IS_DEFAULT'] = False
            df['FAIXA_AGING_PARCELA'] = 'A Vencer / Em Dia'
            df['FAIXA_AGING_CONTRATO'] = 'A Vencer / Em Dia'

        # ------------------------------------------
        # FILTROS LIMPOS
        # ------------------------------------------
        st.sidebar.markdown("---")
        st.sidebar.title(t("🔍 Filtros de Análise"))
        
        produtos = df['TIPO_PRODUTO'].dropna().unique().tolist() if 'TIPO_PRODUTO' in df.columns else []
        safras = sorted([s for s in df['SAFRA'].unique() if pd.notnull(s)]) if 'SAFRA' in df.columns else []
        
        f_produto = st.sidebar.multiselect(t("Tipo de Produto"), produtos, default=produtos) if produtos else []
        f_safra = st.sidebar.multiselect(t("Safra"), safras, default=safras) if safras else []
        
        df_filtered = df.copy()
        if f_produto: df_filtered = df_filtered[df_filtered['TIPO_PRODUTO'].isin(f_produto)]
        if f_safra: df_filtered = df_filtered[df_filtered['SAFRA'].isin(f_safra)]

        st.title(t("📈 Análise de Risco e Rentabilidade - Institucional"))
        
        # --- CÁLCULO DINÂMICO DE VALOR PRESENTE RESIDUAL (PARA A TIR) ---
        if 'DATA_VENCIMENTO' in df_filtered.columns and 'TAXA_CONTRATO' in df_filtered.columns:
            df_filtered['Valor_Presente_Residual'] = df_filtered['SALDO_REMANESCENTE_REF'].copy()
            
            # Traz a valor presente apenas o Saldo Remanescente de parcelas futuras (que ainda vão vencer)
            mask_a_vencer = (df_filtered['DATA_VENCIMENTO'] > data_referencia) & df_filtered['DATA_VENCIMENTO'].notna() & (df_filtered['SALDO_REMANESCENTE_REF'] > 0.01)
            
            if mask_a_vencer.any():
                ref_array = np.full(mask_a_vencer.sum(), data_referencia.date(), dtype='datetime64[D]')
                venc_array = df_filtered.loc[mask_a_vencer, 'DATA_VENCIMENTO'].dt.date.values.astype('datetime64[D]')
                
                du_a_vencer = np.busday_count(ref_array, venc_array, holidays=feriados_br)
                du_a_vencer = np.clip(du_a_vencer, 0, None)
                
                tx = df_filtered.loc[mask_a_vencer, 'TAXA_CONTRATO']
                saldo_futuro = df_filtered.loc[mask_a_vencer, 'SALDO_REMANESCENTE_REF']
                df_filtered.loc[mask_a_vencer, 'Valor_Presente_Residual'] = saldo_futuro / ((1 + tx) ** (du_a_vencer / 21.0))
        else:
            df_filtered['Valor_Presente_Residual'] = df_filtered['SALDO_REMANESCENTE_REF']

        if 'VALOR_DESEMBOLSO' in df_filtered.columns and 'ID_CONTRATO' in df_filtered.columns:
            volume_originado = df_filtered.drop_duplicates('ID_CONTRATO')['VALOR_DESEMBOLSO'].sum()
            st.markdown(t("**Volume Total Originado Filtrado (Desembolso Real por Contrato):** R$ ") + f"{volume_originado:,.2f}")
        
        # Inicializa fpd_data globalmente para evitar NameError na tab3
        fpd_data = pd.DataFrame()
        
        # ==========================================
        # ABAS DO DASHBOARD
        # ==========================================
        tab_orig, tab_tir, tab_tir_pdd, tab1, tab3, tab_coll, tab_par, tab_aging, tab_waterfall, tab_rollrate, tab_concentration = st.tabs([
            t("Originação"),
            t("Análise de TIR"),
            t("TIR (Ajustada PDD)"),
            t("FPD, SPD e TDP"), 
            t("Perda Over {}").format(dias_over),
            t("Collection"),
            t("PAR (Vintage)"),
            t("Aging"),
            t("Ciclo de Pag. (Waterfall)"),
            t("Roll Rate"),
            t("Perfil e Concentração")
        ])

        # ------------------------------------------
        # TAB ORIGINAÇÃO
        # ------------------------------------------
        with tab_orig:
            st.header(t("Originação por Safra"))
            st.markdown(t("Comparativo da Soma das Parcelas Esperadas vs Valor Total Desembolsado. Taxa e Prazo são ponderados pela Exposição do Contrato."))

            if 'SAFRA' in df_filtered.columns and 'FACE_PARCELA' in df_filtered.columns:
                
                # 1. Volume Bruto e VP
                agg_orig = df_filtered.groupby('SAFRA').agg({
                    'FACE_PARCELA': 'sum',
                    'VALOR_AQUISICAO_PARCELA': 'sum'
                }).reset_index()
                
                agg_orig.rename(columns={
                    'FACE_PARCELA': 'Soma_Face_Parcela',
                    'VALOR_AQUISICAO_PARCELA': 'Soma_Aquisicao_Parcela'
                }, inplace=True)

                # 2. Médias Ponderadas via Contrato
                if 'ID_CONTRATO' in df_filtered.columns and 'VALOR_DESEMBOLSO' in df_filtered.columns:
                    agg_dict = {'VALOR_DESEMBOLSO': 'max'}
                    if 'TAXA_CONTRATO' in df_filtered.columns: agg_dict['TAXA_CONTRATO'] = 'first'
                    if 'PRAZO_DU' in df_filtered.columns: agg_dict['PRAZO_DU'] = 'max'
                        
                    df_contracts = df_filtered.groupby(['SAFRA', 'ID_CONTRATO']).agg(agg_dict).reset_index()
                    
                    if 'TAXA_CONTRATO' in df_contracts.columns:
                        df_contracts['TX_VP'] = df_contracts['TAXA_CONTRATO'] * df_contracts['VALOR_DESEMBOLSO']
                    if 'PRAZO_DU' in df_contracts.columns:
                        df_contracts['PRAZO_VP'] = df_contracts['PRAZO_DU'] * df_contracts['VALOR_DESEMBOLSO']
                        
                    agg_weights_cols = {'VALOR_DESEMBOLSO': 'sum'}
                    if 'TX_VP' in df_contracts.columns: agg_weights_cols['TX_VP'] = 'sum'
                    if 'PRAZO_VP' in df_contracts.columns: agg_weights_cols['PRAZO_VP'] = 'sum'
                    
                    agg_weights = df_contracts.groupby('SAFRA').agg(agg_weights_cols).reset_index()
                    
                    # Contagem de contratos para o ticket médio simples
                    qtd_contratos = df_contracts.groupby('SAFRA').size().reset_index(name='QTD_CONTRATOS')
                    agg_weights = agg_weights.merge(qtd_contratos, on='SAFRA', how='left')
                    
                    mask = agg_weights['VALOR_DESEMBOLSO'] > 0
                    
                    if 'TX_VP' in agg_weights.columns:
                        agg_weights['TX_MEDIA_PONDERADA'] = 0.0
                        # Multiplica por 100 para transformar o decimal (0.02) em percentual visual (2.00%)
                        agg_weights.loc[mask, 'TX_MEDIA_PONDERADA'] = (agg_weights.loc[mask, 'TX_VP'] / agg_weights.loc[mask, 'VALOR_DESEMBOLSO']) * 100.0
                        agg_orig = pd.merge(agg_orig, agg_weights[['SAFRA', 'TX_MEDIA_PONDERADA']], on='SAFRA', how='left')
                        
                    if 'PRAZO_VP' in agg_weights.columns:
                        agg_weights['PRAZO_MEDIO_PONDERADO'] = 0.0
                        agg_weights.loc[mask, 'PRAZO_MEDIO_PONDERADO'] = (agg_weights.loc[mask, 'PRAZO_VP'] / agg_weights.loc[mask, 'VALOR_DESEMBOLSO']) / 21.0
                        agg_orig = pd.merge(agg_orig, agg_weights[['SAFRA', 'PRAZO_MEDIO_PONDERADO']], on='SAFRA', how='left')

                    # Calculando o Ticket Médio Simples
                    agg_weights['TICKET_MEDIO_SIMPLES'] = 0.0
                    agg_weights.loc[mask, 'TICKET_MEDIO_SIMPLES'] = agg_weights.loc[mask, 'VALOR_DESEMBOLSO'] / agg_weights.loc[mask, 'QTD_CONTRATOS']
                    
                    agg_orig = pd.merge(agg_orig, agg_weights[['SAFRA', 'TICKET_MEDIO_SIMPLES']], on='SAFRA', how='left')

                fig_orig = go.Figure()
                fig_orig.add_trace(go.Bar(
                    x=agg_orig['SAFRA'], y=agg_orig['Soma_Face_Parcela'],
                    name=t('Soma Face Parcela (Esperado)'), marker_color='#1f77b4', yaxis='y1'
                ))
                fig_orig.add_trace(go.Bar(
                    x=agg_orig['SAFRA'], y=agg_orig['Soma_Aquisicao_Parcela'],
                    name=t('Valor Desembolsado (VP)'), marker_color='#2ca02c', yaxis='y1'
                ))
                
                if 'TX_MEDIA_PONDERADA' in agg_orig.columns:
                    fig_orig.add_trace(go.Scatter(
                        x=agg_orig['SAFRA'], y=agg_orig['TX_MEDIA_PONDERADA'],
                        name=t('Taxa Média Ponderada'), mode='lines+markers', marker_color='red', yaxis='y2'
                    ))
                if 'PRAZO_MEDIO_PONDERADO' in agg_orig.columns:
                    fig_orig.add_trace(go.Scatter(
                        x=agg_orig['SAFRA'], y=agg_orig['PRAZO_MEDIO_PONDERADO'],
                        name=t('Prazo Médio Ponderado (Meses)'), mode='lines+markers', marker_color='purple', yaxis='y3'
                    ))

                fig_orig.update_layout(
                    title=t('Comparativo de Originação, Taxa e Prazo Médio'),
                    xaxis=dict(domain=[0, 0.85]),
                    yaxis=dict(title=t('Volume (R$)')),
                    yaxis2=dict(title=t('Taxa (%)'), overlaying='y', side='right'),
                    yaxis3=dict(title=t('Prazo (Meses)'), overlaying='y', side='right', position=1, anchor='free', showgrid=False),
                    barmode='group', hovermode="x unified"
                )
                st.plotly_chart(fig_orig, use_container_width=True)

                # --- Novo Gráfico de Ticket Médio Simples ---
                if 'TICKET_MEDIO_SIMPLES' in agg_orig.columns:
                    fig_ticket = go.Figure()
                    fig_ticket.add_trace(go.Bar(
                        x=agg_orig['SAFRA'], y=agg_orig['TICKET_MEDIO_SIMPLES'],
                        name=t('Ticket Médio Simples'), marker_color='#9467bd'
                    ))
                    fig_ticket.update_layout(
                        title=t('Evolução do Ticket Médio por Safra (R$)'),
                        yaxis=dict(title=t('Valor (R$)')),
                        barmode='group', hovermode="x unified"
                    )
                    st.plotly_chart(fig_ticket, use_container_width=True)
                # ------------------------------------

                tabela_cols_rename = {'Soma_Face_Parcela': t('Total Face (Esperado)'), 'Soma_Aquisicao_Parcela': t('Total Desembolso (VP)')}
                format_dict = {t('Total Face (Esperado)'): 'R$ {:,.2f}', t('Total Desembolso (VP)'): 'R$ {:,.2f}'}
                
                if 'TX_MEDIA_PONDERADA' in agg_orig.columns:
                    tabela_cols_rename['TX_MEDIA_PONDERADA'] = t('Taxa Média (%)')
                    format_dict[t('Taxa Média (%)')] = '{:.4f}%'
                if 'PRAZO_MEDIO_PONDERADO' in agg_orig.columns:
                    tabela_cols_rename['PRAZO_MEDIO_PONDERADO'] = t('Prazo Médio (Meses)')
                    format_dict[t('Prazo Médio (Meses)')] = '{:.1f}'
                if 'TICKET_MEDIO_SIMPLES' in agg_orig.columns:
                    tabela_cols_rename['TICKET_MEDIO_SIMPLES'] = t('Ticket Médio Simples')
                    format_dict[t('Ticket Médio Simples')] = 'R$ {:,.2f}'
                
                tabela_orig = agg_orig.rename(columns=tabela_cols_rename)
                st.dataframe(tabela_orig.style.format(format_dict), use_container_width=True)

        # ------------------------------------------
        # TAB TIR (TAXA INTERNA DE RETORNO)
        # ------------------------------------------
        with tab_tir:
            st.header(t("Análise de TIR Anualizada (XIRR) por Safra"))
            st.markdown(t("""**Novo Motor de Precisão Diária e Financeira:**
* **D0 a Dn (Originação):** Saídas de caixa alocadas no dia exato da `DATA_ORIGINACAO`. Considera o `VALOR_DESEMBOLSO` único por contrato.
* **Fluxos de Entrada:** Utiliza o `VALOR_PAGO` integral (inclui os ágios de multas e juros, aumentando a rentabilidade real).
* **Fluxo Terminal:** `SALDO_REMANESCENTE` futuro descontado a Valor Presente na data da foto."""))
            
            if 'SAFRA' in df_filtered.columns and 'VALOR_DESEMBOLSO' in df_filtered.columns and 'DATA_ORIGINACAO' in df_filtered.columns:
                safras_presentes = sorted([s for s in df_filtered['SAFRA'].unique() if pd.notnull(s)])
                safras_str_list = [s.strftime('%Y-%m') for s in safras_presentes]
                
                if safras_str_list:
                    st.subheader(t("Haircut de Perda Projetada (%)"))
                    hc_df = pd.DataFrame({t('Safra'): safras_str_list, t('Haircut (%)'): [0.0] * len(safras_str_list)})
                    hc_df_edited = st.data_editor(hc_df, hide_index=True, use_container_width=True, key="hc_edit")
                    hc_dict = dict(zip(hc_df_edited[t('Safra')], hc_df_edited[t('Haircut (%)')]))
                    
                    dict_cfs, terminal_vals, tir_results = {}, {}, {}
                    
                    for safra_date, safra_str in zip(safras_presentes, safras_str_list):
                        df_s = df_filtered[df_filtered['SAFRA'] == safra_date].copy()
                        if df_s.empty: continue
                        
                        min_date = pd.to_datetime(df_s['DATA_ORIGINACAO'].min())
                        cf_series = {}
                        
                        # 1. Fluxos Negativos (Desembolsos Únicos por Contrato)
                        df_contratos = df_s.drop_duplicates(subset=['ID_CONTRATO'])
                        orig_agg = df_contratos.groupby('DATA_ORIGINACAO')['VALOR_DESEMBOLSO'].sum().reset_index()
                        
                        for _, row in orig_agg.iterrows():
                            offset_orig = (pd.to_datetime(row['DATA_ORIGINACAO']) - min_date).days
                            cf_series[offset_orig] = cf_series.get(offset_orig, 0) - row['VALOR_DESEMBOLSO']
                        
                        # 2. Fluxos Positivos (Valores Pagos Reais, incluindo multas)
                        pagos = df_s[(df_s['PAGO_ATE_REF'] == True) & (df_s['DATA_PAGAMENTO'] >= min_date)]
                        if not pagos.empty:
                            pagos_agg = pagos.groupby('DATA_PAGAMENTO')['VALOR_PAGO'].sum().reset_index()
                            for _, row in pagos_agg.iterrows():
                                offset_pag = (pd.to_datetime(row['DATA_PAGAMENTO']) - min_date).days
                                if offset_pag <= 0: offset_pag = 1 # Impede anular D0 no mesmo dia
                                cf_series[offset_pag] = cf_series.get(offset_pag, 0) + row['VALOR_PAGO']
                                
                        # 3. Fluxo Terminal a Valor Presente
                        terminal_offset = (pd.to_datetime(data_referencia) - min_date).days
                        if terminal_offset <= 0: terminal_offset = 1 
                        
                        haircut_pct = hc_dict.get(safra_str, 0.0) / 100.0
                        terminal_val = df_s['Valor_Presente_Residual'].sum() * (1.0 - haircut_pct)
                        
                        cf_series[terminal_offset] = cf_series.get(terminal_offset, 0) + terminal_val
                        terminal_vals[safra_str] = terminal_val
                        dict_cfs[safra_str] = cf_series
                    
                    df_tir = pd.DataFrame(dict_cfs).fillna(0).sort_index()
                    df_tir.index.name = 'Offset (Dias)'
                    
                    if not df_tir.empty:
                        df_tir = df_tir.reindex(range(int(df_tir.index.min()), int(df_tir.index.max()) + 1), fill_value=0)
                    
                    for safra_str in safras_str_list:
                        if safra_str in df_tir.columns:
                            tir = calc_xirr(df_tir[safra_str].values, df_tir.index.values)
                            tir_results[safra_str] = (tir * 100) if tir is not None else 0.0
                    
                    tir_df_plot = pd.DataFrame(list(tir_results.items()), columns=[t('Safra'), t('TIR Anualizada (%)')])
                    fig_tir = px.bar(tir_df_plot, x=t('Safra'), y=t('TIR Anualizada (%)'), text_auto='.2f', title=t('TIR Anualizada Real (Ref: {})').format(data_referencia.strftime("%d/%m/%Y")))
                    fig_tir.update_layout(yaxis_ticksuffix="%")
                    st.plotly_chart(fig_tir, use_container_width=True)

                    # Tabela Auxiliar de Fluxos de Caixa (Detalhe Expansível)
                    with st.expander(t("Ver Matriz de Fluxo de Caixa Diário por Safra (Offset Real)")):
                        st.info(t("💡 **Nota Explicativa:** A matriz distribui as saídas de caixa nos dias exatos das averbações. O marco zero de cada coluna é a primeira data de originação daquela Safra. A última linha exibe o Valor Terminal aplicado."))
                        
                        # Criação de um DataFrame Visual que adiciona a linha de fundo
                        df_tir_vis = df_tir.copy()
                        # Converte o index numérico para string para aceitar o texto especial
                        df_tir_vis.index = df_tir_vis.index.astype(str)
                        
                        # Aloca rigorosamente o Saldo Terminal no final de cada coluna respectiva
                        df_tir_vis.loc[t('➔ Saldo Terminal Aplicado')] = pd.Series(terminal_vals).fillna(0)
                        
                        st.dataframe(df_tir_vis.style.format("R$ {:,.2f}"), use_container_width=True)

        # ------------------------------------------
        # TAB TIR AJUSTADA POR PDD (NOVA)
        # ------------------------------------------
        with tab_tir_pdd:
            st.header(t("Análise de TIR com Provisão Granular (PDD por Efeito Vagão)"))
            st.markdown(t("""**Rigor de Risco:** Nesta visão, o provisionamento do "Valor Terminal" não é linear por Safra. 
            Aplicamos o conceito de **Efeito Vagão**: se um contrato tem qualquer parcela em atraso, a sua pior faixa contamina o saldo total do contrato (vencido e futuro)."""))
            
            if 'SAFRA' in df_filtered.columns and 'VALOR_DESEMBOLSO' in df_filtered.columns and 'FAIXA_AGING_CONTRATO' in df_filtered.columns:
                # 1. Tabela de Provisão Editável
                st.subheader(t("Configuração de PDD por Faixa de Atraso do Contrato (%)"))
                faixas_pdd = [t(f) for f in ['A Vencer / Em Dia', '1-30 Dias', '31-60 Dias', '61-90 Dias', '91-120 Dias', '121-150 Dias', '151-180 Dias', '181-360 Dias', '> 360 Dias']]
                # Valores padrão conservadores para PDD
                default_pdd = [0.5, 5.0, 15.0, 30.0, 50.0, 70.0, 85.0, 95.0, 100.0]
                
                df_pdd_input = pd.DataFrame({t('Faixa de Atraso (Pior do Contrato)'): faixas_pdd, t('Provisão (%)'): default_pdd})
                df_pdd_edited = st.data_editor(df_pdd_input, hide_index=True, use_container_width=True, key="pdd_vagao_edit")
                map_pdd = dict(zip(df_pdd_edited[t('Faixa de Atraso (Pior do Contrato)')], df_pdd_edited[t('Provisão (%)')]))
                
                # 2. Processamento por Safra
                safras_presentes = sorted([s for s in df_filtered['SAFRA'].unique() if pd.notnull(s)])
                safras_str_list = [s.strftime('%Y-%m') for s in safras_presentes]
                
                dict_cfs_pdd, terminal_vals_pdd, tir_results_pdd = {}, {}, {}
                
                for safra_date, safra_str in zip(safras_presentes, safras_str_list):
                    df_s = df_filtered[df_filtered['SAFRA'] == safra_date].copy()
                    if df_s.empty: continue
                    
                    min_date = pd.to_datetime(df_s['DATA_ORIGINACAO'].min())
                    cf_series = {}
                    
                    # A. Saídas (Desembolsos Únicos por Contrato)
                    df_contratos = df_s.drop_duplicates(subset=['ID_CONTRATO'])
                    orig_agg = df_contratos.groupby('DATA_ORIGINACAO')['VALOR_DESEMBOLSO'].sum().reset_index()
                    for _, row in orig_agg.iterrows():
                        offset = (pd.to_datetime(row['DATA_ORIGINACAO']) - min_date).days
                        cf_series[offset] = cf_series.get(offset, 0) - row['VALOR_DESEMBOLSO']
                    
                    # B. Entradas Reais (Pagamentos feitos até a foto)
                    pagos = df_s[(df_s['PAGO_ATE_REF'] == True) & (df_s['DATA_PAGAMENTO'] >= min_date)]
                    if not pagos.empty:
                        pagos_agg = pagos.groupby('DATA_PAGAMENTO')['VALOR_PAGO'].sum().reset_index()
                        for _, row in pagos_agg.iterrows():
                            offset = (pd.to_datetime(row['DATA_PAGAMENTO']) - min_date).days
                            if offset <= 0: offset = 1
                            cf_series[offset] = cf_series.get(offset, 0) + row['VALOR_PAGO']
                    
                    # C. Valor Terminal Ajustado (Efeito Vagão + PDD)
                    # Usamos a FAIXA_AGING_CONTRATO que já considera o pior atraso de cada contrato
                    df_s['PDD_Factor'] = df_s['FAIXA_AGING_CONTRATO'].apply(t).map(map_pdd).fillna(100.0) / 100.0
                    df_s['VP_Recuperavel'] = df_s['Valor_Presente_Residual'] * (1.0 - df_s['PDD_Factor'])
                    
                    terminal_val = df_s['VP_Recuperavel'].sum()
                    terminal_offset = (pd.to_datetime(data_referencia) - min_date).days
                    if terminal_offset <= 0: terminal_offset = 1
                    
                    cf_series[terminal_offset] = cf_series.get(terminal_offset, 0) + terminal_val
                    terminal_vals_pdd[safra_str] = terminal_val
                    dict_cfs_pdd[safra_str] = cf_series

                # 3. Cálculo da TIR PDD
                df_tir_pdd = pd.DataFrame(dict_cfs_pdd).fillna(0).sort_index()
                if not df_tir_pdd.empty:
                    df_tir_pdd = df_tir_pdd.reindex(range(int(df_tir_pdd.index.min()), int(df_tir_pdd.index.max()) + 1), fill_value=0)
                    for s_str in safras_str_list:
                        if s_str in df_tir_pdd.columns:
                            tir = calc_xirr(df_tir_pdd[s_str].values, df_tir_pdd.index.values)
                            tir_results_pdd[s_str] = (tir * 100) if tir is not None else 0.0
                
                # Exibição Visual
                col_kpi1, col_kpi2 = st.columns(2)
                with col_kpi1:
                    tir_df_plot_pdd = pd.DataFrame(list(tir_results_pdd.items()), columns=[t('Safra'), t('TIR (Ajustada PDD) %')])
                    fig_tir_pdd = px.bar(tir_df_plot_pdd, x=t('Safra'), y=t('TIR (Ajustada PDD) %'), text_auto='.2f', 
                                        title=t('TIR Anualizada Pós-PDD (Efeito Vagão)'))
                    fig_tir_pdd.update_layout(yaxis_ticksuffix="%")
                    st.plotly_chart(fig_tir_pdd, use_container_width=True)
                
                with col_kpi2:
                    st.subheader(t("Auditabilidade de Valor Terminal"))
                    st.info(t("💡 Este valor representa o montante que o fundo espera recuperar do saldo devedor atual, já descontando as perdas estimadas por atraso (PDD)."))
                    audit_pdd = pd.DataFrame(list(terminal_vals_pdd.items()), columns=[t('Safra'), t('Valor de Recuperação Esperada (R$)')])
                    st.table(audit_pdd.style.format({t('Valor de Recuperação Esperada (R$)'): '{:,.2f}'}))
                
                with st.expander(t("Ver Matriz de Fluxos de Caixa (Provisão Vagão)")):
                    df_vis_pdd = df_tir_pdd.copy()
                    df_vis_pdd.index = df_vis_pdd.index.astype(str)
                    df_vis_pdd.loc[t('➔ Valor Final Ajustado (PDD)')] = pd.Series(terminal_vals_pdd).fillna(0)
                    st.dataframe(df_vis_pdd.style.format("R$ {:,.2f}"), use_container_width=True)

        # ------------------------------------------
        # TAB FPD, SPD, TDP
        # ------------------------------------------
        with tab1:
            st.header(t("Análise de FPD, SPD e TDP por Safra"))
            visao_pd = st.radio(t("Selecione a Visão:"), [t("Parcela (Visão de Fluxo/Caixa)"), t("Contrato (Efeito Vagão / Visão de Exposição)")], horizontal=True)
            if 'NUMERO_PARCELA' in df_filtered.columns:
                def calc_pd(dataframe, parcela, visao):
                    df_parc = dataframe[(dataframe['NUMERO_PARCELA'] == parcela) & (dataframe['DATA_VENCIMENTO'] <= data_referencia)].copy()
                    if visao == t("Contrato (Efeito Vagão / Visão de Exposição)"):
                        map_val = df_filtered.groupby('ID_CONTRATO')['FACE_PARCELA'].sum()
                        df_parc['VALOR_BASE'] = df_parc['ID_CONTRATO'].map(map_val)
                        df_parc['VALOR_INAD'] = np.where(df_parc['IS_DEFAULT'], df_parc['VALOR_BASE'], 0)
                    else:
                        df_parc['VALOR_BASE'] = df_parc['FACE_PARCELA']
                        df_parc['VALOR_INAD'] = np.where(df_parc['IS_DEFAULT'], df_parc['SALDO_REMANESCENTE_REF'], 0)
                    agg = df_parc.groupby('SAFRA').agg(Total_Esperado=('VALOR_BASE', 'sum'), Total_Inadimplente=('VALOR_INAD', 'sum')).reset_index()
                    agg['Taxa (%)'] = np.where(agg['Total_Esperado'] > 0, (agg['Total_Inadimplente'] / agg['Total_Esperado']) * 100, 0)
                    return agg
                
                # Restaurado o cálculo do FPD, SPD e TDP completos
                fpd_data = calc_pd(df_filtered, 1, visao_pd)
                spd_data = calc_pd(df_filtered, 2, visao_pd)
                tdp_data = calc_pd(df_filtered, 3, visao_pd)
                
                pd_merged = pd.DataFrame({'SAFRA': fpd_data['SAFRA']})
                pd_merged = pd_merged.merge(fpd_data[['SAFRA', 'Taxa (%)']].rename(columns={'Taxa (%)': t('FPD (%)')}), on='SAFRA', how='left')
                pd_merged = pd_merged.merge(spd_data[['SAFRA', 'Taxa (%)']].rename(columns={'Taxa (%)': t('SPD (%)')}), on='SAFRA', how='left')
                pd_merged = pd_merged.merge(tdp_data[['SAFRA', 'Taxa (%)']].rename(columns={'Taxa (%)': t('TDP (%)')}), on='SAFRA', how='left')
                
                fig_pd = px.line(pd_merged, x='SAFRA', y=[t('FPD (%)'), t('SPD (%)'), t('TDP (%)')], markers=True, title=t('Evolução Default - {}').format(visao_pd.split(" ")[0]))
                st.plotly_chart(fig_pd, use_container_width=True)
                
                st.write(t("#### Detalhamento FPD ({})").format(visao_pd.split(' ')[0]))
                st.dataframe(fpd_data.rename(columns={'Total_Inadimplente': t('Inadimplência (Num)'), 'Total_Esperado': t('Exposição (Denom)'), 'Taxa (%)': t('FPD (%)')}).style.format({t('Inadimplência (Num)'): 'R$ {:,.2f}', t('Exposição (Denom)'): 'R$ {:,.2f}', t('FPD (%)'): '{:.2f}%'}), use_container_width=True)

        # ------------------------------------------
        # TAB PERDA OVER X
        # ------------------------------------------
        with tab3:
            st.header(t("FPD vs Perda (Over {})").format(dias_over))
            if 'SAFRA' in df_filtered.columns:
                df_over_eligible = df_filtered[(data_referencia - df_filtered['DATA_VENCIMENTO']).dt.days >= dias_over]
                
                over_data = df_over_eligible.groupby('SAFRA').agg(Total_Volume=('FACE_PARCELA', 'sum'), Volume_Over=('VALOR_OVER', 'sum')).reset_index()
                over_data[t(f'Over {{}} (%)').format(dias_over)] = np.where(over_data['Total_Volume']>0, (over_data['Volume_Over']/over_data['Total_Volume'])*100, 0)
                
                over_data_full = df_filtered.groupby('SAFRA').agg(Total_Volume=('FACE_PARCELA', 'sum'), Volume_Over=('VALOR_OVER', 'sum')).reset_index()
                over_data_full[t(f'Over {{}} (Diluído) (%)').format(dias_over)] = np.where(over_data_full['Total_Volume']>0, (over_data_full['Volume_Over']/over_data_full['Total_Volume'])*100, 0)
                
                if not fpd_data.empty:
                    comp_over = fpd_data[['SAFRA', 'Taxa (%)']].rename(columns={'Taxa (%)': t('FPD (%)')})
                    grafico_dados = comp_over.merge(over_data[['SAFRA', t(f'Over {{}} (%)').format(dias_over)]], on='SAFRA', how='left').merge(over_data_full[['SAFRA', t(f'Over {{}} (Diluído) (%)').format(dias_over)]], on='SAFRA', how='left')
                else:
                    grafico_dados = over_data[['SAFRA', t(f'Over {{}} (%)').format(dias_over)]].copy()
                    grafico_dados[t('FPD (%)')] = 0.0
                    grafico_dados = grafico_dados.merge(over_data_full[['SAFRA', t(f'Over {{}} (Diluído) (%)').format(dias_over)]], on='SAFRA', how='left')

                fig_comp2 = go.Figure()
                fig_comp2.add_trace(go.Scatter(x=grafico_dados['SAFRA'], y=grafico_dados[t('FPD (%)')], name=t('FPD (%)'), mode='lines+markers', line=dict(color='blue', width=3)))
                fig_comp2.add_trace(go.Scatter(x=grafico_dados['SAFRA'], y=grafico_dados[t(f'Over {{}} (%)').format(dias_over)], name=t(f'Over {{}} (Maturada)').format(dias_over), mode='lines+markers', line=dict(color='red', width=3, dash='dot')))
                fig_comp2.add_trace(go.Scatter(x=grafico_dados['SAFRA'], y=grafico_dados[t(f'Over {{}} (Diluído) (%)').format(dias_over)], name=t(f'Over {{}} (Diluída)').format(dias_over), mode='lines+markers', line=dict(color='orange', width=2, dash='dash')))
                st.plotly_chart(fig_comp2, use_container_width=True)

                st.write("---")
                st.write(t("#### Detalhamento: FPD vs Perda (Over {})").format(dias_over))
                
                # Junta os valores absolutos para a tabela de detalhamento
                tabela_resumo = grafico_dados.copy()
                tabela_resumo = tabela_resumo.merge(over_data[['SAFRA', 'Volume_Over', 'Total_Volume']].rename(columns={'Volume_Over': 'Over_Maturado_Num', 'Total_Volume': 'Over_Maturado_Den'}), on='SAFRA', how='left')
                tabela_resumo = tabela_resumo.merge(over_data_full[['SAFRA', 'Volume_Over', 'Total_Volume']].rename(columns={'Volume_Over': 'Over_Diluido_Num', 'Total_Volume': 'Over_Diluido_Den'}), on='SAFRA', how='left')
                
                tabela_exibicao = tabela_resumo.rename(columns={
                    'SAFRA': t('Safra'),
                    t(f'Over {{}} (%)').format(dias_over): t(f'Perda {{}} Maturada (%)').format(dias_over),
                    'Over_Maturado_Num': t('Inadimplência Maturada (Num)'),
                    'Over_Maturado_Den': t('Exposição Maturada (Denom)'),
                    t(f'Over {{}} (Diluído) (%)').format(dias_over): t(f'Perda {{}} Diluída (%)').format(dias_over),
                    'Over_Diluido_Num': t('Inadimplência Total (Num)'),
                    'Over_Diluido_Den': t('Exposição Total (Denom)')
                })
                
                # Ordena as colunas de forma lógica
                col_order = [
                    t('Safra'), t('FPD (%)'), 
                    t('Inadimplência Maturada (Num)'), t('Exposição Maturada (Denom)'), t(f'Perda {{}} Maturada (%)').format(dias_over),
                    t('Inadimplência Total (Num)'), t('Exposição Total (Denom)'), t(f'Perda {{}} Diluída (%)').format(dias_over)
                ]
                tabela_exibicao = tabela_exibicao[col_order]
                
                # Dicionário de formatação visual
                format_dict = {
                    t('FPD (%)'): '{:.2f}%',
                    t('Inadimplência Maturada (Num)'): 'R$ {:,.2f}',
                    t('Exposição Maturada (Denom)'): 'R$ {:,.2f}',
                    t(f'Perda {{}} Maturada (%)').format(dias_over): '{:.2f}%',
                    t('Inadimplência Total (Num)'): 'R$ {:,.2f}',
                    t('Exposição Total (Denom)'): 'R$ {:,.2f}',
                    t(f'Perda {{}} Diluída (%)').format(dias_over): '{:.2f}%'
                }
                
                st.dataframe(tabela_exibicao.style.format(format_dict, na_rep="-"), use_container_width=True)

        # ------------------------------------------
        # TAB COLLECTION
        # ------------------------------------------
        with tab_coll:
            st.header(t("Curvas de Collection por Safra"))
            st.info(t("💡 Utiliza o **VALOR_PAGO** no Numerador (Caixa Real). Denominador soma o que venceu + pré-pagamentos aprovados na curva."))
            
            if 'SAFRA' in df_filtered.columns:
                df_c = df_filtered.copy()
                df_c['SAFRA_DT'] = pd.to_datetime(df_c['SAFRA'])
                
                df_c['MOB_VENC'] = (df_c['DATA_VENCIMENTO'].dt.year - df_c['SAFRA_DT'].dt.year)*12 + (df_c['DATA_VENCIMENTO'].dt.month - df_c['SAFRA_DT'].dt.month)
                df_c['MOB_PAG'] = np.where(df_c['PAGO_ATE_REF'], (df_c['DATA_PAGAMENTO'].dt.year - df_c['SAFRA_DT'].dt.year)*12 + (df_c['DATA_PAGAMENTO'].dt.month - df_c['SAFRA_DT'].dt.month), np.nan)
                
                safras_coll = sorted(df_c['SAFRA'].unique())
                records = []
                
                for safra in safras_coll:
                    safra_str = safra.strftime('%Y-%m')
                    df_s = df_c[df_c['SAFRA'] == safra]
                    mob_snapshot = (data_referencia.year - pd.to_datetime(safra).year)*12 + (data_referencia.month - pd.to_datetime(safra).month)
                    max_mob_venc = int(df_s['MOB_VENC'].max()) if pd.notna(df_s['MOB_VENC'].max()) else 0
                    
                    for m in range(0, min(mob_snapshot, max_mob_venc) + 1):
                        mask_venc = df_s['MOB_VENC'] <= m
                        mask_pre_pago = (df_s['MOB_VENC'] > m) & (df_s['QUITADA_REF']) & (df_s['MOB_PAG'] <= m) & (df_s['MOB_PAG'] >= 0)
                        
                        den = df_s[mask_venc | mask_pre_pago]['FACE_PARCELA'].sum()
                        num = df_s[(df_s['PAGO_ATE_REF']) & (df_s['MOB_PAG'] <= m) & (df_s['MOB_PAG'] >= 0)]['VALOR_PAGO'].sum()
                        
                        if den > 0: records.append({t('Safra'): safra_str, 'MOB': m, t('Collection (%)'): (num/den)*100})
                
                if records:
                    df_coll_plot = pd.DataFrame(records)
                    fig_coll = px.line(df_coll_plot, x='MOB', y=t('Collection (%)'), color=t('Safra'), markers=True)
                    fig_coll.update_layout(yaxis_ticksuffix="%")
                    st.plotly_chart(fig_coll, use_container_width=True)
                    
                    st.dataframe(df_coll_plot.pivot(index=t('Safra'), columns='MOB', values=t('Collection (%)')).style.format("{:.2f}%", na_rep="-"), use_container_width=True)

        # ------------------------------------------
        # TAB PAR (VINTAGE)
        # ------------------------------------------
        with tab_par:
            st.header(t("Curvas de Portfolio at Risk (PAR > {} Dias)").format(dias_over))
            st.markdown(t("O PAR (Portfolio at Risk) responde à pergunta: ***De todo o valor nominal (Face) esperado numa Safra, qual é a proporção do Saldo Devedor que está comprometida por contratos em atraso?***"))
            st.info(t("💡 **Regra do Cálculo (Consistência Nominal):** O denominador agora é a soma de todas as Face_Parcelas da safra. Se naquela foto específica o contrato tinha ao menos uma parcela com mais de **{} dias de atraso**, todo o saldo devedor restante é contabilizado como 'Em Risco'.").format(dias_over))
            
            st.warning(t("⚠️ **Atenção:** O cálculo do PAR Vintage constrói matrizes cruzadas mensais e exige um processamento pesado do computador. Clique no botão abaixo apenas quando quiser calcular os resultados após aplicar seus filtros."))
            
            if st.button(t("🚀 Calcular PAR (Vintage)"), type="primary"):
                with st.spinner(t('Construindo matrizes mensais de vintage... Isso pode levar alguns segundos dependendo do tamanho da base.')):
                    df_par_vintage = calcular_vintage_par_otimizado(df_filtered, data_referencia, dias_over)
                    
                if not df_par_vintage.empty:
                    df_par_vintage[t('Safra')] = df_par_vintage['mes_safra'].dt.strftime('%Y-%m')
                    df_par_vintage[t('PAR (%)')] = df_par_vintage['PAR (%)']
                    fig_par = px.line(df_par_vintage, x='MOB', y=t('PAR (%)'), color=t('Safra'), markers=True,
                                      title=t('Evolução do PAR > {} Dias por Safra (Soma Face)').format(dias_over))
                    fig_par.update_layout(
                        xaxis_title=t('Month on Book (MOB)'),
                        yaxis_title=t('PAR (%)'),
                        yaxis_ticksuffix="%", 
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig_par, use_container_width=True)
                    
                    st.write(t("#### Tabela de Evolução: PAR (%) vs Month on Book (MOB)"))
                    st.dataframe(df_par_vintage.pivot(index=t('Safra'), columns='MOB', values=t('PAR (%)')).style.format("{:.2f}%", na_rep="-"), use_container_width=True)
                else:
                    st.warning(t("Não foi possível gerar a análise de PAR. Certifique-se de ter os IDs de contrato, Valores de Parcela e Datas preenchidos na base."))

        # ------------------------------------------
        # TAB AGING
        # ------------------------------------------
        with tab_aging:
            st.header(t("Análise de Aging da Carteira"))
            st.markdown(t("Distribuição do **Saldo Devedor** por faixa de atraso na fotografia da Data de Referência."))

            col1, col2 = st.columns(2)
            with col1:
                visao_aging = st.radio(t("Selecione a Visão do Aging:"), [t("Contrato (Efeito Vagão / Risco)"), t("Parcela (Visão de Fluxo/Caixa)")], horizontal=True, key="radio_aging")
            with col2:
                tipo_grafico = st.radio(t("Formato do Gráfico:"), [t("Percentual (100%)"), t("Absoluto (R$)")], horizontal=True, key="radio_tipo_grafico")

            col_faixa = 'FAIXA_AGING_CONTRATO' if t("Contrato (Efeito Vagão / Risco)") == visao_aging else 'FAIXA_AGING_PARCELA'

            if 'SAFRA' in df_filtered.columns and col_faixa in df_filtered.columns:
                
                # Agrupamento base
                agg_aging = df_filtered.groupby(['SAFRA', col_faixa], observed=False)['SALDO_REMANESCENTE_REF'].sum().reset_index()
                
                # Traduz as categorias para exibição
                agg_aging[col_faixa] = agg_aging[col_faixa].apply(t)
                
                # Mapeamento de Cores Profissional
                color_map_original = {
                    'A Vencer / Em Dia': '#2ca02c', # Verde
                    '1-30 Dias': '#f1c40f',         # Amarelo
                    '31-60 Dias': '#f39c12',        # Laranja Amarelado
                    '61-90 Dias': '#e67e22',        # Laranja
                    '91-120 Dias': '#d35400',       # Laranja Escuro
                    '121-150 Dias': '#e74c3c',      # Vermelho
                    '151-180 Dias': '#c0392b',      # Vermelho Escuro
                    '181-360 Dias': '#922b21',      # Vinho
                    '> 360 Dias': '#641e16'         # Vinho muito escuro / Quase preto
                }
                color_map = {t(k): v for k, v in color_map_original.items()}

                # Gráfico de Barras Empilhadas
                fig_aging = px.bar(
                    agg_aging,
                    x='SAFRA',
                    y='SALDO_REMANESCENTE_REF',
                    color=col_faixa,
                    title=t('Composição de Aging por Safra - {}').format(visao_aging.split(" ")[0]),
                    labels={'SALDO_REMANESCENTE_REF': t('Saldo Devedor'), col_faixa: t('Faixa de Atraso'), 'SAFRA': t('Safra')},
                    color_discrete_map=color_map
                )

                if t("Percentual (100%)") == tipo_grafico:
                    fig_aging.update_layout(barmode='stack', barnorm='percent', yaxis_title=t("Proporção (%)"))
                else:
                    fig_aging.update_layout(barmode='stack', yaxis_title=t("Volume (R$)"))

                st.plotly_chart(fig_aging, use_container_width=True)

                # Construção das Tabelas de Detalhamento
                st.write("---")
                col_tab1, col_tab2 = st.columns(2)
                
                pivot_aging_abs = agg_aging.pivot(index='SAFRA', columns=col_faixa, values='SALDO_REMANESCENTE_REF').fillna(0)
                cols_order = ['A Vencer / Em Dia', '1-30 Dias', '31-60 Dias', '61-90 Dias', '91-120 Dias', '121-150 Dias', '151-180 Dias', '181-360 Dias', '> 360 Dias']
                cols_order_trad = [t(c) for c in cols_order]
                pivot_aging_abs = pivot_aging_abs[[c for c in cols_order_trad if c in pivot_aging_abs.columns]]
                pivot_aging_abs['Total Saldo'] = pivot_aging_abs.sum(axis=1)

                with col_tab1:
                    st.write(t("#### Detalhamento Financeiro (R$)"))
                    format_dict_aging = {c: 'R$ {:,.2f}' for c in pivot_aging_abs.columns}
                    st.dataframe(pivot_aging_abs.style.format(format_dict_aging), use_container_width=True)

                with col_tab2:
                    st.write(t("#### Concentração Percentual (%)"))
                    cols_present = [c for c in cols_order_trad if c in pivot_aging_abs.columns]
                    pivot_aging_pct = pivot_aging_abs[cols_present].div(pivot_aging_abs['Total Saldo'], axis=0) * 100.0
                    pivot_aging_pct = pivot_aging_pct.fillna(0)
                    
                    format_dict_aging_pct = {c: '{:.2f}%' for c in pivot_aging_pct.columns}
                    st.dataframe(pivot_aging_pct.style.format(format_dict_aging_pct), use_container_width=True)
            else:
                st.warning(t("Colunas de Faixa de Atraso ou Safra não encontradas."))

        # ------------------------------------------
        # TAB WATERFALL (CICLO DE PAGAMENTO)
        # ------------------------------------------
        with tab_waterfall:
            st.header(t("Ciclo de Vida do Pagamento (Waterfall de Originação)"))
            st.markdown(t("Análise de **100% da carteira gerada**: rastreia o destino final de cada Real (R$) originado na Safra, separando em fatias de antecipação, pontualidade, atrasos recuperados e inadimplência em aberto."))
            
            st.warning(t("⚠️ **Atenção:** O cálculo do Waterfall de Originação processa a carteira inteira (linha a linha) e exige um processamento pesado do computador. Clique no botão abaixo apenas quando quiser calcular os resultados após aplicar seus filtros."))
            
            if st.button(t("🚀 Calcular Waterfall"), type="primary", key="btn_waterfall"):
                with st.spinner(t("Processando o ciclo de vida e fatiamento dos pagamentos... Isso pode levar alguns segundos.")):
                    if 'SAFRA' in df_filtered.columns and 'DATA_VENCIMENTO' in df_filtered.columns:
                        
                        # --- PARTE 1: VALORES EFETIVAMENTE PAGOS (VALOR_PAGO_REF) ---
                        df_pago = df_filtered[df_filtered['PAGO_ATE_REF']].copy()
                        df_pago['DELTA_DIAS'] = (df_pago['DATA_PAGAMENTO'] - df_pago['DATA_VENCIMENTO']).dt.days
                        
                        # Macro Status Pagamento
                        df_pago['MACRO_STATUS'] = np.where(df_pago['DELTA_DIAS'] < 0, '2. Pré-Pago', 
                                                    np.where(df_pago['DELTA_DIAS'] == 0, '3. Pago no Vencimento', '4. Pago com Atraso'))
                        
                        # Micro Status (Buckets)
                        bins_pre = [-float('inf'), -61, -31, -1]
                        labels_pre = ['Antecipado > 60 Dias', 'Antecipado 31-60 Dias', 'Antecipado 1-30 Dias']
                        pre_micro = pd.cut(df_pago['DELTA_DIAS'], bins=bins_pre, labels=labels_pre, right=True).astype(str)
                        
                        bins_pos = [0, 30, 60, 90, 120, 150, 180, 360, float('inf')]
                        labels_pos_pago = ['Atraso 1-30 Dias', 'Atraso 31-60 Dias', 'Atraso 61-90 Dias', 'Atraso 91-120 Dias', 'Atraso 121-150 Dias', 'Atraso 151-180 Dias', 'Atraso 181-360 Dias', 'Atraso > 360 Dias']
                        pos_micro = pd.cut(df_pago['DELTA_DIAS'], bins=bins_pos, labels=labels_pos_pago, right=True).astype(str)
                        
                        df_pago['MICRO_STATUS'] = np.where(df_pago['DELTA_DIAS'] == 0, 'No Vencimento', 
                                                    np.where(df_pago['DELTA_DIAS'] < 0, pre_micro, pos_micro))
                        df_pago['VALOR_COMPONENTE'] = df_pago['VALOR_PAGO_REF']
                        
                        # --- PARTE 2: VALORES EM ABERTO (SALDO_REMANESCENTE_REF) ---
                        df_rem = df_filtered[df_filtered['SALDO_REMANESCENTE_REF'] > 0.01].copy()
                        
                        # Macro Status Aberto
                        df_rem['MACRO_STATUS'] = np.where(df_rem['DIAS_ATRASO'] > 0, '5. Vencido / Em Aberto', '1. A Vencer')
                        
                        # Micro Status (Buckets)
                        labels_pos_aberto = ['Aberto 1-30 Dias', 'Aberto 31-60 Dias', 'Aberto 61-90 Dias', 'Aberto 91-120 Dias', 'Aberto 121-150 Dias', 'Aberto 151-180 Dias', 'Aberto 181-360 Dias', 'Aberto > 360 Dias']
                        rem_micro = pd.cut(df_rem['DIAS_ATRASO'], bins=bins_pos, labels=labels_pos_aberto, right=True).astype(str)
                        df_rem['MICRO_STATUS'] = np.where(df_rem['DIAS_ATRASO'] <= 0, 'A Vencer', rem_micro)
                        df_rem['VALOR_COMPONENTE'] = df_rem['SALDO_REMANESCENTE_REF']
                        
                        # --- UNIFICAÇÃO DO WATERFALL ---
                        df_waterfall = pd.concat([
                            df_pago[['SAFRA', 'MACRO_STATUS', 'MICRO_STATUS', 'VALOR_COMPONENTE']],
                            df_rem[['SAFRA', 'MACRO_STATUS', 'MICRO_STATUS', 'VALOR_COMPONENTE']]
                        ])
                        
                        agg_waterfall = df_waterfall.groupby(['SAFRA', 'MACRO_STATUS', 'MICRO_STATUS'])['VALOR_COMPONENTE'].sum().reset_index()
                        
                        # Tradução das labels na UI
                        agg_waterfall['MICRO_STATUS'] = agg_waterfall['MICRO_STATUS'].apply(t)
                        agg_waterfall['MACRO_STATUS'] = agg_waterfall['MACRO_STATUS'].apply(t)
                        
                        # Mapa de Cores Semântico e Lógico
                        color_map_waterfall = {
                            'A Vencer': '#bdc3c7',                      # Cinza
                            'Antecipado > 60 Dias': '#196f3d',          # Verde Muito Escuro
                            'Antecipado 31-60 Dias': '#229954',         # Verde Médio
                            'Antecipado 1-30 Dias': '#2ecc71',          # Verde Claro
                            'No Vencimento': '#2980b9',                 # Azul
                            'Atraso 1-30 Dias': '#f9e79f',              # Amarelo Claro
                            'Atraso 31-60 Dias': '#f5b041',             # Laranja Claro
                            'Atraso 61-90 Dias': '#eb984e',             # Laranja Médio
                            'Atraso 91-120 Dias': '#e67e22',            # Laranja Escuro
                            'Atraso 121-150 Dias': '#d35400',           # Laranja Forte
                            'Atraso 151-180 Dias': '#a04000',           # Marrom Claro
                            'Atraso 181-360 Dias': '#873600',           # Marrom Médio
                            'Atraso > 360 Dias': '#6e2c00',             # Marrom Escuro
                            'Aberto 1-30 Dias': '#f5b7b1',              # Vermelho Claro
                            'Aberto 31-60 Dias': '#f1948a',             # Vermelho Salmão
                            'Aberto 61-90 Dias': '#ec7063',             # Vermelho Médio
                            'Aberto 91-120 Dias': '#e74c3c',            # Vermelho Padrão
                            'Aberto 121-150 Dias': '#cb4335',           # Vermelho Escuro
                            'Aberto 151-180 Dias': '#b03a2e',           # Vermelho Sangue
                            'Aberto 181-360 Dias': '#943126',           # Vinho
                            'Aberto > 360 Dias': '#78281f'              # Vinho Muito Escuro
                        }
                        color_map_waterfall_trad = {t(k): v for k, v in color_map_waterfall.items()}
                        
                        ordem_micro = [
                            'A Vencer',
                            'Antecipado > 60 Dias', 'Antecipado 31-60 Dias', 'Antecipado 1-30 Dias',
                            'No Vencimento',
                            'Atraso 1-30 Dias', 'Atraso 31-60 Dias', 'Atraso 61-90 Dias', 'Atraso 91-120 Dias', 'Atraso 121-150 Dias', 'Atraso 151-180 Dias', 'Atraso 181-360 Dias', 'Atraso > 360 Dias',
                            'Aberto 1-30 Dias', 'Aberto 31-60 Dias', 'Aberto 61-90 Dias', 'Aberto 91-120 Dias', 'Aberto 121-150 Dias', 'Aberto 151-180 Dias', 'Aberto 181-360 Dias', 'Aberto > 360 Dias'
                        ]
                        ordem_micro_trad = [t(x) for x in ordem_micro]
                        
                        agg_waterfall['MICRO_STATUS'] = pd.Categorical(agg_waterfall['MICRO_STATUS'], categories=ordem_micro_trad, ordered=True)
                        agg_waterfall = agg_waterfall.sort_values(by=['SAFRA', 'MACRO_STATUS', 'MICRO_STATUS'])
                        
                        wf_tipo_grafico = st.radio(t("Formato do Gráfico:"), [t("Percentual (100%)"), t("Absoluto (R$)")], horizontal=True, key="wf_tipo_grafico")
                        
                        fig_wf = px.bar(
                            agg_waterfall,
                            x='SAFRA',
                            y='VALOR_COMPONENTE',
                            color='MICRO_STATUS',
                            title=t('Comportamento de Pagamento (Fatiamento Total da Safra)'),
                            labels={'VALOR_COMPONENTE': t('Volume'), 'MICRO_STATUS': t('Status do Componente'), 'SAFRA': t('Safra')},
                            color_discrete_map=color_map_waterfall_trad,
                            category_orders={"MICRO_STATUS": ordem_micro_trad}
                        )
                        
                        if t("Percentual (100%)") == wf_tipo_grafico:
                            fig_wf.update_layout(barmode='stack', barnorm='percent', yaxis_title=t("Composição da Safra (%)"))
                        else:
                            fig_wf.update_layout(barmode='stack', yaxis_title=t("Volume Alocado (R$)"))

                        st.plotly_chart(fig_wf, use_container_width=True)
                        
                        st.write("---")
                        st.write(t("#### Matriz do Ciclo de Liquidação (R$)"))
                        
                        pivot_wf = pd.pivot_table(
                            agg_waterfall, 
                            values='VALOR_COMPONENTE', 
                            index=['MACRO_STATUS', 'MICRO_STATUS'], 
                            columns=['SAFRA'], 
                            aggfunc='sum'
                        ).fillna(0)
                        
                        pivot_wf.loc[(t('➔ TOTAL GERAL'), t('Volume Total Alocado')), :] = pivot_wf.sum()
                        face_original = df_filtered.groupby('SAFRA')['FACE_PARCELA'].sum()
                        pivot_wf.loc[(t('➔ TOTAL GERAL'), t('Volume Nominal Original (Referência)')), :] = face_original
                        
                        st.dataframe(pivot_wf.style.format("R$ {:,.2f}"), use_container_width=True)

                    else:
                        st.warning(t("Dados de Vencimento e Safra ausentes para gerar o Waterfall."))
                        
        # ------------------------------------------
        # TAB ROLL RATE
        # ------------------------------------------
        with tab_rollrate:
            st.header(t("Análise de Roll Rate (Rolagem de Atraso)"))
            st.markdown(t("Avalia a migração do saldo devedor (Efeito Vagão) entre as faixas de atraso de um mês para o outro."))
            
            st.warning(t("⚠️ **Atenção:** O cálculo histórico de Roll Rate constrói fotos retroativas dinâmicas. Clique no botão abaixo para executar."))
            
            meses_historico = st.slider(t("Meses de Histórico para Tendência:"), min_value=1, max_value=12, value=6)
            
            if st.button(t("🚀 Calcular Roll Rate Híbrido"), type="primary", key="btn_rollrate"):
                with st.spinner(t("Construindo a máquina do tempo para os últimos {} meses...").format(meses_historico)):
                    df_trans, df_trend = calcular_roll_rate(df_filtered, data_referencia, meses=meses_historico)
                    
                    if not df_trend.empty:
                        trend_melted = df_trend.melt(id_vars='Periodo_Destino', var_name='Tipo de Rolagem', value_name='Taxa (%)')
                        trend_melted['Tipo de Rolagem'] = trend_melted['Tipo de Rolagem'].apply(t)
                        
                        fig_trend = px.line(trend_melted, x='Periodo_Destino', y='Taxa (%)', color='Tipo de Rolagem', markers=True)
                        fig_trend.update_layout(yaxis_ticksuffix="%", hovermode="x unified", xaxis_title=t("Mês de Destino da Rolagem"))
                        st.plotly_chart(fig_trend, use_container_width=True)
                        
                        st.write("---")
                        st.subheader(t("Matriz de Transição Exata (Último Fechamento)"))
                        
                        ultimo_periodo = df_trans['Periodo'].iloc[-1]
                        df_trans_last = df_trans[df_trans['Periodo'] == ultimo_periodo].copy()
                        
                        # Tradução das labels da Matriz
                        df_trans_last['FAIXA_T0'] = df_trans_last['FAIXA_T0'].apply(t)
                        df_trans_last['FAIXA_T1'] = df_trans_last['FAIXA_T1'].apply(t)
                        
                        ordem_linhas = ['A Vencer / Em Dia', '1-30 Dias', '31-60 Dias', '61-90 Dias', '91-120 Dias', '121-150 Dias', '151-180 Dias', '181-360 Dias', '> 360 Dias']
                        ordem_linhas_trad = [t(x) for x in ordem_linhas]
                        ordem_cols_trad = [t('Liquidado')] + ordem_linhas_trad
                        
                        pivot_matriz = df_trans_last.pivot(index='FAIXA_T0', columns='FAIXA_T1', values='Roll_Pct').fillna(0)
                        linhas_presentes = [x for x in ordem_linhas_trad if x in pivot_matriz.index]
                        cols_presentes = [x for x in ordem_cols_trad if x in pivot_matriz.columns]
                        pivot_matriz = pivot_matriz.loc[linhas_presentes, cols_presentes]
                        
                        st.dataframe(pivot_matriz.style.format("{:.1f}%").background_gradient(axis=1, cmap="YlOrRd"), use_container_width=True)
                    else:
                        st.warning(t("Não há dados de histórico suficientes."))

        # ------------------------------------------
        # TAB PERFIL E CONCENTRAÇÃO
        # ------------------------------------------
        with tab_concentration:
            st.header(t("Análise de Perfil e Concentração da Carteira"))
            
            total_exposure = df_filtered['SALDO_REMANESCENTE_REF'].sum()
            num_clientes = df_filtered['ID_CLIENTE'].nunique() if 'ID_CLIENTE' in df_filtered.columns else 0
            ticket_medio = total_exposure / num_clientes if num_clientes > 0 else 0
            
            if 'ID_CLIENTE' in df_filtered.columns:
                top_10_val = df_filtered.groupby('ID_CLIENTE')['SALDO_REMANESCENTE_REF'].sum().nlargest(10).sum()
                conc_top_10 = (top_10_val / total_exposure * 100) if total_exposure > 0 else 0
            else:
                conc_top_10 = 0

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(t("Exposição Total (Saldo Devedor)"), f"R$ {total_exposure:,.2f}")
            kpi2.metric(t("Ticket Médio por Cliente"), f"R$ {ticket_medio:,.2f}")
            kpi3.metric(t("Concentração Top 10 Clientes"), f"{conc_top_10:.2f}%")

            st.write("---")
            row1_col1, row1_col2 = st.columns(2)
            
            with row1_col1:
                if 'SETOR' in df_filtered.columns:
                    st.subheader(t("Concentração por Setor"))
                    agg_setor = df_filtered.groupby('SETOR')['SALDO_REMANESCENTE_REF'].sum().reset_index()
                    fig_setor = px.treemap(agg_setor, path=['SETOR'], values='SALDO_REMANESCENTE_REF', color='SALDO_REMANESCENTE_REF', color_continuous_scale='Blues')
                    st.plotly_chart(fig_setor, use_container_width=True)

            with row1_col2:
                if 'RATING' in df_filtered.columns:
                    st.subheader(t("Qualidade de Crédito (Rating)"))
                    agg_rating = df_filtered.groupby('RATING')['SALDO_REMANESCENTE_REF'].sum().reset_index().sort_values('RATING')
                    fig_rating = px.bar(agg_rating, x='RATING', y='SALDO_REMANESCENTE_REF', labels={'SALDO_REMANESCENTE_REF': t('Saldo Devedor')}, text_auto='.2s')
                    st.plotly_chart(fig_rating, use_container_width=True)

            st.write("---")
            row2_col1, row2_col2 = st.columns([0.6, 0.4])
            
            with row2_col1:
                if 'UF_ORIGINACAO' in df_filtered.columns:
                    st.subheader(t("Distribuição Geográfica"))
                    agg_uf = df_filtered.groupby('UF_ORIGINACAO')['SALDO_REMANESCENTE_REF'].sum().reset_index().sort_values('SALDO_REMANESCENTE_REF')
                    fig_uf = px.bar(agg_uf, y='UF_ORIGINACAO', x='SALDO_REMANESCENTE_REF', orientation='h', text_auto='.2s')
                    st.plotly_chart(fig_uf, use_container_width=True)

            with row2_col2:
                if 'ID_CLIENTE' in df_filtered.columns:
                    st.subheader(t("Top 10 Maiores Devedores"))
                    df_top10 = df_filtered.groupby('ID_CLIENTE')['SALDO_REMANESCENTE_REF'].sum().nlargest(10).reset_index()
                    df_top10[t('%_Carteira')] = (df_top10['SALDO_REMANESCENTE_REF'] / total_exposure * 100)
                    st.table(df_top10.rename(columns={'SALDO_REMANESCENTE_REF': t('Saldo Devedor')}).style.format({t('Saldo Devedor'): '{:,.2f}', t('%_Carteira'): '{:.2f}%'}))

    else:
        st.error(t("Erro ao carregar dados. Verifique o arquivo."))
