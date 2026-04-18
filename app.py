import streamlit as st
import streamlit.components.v1 as components
import math

# =====================================================
# Configuração da página
# =====================================================
st.set_page_config(
    page_title="Simulador de campo elétrico Física II",
    layout="wide"
)

# =====================================================
# Constante física
# =====================================================
K = 9.0e9  # N·m²/C²

# =====================================================
# Funções auxiliares
# =====================================================
def sig(x, n=2):
    if x == 0:
        return 0.0
    return float(f"{x:.{n}g}")

def sci(x, n=2):
    if x == 0:
        return "0"
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10**exp)
    mant = float(f"{mant:.{n}g}")
    return f"{str(mant).replace('.', '{,}')}\times10^{{{exp}}}"

def latex_sci(x, unit=r"\mathrm{N/C}"):
    if x == 0:
        return rf"0\,{unit}"
    return rf"{sci(x)}\,{unit}"

def arrow_x(v):
    return r"\rightarrow" if v > 0 else r"\leftarrow"

def arrow_y(v):
    return r"\uparrow" if v > 0 else r"\downarrow"

def color_charge(q):
    return "#d62728" if q > 0 else "#1f77b4"

def electric_field(q, xq, yq, xp, yp):
    dx = xp - xq
    dy = yp - yq
    r = math.hypot(dx, dy)
    Ex = K * q * dx / r**3
    Ey = K * q * dy / r**3
    E = math.hypot(Ex, Ey)
    theta = math.degrees(math.atan2(Ey, Ex))
    return Ex, Ey, E, theta, r

# =====================================================
# Cabeçalho
# =====================================================
st.title("Simulador de campo elétrico Física II")
st.write("Verifique o campo elétrico gerado por partículas carregadas em um ponto **P**.")

# =====================================================
# Controles
# =====================================================
with st.expander("Definições (toque para abrir)", expanded=True):

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Partícula 1")
        x1 = st.slider("x₁ (m)", -10.0, 10.0, -4.0, 0.1)
        y1 = st.slider("y₁ (m)", -10.0, 10.0,  0.0, 0.1)
        q1 = st.slider("q₁ (µC)", -5.0, 5.0, 2.0, 0.05) * 1e-6

    with c2:
        st.subheader("Partícula 2")
        x2 = st.slider("x₂ (m)", -10.0, 10.0,  4.0, 0.1)
        y2 = st.slider("y₂ (m)", -10.0, 10.0,  0.0, 0.1)
        q2 = st.slider("q₂ (µC)", -5.0, 5.0, -2.0, 0.05) * 1e-6

    st.subheader("Ponto P")
    xP = st.slider("x_P (m)", -10.0, 10.0, 0.0, 0.1)
    yP = st.slider("y_P (m)", -10.0, 10.0, 2.0, 0.1)

# =====================================================
# Física
# =====================================================
Ex1, Ey1, E1, th1, r1 = electric_field(q1, x1, y1, xP, yP)
Ex2, Ey2, E2, th2, r2 = electric_field(q2, x2, y2, xP, yP)

Exr = Ex1 + Ex2
Eyr = Ey1 + Ey2
Er  = math.hypot(Exr, Eyr)
thr = math.degrees(math.atan2(Eyr, Exr))

# =====================================================
# Abas
# =====================================================
tab_fig, tab_dist, tab_subs, tab_res = st.tabs(
    ["📌 Figura", "📏 Distâncias", "🧮 Substituição numérica", "✅ Resultados"]
)

