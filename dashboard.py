"""
NusaCommerce • Vibe Dashboard
Dashboard Streamlit untuk menjawab 3 pertanyaan bisnis + analisis tambahan + peta wilayah.

Jalankan:  streamlit run app.py
Letakkan data.zip (atau CSV hasil cleaning) di folder yang sama, atau unggah lewat sidebar.
"""
import calendar
import io
import json
import re
from collections import Counter
from html import escape as esc
from itertools import combinations
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="NusaCommerce • Vibe Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

DARK = "#1B4F63"
COPPER = "#E4572E"
SLATE = "#3E6FB0"
TAN = "#F2A541"
GOOD = "#2E9E6F"
BAD = "#D1495B"
INK = "#14262D"
MUTED = "#566A72"
CREAM = "#F1F5F5"
LAND = "#3E4A5D"
SEA = "#FFFFFF"
HEAT = [[0, "#FFE08A"], [0.3, "#FFA94D"], [0.6, "#F0506E"], [0.85, "#B5338A"], [1, "#6A2C91"]]
MAP_BRIGHT = ["#FFB000", "#22D3EE", "#FF6B6B", "#7CE38B", "#C77DFF", "#4D96FF", "#FF8FAB", "#F4F1BB", "#2EC4B6", "#FF9F1C"]
PALETTE = [DARK, COPPER, "#2A9D8F", TAN, SLATE, "#8E5572", "#6B9080", BAD, "#7D8CC4", "#C9A227"]
MONTHS_ID = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
DAYS_ID = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
GROUP_ORDER = ["Selesai", "Diterima (masa retur)", "Dalam pengiriman", "Lainnya", "Batal"]


# =========================
# STYLE
# =========================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, .stMarkdown, p, label, button, input, textarea, h1, h2, h3, h4 { font-family: 'Inter', sans-serif; }
.stApp { background: __CREAM__; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }

/* semua konten di atas koin */
.block-container { position: relative; z-index: 0; isolation: isolate; }

[data-testid="stMain"] label p { color: __INK__; font-weight: 700; font-size: 13px; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] * { color: __MUTED__; }

/* kartu: container ber-border yang memuat judul kartu, dibuat putih solid agar koin tidak tembus */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .card-title) {
    background: #FFFFFF; border: 1px solid #D5DEE0 !important; border-radius: 18px !important;
    position: relative; z-index: 1; }
.card-title { font-size: 16px; font-weight: 800; color: __INK__; text-align: center; margin: 2px 0 0 0; }
.card-sub { font-size: 12px; color: __MUTED__; text-align: center; margin: 2px 0 10px 0; }

