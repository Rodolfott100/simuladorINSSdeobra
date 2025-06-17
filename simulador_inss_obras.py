import streamlit as st
from datetime import date

st.set_page_config(page_title="Simulador INSS de Obras", layout="centered")

st.title("Simulador de INSS de Obras")

# Tabela de percentuais de equivalência conforme IN RFB nº 2.021/2021
percentuais_equivalencia = {
    "Pilotis": 0.5,
    "Quiosque": 0.5,
    "Área aberta com churrasqueira": 0.5,
    "Terraço ou área descoberta sobre lajes": 0.5,
    "Varanda ou sacada": 0.5,
    "Caixa d’água": 0.25,
    "Casa de máquinas": 0.25,
    "Guarita ou portaria": 0.25,
    "Garagem/Estacionamento sob projeção": 0.25
}

# Percentuais para áreas complementares (fora da projeção do corpo principal)
# com opção para coberta (redução de 50%) ou descoberta (redução de 75%)
percentuais_complementares = {
    "Quadra esportiva": (0.5, 0.25),
    "Piscina": (0.5, 0.25),
    "Garagem/Estacionamento fora da projeção": (0.5, 0.25)
}

# Percentuais de equivalência por destinação principal (Manual Sero 08/2024)
percentuais_destinacao = {
    "Residencial Unifamiliar": 0.89,
    "Residencial Multifamiliar": 0.90,
    "Comercial Salas e Lojas": 0.86,
    "Edifício de Garagens": 0.86,
    "Galpão Industrial": 0.95,
    "Casa Popular": 0.98,
    "Conjunto Habitacional Popular": 0.98,
}

# Percentuais de mão de obra por tipo e material
percentuais_mao_obra = {
    "Residencial Unifamiliar": {"Alvenaria": 0.20, "Madeira": 0.15, "Mista": 0.15},
    "Residencial Multifamiliar": {"Alvenaria": 0.20, "Madeira": 0.15, "Mista": 0.15},
    "Comercial Salas e Lojas": {"Alvenaria": 0.20, "Madeira": 0.15, "Mista": 0.15},
    "Edifício de Garagens": {"Alvenaria": 0.20, "Madeira": 0.15, "Mista": 0.15},
    "Galpão Industrial": {"Alvenaria": 0.20, "Madeira": 0.15, "Mista": 0.15},
    "Casa Popular": {"Alvenaria": 0.12, "Madeira": 0.07, "Mista": 0.07},
    "Conjunto Habitacional Popular": {"Alvenaria": 0.12, "Madeira": 0.07, "Mista": 0.07},
}

# Dicionário de VAU por estado, mês e tipo de obra - dados de maio/2025
vau_por_estado = {
    "AC": {}, "AL": {}, "AP": {}, "AM": {}, "BA": {}, "CE": {}, "DF": {}, "ES": {}, "GO": {}, "MA": {}, "MT": {},
    "MS": {}, "MG": {
        "2025-05": {
            "Residencial Unifamiliar": 2903.48,
            "Residencial Multifamiliar": 2505.33,
            "Comercial Salas e Lojas": 2814.14,
            "Edifício de Garagens": 2814.14,
            "Galpão Industrial": 1241.72,
            "Casa Popular": 1614.68,
            "Conjunto Habitacional Popular": 1614.68
        }
    },
    "PA": {}, "PB": {}, "PR": {}, "PE": {}, "PI": {}, "RJ": {}, "RN": {}, "RS": {}, "RO": {}, "RR": {}, "SC": {}, "SP": {}, "SE": {}, "TO": {}
}

