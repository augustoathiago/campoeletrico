import streamlit as st
import streamlit.components.v1 as components
import math

# =====================================================
# Configuração
# =====================================================
st.set_page_config(
    page_title="Simulador de campo elétrico Física II",
    layout="wide"
)

K = 9.0e9  # N·m²/C²

# =====================================================
# Funções auxiliares — NOTAÇÃO CIENTÍFICA CORRETA
# =====================================================
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

def latex_sci(x, n=2, unit=r"\mathrm{m}"):
    if x == 0:
        return rf"0\,{unit}"
    mant, exp = sci_parts(x, n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}\,{unit}"

def latex_sci_no_unit(x, n=2):
    if x == 0:
        return r"0"
    mant, exp = sci_parts(x, n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}"

def latex_charge_C_from_uC(q_uC):
    if q_uC == 0:
        return r"0"
    mant = f"{q_uC:.2f}".replace(".", "{,}")
    return rf"{mant}\times10^{{-6}}"

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
    E  = math.hypot(Ex, Ey)
    th = math.degrees(math.atan2(Ey, Ex))
    return Ex, Ey, E, th, r

# =====================================================
# Cabeçalho
# =====================================================
st.title("Simulador de campo elétrico Física II")
st.write("Verifique o campo elétrico gerado por partículas carregadas em um ponto **P**.")

# =====================================================
# Definições (SEM abas / SEM expander)
# =====================================================
st.header("Definições")

qmin, qmax, qstep = -5.0, 5.0, 0.05
xmin, xmax = -10.0, 10.0
ymin, ymax = -10.0, 10.0

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Partícula 1")
    x1 = st.slider("x₁ (m)", xmin, xmax, -4.0, 0.1)
    y1 = st.slider("y₁ (m)", ymin, ymax,  0.0, 0.1)
    q1_uC = st.slider("q₁ (µC)", qmin, qmax, 2.0, qstep)
    q1 = q1_uC * 1e-6

with c2:
    st.subheader("Partícula 2")
    x2 = st.slider("x₂ (m)", xmin, xmax, 4.0, 0.1)
    y2 = st.slider("y₂ (m)", ymin, ymax, 0.0, 0.1)
    q2_uC = st.slider("q₂ (µC)", qmin, qmax, -2.0, qstep)
    q2 = q2_uC * 1e-6

with c3:
    st.subheader("Ponto P")
    # (6) xP e yP com P como subíndice
    xP = st.slider("xₚ (m)", xmin, xmax, 0.0, 0.1)
    yP = st.slider("yₚ (m)", ymin, ymax, 2.0, 0.1)

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
# Figura
# =====================================================
st.header("Figura – Campo elétrico no ponto P")

ticks = list(range(-15, 16, 2))

html = f"""
<canvas id="c" width="900" height="600" style="background:white;border:1px solid #ddd;"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");

const scale = 20;
const ox = 450, oy = 300;

function X(x){{ return ox + x*scale; }}
function Y(y){{ return oy - y*scale; }}

ctx.clearRect(0,0,900,600);

// Grade e ticks (2 em 2 m)
ctx.strokeStyle="#eee";
{''.join([f'ctx.beginPath();ctx.moveTo(X({t}),Y(-15));ctx.lineTo(X({t}),Y(15));ctx.stroke();'
          f'ctx.beginPath();ctx.moveTo(X(-15),Y({t}));ctx.lineTo(X(15),Y({t}));ctx.stroke();'
          for t in ticks])}

// Eixos
ctx.strokeStyle="#000"; ctx.lineWidth=2;
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

// Vetores proporcionais ao módulo
function drawVector(Ex,Ey,color,label){{
  const Em = Math.hypot(Ex,Ey);
  if (Em===0) return;
  const L = 80*Em/Math.max({E1},{E2},{Er},1e-9);
  const dx = L*Ex/Em;
  const dy = L*Ey/Em;

  ctx.strokeStyle=color; ctx.lineWidth=3;
  ctx.beginPath();
  ctx.moveTo(X({xP}),Y({yP}));
  ctx.lineTo(X({xP})+dx,Y({yP})-dy);
  ctx.stroke();

  ctx.fillText(label,X({xP})+dx+6,Y({yP})-dy-6);
}}

drawVector({Ex1},{Ey1},"#d62728","E₁");
drawVector({Ex2},{Ey2},"#1f77b4","E₂");
drawVector({Exr},{Eyr},"#2ca02c","Eᵣ");
</script>
"""

