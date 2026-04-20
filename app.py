import streamlit as st
import streamlit.components.v1 as components
import math

# ===================== Configuração =====================
st.set_page_config(page_title="Simulador de campo elétrico Física II", layout="wide")
K = 9.0e9  # N·m²/C²

# ===================== Funções auxiliares =====================
def sci_parts(x, n=3):
    """Retorna mantissa e expoente em notação científica com n algarismos significativos."""
    if x == 0:
        return 0.0, 0
    exp = int(math.floor(math.log10(abs(x))))
    mant = x / (10 ** exp)
    mant = float(f"{mant:.{n}g}")
    if abs(mant) >= 10:
        mant /= 10
        exp += 1
    return mant, exp

def latex_sci(x, n=3, unit=r"\mathrm{N/C}"):
    """Formata número em LaTeX com notação científica (n algarismos significativos)."""
    if x == 0:
        return rf"0\,{unit}"
    mant, exp = sci_parts(x, n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}\,{unit}"

def latex_sci_m(x, n=3, unit=r"\mathrm{m}"):
    """Formata distância em LaTeX com notação científica (n algarismos significativos)."""
    if x == 0:
        return rf"0\,{unit}"
    mant, exp = sci_parts(x, n)
    mant_s = f"{mant:.{n}g}".replace(".", "{,}")
    return rf"{mant_s}\times10^{{{exp}}}\,{unit}"

def latex_full(x, sig=15):
    """
    Formata valor com alta precisão (sem arredondar para poucas casas).
    Usa sig dígitos significativos para exibir o valor do float com fidelidade.
    """
    s = f"{x:.{sig}g}"
    return s.replace(".", "{,}")

def arrow_x(v):
    if v > 0:
        return r"\rightarrow"
    elif v < 0:
        return r"\leftarrow"
    return r""

def arrow_y(v):
    if v > 0:
        return r"\uparrow"
    elif v < 0:
        return r"\downarrow"
    return r""

def color_charge(q):
    """Cores: positivo vermelho, negativo azul, neutro borda preta (Item 6)."""
    if q > 0:
        return "#d62728"
    elif q < 0:
        return "#1f77b4"
    return "#000000"

def electric_field(q, xq, yq, xp, yp):
    """Campo elétrico (componentes, módulo, ângulo) devido a uma carga puntiforme."""
    dx, dy = xp - xq, yp - yq
    r = math.hypot(dx, dy)
    Ex = K * q * dx / (r**3)
    Ey = K * q * dy / (r**3)
    E = math.hypot(Ex, Ey)
    th = math.degrees(math.atan2(Ey, Ex))
    return Ex, Ey, E, th, r

def latex_num(x, digits=3):
    """Número com vírgula decimal (para LaTeX)."""
    return f"{x:.{digits}f}".replace(".", "{,}")

# ===================== Logo no início =====================
st.image("logo_maua.png", width=180)

# ===================== Cabeçalho =====================
st.title("Simulador de campo elétrico Física II")
st.write("Verifique o campo elétrico gerado por partículas carregadas em um ponto **P**.")

# ===================== Definições =====================
st.header("Definições")

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Partícula 1")
    x1 = st.slider("x₁ (m)", -10.0, 10.0, -6.0, 0.1)
    y1 = st.slider("y₁ (m)", -10.0, 10.0,  0.0, 0.1)
    q1 = st.slider("q₁ (µC)", -5.0, 5.0,  2.0, 0.05) * 1e-6

with c2:
    st.subheader("Partícula 2")
    x2 = st.slider("x₂ (m)", -10.0, 10.0,  6.0, 0.1)
    y2 = st.slider("y₂ (m)", -10.0, 10.0,  0.0, 0.1)
    q2 = st.slider("q₂ (µC)", -5.0, 5.0, -2.0, 0.05) * 1e-6

with c3:
    st.subheader("Ponto P")
    xP = st.slider("xₚ (m)", -10.0, 10.0,  0.0, 0.1)
    yP = st.slider("yₚ (m)", -10.0, 10.0,  4.0, 0.1)

