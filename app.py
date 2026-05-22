import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def equacao_pressao(v, A, B):
    return A * v + B * v**2

st.title("Ajuste de Curva: $\\nabla P = A v + B v^2$")

st.subheader("Parâmetros do Sistema e do Fluido")
col1, col2, col3 = st.columns(3)
with col1:
    area = st.number_input("Área da seção (m²):", min_value=1e-6, value=1.0000, format="%.4f")
with col2:
    # Ajustado format para notação científica
    u = st.number_input("Viscosidade u (Pa.s):", value=0.0010, format="%.4e") 
with col3:
    rho = st.number_input("Densidade $\\rho$ (kg/m³):", value=1000.0, format="%.1f")

df_inicial = pd.DataFrame({
    "Vazao": [0.0, 0.0, 0.0, 0.0, 0.0],
    "Grad_P": [0.0, 0.0, 0.0, 0.0, 0.0]
})

st.write("Insira os dados:")

# Tabela configurada para mostrar notação científica
df = st.data_editor(
    df_inicial, 
    num_rows="dynamic",
    column_config={
        "Vazao": st.column_config.NumberColumn(format="%.4e"),
        "Grad_P": st.column_config.NumberColumn(format="%.4e")
    }
)

if st.button("Calcular e Gerar Gráfico"):
    df_filtrado = df[(df["Vazao"] != 0) | (df["Grad_P"] != 0)]
    
    if len(df_filtrado) < 2:
        st.error("Insira pelo menos dois pontos de dados não nulos.")
    else:
        v = df_filtrado['Vazao'] / area
        grad_P = df_filtrado['Grad_P']
        
        constantes, _ = curve_fit(equacao_pressao, v, grad_P)
        A, B = constantes
        
        k = u / A
        beta = B / rho
        k_darcy = k / 9.869233e-13
        
        st.subheader("Resultados:")
        st.write(f"**Constante A:** {A:.4e}")
        st.write(f"**Constante B:** {B:.4e}")
        st.write(f"**Permeabilidade (k):** {k:.4e} **[m²]**")
        st.write(f"**Permeabilidade (k):** {k_darcy:.4e} **[Darcy]**")
        st.write(f"**Coeficiente Beta ($\\beta$):** {beta:.4e} **[m⁻¹]**")
        
        fig, ax = plt.subplots()
        ax.scatter(v, grad_P, color="red", label="Dados Experimentais")
        
        v_linha = np.linspace(min(v), max(v), 100)
        ax.plot(v_linha, equacao_pressao(v_linha, A, B), color="blue", label="Curva Ajustada")
        
        ax.set_xlabel("Velocidade $v$ (m/s)")
        ax.set_ylabel("Gradiente de Pressão $\\nabla P$ (Pa/m)")
        ax.legend()
        ax.grid(True)
        
        st.pyplot(fig)
