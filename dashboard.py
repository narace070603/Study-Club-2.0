"""
NusaCommerce • Vibe Dashboard
Dashboard Streamlit untuk menjawab 3 pertanyaan bisnis + analisis tambahan ala Gen Z.

Jalankan:  streamlit run app.py
Letakkan data.zip (atau CSV hasil cleaning) di folder yang sama, atau unggah lewat sidebar.
"""
import calendar
import io
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
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

VIOLET = "#7C3AED"
PINK = "#EC4899"
LIME = "#65A30D"
CYAN = "#06B6D4"
ORANGE = "#FB923C"
RED = "#EF4444"
INK = "#1F1B3A"
MUTED = "#5B5780"
PALETTE = [VIOLET, PINK, CYAN, ORANGE, "#10B981", "#6366F1", "#F43F5E", "#84CC16"]
MONTHS_ID = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
DAYS_ID = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
MEDALS = ["👑", "🥈", "🥉"]
BADGES = ["Main Character", "Bestie Setia", "Si Paling Laku"]
GROUP_ORDER = ["Selesai", "Diterima (masa retur)", "Dalam pengiriman", "Lainnya", "Batal"]


# =========================
# STYLE
# =========================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html, body, .stApp, .stMarkdown, p, label, button, input, textarea, h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp { background: linear-gradient(135deg, #FFF1F9 0%, #F1ECFF 48%, #E3F6FF 100%); }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px; }

/* teks area utama */
[data-testid="stMain"] label p { color: __INK__; font-weight: 700; font-size: 13px; }
[data-testid="stMain"] [data-testid="stCaptionContainer"] * { color: __MUTED__; }