# ===================== Bloqueio de posições coincidentes =====================
points = {(round(x1,2), round(y1,2)), (round(x2,2), round(y2,2)), (round(xP,2), round(yP,2))}
if len(points) < 3:
    st.error("❌ Partículas e ponto P não podem ocupar a mesma posição.")
    st.stop()

# ===================== Física =====================
Ex1, Ey1, E1, th1, r1 = electric_field(q1, x1, y1, xP, yP)
Ex2, Ey2, E2, th2, r2 = electric_field(q2, x2, y2, xP, yP)

Exr, Eyr = Ex1 + Ex2, Ey1 + Ey2
Er = math.hypot(Exr, Eyr)
thr = math.degrees(math.atan2(Eyr, Exr))

# ===================== Figura =====================
st.header("Figura – Campo elétrico no ponto P")

# Eixos -15 a 15 (como você já queria antes)
xmin, xmax = -15, 15
ymin, ymax = -15, 15

W, H = 900, 600
ox, oy = W // 2, H // 2
scale = int(min(W, H) * 0.80 / (xmax - xmin))

minor_ticks = list(range(xmin, xmax + 1, 1))
major_ticks = list(range(xmin, xmax + 1, 5))

Emax = max(E1, E2, Er, 1e-12)
Lmax = 110

html = f"""
<canvas id="c" width="{W}" height="{H}" style="background:white;border:1px solid #ddd;"></canvas>
<script>
const c = document.getElementById("c");
const ctx = c.getContext("2d");

const scale = {scale};
const ox = {ox};
const oy = {oy};

function X(x){{ return ox + x*scale; }}
function Y(y){{ return oy - y*scale; }}

ctx.clearRect(0,0,{W},{H});
ctx.font = "14px sans-serif";
ctx.fillStyle = "#000";

// ===== Grade (minor) =====
ctx.strokeStyle="#f2f2f2";
ctx.lineWidth=1;
{''.join([f"""
ctx.beginPath();
ctx.moveTo(X({t}), Y({ymin}));
ctx.lineTo(X({t}), Y({ymax}));
ctx.stroke();
""" for t in minor_ticks])}

{''.join([f"""
ctx.beginPath();
ctx.moveTo(X({xmin}), Y({t}));
ctx.lineTo(X({xmax}), Y({t}));
ctx.stroke();
""" for t in minor_ticks])}

// ===== Grade (major) + rótulos =====
ctx.strokeStyle="#e0e0e0";
ctx.lineWidth=1.2;

{''.join([f"""
ctx.beginPath();
ctx.moveTo(X({t}), Y({ymin}));
ctx.lineTo(X({t}), Y({ymax}));
ctx.stroke();

ctx.fillStyle="#444";
ctx.fillText("{t}", X({t})-8, Y(0)+18);
ctx.fillStyle="#000";
""" for t in major_ticks])}

{''.join([f"""
ctx.beginPath();
ctx.moveTo(X({xmin}), Y({t}));
ctx.lineTo(X({xmax}), Y({t}));
ctx.stroke();

