import streamlit as st
import streamlit.components.v1 as components
import math

# ===================== Configuração =====================
st.set_page_config(page_title="Simulador de campo elétrico Física II", layout="wide")
K = 9.0e9  # N·m²/C²

# ===================== Funções auxiliares =====================
def sci_parts(x, n=2):
    if x == 0:
        return 0.0, 0
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10 ** exp)
    mant = float(f"{mant:.{n}g}")
    if abs(mant) >= 10:
        mant /= 10
        exp += 1
    return mant, exp

def latex_sci(x, n=2, unit=r"\mathrm{N/C}"):
    if x == 0:
        return rf"0\,{unit}"
    mant, exp = sci_parts(x, n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}\,{unit}"

def arrow_x(v): return r"\rightarrow" if v > 0 else r"\leftarrow"
def arrow_y(v): return r"\uparrow" if v > 0 else r"\downarrow"

def color_charge(q): return "#d62728" if q > 0 else "#1f77b4"

def electric_field(q, xq, yq, xp, yp):
    dx, dy = xp - xq, yp - yq
    r = math.hypot(dx, dy)
    Ex = K * q * dx / r**3
    Ey = K * q * dy / r**3
    E  = math.hypot(Ex, Ey)
    th = math.degrees(math.atan2(Ey, Ex))
    return Ex, Ey, E, th, r

# ===================== Cabeçalho =====================
st.title("Simulador de campo elétrico Física II")
st.write("Verifique o campo elétrico gerado por partículas carregadas em um ponto **P**.")

# ===================== Definições =====================
st.header("Definições")

c1, c2, c3 = st.columns(3)

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

with c3:
    st.subheader("Ponto P")
    xP = st.slider("xₚ (m)", -10.0, 10.0, 0.0, 0.1)
    yP = st.slider("yₚ (m)", -10.0, 10.0, 2.0, 0.1)

# ===================== Bloqueio de posições coincidentes =====================
p1 = (round(x1, 2), round(y1, 2))
p2 = (round(x2, 2), round(y2, 2))
pP = (round(xP, 2), round(yP, 2))
if len({p1, p2, pP}) < 3:
    st.error("❌ Não é permitido colocar partículas ou o ponto P na mesma posição.")
    st.stop()

# ===================== Física =====================
Ex1, Ey1, E1, th1, r1 = electric_field(q1, x1, y1, xP, yP)
Ex2, Ey2, E2, th2, r2 = electric_field(q2, x2, y2, xP, yP)
Exr, Eyr = Ex1 + Ex2, Ey1 + Ey2
Er = math.hypot(Exr, Eyr)
thr = math.degrees(math.atan2(Eyr, Exr))

# ===================== Figura =====================
st.header("Figura – Campo elétrico no ponto P")

ticks = list(range(-15, 16, 2))

