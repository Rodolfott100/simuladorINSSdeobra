import streamlit as st

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

# Entradas do usuário
with st.form("form_inss"):
    st.subheader("Dados da Obra")
    area_principal = st.number_input("Área principal da obra (m²)", min_value=1.0, value=100.0)
    area_complementar = st.number_input("Área complementar (quadra, piscina, estacionamento externo, etc.) (m²)", min_value=0.0, value=0.0)

    st.markdown("### Áreas Equivalentes")
    area_equivalente_total = 0.0
    for tipo, percentual in percentuais_equivalencia.items():
        area = st.number_input(f"{tipo} (m²) — {percentual * 100:.0f}%", min_value=0.0, value=0.0, key=tipo)
        area_equivalente_total += area * percentual

    area_total = area_principal + area_complementar + area_equivalente_total

    vau = st.number_input("Valor Atualizado Unitário - VAU (R$/m²)", min_value=0.0, value=1500.0)
    usa_usinado = st.checkbox("Utiliza usinados/pré-moldados?", value=False)

    st.subheader("Informações Jurídicas")
    e_pf = st.checkbox("Obra registrada como Pessoa Física?", value=True)
    dctf_mensal = st.checkbox("Entrega contínua da DCTFWeb?", value=True)
    rem_corrente = st.number_input("Total de remunerações declaradas (R$)", min_value=0.0, value=80000.0)
    rmt = st.number_input("Remuneração estimada (RMT) da obra (R$)", min_value=0.0, value=120000.0)

    submit = st.form_submit_button("Calcular INSS")

if submit:
    # 1. Cálculo do COD (Custo da Obra Determinado)
    cod = vau * area_total
    if usa_usinado:
        cod *= 0.95

    # 2. Fator social (conforme área principal da obra)
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

    # 3. Fator de ajuste (condicional)
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

    # 4. INSS devido
    inss = base_ajustada * 0.20

    st.markdown("---")
    st.subheader("Resultado")
    st.write(f"**Área total considerada:** {area_total:,.2f} m²")
    st.write(f"**Base COD:** R$ {cod:,.2f}")
    st.write(f"**Fator social aplicado:** {fator_social*100:.0f}%")
    st.write(f"**Base após fator social:** R$ {base_social:,.2f}")

    if fator_ajuste_aplicado:
        st.write(f"**Fator de ajuste aplicado:** 70%")
        st.write(f"**Base final ajustada:** R$ {base_ajustada:,.2f}")
    else:
        st.write(f"**Fator de ajuste não aplicado**")

    st.success(f"Valor estimado do INSS devido: R$ {inss:,.2f}")