ctx.fillStyle="#444";
ctx.fillText("{t}", X(0)-30, Y({t})+5);
ctx.fillStyle="#000";
""" for t in major_ticks])}

// ===== Eixos =====
ctx.strokeStyle="#000";
ctx.lineWidth=2;

// eixo x
ctx.beginPath();
ctx.moveTo(X({xmin}), Y(0));
ctx.lineTo(X({xmax}), Y(0));
ctx.stroke();

// eixo y
ctx.beginPath();
ctx.moveTo(X(0), Y({ymin}));
ctx.lineTo(X(0), Y({ymax}));
ctx.stroke();

// setas dos eixos
function axisArrow(x1,y1,x2,y2){{
  const a = Math.atan2(y2-y1, x2-x1);
  const h = 10;
  ctx.beginPath();
  ctx.moveTo(x2,y2);
  ctx.lineTo(x2 - h*Math.cos(a-0.5), y2 - h*Math.sin(a-0.5));
  ctx.lineTo(x2 - h*Math.cos(a+0.5), y2 - h*Math.sin(a+0.5));
  ctx.closePath();
  ctx.fillStyle="#000";
  ctx.fill();
}}
axisArrow(X({xmin}),Y(0),X({xmax}),Y(0));
axisArrow(X(0),Y({ymin}),X(0),Y({ymax}));

ctx.fillText("x (m)", X({xmax})+12, Y(0)+6);
ctx.fillText("y (m)", X(0)-10, Y({ymax})-12);

// ===== Partículas =====
function particle(x,y,label,borderColor){{
  ctx.beginPath();
  ctx.arc(X(x), Y(y), 14, 0, 2*Math.PI);
  ctx.fillStyle="#fafafa";
  ctx.fill();
  ctx.strokeStyle=borderColor;
  ctx.lineWidth=3;
  ctx.stroke();
  ctx.fillStyle="#000";
  ctx.fillText(label, X(x)-4, Y(y)+5);
}}

particle({x1},{y1},"1","{color_charge(q1)}");
particle({x2},{y2},"2","{color_charge(q2)}");

// ===== Ponto P =====
ctx.beginPath();
ctx.arc(X({xP}), Y({yP}), 4, 0, 2*Math.PI);
ctx.fillStyle="#000";
ctx.fill();
ctx.fillText("P", X({xP})+8, Y({yP})-8);

// ===== Função: desenhar rótulo com "seta do vetor" bem em cima (Item 1) =====
function drawVectorLabel(text, x, y, color) {{
  ctx.fillStyle = color;
  ctx.font = "16px sans-serif";
  ctx.fillText(text, x, y);

  // seta acima do texto
  const w = ctx.measureText(text).width;
  const yArrow = y - 16;     // altura da seta acima do texto
  const x0 = x + 2;
  const x1 = x + w - 2;

  ctx.strokeStyle = color;
  ctx.lineWidth = 2;

  // linha da seta
  ctx.beginPath();
  ctx.moveTo(x0, yArrow);
  ctx.lineTo(x1, yArrow);
  ctx.stroke();

  // ponta da seta (no final)
  const head = 6;
  ctx.beginPath();
  ctx.moveTo(x1, yArrow);
  ctx.lineTo(x1 - head, yArrow - head/2);
  ctx.lineTo(x1 - head, yArrow + head/2);
  ctx.closePath();
  ctx.fill();
}}

// ===== Vetores do campo no ponto P =====
function drawVector(Ex, Ey, color, labelText) {{
  const Em = Math.hypot(Ex, Ey);
  if (Em === 0) return;

  const L = {Lmax} * (Em / {Emax});
  const ux = Ex/Em, uy = Ey/Em;

  const dx = L*ux;
  const dy = L*uy;

  // componentes tracejadas
  ctx.setLineDash([6,5]);
  ctx.strokeStyle=color;
  ctx.lineWidth=2;

  // componente x
  ctx.beginPath();
  ctx.moveTo(X({xP}), Y({yP}));
  ctx.lineTo(X({xP})+dx, Y({yP}));
  ctx.stroke();

  // componente y
  ctx.beginPath();
  ctx.moveTo(X({xP})+dx, Y({yP}));
  ctx.lineTo(X({xP})+dx, Y({yP})-dy);
  ctx.stroke();

  ctx.setLineDash([]);

  // vetor resultante
  ctx.strokeStyle=color;
  ctx.lineWidth=3;
  ctx.beginPath();
  ctx.moveTo(X({xP}), Y({yP}));
  ctx.lineTo(X({xP})+dx, Y({yP})-dy);
  ctx.stroke();

  // ponta da seta
  const a = Math.atan2(-dy, dx);
  const h = 10;
  ctx.beginPath();
  ctx.moveTo(X({xP})+dx, Y({yP})-dy);
  ctx.lineTo(X({xP})+dx - h*Math.cos(a-0.5), Y({yP})-dy - h*Math.sin(a-0.5));
  ctx.lineTo(X({xP})+dx - h*Math.cos(a+0.5), Y({yP})-dy - h*Math.sin(a+0.5));
  ctx.closePath();
  ctx.fillStyle=color;
  ctx.fill();

  // rótulo (Item 1: seta bem encima do "E1/E2/Er")
  const lx = X({xP}) + dx + 10;
  const ly = Y({yP}) - dy - 6;
  drawVectorLabel(labelText, lx, ly, color);

  ctx.fillStyle="#000";
}}

drawVector({Ex1}, {Ey1}, "#d62728", "E₁");
drawVector({Ex2}, {Ey2}, "#1f77b4", "E₂");
drawVector({Exr}, {Eyr}, "#2ca02c", "Eᵣ");
</script>
"""

