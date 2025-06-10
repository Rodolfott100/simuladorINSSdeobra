import streamlit as st

st.set_page_config(page_title="Simulador INSS de Obras", layout="centered")

st.title("Simulador de INSS de Obras")

# Entradas do usuário
with st.form("form_inss"):
    st.subheader("Dados da Obra")
    area = st.number_input("Área da obra (m²)", min_value=1.0, value=100.0)
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
    cod = vau * area
    if usa_usinado:
        cod *= 0.95

    # 2. Fator social (conforme área da obra)
    if area <= 100:
        fator_social = 0.20
    elif area <= 200:
        fator_social = 0.40
    elif area <= 300:
        fator_social = 0.55
    elif area <= 400:
        fator_social = 0.70
    else:
        fator_social = 0.90

    base_social = cod * fator_social

    # 3. Fator de ajuste (condicional)
    fator_ajuste_aplicado = False
    if e_pf and dctf_mensal:
        percentual_min = 0.5 if area <= 350 else 0.7
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
    st.write(f"**Base COD:** R$ {cod:,.2f}")
    st.write(f"**Fator social aplicado:** {fator_social*100:.0f}%")
    st.write(f"**Base após fator social:** R$ {base_social:,.2f}")

    if fator_ajuste_aplicado:
        st.write(f"**Fator de ajuste aplicado:** 70%")
        st.write(f"**Base final ajustada:** R$ {base_ajustada:,.2f}")
    else:
        st.write(f"**Fator de ajuste não aplicado**")

    st.success(f"Valor estimado do INSS devido: R$ {inss:,.2f}")