components.html(html, height=620)

# =====================================================
# Distâncias
# =====================================================
st.header("Distâncias")
cD1, cD2 = st.columns(2)
with cD1:
    st.latex(rf"r_1 = {latex_sci(r1,2,r'\mathrm{{m}}')}")
with cD2:
    st.latex(rf"r_2 = {latex_sci(r2,2,r'\mathrm{{m}}')}")

# =====================================================
# Campo elétrico
# =====================================================
st.header("Campo elétrico")
st.latex(r"E_1 = K\frac{|q_1|}{r_1^2}")
st.latex(r"E_2 = K\frac{|q_2|}{r_2^2}")
st.latex(r"\vec{E}_r=\vec{E}_1+\vec{E}_2")

# =====================================================
# Substituição numérica (bem separada)
# =====================================================
st.header("Substituição numérica (módulos)")

s1, s2 = st.columns(2)

with s1:
    st.subheader("Para $E_1$")
    st.latex(rf"E_1=(9{{,}}0\times10^9)\frac{{|{latex_charge_C_from_uC(q1_uC)}|}}{{({latex_sci_no_unit(r1)})^2}}")
    st.latex(rf"E_1={latex_sci(E1,2,r'\mathrm{{N/C}}')}")

with s2:
    st.subheader("Para $E_2$")
    st.latex(rf"E_2=(9{{,}}0\times10^9)\frac{{|{latex_charge_C_from_uC(q2_uC)}|}}{{({latex_sci_no_unit(r2)})^2}}")
    st.latex(rf"E_2={latex_sci(E2,2,r'\mathrm{{N/C}}')}")

# =====================================================
# Resultados (bem separados)
# =====================================================
st.header("Resultados")

rA, rB, rC = st.columns(3)

with rA:
    st.subheader("$E_1$")
    st.latex(rf"E_1={latex_sci(E1,2,r'\mathrm{{N/C}}')}")
    st.latex(rf"E_{{1x}}={latex_sci(Ex1,2,r'\mathrm{{N/C}}')}\ {arrow_x(Ex1)}")
    st.latex(rf"E_{{1y}}={latex_sci(Ey1,2,r'\mathrm{{N/C}}')}\ {arrow_y(Ey1)}")
    st.latex(rf"\\theta_1={th1:.1f}^\circ")

with rB:
    st.subheader("$E_2$")
    st.latex(rf"E_2={latex_sci(E2,2,r'\mathrm{{N/C}}')}")
    st.latex(rf"E_{{2x}}={latex_sci(Ex2,2,r'\mathrm{{N/C}}')}\ {arrow_x(Ex2)}")
    st.latex(rf"E_{{2y}}={latex_sci(Ey2,2,r'\mathrm{{N/C}}')}\ {arrow_y(Ey2)}")
    st.latex(rf"\\theta_2={th2:.1f}^\circ")

with rC:
    st.subheader("$E_r$")
    st.latex(rf"E_r={latex_sci(Er,2,r'\mathrm{{N/C}}')}")
    st.latex(rf"E_{{rx}}={latex_sci(Exr,2,r'\mathrm{{N/C}}')}\ {arrow_x(Exr)}")
    st.latex(rf"E_{{ry}}={latex_sci(Eyr,2,r'\mathrm{{N/C}}')}\ {arrow_y(Eyr)}")
    st.latex(rf"\\theta_r={thr:.1f}^\circ")
``