# =====================================================
# FIGURA
# =====================================================
with tab_fig:

    html = f"""
<canvas id="c" width="900" height="600" style="background:white;border:1px solid #ddd;"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");

const xMin=-15, xMax=15, yMin=-15, yMax=15;
const scale = 20;
const ox = 450, oy = 300;

function X(x){{ return ox + x*scale; }}
function Y(y){{ return oy - y*scale; }}

ctx.clearRect(0,0,900,600);

// Grade e eixos
ctx.strokeStyle="#ddd";
for(let i=-14;i<=14;i+=2){{
  ctx.beginPath(); ctx.moveTo(X(i),Y(-15)); ctx.lineTo(X(i),Y(15)); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(X(-15),Y(i)); ctx.lineTo(X(15),Y(i)); ctx.stroke();
}}

ctx.strokeStyle="#000";
ctx.lineWidth=2;
ctx.beginPath(); ctx.moveTo(X(-15),Y(0)); ctx.lineTo(X(15),Y(0)); ctx.stroke();
ctx.beginPath(); ctx.moveTo(X(0),Y(-15)); ctx.lineTo(X(0),Y(15)); ctx.stroke();

ctx.fillText("x (m)", X(14), Y(0)-10);
ctx.fillText("y (m)", X(0)+10, Y(14));

// Partículas
function particle(x,y,label,color){{
  ctx.beginPath(); ctx.arc(X(x),Y(y),14,0,2*Math.PI);
  ctx.fillStyle="#fafafa"; ctx.fill();
  ctx.strokeStyle=color; ctx.lineWidth=3; ctx.stroke();
  ctx.fillStyle="#000"; ctx.fillText(label,X(x)-4,Y(y)+4);
}}

particle({x1},{y1},"1","{color_charge(q1)}");
particle({x2},{y2},"2","{color_charge(q2)}");

// Ponto P
ctx.beginPath(); ctx.arc(X({xP}),Y({yP}),4,0,2*Math.PI); ctx.fill();
ctx.fillText("P",X({xP})+8,Y({yP})-6);

// Vetores
function vector(dx,dy,color,label){{
  const L = Math.max(Math.abs(dx),Math.abs(dy),1e-6);
  const s = 80/L;
  dx*=s; dy*=s;

  ctx.strokeStyle=color; ctx.lineWidth=3;
  ctx.beginPath(); ctx.moveTo(X({xP}),Y({yP}));
  ctx.lineTo(X({xP})+dx,Y({yP})-dy); ctx.stroke();

  ctx.fillText(label,X({xP})+dx+6,Y({yP})-dy-6);

  ctx.setLineDash([5,5]);
  ctx.beginPath(); ctx.moveTo(X({xP}),Y({yP}));
  ctx.lineTo(X({xP})+dx,Y({yP})); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(X({xP})+dx,Y({yP}));
  ctx.lineTo(X({xP})+dx,Y({yP})-dy); ctx.stroke();
  ctx.setLineDash([]);
}}

vector({Ex1},{Ey1},"#d62728","E₁");
vector({Ex2},{Ey2},"#1f77b4","E₂");
vector({Exr},{Eyr},"#2ca02c","Eᵣ");
</script>
"""
    components.html(html, height=620)

# =====================================================
# DISTÂNCIAS
# =====================================================
with tab_dist:
    st.latex(rf"r_1 = {latex_sci(r1, r'\mathrm{{m}}')}")
    st.latex(rf"r_2 = {latex_sci(r2, r'\mathrm{{m}}')}")

# =====================================================
# SUBSTITUIÇÃO NUMÉRICA
# =====================================================
with tab_subs:
    st.latex(r"E_1 = K\frac{|q_1|}{r_1^2}")
    st.latex(rf"E_1 = (9{{,}}0\times10^9)\frac{{|{sig(q1)}|}}{{({sig(r1)})^2}}")
    st.latex(rf"E_1 = {latex_sci(E1)}")

    st.latex(r"E_2 = K\frac{|q_2|}{r_2^2}")
    st.latex(rf"E_2 = (9{{,}}0\times10^9)\frac{{|{sig(q2)}|}}{{({sig(r2)})^2}}")
    st.latex(rf"E_2 = {latex_sci(E2)}")

# =====================================================
# RESULTADOS
# =====================================================
with tab_res:
    st.latex(rf"E_1 = {latex_sci(E1)} \quad \theta_1 = {sig(th1)}^\circ")
    st.latex(rf"E_1x = {latex_sci(Ex1)} {arrow_x(Ex1)} \qquad E_1y = {latex_sci(Ey1)} {arrow_y(Ey1)}")

    st.latex(rf"E_2 = {latex_sci(E2)} \quad \theta_2 = {sig(th2)}^\circ")
    st.latex(rf"E_2x = {latex_sci(Ex2)} {arrow_x(Ex2)} \qquad E_2y = {latex_sci(Ey2)} {arrow_y(Ey2)}")

    st.latex(rf"E_r = {latex_sci(Er)} \quad \theta_r = {sig(thr)}^\circ")
    st.latex(rf"E_rx = {latex_sci(Exr)} {arrow_x(Exr)} \qquad E_ry = {latex_sci(Eyr)} {arrow_y(Eyr)}")
