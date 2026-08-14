import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import plotly.graph_objects as go

st.title("Porosidade a partir da Permeabilidade",text_alignment='center')#'justify'
st.header('Dados do sistema',text_alignment='justify')
#entrada de dados 
ent =pd.DataFrame([{'L(m)':0.1,r'μ (N.s/m²)':0.891E-3, r'𝞺 (Kg/m³)':997, 'D (m)':0.018}])
ent =st.data_editor(ent, num_rows='dynamic', column_config={
        r'μ (N.s/m²)': st.column_config.NumberColumn(format="%.6f"),
        'D (m)':st.column_config.NumberColumn(format='%.5f')})
#variaves a ser utilisdo
A = np.pi*((ent['D (m)'].values)/2)**2
L,mu,rho,D = ent.to_numpy()[0]
#dados do esperimento
dado = pd.DataFrame({'ΔP (KPa)':[None]*5, 'Q (l/mim)':[None]*5})
st.header('Valor de entrada da diferença de pressão e vazão')
dado=st.data_editor(dado,num_rows='dynamic')
pr=pd.to_numeric(dado['ΔP (KPa)'].astype(str).str.replace(',','.'), errors='coerce')
q =pd.to_numeric(dado['Q (l/mim)'].astype(str).str.replace(',','.'), errors='coerce')

#organizar as contas
def pre1(x,A,B):
	return A*x + B
def pre2(x,A,B,C):
	return A*x + B*x**2 + C
#funçoes #Ajuste de curva
def ajuste1(q,pr):
	if pr.isna().any() or q.isna().any():
		st.error('Há valores não numéricos na tabela valores de entrada.')
		return None, None
	# ajsute da curva 
	x=q.to_numpy()
	y=pr.to_numpy()
	cont, _ = curve_fit(pre1,x,y)
	return cont,x,y 
def ajuste2(q,pr,c11,c12,c21,c22):
	if pr.isna().any() or q.isna().any():
		st.error('Há valores não numéricos na tabela valores de entrada.')
		return None, None
	# ajsute da curva 
	x=q.to_numpy()
	y=pr.to_numpy()
	cont, _ = curve_fit(pre2,x,y,bounds=([c11, c21, -np.inf], [c12, c22, np.inf]))
	return cont,x,y 

def grafico(x,y,fit, cons,gral):
	fig = go.Figure()
	# 3. Adiciona os pontos experimentais (Marcadores isolados)
	fig.add_trace(go.Scatter(x=x,y=y, mode='markers', name='Dados Experimentais',
		marker=dict(color='red', size=8, symbol='circle'),))
	# 4. Adiciona a curva ajustada (Linha contínua)
	if gral == 2:
		fig.add_trace(go.Scatter( x=x,y=fit, mode='lines', 
			name=f'Ajuste: ΔP = {cons[0]:.1E} Q + {cons[1]:.1E} Q² + {cons[2]:.1E}',
	        line=dict(color='blue', width=2),))
	elif gral == 1:
		fig.add_trace(go.Scatter( x=x,y=fit, mode='lines', 
			name=f'Ajuste: ΔP = {cons[0]:.2E} Q + {cons[1]:.2E}',
	        line=dict(color='blue', width=2),))
	# 5. Configuração dos eixos, títulos e estilo do gráfico
	fig.update_layout(
	    title='Ajuste da Curva de Pressão',
	    xaxis_title='Q (l/mim)',
	    yaxis_title='ΔP (KPa)',
	    template='plotly_white',  # Fundo limpo
	    hovermode='x unified',  # Exibe os valores exatos ao passar o mouse
	    legend=dict(x=0, y=1),)
	# 6. Exibição interativa no Streamlit
	return fig

#escolha o tipo de função 
selecione = st.radio('Escolha entre função do primeiro grau ou do segundo grau.',
	[r'$1º$', r'$2º$'], horizontal=True)
if selecione == r'$2º$':
	c1c2 = pd.DataFrame({f'C_1':[0,np.inf], f'C_2':[0,np.inf]})
	c1c2=st.data_editor(c1c2,num_rows='dynamic')
#botao
if st.button('calculo'):
	if selecione ==r'$2º$':
		c11,c21,c12,c22 = c1c2.to_numpy().flatten()
		cont,x,y = ajuste2(q,pr,c11,c12,c21,c22)
		c1,c2,c = cont
		c1 = c1*60E6 #comvertendo para o sitema internacional
		c2 =  c2*3.6E12
		fit= pre2(x,*cont)
		st.plotly_chart(grafico(x,y,fit,cont,2), use_container_width=True)
	#encomtra mais variaves 
		po = np.cbrt((3.0625*(rho**2)*L*c1)/(150*mu*A*A*A*c2**2))
		dp = (1.75*rho*L*(1-po))/(c2*(po**3) * A**2)
		Re = 0
		for i in x:
			Rei = (rho*i*dp)/(mu*A*(1-po))
			Re = Re + Rei
		Re = Re/len(x) 
		k=(mu*L)/(c1*A)
		kd=k/(9.86923E-13)
		#mostrao resultado
		st.header(r'$\Delta P$ = $C_1 Q$ + $C_2 Q²$ + $C$',text_alignment='justify')
		resutado = pd.DataFrame({r'$C_1$ (Pa.s/m³)':c1, r'$C_2$ (Pa.s²/m⁶)':c2,r'$R_e$':Re,
		 r'$\Phi$ ':po, r'$d_p$ (m)':dp, r'$k$ (m²)':k, r'$k$ (Darcy)':kd})
		st.table(resutado.style.format('{:.3E}'))

	elif  selecione ==r'$1º$':
		cont,x,y = ajuste1(q,pr)
		c1,c = cont
		c1 = c1*60E6
		fit= pre1(x,*cont)
		st.plotly_chart(grafico(x,y,fit,cont,1), use_container_width=True)
	#encomtra mais variaves 
		k=(mu*L)/(c1*A)
		kd = k/(9.86923E-13)
		#mostrao resultado
		st.header(r'$\Delta P$ = $C_1 Q$ + $C$',text_alignment='justify')
		resutado = pd.DataFrame({r'$C_1$ (Pa.s/m³)':[cont[0]],r'$k$ (m²)':k, r'$k$ (Darcy)':kd})
		st.table(resutado.style.format('{:.3E}'))