html = f"""
<canvas id="c" width="900" height="600" style="background:white;border:1px solid #ddd;"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");
const scale = 20, ox = 450, oy = 300;

function X(x){{return ox + x*scale;}}
function Y(y){{return oy - y*scale;}}

ctx.clearRect(0,0,900,600);

// Grade e ticks numerados
ctx.strokeStyle="#eee";
{''.join([f'ctx.beginPath();ctx.moveTo(X({t}),Y(-15));ctx.lineTo(X({t}),Y(15));ctx.stroke();'
          f'ctx.beginPath();ctx.moveTo(X(-15),Y({t}));ctx.lineTo(X(15),Y({t}));ctx.stroke();'
          for t in ticks])}

// Eixos
ctx.strokeStyle="#000"; ctx.lineWidth=2;
ctx.beginPath(); ctx.moveTo(X(-15),Y(0)); ctx.lineTo(X(15),Y(0)); ctx.stroke();
ctx.beginPath(); ctx.moveTo(X(0),Y(-15)); ctx.lineTo(X(0),Y(15)); ctx.stroke();

// Números nos ticks
ctx.fillStyle="#000"; ctx.font="12px Arial";
{''.join([f'ctx.fillText("{t}",X({t})-6,Y(0)+14);ctx.fillText("{t}",X(0)-22,Y({t})+4);'
          for t in ticks])}

ctx.fillText("x (m)",X(14),Y(0)-10);
ctx.fillText("y (m)",X(0)+10,Y(14));

// Partículas
function particle(x,y,l,c){{
  ctx.beginPath();ctx.arc(X(x),Y(y),14,0,2*Math.PI);
  ctx.fillStyle="#fafafa";ctx.fill();
  ctx.strokeStyle=c;ctx.lineWidth=3;ctx.stroke();
  ctx.fillStyle="#000";ctx.fillText(l,X(x)-4,Y(y)+4);
}}
particle({x1},{y1},"1","{color_charge(q1)}");
particle({x2},{y2},"2","{color_charge(q2)}");

// Ponto P
ctx.beginPath();ctx.arc(X({xP}),Y({yP}),4,0,2*Math.PI);ctx.fill();
ctx.fillText("P",X({xP})+8,Y({yP})-6);

// Vetores com setas
function drawVector(Ex,Ey,color,label){{
  const Em=Math.hypot(Ex,Ey); if(Em===0)return;
  const L=80*Em/Math.max({E1},{E2},{Er});
  const dx=L*Ex/Em, dy=L*Ey/Em;
  ctx.strokeStyle=color;ctx.lineWidth=3;
  ctx.beginPath();ctx.moveTo(X({xP}),Y({yP}));
  ctx.lineTo(X({xP})+dx,Y({yP})-dy);ctx.stroke();
  const a=Math.atan2(-dy,dx),h=8;
  ctx.beginPath();
  ctx.moveTo(X({xP})+dx,Y({yP})-dy);
  ctx.lineTo(X({xP})+dx-h*Math.cos(a-0.5),Y({yP})-dy-h*Math.sin(a-0.5));
  ctx.lineTo(X({xP})+dx-h*Math.cos(a+0.5),Y({yP})-dy-h*Math.sin(a+0.5));
  ctx.closePath();ctx.fillStyle=color;ctx.fill();
  ctx.fillText(label,X({xP})+dx+6,Y({yP})-dy-6);
}}
drawVector({Ex1},{Ey1},"#d62728","E₁");
drawVector({Ex2},{Ey2},"#1f77b4","E₂");
drawVector({Exr},{Eyr},"#2ca02c","Eᵣ");
</script>
"""
components.html(html, height=620)

# ===================== Resultados =====================
st.header("Resultados")

cA, cB, cC = st.columns(3)

with cA:
    st.subheader("E₁")
    st.latex(rf"E_1 = {latex_sci(E1)}")
    st.latex(rf"E_{{1x}} = {latex_sci(Ex1)}\ {arrow_x(Ex1)}")
    st.latex(rf"E_{{1y}} = {latex_sci(Ey1)}\ {arrow_y(Ey1)}")
    st.latex(rf"\theta = {th1:.1f}^\circ")

with cB:
    st.subheader("E₂")
    st.latex(rf"E_2 = {latex_sci(E2)}")
    st.latex(rf"E_{{2x}} = {latex_sci(Ex2)}\ {arrow_x(Ex2)}")
    st.latex(rf"E_{{2y}} = {latex_sci(Ey2)}\ {arrow_y(Ey2)}")
    st.latex(rf"\theta = {th2:.1f}^\circ")

with cC:
    st.subheader("Eᵣ")
    st.latex(rf"E_r = {latex_sci(Er)}")
    st.latex(rf"E_{{rx}} = {latex_sci(Exr)}\ {arrow_x(Exr)}")
    st.latex(rf"E_{{ry}} = {latex_sci(Eyr)}\ {arrow_y(Eyr)}")
    st.latex(rf"\theta = {thr:.1f}^\circ")