with st.form("form_inss"):
    st.subheader("Dados da Obra")
    tipo_obra = st.selectbox("Tipo da Obra", list(percentuais_mao_obra.keys()))
    tipo_material = st.selectbox("Tipo de Material", ["Alvenaria", "Madeira", "Mista"])

    estado = st.selectbox("Estado da obra (UF)", list(vau_por_estado.keys()))
    data_inicio = st.date_input("Data de início da obra", value=date(2023, 1, 1))
    data_fim = st.date_input("Data de conclusão da obra", value=date.today())

    area_principal = st.number_input("Área principal da obra (m²)", min_value=1.0, value=100.0)
    percentual_fixo = percentuais_destinacao.get(tipo_obra, 1.0)
    area_total_calculo = area_principal * percentual_fixo

    st.subheader("Áreas Complementares")
    area_complementar_total = 0.0
    for area, (perc_coberta, perc_descoberta) in percentuais_complementares.items():
        area_coberta = st.number_input(f"Área coberta de {area} (m²)", min_value=0.0, value=0.0)
        area_descoberta = st.number_input(f"Área descoberta de {area} (m²)", min_value=0.0, value=0.0)
        area_complementar_total += (area_coberta * perc_coberta) + (area_descoberta * perc_descoberta)

    area_total_calculo += area_complementar_total

    chave_mes = "2025-05"
    vau = vau_por_estado.get(estado, {}).get(chave_mes, {}).get(tipo_obra, 0.0)
    if vau == 0.0:
        st.warning("VAU não encontrado para esta combinação. Insira manualmente.")
        vau = st.number_input("VAU (R$/m²)", min_value=0.0, value=1500.0)

    usa_usinado = st.checkbox("Utiliza usinados/pré-moldados?", value=False)

    st.subheader("Informações Jurídicas")
    e_pf = st.checkbox("Obra registrada como Pessoa Física?", value=True)
    dctf_mensal = st.checkbox("Entrega contínua da DCTFWeb?", value=True)
    rem_corrente = st.number_input("Total de remunerações declaradas (R$)", min_value=0.0, value=80000.0)
    creditos = st.number_input("Créditos a compensar (R$)", min_value=0.0, value=0.0)

    submit = st.form_submit_button("Calcular INSS")

if submit:
    anos_conclusao = (date.today() - data_fim).days / 365
    obra_decadente = anos_conclusao > 5

    cod = vau * area_total_calculo
    if usa_usinado:
        cod *= 0.95

    percentual_mao_obra = percentuais_mao_obra[tipo_obra][tipo_material]
    rmt = cod * percentual_mao_obra

    if area_principal <= 100:
        fator_social = 0.20
    elif area_principal <= 200:
        fator_social = 0.40
    elif area_principal <= 300:
        fator_social = 0.55
    elif area_principal <= 400:
        fator_social = 0.70
    else:
        fator_social = 0.90

    base_social = cod * fator_social

    fator_ajuste_aplicado = False
    if e_pf and dctf_mensal:
        percentual_min = 0.5 if area_principal <= 350 else 0.7
        if rmt > 0 and (rem_corrente / rmt) >= percentual_min:
            fator_ajuste = 0.70
            base_ajustada = base_social * (1 - fator_ajuste)
            fator_ajuste_aplicado = True
        else:
            base_ajustada = base_social
    else:
        base_ajustada = base_social

    inss_bruto = base_ajustada * 0.20
    inss_final = max(inss_bruto - creditos, 0)
    inss_sem_ajuste = base_social * 0.20
    economia = inss_sem_ajuste - inss_bruto

    st.markdown("---")
    st.subheader("Resultado")
    st.write(f"**Área total considerada para cálculo:** {area_total_calculo:,.2f} m²")
    st.write(f"**Percentual de equivalência aplicado à área principal:** {percentual_fixo * 100:.0f}%")
    st.write(f"**Base COD:** R$ {cod:,.2f}")
    st.write(f"**Percentual de mão de obra aplicado:** {percentual_mao_obra*100:.0f}%")
    st.write(f"**RMT calculada:** R$ {rmt:,.2f}")
    st.write(f"**Fator social aplicado:** {fator_social*100:.0f}%")
    st.write(f"**Base após fator social:** R$ {base_social:,.2f}")

    if fator_ajuste_aplicado:
        st.write(f"**Fator de ajuste aplicado:** 70%")
        st.write(f"**Base final ajustada:** R$ {base_ajustada:,.2f}")
        st.write(f"**INSS sem fator de ajuste:** R$ {inss_sem_ajuste:,.2f}")
        st.write(f"**Economia estimada com fator de ajuste:** R$ {economia:,.2f}")
    else:
        st.write(f"**Fator de ajuste não aplicado**")

    st.write(f"**Créditos compensados:** R$ {creditos:,.2f}")
    st.success(f"Valor estimado do INSS devido: R$ {inss_final:,.2f}")

    if obra_decadente:
        st.warning("Obra concluída há mais de 5 anos — pode estar dentro do prazo decadente (verifique com contador).")