components.html(html, height=H + 30)

# ===================== Distâncias (Item 2) =====================
st.header("Distâncias")

d1, d2 = st.columns(2)
with d1:
    st.subheader("Entre a partícula 1 e P")
    st.latex(rf"r_1 = {latex_sci_m(r1, n=3)}")

with d2:
    st.subheader("Entre a partícula 2 e P")
    st.latex(rf"r_2 = {latex_sci_m(r2, n=3)}")

# ===================== Campo elétrico =====================
st.header("Campo elétrico")

st.write(
    "onde **q₁ e q₂** são as cargas das partículas, **r₁ e r₂** são as distâncias entre as partículas e o ponto **P**, "
    "e **K** é a constante de Coulomb igual a **9,0×10⁹ N·m²/C²**."
)

st.latex(r"\vec{E}_1 = K\frac{q_1}{r_1^2}\,\hat{r}_1 \qquad \text{e} \qquad \vec{E}_2 = K\frac{q_2}{r_2^2}\,\hat{r}_2")
st.latex(r"\vec{E}_r = \vec{E}_1 + \vec{E}_2")

# ===================== Substituição numérica (módulos) (Item 3) =====================
st.subheader("Substituição numérica (módulos)")

# módulos (para substituição) - E1mag e E2mag aqui são escalares (podem ser negativos se q<0)
E1mag = K * q1 / (r1**2)
E2mag = K * q2 / (r2**2)

# Mostrar r1 e r2 "sem arredondamentos" (alta precisão) e arredondar só o resultado final
st.latex(
    rf"E_1 = K\frac{{|q_1|}}{{r_1^2}} = (9,0\times10^9)\frac{{|{latex_full(q1, 15)}|}}{{({latex_full(r1, 15)})^2}}"
    rf" = {latex_sci(abs(E1mag), n=3)}"
)
st.latex(
    rf"E_2 = K\frac{{|q_2|}}{{r_2^2}} = (9,0\times10^9)\frac{{|{latex_full(q2, 15)}|}}{{({latex_full(r2, 15)})^2}}"
    rf" = {latex_sci(abs(E2mag), n=3)}"
)

# (Item 4) Seção de componentes com valores substituídos foi removida.

# ===================== Resultados (Item 5) =====================
st.header("Resultados")

cA, cB, cC = st.columns(3)

with cA:
    st.subheader("E₁")
    st.latex(rf"E_1 = {latex_sci(E1)}")
    st.latex(rf"\theta_1 = {latex_num(th1, 1)}^\circ")
    st.latex(rf"E_{{1x}} = {latex_sci(Ex1)}\;{arrow_x(Ex1)}")
    st.latex(rf"E_{{1y}} = {latex_sci(Ey1)}\;{arrow_y(Ey1)}")

with cB:
    st.subheader("E₂")
    st.latex(rf"E_2 = {latex_sci(E2)}")
    st.latex(rf"\theta_2 = {latex_num(th2, 1)}^\circ")
    st.latex(rf"E_{{2x}} = {latex_sci(Ex2)}\;{arrow_x(Ex2)}")
    st.latex(rf"E_{{2y}} = {latex_sci(Ey2)}\;{arrow_y(Ey2)}")

with cC:
    st.subheader("Eᵣ")
    st.latex(rf"E_r = {latex_sci(Er)}")
    st.latex(rf"\theta_r = {latex_num(thr, 1)}^\circ")
    st.latex(rf"E_{{rx}} = {latex_sci(Exr)}\;{arrow_x(Exr)}")
    st.latex(rf"E_{{ry}} = {latex_sci(Eyr)}\;{arrow_y(Eyr)}")
