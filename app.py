import streamlit as st
import streamlit.components.v1 as components
import math

# ===================== Configuração =====================
st.set_page_config(
    page_title="Simulador de campo elétrico Física II",
    layout="wide"
)

# ===================== Constante =====================
K = 9.0e9  # N·m²/C²

# ===================== Funções auxiliares =====================
def sig(x, n=2):
    if x == 0:
        return 0
    return float(f"{x:.{n}g}")

def arrow_x(v):
    return r"\rightarrow" if v > 0 else r"\leftarrow"

def arrow_y(v):
    return r"\uparrow" if v > 0 else r"\downarrow"

def color_charge(q):
    if q > 0:
        return "#d62728"
    elif q < 0:
        return "#1f77b4"
    return "#111111"

def electric_field_2d(q, xq, yq, xp, yp):
    dx = xp - xq
    dy = yp - yq
    r = math.hypot(dx, dy)
    Ex = K * q * dx / r**3
    Ey = K * q * dy / r**3
    E = math.hypot(Ex, Ey)
    theta = math.degrees(math.atan2(Ey, Ex))
    return Ex, Ey, E, theta, r

# ===================== Cabeçalho =====================
st.title("Simulador de campo elétrico Física II")
st.write("Verifique o campo elétrico gerado por partículas carregadas em um ponto **P**.")

# ===================== Controles =====================
st.header("Definições")

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Partícula 1")
    x1 = st.slider("x₁ (m)", -10.0, 10.0, -4.0, 0.1)
    y1 = st.slider("y₁ (m)", -10.0, 10.0, 0.0, 0.1)
    q1 = st.slider("q₁ (µC)", -5.0, 5.0, 2.0, 0.05) * 1e-6

with c2:
    st.subheader("Partícula 2")
    x2 = st.slider("x₂ (m)", -10.0, 10.0, 4.0, 0.1)
    y2 = st.slider("y₂ (m)", -10.0, 10.0, 0.0, 0.1)
    q2 = st.slider("q₂ (µC)", -5.0, 5.0, -2.0, 0.05) * 1e-6

with c3:
    st.subheader("Ponto P")
    xP = st.slider("x_P (m)", -10.0, 10.0, 0.0, 0.1)
    yP = st.slider("y_P (m)", -10.0, 10.0, 2.0, 0.1)

# ===================== Física =====================
Ex1, Ey1, E1, th1, r1 = electric_field_2d(q1, x1, y1, xP, yP)
Ex2, Ey2, E2, th2, r2 = electric_field_2d(q2, x2, y2, xP, yP)

Exr = Ex1 + Ex2
Eyr = Ey1 + Ey2
Er  = math.hypot(Exr, Eyr)
thr = math.degrees(math.atan2(Eyr, Exr))

# ===================== Figura =====================
st.header("Figura – Campo elétrico no ponto P")

html = f"""
<canvas id="c" width="900" height="600"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");

function X(x) {{ return 450 + x*30; }}
function Y(y) {{ return 300 - y*30; }}

ctx.clearRect(0,0,900,600);

// eixos
ctx.strokeStyle="#aaa";
ctx.beginPath();
ctx.moveTo(0,300); ctx.lineTo(900,300);
ctx.moveTo(450,0); ctx.lineTo(450,600);
ctx.stroke();

// partículas
function particle(x,y,color,label) {{
  ctx.beginPath();
  ctx.arc(X(x),Y(y),12,0,2*Math.PI);
  ctx.fillStyle="#fafafa";
  ctx.fill();
  ctx.strokeStyle=color;
  ctx.lineWidth=3;
  ctx.stroke();
  ctx.fillStyle="#111";
  ctx.fillText(label,X(x)-4,Y(y)+4);
}}

particle({x1},{y1},"{color_charge(q1)}","1");
particle({x2},{y2},"{color_charge(q2)}","2");

// ponto P
ctx.beginPath();
ctx.arc(X({xP}),Y({yP}),5,0,2*Math.PI);
ctx.fill();
ctx.fillText("P",X({xP})+8,Y({yP})-6);

// vetores E
function vector(x,y,dx,dy,color,label) {{
  ctx.strokeStyle=color;
  ctx.lineWidth=3;
  ctx.beginPath();
  ctx.moveTo(X(x),Y(y));
  ctx.lineTo(X(x)+dx,Y(y)-dy);
  ctx.stroke();

  ctx.fillText(label,X(x)+dx+5,Y(y)-dy-5);

  ctx.setLineDash([5,5]);
  ctx.beginPath();
  ctx.moveTo(X(x),Y(y));
  ctx.lineTo(X(x)+dx,Y(y));
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(X(x)+dx,Y(y));
  ctx.lineTo(X(x)+dx,Y(y)-dy);
  ctx.stroke();
  ctx.setLineDash([]);
}}

vector({xP},{yP},{Ex1*2},{Ey1*2},"#d62728","E₁");
vector({xP},{yP},{Ex2*2},{Ey2*2},"#1f77b4","E₂");
vector({xP},{yP},{Exr*2},{Eyr*2},"#2ca02c","Eᵣ");
</script>
"""

components.html(html, height=620)

# ===================== Distâncias =====================
st.header("Distâncias")
st.latex(rf"r_1 = {sig(r1,2)}\ \mathrm{{m}}")
st.latex(rf"r_2 = {sig(r2,2)}\ \mathrm{{m}}")

# ===================== Campo elétrico =====================
st.header("Campo elétrico")
st.latex(r"E_1 = K\frac{|q_1|}{r_1^2}")
st.latex(r"E_2 = K\frac{|q_2|}{r_2^2}")

# ===================== Substituição =====================
st.header("Substituição numérica (módulos)")
st.latex(rf"E_1 = {sig(E1,2)}\ \mathrm{{N/C}}")
st.latex(rf"E_2 = {sig(E2,2)}\ \mathrm{{N/C}}")

# ===================== Resultados =====================
st.header("Resultados")

st.latex(rf"E_1x = {sig(Ex1,2)}\ {arrow_x(Ex1)} \qquad E_1y = {sig(Ey1,2)}\ {arrow_y(Ey1)}")
st.latex(rf"E_2x = {sig(Ex2,2)}\ {arrow_x(Ex2)} \qquad E_2y = {sig(Ey2,2)}\ {arrow_y(Ey2)}")
st.latex(rf"E_r = {sig(Er,2)}\ \mathrm{{N/C}}")