/* kartu (st.container border) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.86);
    border: 1px solid #E8E1FA !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 26px rgba(76,29,149,.08);
}
.card-title { font-size: 16px; font-weight: 800; color: __INK__; margin: 2px 0 0 0; }
.card-sub { font-size: 12.5px; color: __MUTED__; font-weight: 500; margin: 2px 0 10px 0; }

/* sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #2A1B5E 0%, #1F1B3A 100%); border-right: none; }
[data-testid="stSidebar"] * { color: #FFFFFF; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: __INK__ !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] section { background: rgba(255,255,255,.12); }
[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
[data-testid="stSidebar"] [data-testid="stFileUploader"] button { color: __INK__ !important; }
.brand { display:flex; align-items:center; gap:12px; padding:10px 12px; background: rgba(255,255,255,.12);
         border-radius:16px; margin-bottom:14px; }
.brand-avatar { width:42px; height:42px; border-radius:14px; background: linear-gradient(135deg,#EC4899,#F59E0B);
                display:flex; align-items:center; justify-content:center; font-size:22px; flex-shrink:0; }
.brand-name { font-weight:800; font-size:14px; line-height:1.2; }
.brand-role { font-size:11px; opacity:.85; }
.side-label { font-size:11px; text-transform:uppercase; letter-spacing:.8px; opacity:.9;
              margin:18px 0 6px 2px; font-weight:800; }
[data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding:10px 14px; border-radius:12px; width:100%;
    cursor:pointer; transition: background .15s; }
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background: rgba(255,255,255,.12); }
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display:none; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, #EC4899, #8B5CF6); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * { font-weight: 800; }

/* judul halaman */
.page-title { font-size: 32px; font-weight: 800; letter-spacing: -.5px; margin: 0; line-height: 1.2;
    background: linear-gradient(90deg, #7C3AED, #EC4899); -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; background-clip: text; width: fit-content; }
.page-sub { color: __MUTED__; font-size: 14px; font-weight: 500; margin: 4px 0 18px 0; }

/* KPI */
.kpi { background: rgba(255,255,255,.9); border: 1px solid #E8E1FA; border-radius: 20px; padding: 14px 16px;
       box-shadow: 0 8px 26px rgba(76,29,149,.08); display:flex; gap:12px; align-items:center; min-height: 96px; }
.kpi-icon { width:46px; height:46px; border-radius:14px; display:flex; align-items:center; justify-content:center;
            font-size:22px; flex-shrink:0; }
.kpi-body { min-width:0; flex:1; }
.kpi-title { font-size:12px; color:__MUTED__; font-weight:700; }
.kpi-value { font-size:22px; font-weight:800; color:__INK__; line-height:1.2; overflow-wrap:anywhere; }
.kpi-sub { font-size:11.5px; font-weight:700; color:__MUTED__; }
.up { color:#16A34A; } .down { color:#DC2626; } .flat { color:__MUTED__; }

/* kartu jawaban */
.ans { border-radius: 20px; padding: 16px 18px; min-height: 190px; color: #fff; display:flex; flex-direction:column;
       gap:6px; box-shadow: 0 10px 28px rgba(76,29,149,.16); }
.ans-q { font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing:.6px; opacity:.92; }
.ans-a { font-size: 21px; font-weight: 800; line-height: 1.2; overflow-wrap:anywhere; }
.ans-d { font-size: 13px; font-weight: 500; line-height: 1.45; opacity: .96; overflow-wrap:anywhere; }
.g1 { background: linear-gradient(135deg, #7C3AED, #C084FC); }
.g2 { background: linear-gradient(135deg, #EC4899, #FB923C); }
.g3 { background: linear-gradient(135deg, #0891B2, #22D3EE); }

/* leaderboard */
.lb { display:grid; grid-template-columns: 34px minmax(0,1fr) auto; gap:12px; align-items:center;
      padding:10px 12px; border:1px solid #EEE8FB; border-radius:14px; margin-bottom:8px; background:#FCFAFF; }
.lb-rank { font-size:18px; text-align:center; font-weight:800; color:__MUTED__; }
.lb-name { font-weight:700; font-size:13.5px; color:__INK__; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.lb-badge { font-size:11px; font-weight:700; color:__MUTED__; }
.lb-bar { height:6px; border-radius:6px; background:#EDE9FE; margin-top:6px; overflow:hidden; }
.lb-bar > div { height:100%; background: linear-gradient(90deg, #7C3AED, #EC4899); border-radius:6px; }
.lb-val { text-align:right; font-weight:800; font-size:14px; color:__INK__; white-space:nowrap; }
.lb-val small { display:block; font-weight:600; color:__MUTED__; font-size:11px; }

/* insight */
.tea { background:#FFF7ED; border-left:5px solid #EC4899; border-radius:12px; padding:10px 14px;
       margin-bottom:8px; font-size:13.5px; color:#4A2B1B; line-height:1.5; overflow-wrap:anywhere; }

/* tombol */
div.stDownloadButton > button, div.stButton > button {
    background: linear-gradient(90deg, #7C3AED, #EC4899); color:#fff; font-weight:800; border:none;
    border-radius:12px; padding:10px 22px; }
div.stDownloadButton > button:hover { filter: brightness(1.08); color:#fff; }
</style>
"""


def inject_css():
    css = CSS.replace("__INK__", INK).replace("__MUTED__", MUTED)
    st.markdown(css, unsafe_allow_html=True)


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
    st.markdown(f'<div class="page-title">{title}</div><div class="page-sub">{sub}</div>', unsafe_allow_html=True)


def kpi(col, icon, bg, title, value, sub=""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    col.markdown(
        f'<div class="kpi"><div class="kpi-icon" style="background:{bg}">{icon}</div>'
        f'<div class="kpi-body"><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value">{value}</div>{sub_html}</div></div>',
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
        font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color=INK, size=12),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="left", x=0, title_text=""),
        hoverlabel=dict(font_family="Plus Jakarta Sans"),
    )
    fig.update_xaxes(showgrid=False, title_text="", automargin=True, linecolor="#E5E0F5")
    fig.update_yaxes(gridcolor="#ECE8FA", title_text="", zeroline=False, automargin=True)
    return fig


def show(fig, key):
    st.plotly_chart(fig, width="stretch", key=key)


def hbar(data, value, label, color, fmt, height=None, pad=1.3, highlight=None, sign_colors=False):
    """Bar horizontal rapi: label dipotong, angka di luar bar, ruang kanan disiapkan."""
    d = data.sort_values(value, ascending=True).copy()
    labels = d[label].astype(str).map(lambda v: shorten(v, 34))
    if labels.duplicated().any():
        labels = d[label].astype(str)
    if sign_colors:
        colors = [LIME if v >= 0 else RED for v in d[value]]
    elif highlight is not None:
        colors = [PINK if str(v) == str(highlight) else color for v in d[label]]
    else:
        colors = color
    vmax = float(d[value].max()) if len(d) else 1.0
    vmin = float(d[value].min()) if len(d) else 0.0
    fig = go.Figure(
        go.Bar(
            x=d[value], y=labels, orientation="h", marker_color=colors,
            text=d[value].map(fmt), textposition="outside", cliponaxis=False,
            customdata=d[label].astype(str), hovertemplate="<b>%{customdata}</b><br>%{text}<extra></extra>",
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
    for i, (_, r) in enumerate(top.iterrows()):
        medal = MEDALS[i] if i < len(MEDALS) else f"#{i + 1}"
        badge = BADGES[i] if i < len(BADGES) else "Anak Emas"
        sub = f"<small>{sub_fn(r)}</small>" if sub_fn else ""
        pct = max(4, float(r[value_col]) / mx * 100)
        html += (
            f'<div class="lb"><div class="lb-rank">{medal}</div>'
            f'<div style="min-width:0"><div class="lb-name" title="{esc(str(r[label_col]))}">{esc(str(r[label_col]))}</div>'
            f'<div class="lb-badge">{badge}</div><div class="lb-bar"><div style="width:{pct:.0f}%"></div></div></div>'
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


@st.cache_data(show_spinner="Lagi nyiapin data… ✨")
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
    x = frame[["order_id", "product_categories", "total_pembayaran", "total_qty", "kota_kabupaten", "month"]].copy()
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
        return "SLAY 💅", "Bisnis lagi glowing banget!"
    if score >= 55:
        return "Aman Jaya 😎", "Vibes-nya oke, tinggal dipoles dikit."
    if score >= 35:
        return "Mid 😐", "Biasa aja, ada PR yang harus digarap."
    return "Flop Era 🥲", "Waktunya glow-up besar-besaran."


def default_city(cities):
    for c in cities:
        if c.strip().upper() == "KAB. BOGOR":
            return c
    for c in cities:
        if "BOGOR" in c.upper() and "KOTA" not in c.upper():
            return c
    return cities[0]


# =========================
# SIDEBAR: MENU, DATA, FILTER
# =========================
PAGES = [
    "🏠 Beranda",
    "💰 Cuan Kategori",
    "📈 Tren Penjualan",
    "📍 Kabupaten Bogor",
    "⏰ Jam & Tanggal Cuan",
    "💳 Bayar, Kirim & Batal",
    "🗂️ Data Transaksi",
]

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-avatar">🛍️</div><div>'
        '<div class="brand-name">NusaCommerce</div><div class="brand-role">Vibe Dashboard ✨</div></div></div>',
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
    sel_year = st.selectbox("📅 Tahun", ["Semua Tahun"] + years)
    groups_present = [g for g in GROUP_ORDER if g in set(d_all["status_group"]) and g != "Batal"]
    valid_groups = st.multiselect(
        "✅ Status yang dihitung sebagai penjualan",
        groups_present,
        default=["Selesai"] if "Selesai" in groups_present else groups_present,
    )
    provinces = sorted(d_all["provinsi"].unique().tolist())
    sel_prov = st.selectbox("🗺️ Provinsi", ["Semua Provinsi"] + provinces)
    alloc_mode = st.radio(
        "🧮 Omzet pesanan multi-kategori",
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
    page_header("Vibe Check Penjualan ✨", "Ringkasan 3 pertanyaan bisnis + fakta seru dari datamu, dalam satu layar.")

    k = st.columns(5)
    kpi(k[0], "💸", "#EDE9FE", "Total Penjualan", format_short(total_rev), chip(rev_growth) + " vs bulan lalu" if rev_growth is not None else "")
    kpi(k[1], "🧾", "#FCE7F3", "Jumlah Pesanan", format_int(total_orders), chip(ord_growth) + " vs bulan lalu" if ord_growth is not None else "")
    kpi(k[2], "📦", "#CFFAFE", "Barang Terjual", format_int(total_items))
    kpi(k[3], "🛒", "#FFEDD5", "Rata-rata Nilai Pesanan", format_short(aov))
    kpi(k[4], "🙅", "#FEE2E2", "Tingkat Batal", format_pct(cancel_rate), "dari semua pesanan")
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ---- 3 jawaban cepat
    st.markdown('<div class="card-title" style="margin-bottom:8px">🎯 Jawaban 3 Pertanyaan Utama</div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)

    if len(cat_tbl):
        top1 = cat_tbl.iloc[0]
        a1.markdown(
            f'<div class="ans g1"><div class="ans-q">1 · Produk/kategori omzet tertinggi</div>'
            f'<div class="ans-a">{esc(str(top1["kategori"]))}</div>'
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
                f'<div class="ans-a">{esc(str(cnt_b.index[0]))}</div>'
                f'<div class="ans-d">Muncul di {format_int(cnt_b.iloc[0])} pesanan. Posisi berikutnya: '
                f'<b>{esc(str(cnt_b.index[1])) if len(cnt_b) > 1 else "-"}</b>.</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.5])
    with left:
        box = card("🔮 Vibe Score Bisnis", "Gabungan: tingkat batal, pertumbuhan bulan terakhir, dan retur")
        score = vibe_score(cancel_rate, rev_growth, return_rate)
        title, desc = vibe_label(score)
        with box:
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=score,
                number=dict(font=dict(size=44, color=INK)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickwidth=0),
                    bar=dict(color=VIOLET, thickness=0.28),
                    bgcolor="white", borderwidth=0,
                    steps=[dict(range=[0, 35], color="#FEE2E2"), dict(range=[35, 55], color="#FEF3C7"),
                           dict(range=[55, 75], color="#DBEAFE"), dict(range=[75, 100], color="#DCFCE7")],
                ),
            ))
            fig.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)",
                              font=dict(family="Plus Jakarta Sans"))
            show(fig, "vibe_gauge")
            st.markdown(
                f'<div style="text-align:center;font-weight:800;font-size:18px;color:{INK}">{title}</div>'
                f'<div style="text-align:center;font-size:13px;color:{MUTED}">{desc}</div>',
                unsafe_allow_html=True,
            )
    with right:
        box = card("🍵 Spill the Tea", "Temuan otomatis dari data yang sedang difilter")
        tea = []
        if len(cat_tbl):
            t0 = cat_tbl.iloc[0]
            tea.append(f"👑 <b>{esc(str(t0['kategori']))}</b> itu main character-nya: nyumbang <b>{t0['share']:.0f}%</b> omzet ({format_short(t0['omzet'])}).")
        reg = sales.groupby("kota_kabupaten")["order_id"].nunique().sort_values(ascending=False)
        if len(reg):
            tea.append(f"📍 Wilayah paling rajin checkout: <b>{esc(str(reg.index[0]))}</b> dengan {format_int(reg.iloc[0])} pesanan.")
        if not monthly_all.empty:
            best = monthly_all.loc[monthly_all["omzet"].idxmax()]
            tea.append(f"🏆 Bulan paling cuan: <b>{month_label(best['month'])}</b> ({format_short(best['omzet'])}).")
        hh = sales.dropna(subset=["hour"])
        if not hh.empty:
            h = int(hh.groupby("hour")["order_id"].nunique().idxmax())
            d = int(hh.groupby("weekday")["order_id"].nunique().idxmax())
            tea.append(f"⏰ Prime time belanja: jam <b>{h:02d}.00</b>, hari terfavorit <b>{DAYS_ID[d]}</b>.")
        if base["is_cod"].any():
            cod_share = base["is_cod"].mean() * 100
            cr_cod = base.loc[base["is_cod"], "is_batal"].mean() * 100
            cr_non = base.loc[~base["is_cod"], "is_batal"].mean() * 100
            tea.append(f"💵 {cod_share:.0f}% pesanan pakai COD. Tingkat batal COD <b>{cr_cod:.1f}%</b> vs non-COD <b>{cr_non:.1f}%</b>.")
        if rev_growth is not None:
            arah = "naik 📈" if rev_growth >= 0 else "turun 📉"
            tea.append(f"Omzet bulan terakhir <b>{arah} {abs(rev_growth):.1f}%</b> dibanding bulan sebelumnya.")
        with box:
            for t in tea:
                st.markdown(f'<div class="tea">{t}</div>', unsafe_allow_html=True)

    box = card("🏅 Leaderboard Kategori", "Top 5 berdasarkan omzet")
    with box:
        leaderboard(cat_tbl, "kategori", "omzet", format_short, n=5,
                    sub_fn=lambda r: f"{format_int(r['pesanan'])} pesanan")

    with st.expander("ℹ️ Catatan metode (biar nggak salah baca)"):
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
    page_header("Cuan Kategori 💰", "Pertanyaan 1: kategori/produk apa yang menghasilkan pendapatan tertinggi?")
    top_n = st.slider("Tampilkan Top", 5, 20, 10)
    top = cat_tbl.head(top_n)

    left, right = st.columns([1.15, 1])
    with left:
        box = card("Omzet per Kategori", f"Top {top_n} kategori · mode: {alloc_mode.lower()}")
        with box:
            show(hbar(top, "omzet", "kategori", VIOLET, format_short), "cuan_bar")
    with right:
        box = card("Pareto 80/20", "Berapa kategori yang menyumbang mayoritas omzet? (angka di sumbu X = peringkat)")
        with box:
            n_show = min(len(cat_tbl), 15)
            p = cat_tbl.head(n_show).copy()
            p["rank"] = range(1, n_show + 1)
            p["cum"] = cat_tbl["share"].cumsum().head(n_show)
            n80 = int((cat_tbl["share"].cumsum() < 80).sum() + 1)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=p["rank"], y=p["omzet"], name="Omzet", marker_color=VIOLET, customdata=p["kategori"],
                                 hovertemplate="#%{x} %{customdata}<br>%{y:,.0f}<extra></extra>"), secondary_y=False)
            fig.add_trace(go.Scatter(x=p["rank"], y=p["cum"], name="Kumulatif %", mode="lines+markers",
                                     line=dict(color=PINK, width=3)), secondary_y=True)
            fig.add_hline(y=80, line_dash="dot", line_color=MUTED, secondary_y=True)
            style_fig(fig, 340, legend=True)
            fig.update_xaxes(dtick=1)
            fig.update_yaxes(range=[0, 105], ticksuffix="%", secondary_y=True, showgrid=False)
            fig.update_yaxes(tickformat=".2s", secondary_y=False)
            show(fig, "cuan_pareto")
            st.caption(f"💡 {n80} dari {len(cat_tbl)} kategori sudah menyumbang ±80% omzet.")

    l2, r2 = st.columns([1, 1])
    with l2:
        box = card("Naik Daun vs Turun Kasta 🎢", "Perubahan omzet bulan terakhir vs bulan sebelumnya (Top 10 kategori)")
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
                    show(hbar(g, "growth", "kategori", LIME, lambda v: f"{v:+.0f}%", sign_colors=True, pad=1.35), "cuan_growth")
                else:
                    st.info("Data bulanan kategori belum cukup.")
            else:
                st.info("Butuh minimal 2 bulan penuh untuk membandingkan.")
    with r2:
        box = card("Duo Maut 🤝", "Pasangan kategori yang paling sering dibeli dalam satu pesanan (ide bundling)")
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
                show(hbar(pairs, "pesanan", "pasangan", PINK, format_int, pad=1.2), "cuan_pairs")
            else:
                st.info("Tidak ada pesanan multi-kategori pada filter ini.")

    box = card("Tabel Kategori Lengkap", "Unit = estimasi (total_qty dibagi rata untuk pesanan multi-kategori)")
    with box:
        tbl = cat_tbl.rename(columns={
            "kategori": "Kategori", "omzet": "Omzet", "share": "Kontribusi (%)", "pesanan": "Pesanan",
            "unit": "Estimasi Unit", "omzet_per_pesanan": "Omzet / Pesanan"})
        tbl = tbl[["Kategori", "Omzet", "Kontribusi (%)", "Pesanan", "Estimasi Unit", "Omzet / Pesanan"]].copy()
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
    page_header("Tren Penjualan 📈", "Pertanyaan 2: bagaimana tren penjualan setiap tahun?")

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
                st.caption("⚠️ Tahun dengan ≤2 bulan data sebaiknya dibaca hati-hati; kemungkinan hanya sisa transaksi di batas periode.")

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
                                     line=dict(color=VIOLET, width=3, shape="spline"), marker=dict(size=5),
                                     fill="tozeroy", fillcolor="rgba(124,58,237,.12)"), row=1, col=1)
            fig.add_trace(go.Bar(x=agg["dt"], y=agg["pesanan"], name="Pesanan", marker_color=ORANGE), row=2, col=1)
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
                    marker_color=[LIME if v >= 0 else RED for v in g["growth"]],
                    text=[f"{v:+.0f}%" for v in g["growth"]], textposition="outside", cliponaxis=False))
                lo, hi = float(g["growth"].min()), float(g["growth"].max())
                fig.update_yaxes(range=[min(0, lo * 1.3) - 5, max(0, hi * 1.3) + 5], ticksuffix="%")
                fig.update_xaxes(tickangle=-45)
                show(style_fig(fig, 340), "tren_mom")
            else:
                st.info("Butuh minimal 2 bulan penuh.")
    with r2:
        box = card("Proyeksi Kasar 3 Bulan ke Depan 🔮", "Garis tren linear dari ≤6 bulan penuh terakhir. Bukan ramalan pasti!")
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
                                         line=dict(color=VIOLET, width=3)))
                fig.add_trace(go.Scatter(x=[recent["month"].iloc[-1]] + fut_months,
                                         y=[recent["omzet"].iloc[-1]] + list(fut_y), name="Proyeksi",
                                         mode="lines+markers", line=dict(color=PINK, width=3, dash="dash")))
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
    page_header("Kabupaten Bogor 📍", "Pertanyaan 3: kategori apa yang paling banyak dibeli di wilayah ini? (bisa ganti wilayah)")

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
    kpi(k[0], "🧾", "#EDE9FE", "Pesanan Selesai", format_int(loc["order_id"].nunique()), f"peringkat #{rank_pos} dari {len(rank_city)} wilayah")
    kpi(k[1], "💸", "#FCE7F3", "Omzet", format_short(loc["total_pembayaran"].sum()))
    kpi(k[2], "📦", "#CFFAFE", "Barang Terjual", format_int(loc["total_qty"].sum()), f"{int(loc['total_qty'].isna().sum())} baris tanpa qty")
    best_cat = loc_tbl.sort_values("pesanan", ascending=False).iloc[0]["kategori"]
    kpi(k[3], "👑", "#FFEDD5", "Kategori Terlaris", esc(shorten(best_cat, 22)), "berdasarkan jumlah pesanan")
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        box = card(f"Kategori Terlaris — {metric}", f"Top {topn} di {pick.title()}")
        with box:
            show(hbar(loc_tbl.head(0).pipe(lambda _: loc_tbl.sort_values(mcol, ascending=False).head(topn)),
                      mcol, "kategori", VIOLET, mfmt), "bogor_bar")
    with right:
        box = card("Indeks Kegemaran 🔥", "Seberapa lebih doyan wilayah ini dibanding rata-rata nasional (1× = sama; >1× = lebih doyan)")
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
                fig = hbar(idx_df, "indeks", "kategori", PINK, lambda v: f"{v:.1f}×", pad=1.25)
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
                s["Total Barang"] = s["Total Barang"].round(0)
                st.dataframe(s, width="stretch", hide_index=True, height=360)
    with r2:
        box = card("Peringkat Wilayah", "10 wilayah dengan pesanan terbanyak (wilayah pilihanmu disorot pink)")
        with box:
            rc = rank_city.head(10).reset_index()
            rc.columns = ["wilayah", "pesanan"]
            if pick not in rc["wilayah"].values:
                rc = pd.concat([rc.head(9), pd.DataFrame({"wilayah": [pick], "pesanan": [rank_city[pick]]})])
            show(hbar(rc, "pesanan", "wilayah", CYAN, format_int, highlight=pick, height=400), "bogor_rank")


# =========================================================
# HALAMAN 5: JAM & TANGGAL CUAN
# =========================================================
elif page == PAGES[4]:
    page_header("Jam & Tanggal Cuan ⏰", "Kapan pembeli paling rajin checkout? Cek prime time, tanggal kembar, dan efek gajian.")
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
            colorscale=[[0, "#F5F3FF"], [0.5, "#C084FC"], [1, "#DB2777"]],
            colorbar=dict(title="Pesanan", thickness=12),
            hovertemplate="%{y} jam %{x}.00<br>%{z} pesanan<extra></extra>"))
        style_fig(fig, 340)
        fig.update_yaxes(autorange="reversed", showgrid=False)
        fig.update_xaxes(title_text="Jam", dtick=1)
        show(fig, "jam_heat")
        top_h = int(dd.groupby("hour")["order_id"].nunique().idxmax())
        top_d = int(dd.groupby("weekday")["order_id"].nunique().idxmax())
        st.caption(f"💡 Puncak pesanan di jam {top_h:02d}.00 dan hari {DAYS_ID[top_d]}. Cocok buat jadwal flash sale atau posting promo.")

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
        box = card("Efek Tanggal Kembar & Gajian 💸", "Rata-rata pesanan per hari menurut jenis tanggal")
        with box:
            g = per_day.groupby("grup").agg(rata_pesanan=("pesanan", "mean"), hari=("tgl", "count")).reset_index()
            cmap = {"Tanggal kembar": PINK, "Gajian (25–5)": ORANGE, "Tanggal biasa": VIOLET}
            fig = go.Figure(go.Bar(
                x=g["grup"], y=g["rata_pesanan"], marker_color=[cmap[v] for v in g["grup"]],
                text=[f"{v:.0f}" for v in g["rata_pesanan"]], textposition="outside", cliponaxis=False,
                customdata=g["hari"], hovertemplate="%{x}<br>%{y:.1f} pesanan/hari (%{customdata} hari)<extra></extra>"))
            fig.update_yaxes(range=[0, g["rata_pesanan"].max() * 1.25], showticklabels=False)
            show(style_fig(fig, 320), "jam_twin")
            if {"Tanggal kembar", "Tanggal biasa"} <= set(g["grup"]):
                a = g.set_index("grup")["rata_pesanan"]
                diff = (a["Tanggal kembar"] / a["Tanggal biasa"] - 1) * 100
                st.caption(f"💡 Tanggal kembar rata-rata {diff:+.0f}% dibanding tanggal biasa.")
    with r:
        box = card("Pesanan per Tanggal dalam Bulan", "Rata-rata pesanan per hari menurut tanggal (oranye = periode gajian)")
        with box:
            dm = per_day.groupby("day")["pesanan"].mean().reset_index()
            fig = go.Figure(go.Bar(
                x=dm["day"], y=dm["pesanan"],
                marker_color=[ORANGE if (d >= 25 or d <= 5) else VIOLET for d in dm["day"]],
                hovertemplate="Tanggal %{x}<br>%{y:.1f} pesanan<extra></extra>"))
            fig.update_xaxes(dtick=1, tickangle=0)
            show(style_fig(fig, 320), "jam_dom")

    box = card("Hari Terbaik dalam Seminggu", "Total omzet per hari")
    with box:
        wd = dd.groupby("weekday")["total_pembayaran"].sum().reindex(range(7), fill_value=0).reset_index()
        wd["hari"] = [DAYS_ID[i] for i in wd["weekday"]]
        fig = go.Figure(go.Bar(
            x=wd["hari"], y=wd["total_pembayaran"], marker_color=PALETTE[: 7] if len(PALETTE) >= 7 else VIOLET,
            text=wd["total_pembayaran"].map(format_short), textposition="outside", cliponaxis=False))
        fig.update_yaxes(range=[0, wd["total_pembayaran"].max() * 1.2], showticklabels=False)
        show(style_fig(fig, 300), "jam_wd")


# =========================================================
# HALAMAN 6: BAYAR, KIRIM & BATAL
# =========================================================
elif page == PAGES[5]:
    page_header("Bayar, Kirim & Batal 💳", "Metode bayar favorit, opsi pengiriman, dan kenapa pesanan batal.")
    disc_total = sales["total_diskon"].sum()
    cod_share = base["is_cod"].mean() * 100 if len(base) else 0
    k = st.columns(4)
    kpi(k[0], "🙅", "#FEE2E2", "Tingkat Batal", format_pct(cancel_rate), f"{format_int(base['is_batal'].sum())} pesanan batal")
    kpi(k[1], "🏷️", "#FCE7F3", "Total Diskon", format_short(disc_total))
    kpi(k[2], "🧮", "#EDE9FE", "Diskon / Omzet", format_pct(disc_total / total_rev * 100 if total_rev else 0))
    kpi(k[3], "💵", "#FFEDD5", "Pesanan COD", format_pct(cod_share), "dari semua pesanan")
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
                show(hbar(cb, "rate", "metode_pembayaran", RED, lambda v: f"{v:.1f}%", pad=1.25), "bayar_cancel")

    l2, r2 = st.columns(2)
    with l2:
        box = card("Tingkat Batal per Opsi Pengiriman", "Hanya opsi dengan ≥30 pesanan")
        with box:
            cs = cancel_by("opsi_pengiriman")
            if cs.empty:
                st.info("Data belum cukup.")
            else:
                show(hbar(cs, "rate", "opsi_pengiriman", ORANGE, lambda v: f"{v:.1f}%", pad=1.25), "kirim_cancel")
    with r2:
        box = card("Alasan Pembatalan Terbanyak", "Top 8 dari pesanan batal")
        with box:
            cr = base[base["is_batal"]]["alasan_pembatalan"].value_counts().head(8).reset_index()
            cr.columns = ["alasan", "jumlah"]
            if cr.empty:
                st.info("Tidak ada data pembatalan.")
            else:
                cr["alasan"] = cr["alasan"].map(lambda v: shorten(v, 44))
                show(hbar(cr, "jumlah", "alasan", PINK, format_int, pad=1.2), "batal_reason")

    box = card("Tingkat Batal per Bulan")
    with box:
        mc = base.dropna(subset=["month"]).groupby("month")["is_batal"].mean().mul(100).reset_index()
        if mc.empty:
            st.info("Data tanggal tidak tersedia.")
        else:
            fig = go.Figure(go.Scatter(x=mc["month"], y=mc["is_batal"], mode="lines+markers",
                                       line=dict(color=RED, width=3), marker=dict(size=7)))
            fig.update_yaxes(ticksuffix="%")
            show(style_fig(fig, 300), "batal_month")


# =========================================================
# HALAMAN 7: DATA TRANSAKSI
# =========================================================
else:
    page_header("Data Transaksi 🗂️", "Telusuri, cari, dan unduh data hasil filter.")
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