/* sidebar */
[data-testid="stSidebar"] { background: #0F2E3A; border-right: none; }
[data-testid="stSidebar"] * { color: #F1F5F5; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] div, [data-testid="stSidebar"] [data-testid="stMultiSelect"] div,
[data-testid="stSidebar"] [data-baseweb="select"] div { background-color: #1B4F63 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] *, [data-testid="stSidebar"] [data-testid="stMultiSelect"] *,
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #F1F5F5 !important; -webkit-text-fill-color: #F1F5F5 !important; }
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg, [data-testid="stSidebar"] [data-testid="stMultiSelect"] svg { fill: #F1F5F5; }
[data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"], [data-testid="stSidebar"] [data-testid="stMultiSelect"] span[data-baseweb="tag"] div { background-color: #E4572E !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"], [data-testid="stSidebar"] [data-testid="stWidgetLabel"] *,
[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] *, [data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-testid="stWidgetLabel"] *,
[data-testid="stSidebar"] [data-testid="stSelectbox"] label, [data-testid="stSidebar"] [data-testid="stMultiSelect"] label { background-color: transparent !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] section { background: #1B4F63; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
[data-testid="stSidebar"] [data-testid="stFileUploader"] span { color: #D5DEE0 !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] button { background: #F1F5F5; color: #0F2E3A !important; border: none; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] button * { color: #0F2E3A !important; }
.brand { display: flex; align-items: center; gap: 12px; padding: 12px 14px; background: #1B4F63; border-radius: 14px; margin-bottom: 14px; }
.avatar { width: 46px; height: 46px; border-radius: 50%; background: #CBD8DC; overflow: hidden; flex-shrink: 0; }
.avatar svg { width: 100%; height: 100%; fill: #8FA6AD; display: block; }
.brand-name { font-weight: 800; font-size: 15px; line-height: 1.2; }
.brand-role { font-size: 11px; opacity: .8; }
.side-label { font-size: 11px; text-transform: uppercase; letter-spacing: .8px; opacity: .8;
              margin: 18px 0 6px 2px; font-weight: 800; }
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding: 10px 14px; border-radius: 10px; width: 100%; cursor: pointer; }
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: #1B4F63; }
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child, [data-testid="stSidebar"] div[role="radiogroup"] label [data-baseweb="radio"] > div:first-child { display: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background: #F1F5F5; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * { color: #0F2E3A !important; font-weight: 800; }

/* banner judul */
.page-banner { background: #0F2E3A; border-radius: 18px; padding: 16px 24px; text-align: center; margin-bottom: 16px; }
.page-title { color: #FFFFFF; font-size: 28px; font-weight: 800; margin: 0; letter-spacing: -.3px; }
.page-sub { color: #D5DEE0; font-size: 13.5px; margin: 4px 0 0 0; }

/* KPI */
.kpi { background: #FFFFFF; border: 1px solid #D5DEE0; border-left: 14px solid #1B4F63; border-radius: 18px;
       padding: 14px 12px; text-align: center; min-height: 98px; display: flex; flex-direction: column;
       justify-content: center; }
.kpi-value { font-size: 26px; font-weight: 800; color: #1B4F63; line-height: 1.2; overflow-wrap: anywhere; }
.kpi-title { font-size: 13px; font-weight: 700; color: __INK__; }
.kpi-sub { font-size: 11.5px; font-weight: 600; color: __MUTED__; }
.up { color: #2E9E6F; } .down { color: #D1495B; } .flat { color: __MUTED__; }

/* kartu jawaban */
.ans { border-radius: 18px; padding: 16px 18px; min-height: 190px; color: #FFFFFF; display: flex;
       flex-direction: column; gap: 6px; }
.ans-q { font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: .6px; opacity: .9; }
.ans-a { font-size: 21px; font-weight: 800; line-height: 1.25; overflow-wrap: anywhere; }
.ans-d { font-size: 13px; font-weight: 500; line-height: 1.45; opacity: .95; overflow-wrap: anywhere; }
.g1 { background: #1B4F63; } .g2 { background: #2A9D8F; } .g3 { background: #E4572E; }

/* leaderboard */
.lb { display: grid; grid-template-columns: 26px 42px minmax(0,1fr) auto; gap: 12px; align-items: center;
      padding: 10px 12px; border: 1px solid #E3EAEB; border-radius: 14px; margin-bottom: 8px; background: #F7FAFA; }
.lb-rank { text-align: center; font-weight: 800; color: __MUTED__; font-size: 15px; }
.lb-icon { width: 42px; height: 42px; border-radius: 12px; background: #E4F0F1; display: flex;
           align-items: center; justify-content: center; font-size: 22px; }
.lb-name { font-weight: 700; font-size: 13.5px; color: __INK__; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lb-bar { height: 6px; border-radius: 6px; background: #E3EAEB; margin-top: 6px; overflow: hidden; }
.lb-bar > div { height: 100%; background: #2A7F8E; border-radius: 6px; }
.lb-val { text-align: right; font-weight: 800; font-size: 14px; color: __INK__; white-space: nowrap; }
.lb-val small { display: block; font-weight: 600; color: __MUTED__; font-size: 11px; }

/* insight */
.tea { background: #F1F5F5; border-left: 4px solid #E4572E; border-radius: 10px; padding: 10px 14px;
       margin-bottom: 8px; font-size: 13.5px; color: __INK__; line-height: 1.5; overflow-wrap: anywhere; }

/* tombol */
div.stDownloadButton > button, div.stButton > button {
    background: #1B4F63; color: #FFFFFF; font-weight: 700; border: none; border-radius: 10px; padding: 10px 22px; }
div.stDownloadButton > button:hover { background: #0F2E3A; color: #FFFFFF; }

/* koin jatuh (di belakang semua konten) */
div[data-testid="stElementContainer"]:has(.coins-container), .element-container:has(.coins-container) {
    height: 0; margin: 0; padding: 0; }
.coins-container { position: fixed; inset: 0; pointer-events: none; z-index: -1; overflow: hidden; opacity: .55; }
.coin { position: absolute; top: 0; width: 30px; height: 30px; border-radius: 50%; background: #D9A441;
        border: 3px solid #B9822A; box-shadow: inset 0 0 0 2px #EBC77A; color: #7A4E0E; font-size: 10px;
        font-weight: 800; display: flex; align-items: center; justify-content: center; opacity: 0;
        animation: coinfall linear infinite; }
@keyframes coinfall {
    0% { transform: translateY(-60px) rotateY(0deg); opacity: 0; }
    12% { opacity: .6; }
    90% { opacity: .6; }
    100% { transform: translateY(105vh) rotateY(720deg); opacity: 0; }
}
.coin:nth-child(1) { left: 3%;  animation-duration: 9s; }
.coin:nth-child(2) { left: 13%; animation-duration: 12s; animation-delay: 2s; }
.coin:nth-child(3) { left: 26%; animation-duration: 10s; animation-delay: 5s; }
.coin:nth-child(4) { left: 38%; animation-duration: 13s; animation-delay: 1s; }
.coin:nth-child(5) { left: 50%; animation-duration: 9.5s; animation-delay: 6s; }
.coin:nth-child(6) { left: 62%; animation-duration: 12.5s; animation-delay: 3s; }
.coin:nth-child(7) { left: 74%; animation-duration: 10.5s; animation-delay: 7s; }
.coin:nth-child(8) { left: 86%; animation-duration: 11s; animation-delay: 4s; }
.coin:nth-child(9) { left: 95%; animation-duration: 13s; animation-delay: 0.5s; }
</style>
"""


def inject_css():
    css = CSS.replace("__INK__", INK).replace("__MUTED__", MUTED).replace("__CREAM__", CREAM)
    coins = '<div class="coins-container">' + '<div class="coin">Rp</div>' * 9 + "</div>"
    st.markdown(css + coins, unsafe_allow_html=True)


inject_css()


# =========================
# HELPER FORMAT
# =========================
def format_rp(value):
    if pd.isna(value):
        value = 0
    return "Rp " + f"{value:,.0f}".replace(",", ".")


def format_short(value):
    if pd.isna(value):
        value = 0
    a = abs(value)
    for limit, suffix in ((1e12, " T"), (1e9, " M"), (1e6, " jt"), (1e3, " rb")):
        if a >= limit:
            return "Rp " + f"{value / limit:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + suffix
    return format_rp(value)


def format_int(value):
    if pd.isna(value):
        value = 0
    return f"{value:,.0f}".replace(",", ".")


def format_pct(value, digits=1):
    return f"{value:.{digits}f}".replace(".", ",") + "%"


def shorten(text, n=30):
    t = str(text)
    return t if len(t) <= n else t[: n - 1] + "…"


def month_label(ts):
    return f"{MONTHS_ID[ts.month - 1]} {ts.year}"


def chip(g):
    if g is None or pd.isna(g):
        return ""
    cls = "up" if g > 0 else ("down" if g < 0 else "flat")
    arrow = "▲" if g > 0 else ("▼" if g < 0 else "●")
    return f'<span class="{cls}">{arrow} {abs(g):.1f}%</span>'


def growth(series):
    s = series.dropna()
    if len(s) < 2 or s.iloc[-2] == 0:
        return None
    return (s.iloc[-1] - s.iloc[-2]) / abs(s.iloc[-2]) * 100


# =========================
# HELPER UI
# =========================
def page_header(title, sub):
    st.markdown(
        f'<div class="page-banner"><div class="page-title">{title}</div><div class="page-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def kpi(col, title, value, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    col.markdown(
        f'<div class="kpi"><div class="kpi-value">{value}</div><div class="kpi-title">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def card(title, sub=""):
    box = st.container(border=True)
    with box:
        sub_html = f'<div class="card-sub">{sub}</div>' if sub else '<div style="height:6px"></div>'
        st.markdown(f'<div class="card-title">{title}</div>{sub_html}', unsafe_allow_html=True)
    return box


def style_fig(fig, height=340, legend=False):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=24, t=16, b=72 if legend else 16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Inter, sans-serif", color=INK, size=12),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0, title_text=""),
        hoverlabel=dict(font_family="Inter"),
    )
    fig.update_xaxes(showgrid=False, title_text="", automargin=True, linecolor="#D5DEE0", tickfont=dict(color=INK))
    fig.update_yaxes(gridcolor="#E3EAEB", title_text="", zeroline=False, automargin=True, tickfont=dict(color=INK))
    return fig


def show(fig, key):
    st.plotly_chart(fig, width="stretch", key=key)


ICON_RULES = [
    (r"celengan|tabungan", "🐷"),
    (r"baskom|ember", "🪣"),
    (r"sambal|saus|mangkok|mangkuk", "🥣"),
    (r"pintu|engsel|kunci|handle|gerendel", "🚪"),
    (r"nampan|tray|piring|talam", "🍽️"),
    (r"seal|baut|roof|atap|sekrup", "🔩"),
    (r"\brak\b|lemari|etalase", "🗄️"),
    (r"lunch|rantang|bekal", "🍱"),
    (r"keranjang|basket", "🧺"),
    (r"nasi|rice", "🍚"),
    (r"botol|gelas|mug|tumbler|cangkir", "🥤"),
    (r"toples|stoples|jar", "🥫"),
    (r"sendok|garpu|sumpit|alat makan", "🍴"),
    (r"hanger|gantungan|jemuran|laundry", "👕"),
    (r"sapu|pel|sikat|bersih", "🧹"),
    (r"mainan|toy", "🧸"),
    (r"hias|dekor|bunga|vas", "🌷"),
]


def cat_icon(name):
    t = str(name).lower()
    for pattern, icon in ICON_RULES:
        if re.search(pattern, t):
            return icon
    return "📦"


def with_icon(name):
    return f"{cat_icon(name)} {name}"


def hbar(data, value, label, color, fmt, height=None, pad=1.3, highlight=None, sign_colors=False, icons=False):
    """Bar horizontal rapi: label dipotong, angka di luar bar, ruang kanan disiapkan."""
    d = data.sort_values(value, ascending=True).copy()
    raw = d[label].astype(str)
    if icons:
        labels = raw.map(lambda v: f"{cat_icon(v)} {shorten(v, 30)}")
    else:
        labels = raw.map(lambda v: shorten(v, 34))
    if labels.duplicated().any():
        labels = raw
    if sign_colors:
        colors = [GOOD if v >= 0 else BAD for v in d[value]]
    elif highlight is not None:
        colors = [COPPER if str(v) == str(highlight) else color for v in d[label]]
    else:
        colors = color
    vmax = float(d[value].max()) if len(d) else 1.0
    vmin = float(d[value].min()) if len(d) else 0.0
    fig = go.Figure(
        go.Bar(
            x=d[value], y=labels, orientation="h", marker_color=colors,
            text=d[value].map(fmt), textposition="outside", cliponaxis=False,
            customdata=raw, hovertemplate="<b>%{customdata}</b><br>%{text}<extra></extra>",
        )
    )
    fig.update_xaxes(range=[min(0, vmin * pad), max(0.0001, vmax * pad)], showticklabels=False, showgrid=False)
    style_fig(fig, height or max(260, 40 * len(d) + 40))
    fig.update_yaxes(showgrid=False)
    return fig


def leaderboard(data, label_col, value_col, fmt, n=5, sub_fn=None):
    top = data.sort_values(value_col, ascending=False).head(n)
    if top.empty:
        st.info("Belum ada data.")
        return
    mx = float(top[value_col].max()) or 1.0
    html = ""
    for i, (_, r) in enumerate(top.iterrows(), 1):
        name = str(r[label_col])
        sub = f"<small>{sub_fn(r)}</small>" if sub_fn else ""
        pct = max(4, float(r[value_col]) / mx * 100)
        html += (
            f'<div class="lb"><div class="lb-rank">{i}</div><div class="lb-icon">{cat_icon(name)}</div>'
            f'<div style="min-width:0"><div class="lb-name" title="{esc(name)}">{esc(name)}</div>'
            f'<div class="lb-bar"><div style="width:{pct:.0f}%"></div></div></div>'
            f'<div class="lb-val">{fmt(r[value_col])}{sub}</div></div>'
        )
    st.markdown(html, unsafe_allow_html=True)


# =========================
# LOAD DATA
# =========================
BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path(".")


def read_csv_bytes(data: bytes, filename: str):
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        for sep in (";", ",", "\t", "|", None):
            try:
                if sep is None:
                    frame = pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=encoding)
                else:
                    frame = pd.read_csv(io.BytesIO(data), sep=sep, encoding=encoding)
                if len(frame.columns) > 1:
                    frame.columns = [str(c).strip().replace("\ufeff", "") for c in frame.columns]
                    return frame
            except Exception as exc:  # noqa: BLE001
                last_error = exc
    raise ValueError(f"Gagal membaca {filename}: {last_error}")


@st.cache_data(show_spinner=False)
def get_data_options():
    options = {}
    seen = set()
    for folder in (BASE_DIR, Path(".")):
        for p in sorted(folder.glob("*.csv")):
            if p.resolve() in seen:
                continue
            seen.add(p.resolve())
            try:
                options[p.name] = read_csv_bytes(p.read_bytes(), p.name)
            except Exception:  # noqa: BLE001
                pass
        for zpath in sorted(folder.glob("*.zip")):
            if zpath.resolve() in seen:
                continue
            seen.add(zpath.resolve())
            try:
                with ZipFile(zpath) as zf:
                    for member in zf.namelist():
                        if member.lower().endswith(".csv") and not member.endswith("/"):
                            try:
                                options[f"{zpath.name} ▸ {Path(member).name}"] = read_csv_bytes(zf.read(member), member)
                            except Exception:  # noqa: BLE001
                                pass
            except (BadZipFile, OSError):
                pass
    return options


def snake(c):
    c = str(c).strip().replace("\ufeff", "").lower()
    c = re.sub(r"[/\s]+", "_", c)
    c = re.sub(r"_+", "_", c)
    return c.strip("_")


REQUIRED = ["order_id", "product_categories", "total_pembayaran", "status_pesanan", "kota_kabupaten"]
NUMERIC = [
    "total_qty", "total_weight_gr", "total_returned_qty", "total_diskon", "num_product_categories",
    "ongkos_kirim_dibayar_oleh_pembeli", "estimasi_potongan_biaya_pengiriman", "total_pembayaran",
    "perkiraan_ongkos_kirim",
]
TEXT_DEFAULTS = {
    "provinsi": "Tidak diketahui", "metode_pembayaran": "Tidak diketahui",
    "opsi_pengiriman": "Tidak diketahui", "alasan_pembatalan": "Tidak dibatalkan",
}


def status_group(s):
    t = str(s).lower()
    if t.startswith("selesai"):
        return "Selesai"
    if "batal" in t or "cancel" in t:
        return "Batal"
    if "pengembalian" in t or "diterima" in t:
        return "Diterima (masa retur)"
    if "dikirim" in t:
        return "Dalam pengiriman"
    return "Lainnya"


def parse_dates(series):
    try:
        return pd.to_datetime(series, errors="coerce", format="mixed", dayfirst=True)
    except (TypeError, ValueError):
        return pd.to_datetime(series, errors="coerce", dayfirst=True)


@st.cache_data(show_spinner="Lagi nyiapin data…")
def prepare(raw):
    df = raw.copy()
    df.columns = [snake(c) for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return None, missing
    df = df.drop_duplicates().copy()

    for c in NUMERIC:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            df[c] = np.nan if c == "total_qty" else 0
    df["total_pembayaran"] = df["total_pembayaran"].fillna(0)
    df["total_diskon"] = df["total_diskon"].fillna(0)
    df["total_returned_qty"] = df["total_returned_qty"].fillna(0)

    for c, default in TEXT_DEFAULTS.items():
        df[c] = df[c].fillna(default).astype(str).str.strip() if c in df.columns else default
    df["product_categories"] = df["product_categories"].fillna("Tidak diketahui").astype(str).str.strip()
    df["status_pesanan"] = df["status_pesanan"].fillna("Lainnya").astype(str).str.strip()
    df["kota_kabupaten"] = df["kota_kabupaten"].fillna("Tidak diketahui").astype(str).str.strip().str.upper()
    df["provinsi"] = df["provinsi"].astype(str).str.upper()
    df["order_id"] = df["order_id"].astype(str)

    # Tanggal: utamakan waktu_pesanan_dibuat (format ISO, lengkap), cadangan order_date
    dt = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    if "waktu_pesanan_dibuat" in df.columns:
        dt = pd.to_datetime(df["waktu_pesanan_dibuat"], errors="coerce")
    if "order_date" in df.columns:
        dt = dt.fillna(parse_dates(df["order_date"]))
    df["dt"] = dt
    df["year"] = df["dt"].dt.year
    df["month"] = df["dt"].dt.to_period("M").dt.to_timestamp()
    df["weekday"] = df["dt"].dt.dayofweek
    df["hour"] = df["dt"].dt.hour

    df["status_group"] = df["status_pesanan"].map(status_group)
    df["is_batal"] = df["status_group"].eq("Batal")
    df["is_cod"] = df["metode_pembayaran"].str.contains("COD", case=False, na=False)
    return df, []


def explode_categories(frame, mode):
    """Satu baris per (pesanan, kategori). Omzet pesanan multi-kategori dibagi rata atau dikredit penuh."""
    x = frame[["order_id", "product_categories", "total_pembayaran", "total_qty", "kota_kabupaten", "provinsi", "month"]].copy()
    x["kategori"] = x["product_categories"].str.split(",")
    x["n_kat"] = x["kategori"].str.len().clip(lower=1)
    x = x.explode("kategori")
    x["kategori"] = x["kategori"].str.strip()
    x = x[x["kategori"].ne("")].copy()
    x["omzet_alloc"] = x["total_pembayaran"] / x["n_kat"] if mode == "Bagi rata" else x["total_pembayaran"]
    x["qty_est"] = x["total_qty"] / x["n_kat"]
    return x


def category_table(ex):
    if ex.empty:
        return pd.DataFrame(columns=["kategori", "omzet", "pesanan", "unit", "share", "omzet_per_pesanan"])
    t = ex.groupby("kategori").agg(
        omzet=("omzet_alloc", "sum"), pesanan=("order_id", "nunique"), unit=("qty_est", "sum")
    ).reset_index()
    tot = t["omzet"].sum()
    t["share"] = t["omzet"] / tot * 100 if tot else 0.0
    t["omzet_per_pesanan"] = t["omzet"] / t["pesanan"].replace(0, np.nan)
    return t.sort_values("omzet", ascending=False).reset_index(drop=True)


def yearly_table(frame):
    f = frame.dropna(subset=["dt"])
    if f.empty:
        return pd.DataFrame()
    g = f.groupby("year").agg(
        pesanan=("order_id", "nunique"), omzet=("total_pembayaran", "sum"), bulan_aktif=("month", "nunique")
    ).reset_index()
    g["year"] = g["year"].astype(int)
    g["omzet_per_bulan"] = g["omzet"] / g["bulan_aktif"].replace(0, np.nan)
    g["growth_per_bulan"] = g["omzet_per_bulan"].pct_change() * 100
    return g


def monthly_table(frame):
    f = frame.dropna(subset=["dt"])
    if f.empty:
        return pd.DataFrame(columns=["month", "omzet", "pesanan"])
    return f.groupby("month").agg(omzet=("total_pembayaran", "sum"), pesanan=("order_id", "nunique")).reset_index()


def full_months(m, frame):
    """Buang bulan terakhir bila datanya belum lengkap."""
    if m.empty:
        return m
    last = frame["dt"].max()
    if pd.isna(last):
        return m
    last_month = last.to_period("M").to_timestamp()
    if last_month == m["month"].max() and last.day < calendar.monthrange(last.year, last.month)[1] - 1:
        return m.iloc[:-1]
    return m


def vibe_score(cancel_rate, growth_pct, return_rate):
    s_cancel = float(np.clip(100 - cancel_rate * 4, 0, 100))
    s_growth = float(np.clip(50 + (growth_pct or 0) * 2, 0, 100))
    s_return = float(np.clip(100 - return_rate * 10, 0, 100))
    return int(round(0.4 * s_cancel + 0.4 * s_growth + 0.2 * s_return))


def vibe_label(score):
    if score >= 75:
        return "SLAY", "Bisnis lagi glowing banget!"
    if score >= 55:
        return "Aman Jaya", "Vibes-nya oke, tinggal dipoles dikit."
    if score >= 35:
        return "Mid", "Biasa aja, ada PR yang harus digarap."
    return "Flop Era", "Waktunya glow-up besar-besaran."


def default_city(cities):
    for c in cities:
        if c.strip().upper() == "KAB. BOGOR":
            return c
    for c in cities:
        if "BOGOR" in c.upper() and "KOTA" not in c.upper():
            return c
    return cities[0]


# =========================
# GEOSPASIAL
# =========================
PROV_COORDS = """ACEH|4.70|96.75
SUMATERA UTARA|2.10|99.00
SUMATERA BARAT|-0.74|100.80
RIAU|0.50|101.50
KEPULAUAN RIAU|1.10|104.00
JAMBI|-1.60|103.60
SUMATERA SELATAN|-3.30|104.20
BANGKA BELITUNG|-2.70|106.40
BENGKULU|-3.80|102.30
LAMPUNG|-4.90|105.00
DKI JAKARTA|-6.20|106.85
JAWA BARAT|-6.90|107.60
BANTEN|-6.40|106.10
JAWA TENGAH|-7.20|110.20
DI YOGYAKARTA|-7.88|110.40
JAWA TIMUR|-7.70|112.60
BALI|-8.40|115.20
NUSA TENGGARA BARAT|-8.60|117.40
NUSA TENGGARA TIMUR|-9.80|122.00
KALIMANTAN BARAT|-0.30|111.00
KALIMANTAN TENGAH|-1.70|113.40
KALIMANTAN SELATAN|-3.10|115.30
KALIMANTAN TIMUR|0.50|116.40
KALIMANTAN UTARA|3.00|116.50
SULAWESI UTARA|1.00|124.50
GORONTALO|0.70|122.40
SULAWESI TENGAH|-1.40|121.40
SULAWESI BARAT|-2.50|119.30
SULAWESI SELATAN|-3.70|120.00
SULAWESI TENGGARA|-4.10|122.10
MALUKU|-3.20|129.40
MALUKU UTARA|1.50|127.80
PAPUA|-4.00|138.10
PAPUA BARAT|-1.30|133.20
PAPUA BARAT DAYA|-1.00|131.50
PAPUA SELATAN|-7.50|139.50
PAPUA TENGAH|-3.80|136.90
PAPUA PEGUNUNGAN|-4.10|139.00"""

CITY_COORDS = """KOTA JAKARTA BARAT|-6.17|106.74
KOTA JAKARTA SELATAN|-6.26|106.81
KOTA JAKARTA TIMUR|-6.23|106.90
KOTA JAKARTA PUSAT|-6.18|106.83
KOTA JAKARTA UTARA|-6.14|106.88
KAB. KEPULAUAN SERIBU|-5.60|106.60
KAB. BOGOR|-6.50|106.85
KOTA BOGOR|-6.595|106.80
KOTA DEPOK|-6.40|106.82
KOTA BEKASI|-6.24|106.99
KAB. BEKASI|-6.30|107.17
KOTA TANGERANG|-6.18|106.63
KAB. TANGERANG|-6.20|106.45
KOTA TANGERANG SELATAN|-6.29|106.71
KOTA SERANG|-6.12|106.15
KAB. SERANG|-6.17|106.05
KOTA CILEGON|-6.00|106.02
KAB. LEBAK|-6.56|106.25
KAB. PANDEGLANG|-6.31|106.10
KOTA BANDUNG|-6.917|107.62
KAB. BANDUNG|-7.05|107.55
KAB. BANDUNG BARAT|-6.85|107.45
KOTA CIMAHI|-6.88|107.54
KAB. SUKABUMI|-7.00|106.85
KOTA SUKABUMI|-6.92|106.93
KAB. CIANJUR|-6.82|107.14
KAB. KARAWANG|-6.32|107.34
KAB. PURWAKARTA|-6.56|107.44
KAB. SUBANG|-6.57|107.76
KAB. INDRAMAYU|-6.33|108.32
KAB. CIREBON|-6.75|108.50
KOTA CIREBON|-6.73|108.55
KAB. GARUT|-7.20|107.90
KAB. TASIKMALAYA|-7.40|108.10
KOTA TASIKMALAYA|-7.33|108.22
KAB. SUMEDANG|-6.86|107.92
KAB. MAJALENGKA|-6.84|108.23
KAB. KUNINGAN|-6.98|108.48
KAB. CIAMIS|-7.33|108.35
KOTA BANJAR|-7.37|108.54
KOTA SEMARANG|-6.97|110.42
KAB. SEMARANG|-7.15|110.45
KOTA SURAKARTA|-7.57|110.82
KAB. SUKOHARJO|-7.68|110.84
KAB. KLATEN|-7.70|110.60
KAB. BOYOLALI|-7.53|110.60
KAB. KARANGANYAR|-7.60|111.00
KAB. SRAGEN|-7.43|111.00
KAB. KUDUS|-6.80|110.84
KAB. DEMAK|-6.89|110.64
KAB. JEPARA|-6.59|110.67
KAB. PATI|-6.75|111.04
KAB. BREBES|-6.87|109.04
KAB. TEGAL|-7.00|109.10
KOTA TEGAL|-6.87|109.14
KOTA PEKALONGAN|-6.89|109.67
KAB. BANYUMAS|-7.45|109.20
KAB. CILACAP|-7.70|109.00
KAB. KEBUMEN|-7.67|109.65
KAB. MAGELANG|-7.55|110.20
KOTA MAGELANG|-7.47|110.22
KAB. KENDAL|-7.00|110.20
KAB. PEMALANG|-7.00|109.40
KOTA SALATIGA|-7.33|110.50
KOTA YOGYAKARTA|-7.80|110.37
KAB. SLEMAN|-7.70|110.35
KAB. BANTUL|-7.90|110.35
KAB. KULON PROGO|-7.85|110.15
KAB. GUNUNGKIDUL|-7.98|110.60
KOTA SURABAYA|-7.25|112.75
KAB. SIDOARJO|-7.45|112.70
KAB. GRESIK|-7.15|112.65
KOTA MALANG|-7.98|112.63
KAB. MALANG|-8.15|112.70
KOTA BATU|-7.87|112.52
KAB. PASURUAN|-7.65|112.90
KOTA PASURUAN|-7.645|112.91
KAB. MOJOKERTO|-7.50|112.40
KOTA MOJOKERTO|-7.47|112.43
KAB. JEMBER|-8.17|113.70
KAB. BANYUWANGI|-8.20|114.37
KAB. KEDIRI|-7.80|112.05
KOTA KEDIRI|-7.82|112.01
KOTA BLITAR|-8.10|112.17
KAB. BLITAR|-8.15|112.25
KAB. JOMBANG|-7.55|112.23
KAB. LAMONGAN|-7.12|112.40
KAB. TUBAN|-6.90|112.05
KAB. MADIUN|-7.60|111.60
KOTA MADIUN|-7.63|111.52
KAB. PROBOLINGGO|-7.78|113.20
KAB. BANGKALAN|-7.05|112.90
KAB. SUMENEP|-7.00|113.87
KOTA MEDAN|3.595|98.67
KAB. DELI SERDANG|3.50|98.90
KOTA BINJAI|3.60|98.49
KOTA PEKANBARU|0.51|101.45
KOTA PADANG|-0.95|100.35
KOTA PALEMBANG|-2.98|104.75
KOTA JAMBI|-1.61|103.61
KOTA BENGKULU|-3.80|102.26
KOTA BANDAR LAMPUNG|-5.43|105.26
KAB. LAMPUNG SELATAN|-5.60|105.50
KOTA BATAM|1.13|104.05
KOTA TANJUNG PINANG|0.92|104.45
KOTA PANGKAL PINANG|-2.13|106.11
KOTA BANDA ACEH|5.55|95.32
KOTA LHOKSEUMAWE|5.18|97.15
KOTA DUMAI|1.67|101.45
KOTA PONTIANAK|-0.03|109.33
KOTA BANJARMASIN|-3.32|114.59
KOTA BALIKPAPAN|-1.24|116.83
KOTA SAMARINDA|-0.50|117.15
KOTA PALANGKA RAYA|-2.21|113.92
KOTA BANJARBARU|-3.44|114.83
KOTA TARAKAN|3.30|117.63
KOTA BONTANG|0.13|117.50
KOTA MAKASSAR|-5.15|119.43
KOTA MANADO|1.47|124.84
KOTA PALU|-0.90|119.87
KOTA KENDARI|-3.97|122.51
KOTA GORONTALO|0.54|123.06
KOTA PARE-PARE|-4.01|119.62
KOTA DENPASAR|-8.65|115.22
KAB. BADUNG|-8.55|115.18
KAB. GIANYAR|-8.54|115.33
KAB. TABANAN|-8.54|115.12
KOTA MATARAM|-8.58|116.12
KAB. LOMBOK TENGAH|-8.70|116.28
KOTA KUPANG|-10.17|123.60
KOTA AMBON|-3.70|128.18
KOTA JAYAPURA|-2.53|140.70
KOTA TERNATE|0.78|127.37
KOTA SORONG|-0.88|131.26"""


def _parse_coords(block):
    out = {}
    for line in block.strip().splitlines():
        name, lat, lon = line.split("|")
        out[name] = (float(lat), float(lon))
    return out


PROV_GEO = _parse_coords(PROV_COORDS)
CITY_GEO = _parse_coords(CITY_COORDS)


def norm_prov(s):
    t = re.sub(r"\s+", " ", str(s).upper().strip()).replace("PROVINSI ", "")
    t = t.replace("KEP.", "KEPULAUAN").replace("DAERAH ISTIMEWA", "DI")
    t = t.replace("KEPULAUAN BANGKA BELITUNG", "BANGKA BELITUNG")
    t = t.replace("NANGGROE ACEH DARUSSALAM", "ACEH").replace("DI. ACEH", "ACEH").replace("DI ACEH", "ACEH")
    t = t.replace("NUSATENGGARA", "NUSA TENGGARA")
    if t in ("JAKARTA", "DKI JAKARTA RAYA"):
        t = "DKI JAKARTA"
    if t == "YOGYAKARTA":
        t = "DI YOGYAKARTA"
    return t


def norm_city(s):
    t = re.sub(r"\s+", " ", str(s).upper().strip())
    t = t.replace("KABUPATEN ", "KAB. ").replace("KAB ", "KAB. ").replace("KOTA ADM. ", "KOTA ")
    t = t.replace("KOTA ADMINISTRASI ", "KOTA ").replace("PAREPARE", "PARE-PARE")
    return t


def geo_lookup(name, level, custom=None):
    key = norm_prov(name) if level == "Provinsi" else norm_city(name)
    if custom and key in custom:
        return custom[key]
    table = PROV_GEO if level == "Provinsi" else CITY_GEO
    return table.get(key, (np.nan, np.nan))


def load_custom_geo(file):
    """CSV koordinat buatan sendiri: kolom nama wilayah + lat + lon."""
    if file is None:
        return {}
    try:
        frame = read_csv_bytes(file.getvalue(), file.name)
    except Exception:  # noqa: BLE001
        return {}
    frame.columns = [snake(c) for c in frame.columns]
    name_col = next((c for c in ("kota_kabupaten", "provinsi", "wilayah", "nama") if c in frame.columns), None)
    lat_col = next((c for c in ("lat", "latitude") if c in frame.columns), None)
    lon_col = next((c for c in ("lon", "lng", "long", "longitude") if c in frame.columns), None)
    if not (name_col and lat_col and lon_col):
        return {}
    out = {}
    for n, la, lo in zip(frame[name_col], frame[lat_col], frame[lon_col]):
        try:
            la, lo = float(la), float(lo)
        except (TypeError, ValueError):
            continue
        out[norm_city(n)] = (la, lo)
        out[norm_prov(n)] = (la, lo)
    return out


PROV_ALIAS = {
    "PAPUA SELATAN": "PAPUA", "PAPUA TENGAH": "PAPUA", "PAPUA PEGUNUNGAN": "PAPUA", "PAPUA BARAT DAYA": "PAPUA BARAT",
}


def poly_name(s):
    n = norm_prov(s)
    return PROV_ALIAS.get(n, n)


@st.cache_data(show_spinner=False)
def load_geojson():
    """Batas provinsi Indonesia (file indonesia_provinsi.geojson di folder yang sama dengan app.py)."""
    for folder in (BASE_DIR, Path(".")):
        p = folder / "indonesia_provinsi.geojson"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                return None
    return None


HAS_MAPLIBRE = hasattr(go, "Choroplethmap")
SEA_BOX = {
    "type": "FeatureCollection",
    "features": [{"type": "Feature", "properties": {}, "geometry": {
        "type": "Polygon", "coordinates": [[[60, -40], [180, -40], [180, 40], [60, 40], [60, -40]]]}}],
}


def add_land(fig, data=None, geo_key=None, col=None, fmt=None, title=""):
    """Gambar daratan Indonesia. Jika data diberikan, provinsi diwarnai menurut nilai (choropleth)."""
    gj = load_geojson()
    if gj is None:
        return False
    choro = go.Choroplethmap if HAS_MAPLIBRE else go.Choroplethmapbox
    names = [f["id"] for f in gj["features"]]
    line = dict(color="#7C8AA0", width=0.5)
    fig.add_trace(choro(
        geojson=gj, featureidkey="id", locations=names, z=[0] * len(names),
        colorscale=[[0, LAND], [1, LAND]], showscale=False, marker=dict(line=line, opacity=1), hoverinfo="skip"))
    if data is not None:
        agg = data.assign(_p=data[geo_key].map(poly_name)).groupby("_p")[col].sum()
        locs = [n for n in names if n in agg.index and agg[n] > 0]
        z = [float(agg[n]) for n in locs]
        hover = [f"<b>{n.title()}</b><br>{fmt(v)}" for n, v in zip(locs, z)]
        fig.add_trace(choro(
            geojson=gj, featureidkey="id", locations=locs, z=z, colorscale=HEAT, marker=dict(line=line, opacity=1),
            hovertext=hover, hoverinfo="text",
            colorbar=dict(title=dict(text=title, side="top"), orientation="h", x=0.02, xanchor="left", y=0.03, yanchor="bottom",
                          thickness=10, len=0.38, tickformat=".2s", outlinewidth=0)))
    return True


def map_trace(lat, lon, size, color, text, name=None):
    cls = go.Scattermap if HAS_MAPLIBRE else go.Scattermapbox
    return cls(
        lat=list(lat), lon=list(lon), mode="markers",
        marker=dict(size=list(size), color=color, opacity=0.9),
        text=list(text), hoverinfo="text", name=name, showlegend=name is not None,
    )


def map_layout(fig, height=560, legend=False):
    key = "map" if HAS_MAPLIBRE else "mapbox"
    fig.update_layout(
        **{key: dict(
            style="white-bg", center=dict(lat=-2.3, lon=118.9), zoom=3.5,
            layers=[],
        )},
        height=height,
        margin=dict(l=0, r=0, t=0, b=56 if legend else 0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=INK, size=12),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.01, xanchor="left", x=0, title_text="", bgcolor="rgba(255,255,255,.9)"),
    )
    return fig


# =========================
# SIDEBAR: MENU, DATA, FILTER
# =========================
PAGES = [
    "Beranda",
    "Cuan Kategori",
    "Tren Penjualan",
    "Kabupaten Bogor",
    "Peta Wilayah",
    "Jam & Tanggal Cuan",
    "Bayar, Kirim & Batal",
    "Data Transaksi",
]

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="avatar"><svg viewBox="0 0 24 24" aria-hidden="true">'
        '<circle cx="12" cy="8.5" r="4.2"/><path d="M3.5 22c0-5 3.8-8 8.5-8s8.5 3 8.5 8z"/></svg></div>'
        '<div><div class="brand-name">NusaCommerce</div><div class="brand-role">Admin Toko</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">Menu</div>', unsafe_allow_html=True)
    page = st.radio("Halaman", PAGES, label_visibility="collapsed")

    st.markdown('<div class="side-label">Sumber Data</div>', unsafe_allow_html=True)
    data_options = get_data_options()
    uploaded = st.file_uploader("Unggah CSV / ZIP", type=["csv", "zip"])

    df_raw = None
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith(".zip"):
                with ZipFile(uploaded) as zf:
                    members = [n for n in zf.namelist() if n.lower().endswith(".csv") and not n.endswith("/")]
                    if not members:
                        st.error("ZIP tidak berisi file CSV.")
                        st.stop()
                    member = st.selectbox("Pilih file dalam ZIP", members)
                    df_raw = read_csv_bytes(zf.read(member), member)
            else:
                df_raw = read_csv_bytes(uploaded.getvalue(), uploaded.name)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Gagal memproses file: {exc}")
            st.stop()
    elif data_options:
        ranked = []
        for name, frame in data_options.items():
            cols = {snake(c) for c in frame.columns}
            ranked.append((all(c in cols for c in REQUIRED), len(frame), "clean" in name.lower(), name))
        ranked.sort(reverse=True)
        names = list(data_options.keys())
        chosen = st.selectbox("Pilih Dataset", names, index=names.index(ranked[0][3]))
        df_raw = data_options[chosen].copy()
    else:
        st.warning("Taruh data.zip / CSV di folder yang sama dengan app.py, atau unggah lewat sini.")
        st.stop()

    if df_raw is None or df_raw.empty:
        st.error("Data kosong.")
        st.stop()

    d_all, missing_cols = prepare(df_raw)
    if d_all is None:
        st.error("Kolom wajib tidak ditemukan: " + ", ".join(missing_cols))
        st.stop()

    st.markdown('<div class="side-label">Filter</div>', unsafe_allow_html=True)
    years = sorted(d_all["year"].dropna().astype(int).unique().tolist(), reverse=True)
    sel_year = st.selectbox("Tahun", ["Semua Tahun"] + years)
    groups_present = [g for g in GROUP_ORDER if g in set(d_all["status_group"]) and g != "Batal"]
    valid_groups = st.multiselect(
        "Status yang dihitung sebagai penjualan",
        groups_present,
        default=["Selesai"] if "Selesai" in groups_present else groups_present,
    )
    provinces = sorted(d_all["provinsi"].unique().tolist())
    sel_prov = st.selectbox("Provinsi", ["Semua Provinsi"] + provinces)
    alloc_mode = st.radio(
        "Omzet pesanan multi-kategori",
        ["Bagi rata", "Kredit penuh"],
        help="Satu pesanan bisa berisi beberapa kategori. 'Bagi rata' = omzet dibagi sama rata ke tiap kategori "
             "(total tetap akurat). 'Kredit penuh' = tiap kategori dapat seluruh omzet pesanan.",
    )

if not valid_groups:
    page_header("Dashboard E-Commerce", "Pilih minimal satu status penjualan di sidebar.")
    st.warning("Belum ada status yang dipilih.")
    st.stop()

year_mask = (d_all["year"] == sel_year) if sel_year != "Semua Tahun" else pd.Series(True, index=d_all.index)
prov_mask = (d_all["provinsi"] == sel_prov) if sel_prov != "Semua Provinsi" else pd.Series(True, index=d_all.index)

base = d_all[year_mask & prov_mask]                          # semua status (untuk analisis batal)
sales = base[base["status_group"].isin(valid_groups)]        # penjualan valid
sales_nat = d_all[year_mask & d_all["status_group"].isin(valid_groups)]  # nasional, tanpa filter provinsi

if sales.empty:
    page_header("Dashboard E-Commerce", "Tidak ada data untuk kombinasi filter ini.")
    st.warning("Coba longgarkan filter di sidebar.")
    st.stop()

# Metrik umum
total_rev = sales["total_pembayaran"].sum()
total_orders = sales["order_id"].nunique()
total_items = sales["total_qty"].sum()
aov = total_rev / total_orders if total_orders else 0
cancel_rate = base["is_batal"].mean() * 100
qty_sum = sales["total_qty"].sum()
return_rate = (sales["total_returned_qty"].sum() / qty_sum * 100) if qty_sum else 0

monthly_all = monthly_table(sales)
monthly_ok = full_months(monthly_all, sales)
rev_growth = growth(monthly_ok["omzet"]) if not monthly_ok.empty else None
ord_growth = growth(monthly_ok["pesanan"]) if not monthly_ok.empty else None

ex_sales = explode_categories(sales, alloc_mode)
cat_tbl = category_table(ex_sales)
yearly = yearly_table(sales)


# =========================================================
# HALAMAN 1: BERANDA
# =========================================================
if page == PAGES[0]:
    page_header("Vibe Check Penjualan", "Ringkasan 3 pertanyaan bisnis + fakta seru dari datamu, dalam satu layar.")

    k = st.columns(5)
    kpi(k[0], "Total Penjualan", format_short(total_rev), chip(rev_growth) + " vs bulan lalu" if rev_growth is not None else "")
    kpi(k[1], "Jumlah Pesanan", format_int(total_orders), chip(ord_growth) + " vs bulan lalu" if ord_growth is not None else "")
    kpi(k[2], "Barang Terjual", format_int(total_items))
    kpi(k[3], "Rata-rata Nilai Pesanan", format_short(aov))
    kpi(k[4], "Tingkat Batal", format_pct(cancel_rate), "dari semua pesanan")
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ---- 3 jawaban cepat
    st.markdown('<div class="card-title" style="margin-bottom:8px">Jawaban 3 Pertanyaan Utama</div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)

    if len(cat_tbl):
        top1 = cat_tbl.iloc[0]
        a1.markdown(
            f'<div class="ans g1"><div class="ans-q">1 · Produk/kategori omzet tertinggi</div>'
            f'<div class="ans-a">{cat_icon(top1["kategori"])} {esc(str(top1["kategori"]))}</div>'
            f'<div class="ans-d">Omzet {format_short(top1["omzet"])} ({top1["share"]:.0f}% dari total) dari '
            f'{format_int(top1["pesanan"])} pesanan. Runner-up: '
            f'<b>{esc(str(cat_tbl.iloc[1]["kategori"])) if len(cat_tbl) > 1 else "-"}</b>.</div></div>',
            unsafe_allow_html=True,
        )
    if len(yearly) >= 1:
        last = yearly.iloc[-1]
        if len(yearly) >= 2 and pd.notna(last["growth_per_bulan"]):
            arah = "naik" if last["growth_per_bulan"] >= 0 else "turun"
            prev = yearly.iloc[-2]
            desc = (
                f"Rata-rata omzet per bulan {int(last['year'])}: {format_short(last['omzet_per_bulan'])}, "
                f"{arah} {abs(last['growth_per_bulan']):.1f}% dibanding {int(prev['year'])} "
                f"({format_short(prev['omzet_per_bulan'])}/bulan)."
            )
            head = f"{int(last['year'])} {arah} {abs(last['growth_per_bulan']):.0f}%"
        else:
            desc = f"Omzet {int(last['year'])}: {format_short(last['omzet'])} dari {int(last['bulan_aktif'])} bulan data."
            head = f"Tahun {int(last['year'])}"
        a2.markdown(
            f'<div class="ans g2"><div class="ans-q">2 · Tren penjualan tahunan</div>'
            f'<div class="ans-a">{head}</div><div class="ans-d">{desc}</div></div>',
            unsafe_allow_html=True,
        )

    city_all = sorted(sales_nat["kota_kabupaten"].unique().tolist())
    bogor_city = default_city(city_all) if city_all else None
    if bogor_city:
        ex_b = explode_categories(sales_nat[sales_nat["kota_kabupaten"] == bogor_city], alloc_mode)
        cnt_b = ex_b.groupby("kategori")["order_id"].nunique().sort_values(ascending=False)
        if len(cnt_b):
            a3.markdown(
                f'<div class="ans g3"><div class="ans-q">3 · Terlaris di {esc(bogor_city.title())}</div>'
                f'<div class="ans-a">{cat_icon(cnt_b.index[0])} {esc(str(cnt_b.index[0]))}</div>'
                f'<div class="ans-d">Muncul di {format_int(cnt_b.iloc[0])} pesanan. Posisi berikutnya: '
                f'<b>{esc(str(cnt_b.index[1])) if len(cnt_b) > 1 else "-"}</b>.</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.5])
    with left:
        box = card("Vibe Score Bisnis", "Gabungan: tingkat batal, pertumbuhan bulan terakhir, dan retur")
        score = vibe_score(cancel_rate, rev_growth, return_rate)
        title, desc = vibe_label(score)
        with box:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                number=dict(font=dict(size=44, color=INK)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickwidth=0),
                    bar=dict(color=DARK, thickness=0.28),
                    bgcolor="white", borderwidth=0,
                    steps=[dict(range=[0, 35], color="#F7D9D3"), dict(range=[35, 55], color="#FBE7C0"),
                           dict(range=[55, 75], color="#D6E4F0"), dict(range=[75, 100], color="#D2EBDD")],
                ),
            ))
            fig.update_layout(height=230, margin=dict(l=40, r=40, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Inter"))
            show(fig, "vibe_gauge")
            st.markdown(
                f'<div style="text-align:center;font-weight:800;font-size:18px;color:{INK}">{title}</div>'
                f'<div style="text-align:center;font-size:13px;color:{MUTED}">{desc}</div>',
                unsafe_allow_html=True,
            )
    with right:
        box = card("Spill the Tea", "Temuan otomatis dari data yang sedang difilter")
        tea = []
        if len(cat_tbl):
            t0 = cat_tbl.iloc[0]
            tea.append(f"{cat_icon(t0['kategori'])} <b>{esc(str(t0['kategori']))}</b> itu main character-nya: nyumbang <b>{t0['share']:.0f}%</b> omzet ({format_short(t0['omzet'])}).")
        reg = sales.groupby("kota_kabupaten")["order_id"].nunique().sort_values(ascending=False)
        if len(reg):
            tea.append(f"Wilayah paling rajin checkout: <b>{esc(str(reg.index[0]))}</b> dengan {format_int(reg.iloc[0])} pesanan.")
        if not monthly_all.empty:
            best = monthly_all.loc[monthly_all["omzet"].idxmax()]
            tea.append(f"Bulan paling cuan: <b>{month_label(best['month'])}</b> ({format_short(best['omzet'])}).")
        hh = sales.dropna(subset=["hour"])
        if not hh.empty:
            h = int(hh.groupby("hour")["order_id"].nunique().idxmax())
            d = int(hh.groupby("weekday")["order_id"].nunique().idxmax())
            tea.append(f"Prime time belanja: jam <b>{h:02d}.00</b>, hari terfavorit <b>{DAYS_ID[d]}</b>.")
        if base["is_cod"].any():
            cod_share = base["is_cod"].mean() * 100
            cr_cod = base.loc[base["is_cod"], "is_batal"].mean() * 100
            cr_non = base.loc[~base["is_cod"], "is_batal"].mean() * 100
            tea.append(f"{cod_share:.0f}% pesanan pakai COD. Tingkat batal COD <b>{cr_cod:.1f}%</b> vs non-COD <b>{cr_non:.1f}%</b>.")
        if rev_growth is not None:
            arah = "naik" if rev_growth >= 0 else "turun"
            tea.append(f"Omzet bulan terakhir <b>{arah} {abs(rev_growth):.1f}%</b> dibanding bulan sebelumnya.")
        with box:
            for t in tea:
                st.markdown(f'<div class="tea">{t}</div>', unsafe_allow_html=True)

    box = card("Leaderboard Kategori", "Top 5 berdasarkan omzet")
    with box:
        leaderboard(cat_tbl, "kategori", "omzet", format_short, n=5,
                    sub_fn=lambda r: f"{format_int(r['pesanan'])} pesanan")

    with st.expander("Catatan metode (biar nggak salah baca)"):
        st.markdown(
            "- **Dataset tidak punya kolom nama produk**, jadi `product_categories` dipakai sebagai 'produk'.\n"
            "- Satu pesanan bisa berisi beberapa kategori (dipisah koma). Pesanan dipecah per kategori; omzet dibagi "
            "rata (default) atau dikredit penuh, sesuai pilihan di sidebar.\n"
            "- **Tanggal** diambil dari `waktu_pesanan_dibuat` (formatnya konsisten), cadangannya `order_date`. "
            "Ini mencegah ratusan baris hilang karena format tanggal campur aduk.\n"
            "- Penjualan = status yang dipilih di sidebar (default: **Selesai**). Pesanan **Batal** tidak masuk omzet.\n"
            "- Tahun yang datanya tidak penuh 12 bulan dibandingkan lewat **omzet rata-rata per bulan**."
        )


# =========================================================
# HALAMAN 2: CUAN KATEGORI  (Pertanyaan 1)
# =========================================================
elif page == PAGES[1]:
    page_header("Cuan Kategori", "Pertanyaan 1: kategori/produk apa yang menghasilkan pendapatan tertinggi?")
    top_n = st.slider("Tampilkan Top", 5, 20, 10)
    top = cat_tbl.head(top_n)

    left, right = st.columns([1.15, 1])
    with left:
        box = card("Omzet per Kategori", f"Top {top_n} kategori · mode: {alloc_mode.lower()}")
        with box:
            show(hbar(top, "omzet", "kategori", DARK, format_short, icons=True), "cuan_bar")
    with right:
        box = card("Pareto 80/20", "Berapa kategori yang menyumbang mayoritas omzet? (angka di sumbu X = peringkat)")
        with box:
            n_show = min(len(cat_tbl), 15)
            p = cat_tbl.head(n_show).copy()
            p["rank"] = range(1, n_show + 1)
            p["cum"] = cat_tbl["share"].cumsum().head(n_show)
            n80 = int((cat_tbl["share"].cumsum() < 80).sum() + 1)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=p["rank"], y=p["omzet"], name="Omzet", marker_color=DARK, customdata=p["kategori"],
                                 hovertemplate="#%{x} %{customdata}<br>%{y:,.0f}<extra></extra>"), secondary_y=False)
            fig.add_trace(go.Scatter(x=p["rank"], y=p["cum"], name="Kumulatif %", mode="lines+markers",
                                     line=dict(color=COPPER, width=3)), secondary_y=True)
            fig.add_hline(y=80, line_dash="dot", line_color=MUTED, secondary_y=True)
            style_fig(fig, 340, legend=True)
            fig.update_xaxes(dtick=1)
            fig.update_yaxes(range=[0, 105], tickvals=[0, 20, 40, 60, 80, 100], ticksuffix="%", secondary_y=True, showgrid=False)
            fig.update_yaxes(tickformat=".2s", secondary_y=False)
            show(fig, "cuan_pareto")
            st.caption(f"{n80} dari {len(cat_tbl)} kategori sudah menyumbang ±80% omzet.")

    l2, r2 = st.columns([1, 1])
    with l2:
        box = card("Naik Daun vs Turun Kasta", "Perubahan omzet bulan terakhir vs bulan sebelumnya (Top 10 kategori)")
        with box:
            mc = ex_sales.dropna(subset=["month"]).groupby(["month", "kategori"])["omzet_alloc"].sum().reset_index()
            months_ok = monthly_ok["month"].tolist()
            if len(months_ok) >= 2:
                m_last, m_prev = months_ok[-1], months_ok[-2]
                pv = mc.pivot(index="kategori", columns="month", values="omzet_alloc").fillna(0)
                if m_last in pv.columns and m_prev in pv.columns:
                    top_cats = cat_tbl.head(10)["kategori"].tolist()
                    g = pv.loc[pv.index.isin(top_cats), [m_prev, m_last]].copy()
                    g = g[g[m_prev] > 0]
                    g["growth"] = (g[m_last] - g[m_prev]) / g[m_prev] * 100
                    g = g.reset_index()
                    st.caption(f"{month_label(m_last)} dibanding {month_label(m_prev)}")
                    show(hbar(g, "growth", "kategori", GOOD, lambda v: f"{v:+.0f}%", sign_colors=True, pad=1.35, icons=True), "cuan_growth")
                else:
                    st.info("Data bulanan kategori belum cukup.")
            else:
                st.info("Butuh minimal 2 bulan penuh untuk membandingkan.")
    with r2:
        box = card("Duo Maut", "Pasangan kategori yang paling sering dibeli dalam satu pesanan (ide bundling)")
        with box:
            multi = sales[sales["product_categories"].str.contains(",", regex=False)]
            cnt = Counter()
            for s in multi["product_categories"]:
                cats = sorted({c.strip() for c in s.split(",") if c.strip()})
                for pair in combinations(cats, 2):
                    cnt[pair] += 1
            if cnt:
                pairs = pd.DataFrame(
                    [(f"{a} + {b}", v) for (a, b), v in cnt.most_common(10)], columns=["pasangan", "pesanan"]
                )
                show(hbar(pairs, "pesanan", "pasangan", COPPER, format_int, pad=1.2), "cuan_pairs")
            else:
                st.info("Tidak ada pesanan multi-kategori pada filter ini.")

    box = card("Tabel Kategori Lengkap", "Unit = estimasi (total_qty dibagi rata untuk pesanan multi-kategori)")
    with box:
        tbl = cat_tbl.rename(columns={
            "kategori": "Kategori", "omzet": "Omzet", "share": "Kontribusi (%)", "pesanan": "Pesanan",
            "unit": "Estimasi Unit", "omzet_per_pesanan": "Omzet / Pesanan"})
        tbl = tbl[["Kategori", "Omzet", "Kontribusi (%)", "Pesanan", "Estimasi Unit", "Omzet / Pesanan"]].copy()
        tbl["Kategori"] = tbl["Kategori"].map(with_icon)
        tbl["Kontribusi (%)"] = tbl["Kontribusi (%)"].round(1)
        tbl["Estimasi Unit"] = tbl["Estimasi Unit"].round(0)
        tbl["Omzet"] = tbl["Omzet"].round(0)
        tbl["Omzet / Pesanan"] = tbl["Omzet / Pesanan"].round(0)
        st.dataframe(tbl, width="stretch", hide_index=True, height=320)
        st.download_button("Unduh Tabel Kategori (CSV)", tbl.to_csv(index=False).encode("utf-8-sig"),
                           "ringkasan_kategori.csv", "text/csv")


# =========================================================
# HALAMAN 3: TREN PENJUALAN  (Pertanyaan 2)
# =========================================================
elif page == PAGES[2]:
    page_header("Tren Penjualan", "Pertanyaan 2: bagaimana tren penjualan setiap tahun?")

    left, right = st.columns([1, 1.3])
    with left:
        box = card("Omzet per Tahun", "Tahun dengan bulan data lebih sedikit tidak sebanding langsung, lihat tabel di bawah")
        with box:
            if yearly.empty:
                st.info("Data tanggal tidak tersedia.")
            else:
                y = yearly.copy()
                y["tahun"] = y["year"].astype(str)
                fig = go.Figure(go.Bar(
                    x=y["tahun"], y=y["omzet"], marker_color=[PALETTE[i % len(PALETTE)] for i in range(len(y))],
                    text=y["omzet"].map(format_short), textposition="outside", cliponaxis=False))
                fig.update_yaxes(range=[0, y["omzet"].max() * 1.2], showticklabels=False)
                show(style_fig(fig, 320), "tren_year")
    with right:
        box = card("Tahun vs Tahun per Bulan", "Satu garis = satu tahun, supaya pola musiman kelihatan")
        with box:
            f = sales.dropna(subset=["dt"]).copy()
            if f.empty:
                st.info("Data tanggal tidak tersedia.")
            else:
                f["mon"] = f["dt"].dt.month
                yy = f.groupby(["year", "mon"])["total_pembayaran"].sum().reset_index()
                fig = go.Figure()
                for i, (yr, grp) in enumerate(yy.groupby("year")):
                    fig.add_trace(go.Scatter(
                        x=[MONTHS_ID[m - 1] for m in grp["mon"]], y=grp["total_pembayaran"], name=str(int(yr)),
                        mode="lines+markers", line=dict(color=PALETTE[i % len(PALETTE)], width=3)))
                fig.update_xaxes(categoryorder="array", categoryarray=MONTHS_ID)
                fig.update_yaxes(tickformat=".2s")
                show(style_fig(fig, 320, legend=True), "tren_yoy")

    box = card("Tabel Perbandingan Tahunan", "Pembanding yang adil = omzet rata-rata per bulan aktif")
    with box:
        if not yearly.empty:
            t = yearly.rename(columns={
                "year": "Tahun", "pesanan": "Pesanan", "omzet": "Omzet", "bulan_aktif": "Bulan Data",
                "omzet_per_bulan": "Omzet / Bulan", "growth_per_bulan": "Growth Omzet/Bulan (%)"}).copy()
            t["Omzet"] = t["Omzet"].round(0)
            t["Omzet / Bulan"] = t["Omzet / Bulan"].round(0)
            t["Growth Omzet/Bulan (%)"] = t["Growth Omzet/Bulan (%)"].round(1)
            st.dataframe(t, width="stretch", hide_index=True)
            tiny = yearly[yearly["bulan_aktif"] <= 2]
            if len(tiny):
                st.caption("Tahun dengan ≤2 bulan data sebaiknya dibaca hati-hati; kemungkinan hanya sisa transaksi di batas periode.")

    box = card("Ikhtisar Penjualan", "Omzet (atas) dan jumlah pesanan (bawah) pada rentang pilihanmu")
    with box:
        gran = st.radio("Rentang", ["Harian", "Mingguan", "Bulanan"], index=2, horizontal=True, label_visibility="collapsed")
        freq = {"Harian": "D", "Mingguan": "W", "Bulanan": "MS"}[gran]
        ts = sales.dropna(subset=["dt"]).set_index("dt")
        if ts.empty:
            st.info("Data tanggal tidak tersedia.")
        else:
            agg = ts.groupby(pd.Grouper(freq=freq)).agg(
                omzet=("total_pembayaran", "sum"), pesanan=("order_id", "nunique")).reset_index()
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.62, 0.38])
            fig.add_trace(go.Scatter(x=agg["dt"], y=agg["omzet"], name="Omzet", mode="lines+markers",
                                     line=dict(color=DARK, width=3, shape="spline"), marker=dict(size=5),
                                     fill="tozeroy", fillcolor="rgba(78,52,46,.12)"), row=1, col=1)
            fig.add_trace(go.Bar(x=agg["dt"], y=agg["pesanan"], name="Pesanan", marker_color=TAN), row=2, col=1)
            style_fig(fig, 460, legend=True)
            fig.update_yaxes(tickformat=".2s", row=1, col=1)
            show(fig, "tren_main")

    l2, r2 = st.columns(2)
    with l2:
        box = card("Pertumbuhan Bulan ke Bulan", "Hijau = naik, merah = turun (bulan penuh saja)")
        with box:
            if len(monthly_ok) >= 2:
                g = monthly_ok.copy()
                g["growth"] = g["omzet"].pct_change() * 100
                g = g.dropna(subset=["growth"])
                fig = go.Figure(go.Bar(
                    x=[month_label(m) for m in g["month"]], y=g["growth"],
                    marker_color=[GOOD if v >= 0 else BAD for v in g["growth"]],
                    text=[f"{v:+.0f}%" for v in g["growth"]], textposition="outside", cliponaxis=False))
                lo, hi = float(g["growth"].min()), float(g["growth"].max())
                fig.update_yaxes(range=[min(0, lo * 1.3) - 5, max(0, hi * 1.3) + 5], ticksuffix="%")
                fig.update_xaxes(tickangle=-45)
                show(style_fig(fig, 340), "tren_mom")
            else:
                st.info("Butuh minimal 2 bulan penuh.")
    with r2:
        box = card("Proyeksi Kasar 3 Bulan ke Depan", "Garis tren linear dari ≤6 bulan penuh terakhir. Bukan ramalan pasti!")
        with box:
            if len(monthly_ok) >= 3:
                recent = monthly_ok.tail(6).reset_index(drop=True)
                xs = np.arange(len(recent))
                slope, intercept = np.polyfit(xs, recent["omzet"].values, 1)
                fut_x = np.arange(len(recent), len(recent) + 3)
                fut_months = [recent["month"].iloc[-1] + pd.DateOffset(months=i + 1) for i in range(3)]
                fut_y = np.maximum(slope * fut_x + intercept, 0)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=monthly_ok["month"], y=monthly_ok["omzet"], name="Aktual", mode="lines+markers",
                                         line=dict(color=DARK, width=3)))
                fig.add_trace(go.Scatter(x=[recent["month"].iloc[-1]] + fut_months,
                                         y=[recent["omzet"].iloc[-1]] + list(fut_y), name="Proyeksi",
                                         mode="lines+markers", line=dict(color=COPPER, width=3, dash="dash")))
                fig.update_yaxes(tickformat=".2s")
                show(style_fig(fig, 340, legend=True), "tren_forecast")
                arah = "naik" if slope >= 0 else "turun"
                st.caption(f"Tren {arah} ±{format_short(abs(slope))} per bulan. Proyeksi {month_label(fut_months[0])}: {format_short(fut_y[0])}.")
            else:
                st.info("Butuh minimal 3 bulan penuh untuk proyeksi.")


# =========================================================
# HALAMAN 4: KABUPATEN BOGOR  (Pertanyaan 3)
# =========================================================
elif page == PAGES[3]:
    page_header("Kabupaten Bogor", "Pertanyaan 3: kategori apa yang paling banyak dibeli di wilayah ini? (bisa ganti wilayah)")

    c1, c2, c3 = st.columns([1.3, 1.2, 1])
    city_list = sorted(sales_nat["kota_kabupaten"].unique().tolist())
    pick = c1.selectbox("Pilih wilayah", city_list, index=city_list.index(default_city(city_list)))
    metric = c2.radio("Ukur berdasarkan", ["Jumlah pesanan", "Estimasi unit", "Omzet"], horizontal=True)
    topn = c3.slider("Tampilkan Top", 5, 15, 10)

    loc = sales_nat[sales_nat["kota_kabupaten"] == pick]
    if loc.empty:
        st.warning("Tidak ada transaksi untuk wilayah ini pada filter sekarang.")
        st.stop()
    ex_loc = explode_categories(loc, alloc_mode)
    ex_nat = explode_categories(sales_nat, alloc_mode)
    loc_tbl = category_table(ex_loc)
    nat_tbl = category_table(ex_nat)
    mcol = {"Jumlah pesanan": "pesanan", "Estimasi unit": "unit", "Omzet": "omzet"}[metric]
    mfmt = format_short if metric == "Omzet" else format_int

    rank_city = sales_nat.groupby("kota_kabupaten")["order_id"].nunique().sort_values(ascending=False)
    rank_pos = int(list(rank_city.index).index(pick) + 1)
    k = st.columns(4)
    kpi(k[0], "Pesanan Selesai", format_int(loc["order_id"].nunique()), f"peringkat #{rank_pos} dari {len(rank_city)} wilayah")
    kpi(k[1], "Omzet", format_short(loc["total_pembayaran"].sum()))
    kpi(k[2], "Barang Terjual", format_int(loc["total_qty"].sum()), f"{int(loc['total_qty'].isna().sum())} baris tanpa qty")
    best_cat = loc_tbl.sort_values("pesanan", ascending=False).iloc[0]["kategori"]
    kpi(k[3], "Kategori Terlaris", cat_icon(best_cat) + " " + esc(shorten(best_cat, 22)), "berdasarkan jumlah pesanan")
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        box = card(f"Kategori Terlaris — {metric}", f"Top {topn} di {pick.title()}")
        with box:
            show(hbar(loc_tbl.sort_values(mcol, ascending=False).head(topn), mcol, "kategori", DARK, mfmt, icons=True), "bogor_bar")
    with right:
        box = card("Indeks Kegemaran", "Seberapa lebih doyan wilayah ini dibanding rata-rata nasional (1× = sama; >1× = lebih doyan)")
        with box:
            loc_share = loc_tbl.set_index("kategori")["pesanan"] / loc_tbl["pesanan"].sum()
            nat_share = nat_tbl.set_index("kategori")["pesanan"] / nat_tbl["pesanan"].sum()
            idx = (loc_share / nat_share).dropna()
            idx = idx[loc_tbl.set_index("kategori").loc[idx.index, "pesanan"] >= 10]
            idx_df = idx.sort_values(ascending=False).head(topn).reset_index()
            idx_df.columns = ["kategori", "indeks"]
            if idx_df.empty:
                st.info("Belum cukup data (minimal 10 pesanan per kategori).")
            else:
                fig = hbar(idx_df, "indeks", "kategori", COPPER, lambda v: f"{v:.1f}×", pad=1.25, icons=True)
                fig.add_vline(x=1, line_dash="dash", line_color=MUTED)
                show(fig, "bogor_index")
                st.caption("Hanya kategori dengan ≥10 pesanan di wilayah ini yang dihitung.")

    l2, r2 = st.columns([1.1, 1])
    with l2:
        box = card("Unit Pasti: Pesanan 1 Kategori", "Jumlah barang yang akurat per kategori (pesanan campuran dikeluarkan)")
        with box:
            single = loc[~loc["product_categories"].str.contains(",", regex=False) & loc["total_qty"].notna()]
            if single.empty:
                st.info("Tidak ada pesanan satu kategori.")
            else:
                s = single.groupby("product_categories").agg(
                    total_barang=("total_qty", "sum"), pesanan=("order_id", "nunique")).reset_index()
                s = s.sort_values("total_barang", ascending=False).head(topn)
                s.columns = ["Kategori", "Total Barang", "Pesanan"]
                s["Kategori"] = s["Kategori"].map(with_icon)
                s["Total Barang"] = s["Total Barang"].round(0)
                st.dataframe(s, width="stretch", hide_index=True, height=360)
    with r2:
        box = card("Peringkat Wilayah", "10 wilayah dengan pesanan terbanyak (wilayah pilihanmu disorot pink)")
        with box:
            rc = rank_city.head(10).reset_index()
            rc.columns = ["wilayah", "pesanan"]
            if pick not in rc["wilayah"].values:
                rc = pd.concat([rc.head(9), pd.DataFrame({"wilayah": [pick], "pesanan": [rank_city[pick]]})])
            show(hbar(rc, "pesanan", "wilayah", SLATE, format_int, highlight=pick, height=400), "bogor_rank")


# =========================================================
# HALAMAN 5: PETA WILAYAH (GEOSPASIAL)
# =========================================================
elif page == PAGES[4]:
    page_header("Peta Wilayah", "Sebaran omzet, pesanan, dan barang terjual di seluruh Indonesia. Bubble makin besar = nilai makin tinggi.")

    c1, c2, c3 = st.columns([1.1, 1.3, 1])
    level = c1.radio("Tingkat wilayah", ["Provinsi", "Kota/Kabupaten"], horizontal=True)
    metric = c2.radio("Ukuran bubble", ["Omzet", "Pesanan", "Barang terjual"], horizontal=True)
    top_n = c3.slider("Peringkat Top", 5, 20, 10)
    geo_key = "provinsi" if level == "Provinsi" else "kota_kabupaten"
    mcol = {"Omzet": "omzet", "Pesanan": "pesanan", "Barang terjual": "barang"}[metric]
    mfmt = format_short if metric == "Omzet" else format_int

    with st.expander("Wilayah tidak muncul di peta? Unggah CSV koordinat sendiri"):
        st.caption("Kolom yang dibaca: nama wilayah (kota_kabupaten atau provinsi), lat, lon. "
                   "Koordinat bawaan mencakup semua provinsi dan sekitar 150 kota/kabupaten besar.")
        geo_file = st.file_uploader("CSV koordinat", type=["csv"], key="geo_csv")
    custom = load_custom_geo(geo_file)

    g = sales.groupby(geo_key).agg(
        omzet=("total_pembayaran", "sum"), pesanan=("order_id", "nunique"), barang=("total_qty", "sum")
    ).reset_index()
    coords = [geo_lookup(v, level, custom) for v in g[geo_key]]
    g["lat"] = [c[0] for c in coords]
    g["lon"] = [c[1] for c in coords]
    mapped = g.dropna(subset=["lat", "lon"]).copy()
    unmapped = g[g["lat"].isna()]
    omzet_g = g["omzet"].sum()
    cover = mapped["omzet"].sum() / omzet_g * 100 if omzet_g else 0
    top_row = g.sort_values(mcol, ascending=False).iloc[0]

    k = st.columns(4)
    kpi(k[0], "Wilayah Terpetakan", f"{len(mapped)} dari {len(g)}")
    kpi(k[1], "Cakupan Omzet di Peta", format_pct(cover))
    kpi(k[2], f"Teratas ({metric})", esc(shorten(str(top_row[geo_key]).title(), 22)), mfmt(top_row[mcol]))
    kpi(k[3], "Rata-rata Omzet / Wilayah", format_short(g["omzet"].mean()))
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if True:
        box = card(f"Peta Sebaran {metric}", f"Per {level.lower()}; arahkan kursor ke bubble untuk detail")
        with box:
            if mapped.empty:
                st.info("Belum ada wilayah yang punya koordinat. Unggah CSV koordinat di atas.")
            else:
                vals = mapped[mcol].fillna(0).clip(lower=0).astype(float)
                vmax = float(vals.max()) or 1.0
                sizes = 8 + 40 * np.sqrt(vals / vmax)
                text_hover = [
                    f"<b>{str(r[geo_key]).title()}</b><br>Omzet: {format_rp(r['omzet'])}"
                    f"<br>Pesanan: {format_int(r['pesanan'])}<br>Barang: {format_int(r['barang'])}"
                    for _, r in mapped.iterrows()
                ]
                fig = go.Figure()
                if level == "Provinsi":
                    land_ok = add_land(fig, g, geo_key, mcol, mfmt, metric)
                else:
                    land_ok = add_land(fig)
                if not land_ok:
                    st.warning("File indonesia_provinsi.geojson tidak ditemukan di folder app.py, jadi batas wilayah belum bisa digambar.")
                fig.add_trace(map_trace(mapped["lat"], mapped["lon"], sizes, "#22D3EE" if level == "Provinsi" else "#FFB000", text_hover))
                show(map_layout(fig, 430), "peta_utama")
    left, right = st.columns([1, 1])
    with left:
        box = card(f"Peringkat {level}", f"Top {top_n} berdasarkan {metric.lower()}")
        with box:
            rk = g.assign(label=g[geo_key].str.title()).sort_values(mcol, ascending=False).head(top_n)
            show(hbar(rk, mcol, "label", DARK, mfmt, height=max(300, 40 * top_n + 60), pad=1.7), "peta_rank")
    with right:
        box = card(f"Tabel {level}", "Semua wilayah, diurutkan menurut " + metric.lower())
        with box:
            tb = g[[geo_key, "omzet", "pesanan", "barang"]].sort_values(mcol, ascending=False).copy()
            tb[geo_key] = tb[geo_key].str.title()
            tb["omzet"] = tb["omzet"].round(0)
            tb["barang"] = tb["barang"].round(0)
            tb.columns = [level, "Omzet", "Pesanan", "Barang"]
            st.dataframe(tb, width="stretch", hide_index=True, height=max(300, 40 * top_n + 60))

    box = card(f"Kategori Terlaris per {level}", "Warna bubble = kategori dengan pesanan terbanyak di wilayah itu; ukuran = jumlah pesanan")
    with box:
        if mapped.empty:
            st.info("Belum ada wilayah yang punya koordinat.")
        else:
            cnt = ex_sales.groupby([geo_key, "kategori"])["order_id"].nunique().reset_index(name="n")
            dom = cnt.loc[cnt.groupby(geo_key)["n"].idxmax()]
            dom = dom.merge(mapped[[geo_key, "lat", "lon", "pesanan"]], on=geo_key, how="inner")
            pmax = float(dom["pesanan"].max()) or 1.0
            fig = go.Figure()
            add_land(fig)
            for i, cat in enumerate(dom["kategori"].value_counts().index.tolist()):
                part = dom[dom["kategori"] == cat]
                sz = 8 + 34 * np.sqrt(part["pesanan"] / pmax)
                txt = [f"<b>{str(r[geo_key]).title()}</b><br>Terlaris: {cat}<br>Pesanan wilayah: {format_int(r['pesanan'])}"
                       for _, r in part.iterrows()]
                fig.add_trace(map_trace(part["lat"], part["lon"], sz, MAP_BRIGHT[i % len(MAP_BRIGHT)], txt, name=cat))
            show(map_layout(fig, 470, legend=True), "peta_kategori")

    if len(unmapped):
        with st.expander(f"{len(unmapped)} wilayah belum punya koordinat"):
            miss = unmapped[[geo_key, "pesanan", "omzet"]].sort_values("pesanan", ascending=False)
            miss.columns = ["Wilayah", "Pesanan", "Omzet"]
            st.dataframe(miss, width="stretch", hide_index=True, height=260)


# =========================================================
# HALAMAN 6: JAM & TANGGAL CUAN
# =========================================================
elif page == PAGES[5]:
    page_header("Jam & Tanggal Cuan", "Kapan pembeli paling rajin checkout? Cek prime time, tanggal kembar, dan efek gajian.")
    dd = sales.dropna(subset=["dt"]).copy()
    if dd.empty:
        st.info("Data tanggal tidak tersedia.")
        st.stop()

    box = card("Peta Panas Prime Time", "Jumlah pesanan berdasarkan hari × jam (warna makin pekat = makin ramai)")
    with box:
        hm = dd.groupby(["weekday", "hour"])["order_id"].nunique().unstack(fill_value=0)
        hm = hm.reindex(index=range(7), columns=range(24), fill_value=0)
        fig = go.Figure(go.Heatmap(
            z=hm.values, x=[f"{h:02d}" for h in range(24)], y=DAYS_ID,
            colorscale=[[0, "#F1F5F5"], [0.5, "#F2A541"], [1, "#C23B22"]],
            colorbar=dict(title="Pesanan", thickness=12),
            hovertemplate="%{y} jam %{x}.00<br>%{z} pesanan<extra></extra>"))
        style_fig(fig, 340)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(title_text="Jam", dtick=1)
        show(fig, "jam_heat")
        top_h = int(dd.groupby("hour")["order_id"].nunique().idxmax())
        top_d = int(dd.groupby("weekday")["order_id"].nunique().idxmax())
        st.caption(f"Puncak pesanan di jam {top_h:02d}.00 dan hari {DAYS_ID[top_d]}. Cocok buat jadwal flash sale atau posting promo.")

    per_day = dd.groupby(dd["dt"].dt.normalize()).agg(
        pesanan=("order_id", "nunique"), omzet=("total_pembayaran", "sum")).reset_index()
    per_day.columns = ["tgl", "pesanan", "omzet"]
    per_day["day"] = per_day["tgl"].dt.day
    per_day["mon"] = per_day["tgl"].dt.month
    per_day["grup"] = np.where(
        per_day["day"] == per_day["mon"], "Tanggal kembar",
        np.where((per_day["day"] >= 25) | (per_day["day"] <= 5), "Gajian (25–5)", "Tanggal biasa"))

    l, r = st.columns(2)
    with l:
        box = card("Efek Tanggal Kembar & Gajian", "Rata-rata pesanan per hari menurut jenis tanggal")
        with box:
            g = per_day.groupby("grup").agg(rata_pesanan=("pesanan", "mean"), hari=("tgl", "count")).reset_index()
            cmap = {"Tanggal kembar": COPPER, "Gajian (25–5)": TAN, "Tanggal biasa": DARK}
            fig = go.Figure(go.Bar(
                x=g["grup"], y=g["rata_pesanan"], marker_color=[cmap[v] for v in g["grup"]],
                text=[f"{v:.0f}" for v in g["rata_pesanan"]], textposition="outside", cliponaxis=False,
                customdata=g["hari"], hovertemplate="%{x}<br>%{y:.1f} pesanan/hari (%{customdata} hari)<extra></extra>"))
            fig.update_yaxes(range=[0, g["rata_pesanan"].max() * 1.25], showticklabels=False)
            show(style_fig(fig, 320), "jam_twin")
            if {"Tanggal kembar", "Tanggal biasa"} <= set(g["grup"]):
                a = g.set_index("grup")["rata_pesanan"]
                diff = (a["Tanggal kembar"] / a["Tanggal biasa"] - 1) * 100
                st.caption(f"Tanggal kembar rata-rata {diff:+.0f}% dibanding tanggal biasa.")
    with r:
        box = card("Pesanan per Tanggal dalam Bulan", "Rata-rata pesanan per hari menurut tanggal (oranye = periode gajian)")
        with box:
            dm = per_day.groupby("day")["pesanan"].mean().reset_index()
            fig = go.Figure(go.Bar(
                x=dm["day"], y=dm["pesanan"],
                marker_color=[TAN if (d >= 25 or d <= 5) else DARK for d in dm["day"]],
                hovertemplate="Tanggal %{x}<br>%{y:.1f} pesanan<extra></extra>"))
            fig.update_xaxes(dtick=1, tickangle=0)
            show(style_fig(fig, 320), "jam_dom")

    box = card("Hari Terbaik dalam Seminggu", "Total omzet per hari")
    with box:
        wd = dd.groupby("weekday")["total_pembayaran"].sum().reindex(range(7), fill_value=0).reset_index()
        wd["hari"] = [DAYS_ID[i] for i in wd["weekday"]]
        fig = go.Figure(go.Bar(
            x=wd["hari"], y=wd["total_pembayaran"], marker_color=PALETTE[: 7] if len(PALETTE) >= 7 else DARK,
            text=wd["total_pembayaran"].map(format_short), textposition="outside", cliponaxis=False))
        fig.update_yaxes(range=[0, wd["total_pembayaran"].max() * 1.2], showticklabels=False)
        show(style_fig(fig, 300), "jam_wd")


# =========================================================
# HALAMAN 6: BAYAR, KIRIM & BATAL
# =========================================================
elif page == PAGES[6]:
    page_header("Bayar, Kirim & Batal", "Metode bayar favorit, opsi pengiriman, dan kenapa pesanan batal.")
    disc_total = sales["total_diskon"].sum()
    cod_share = base["is_cod"].mean() * 100 if len(base) else 0
    k = st.columns(4)
    kpi(k[0], "Tingkat Batal", format_pct(cancel_rate), f"{format_int(base['is_batal'].sum())} pesanan batal")
    kpi(k[1], "Total Diskon", format_short(disc_total))
    kpi(k[2], "Diskon / Omzet", format_pct(disc_total / total_rev * 100 if total_rev else 0))
    kpi(k[3], "Pesanan COD", format_pct(cod_share), "dari semua pesanan")
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    def cancel_by(col, min_n=30):
        g = base.groupby(col).agg(total=("order_id", "nunique"), batal=("is_batal", "sum")).reset_index()
        g = g[g["total"] >= min_n].copy()
        g["rate"] = g["batal"] / g["total"] * 100
        return g

    l, r = st.columns(2)
    with l:
        box = card("Metode Pembayaran Favorit", "Porsi pesanan penjualan valid")
        with box:
            pm = sales["metode_pembayaran"].value_counts()
            if len(pm) > 6:
                pm = pd.concat([pm.head(6), pd.Series({"Lainnya": pm.iloc[6:].sum()})])
            pm_df = pm.reset_index()
            pm_df.columns = ["Metode", "Jumlah"]
            fig = px.pie(pm_df, names="Metode", values="Jumlah", hole=0.55, color_discrete_sequence=PALETTE)
            fig.update_traces(textinfo="percent", textposition="inside", sort=False)
            fig.update_layout(uniformtext_minsize=11, uniformtext_mode="hide")
            style_fig(fig, 360, legend=True)
            fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="left", x=0, font=dict(size=11)))
            show(fig, "bayar_pie")
    with r:
        box = card("Tingkat Batal per Metode Bayar", "Hanya metode dengan ≥30 pesanan")
        with box:
            cb = cancel_by("metode_pembayaran")
            if cb.empty:
                st.info("Data belum cukup.")
            else:
                show(hbar(cb, "rate", "metode_pembayaran", BAD, lambda v: f"{v:.1f}%", pad=1.25), "bayar_cancel")

    l2, r2 = st.columns(2)
    with l2:
        box = card("Tingkat Batal per Opsi Pengiriman", "Hanya opsi dengan ≥30 pesanan")
        with box:
            cs = cancel_by("opsi_pengiriman")
            if cs.empty:
                st.info("Data belum cukup.")
            else:
                show(hbar(cs, "rate", "opsi_pengiriman", TAN, lambda v: f"{v:.1f}%", pad=1.25), "kirim_cancel")
    with r2:
        box = card("Alasan Pembatalan Terbanyak", "Top 8 dari pesanan batal")
        with box:
            cr = base[base["is_batal"]]["alasan_pembatalan"].value_counts().head(8).reset_index()
            cr.columns = ["alasan", "jumlah"]
            if cr.empty:
                st.info("Tidak ada data pembatalan.")
            else:
                cr["alasan"] = cr["alasan"].map(lambda v: shorten(v, 44))
                show(hbar(cr, "jumlah", "alasan", COPPER, format_int, pad=1.2), "batal_reason")

    box = card("Tingkat Batal per Bulan")
    with box:
        mc = base.dropna(subset=["month"]).groupby("month")["is_batal"].mean().mul(100).reset_index()
        if mc.empty:
            st.info("Data tanggal tidak tersedia.")
        else:
            fig = go.Figure(go.Scatter(x=mc["month"], y=mc["is_batal"], mode="lines+markers",
                                       line=dict(color=BAD, width=3), marker=dict(size=7)))
            fig.update_yaxes(ticksuffix="%")
            show(style_fig(fig, 300), "batal_month")


# =========================================================
# HALAMAN 7: DATA TRANSAKSI
# =========================================================
else:
    page_header("Data Transaksi", "Telusuri, cari, dan unduh data hasil filter.")
    box = card("Detail Data Penjualan")
    with box:
        q = st.text_input("Cari transaksi", placeholder="Ketik kategori, wilayah, atau ID pesanan…")
        cols = [c for c in [
            "order_id", "dt", "product_categories", "total_qty", "total_pembayaran", "status_group", "kota_kabupaten",
            "provinsi", "metode_pembayaran", "opsi_pengiriman", "total_diskon"] if c in sales.columns]
        visible = sales[cols].rename(columns={"dt": "waktu_pesanan"})
        if q.strip():
            mask = visible.astype(str).apply(lambda s: s.str.contains(q.strip(), case=False, na=False, regex=False)).any(axis=1)
            visible = visible[mask]
        st.caption(f"{format_int(len(visible))} baris ditampilkan dari {format_int(len(sales))} baris penjualan.")
        st.dataframe(visible, width="stretch", height=480, hide_index=True)
        st.download_button("Unduh Data Hasil Filter (CSV)", visible.to_csv(index=False).encode("utf-8-sig"),
                           "data_penjualan_terfilter.csv", "text/csv")