from pathlib import Path
from zipfile import ZipFile, BadZipFile
import io
import re
from html import escape as html_escape
from urllib.parse import quote

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

BLUE = "#2F5BEA"
BLUE_LIGHT = "#BFD3FF"
YELLOW = "#F5B83D"
GREEN = "#16A34A"
RED = "#E5484D"
INK = "#1E293B"
MUTED = "#475569"
PALETTE = [BLUE, YELLOW, "#10B981", "#8B5CF6", "#F97316", "#06B6D4", "#EC4899", "#84CC16"]

# =========================
# STYLE
# =========================
def inject_css():
    coins = '<div class="coins-container">' + '<div class="coin"></div>' * 7 + "</div>"
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

        .stApp {{ background: linear-gradient(135deg, #EEF2FB 0%, #E7ECF8 100%); }}

        /* Header Streamlit */
        header[data-testid="stHeader"] {{ background: transparent; }}
        .block-container {{ padding-top: 2.2rem; max-width: 1500px; }}

        /* Teks area utama (tidak menimpa sidebar) */
        [data-testid="stMain"] label, [data-testid="stMain"] label *, [data-testid="stMain"] .stMarkdown p,
        [data-testid="stMain"] [data-testid="stCaptionContainer"] *, [data-testid="stMain"] [data-testid="stRadio"] * {{ color: {INK}; }}
        [data-testid="stMain"] label p {{ font-weight: 600; font-size: 13px; }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #2B4FA8 0%, #223F8C 60%, #1B3476 100%);
            border-right: none;
        }}
        [data-testid="stSidebar"] * {{ color: #FFFFFF; }}
        [data-testid="stSidebar"] [data-baseweb="select"] * {{ color: {INK} !important; }}
        [data-testid="stSidebar"] [data-testid="stFileUploader"] section {{ background: rgba(255,255,255,.1); }}
        [data-testid="stSidebar"] [data-testid="stFileUploader"] small,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] span,
        [data-testid="stSidebar"] [data-testid="stFileUploader"] button {{ color: {INK} !important; }}

        .brand {{
            display:flex; align-items:center; gap:12px; padding:10px 12px;
            background: rgba(255,255,255,.12); border-radius:14px; margin-bottom:14px;
        }}
        .brand-avatar {{
            width:42px; height:42px; border-radius:50%; background:{YELLOW};
            display:flex; align-items:center; justify-content:center;
            font-weight:800; color:#fff !important; font-size:15px;
        }}
        .brand-name {{ font-weight:700; font-size:14px; line-height:1.2; }}
        .brand-role {{ font-size:11px; opacity:.95; }}

        /* Menu navigasi (radio) */
        [data-testid="stSidebar"] div[role="radiogroup"] {{ gap: 4px; }}
        [data-testid="stSidebar"] div[role="radiogroup"] label {{
            padding: 10px 14px; border-radius: 10px; width: 100%; cursor: pointer;
            transition: background .15s;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{ background: rgba(255,255,255,.12); }}
        [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{ display:none; }}
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
            background: {YELLOW};
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {{
            color: #3B2A00 !important; font-weight: 800;
        }}
        .side-label {{
            font-size: 11px; text-transform: uppercase; letter-spacing: .8px;
            opacity: .95; margin: 18px 0 6px 4px; font-weight: 800;
        }}

        /* Header halaman */
        .page-title {{ font-size: 30px; font-weight: 800; color: {INK}; letter-spacing: -.5px; margin: 0; }}
        .page-sub {{ color: {MUTED}; font-size: 14px; font-weight:500; margin: 2px 0 18px 0; }}

        /* Kartu */
        .card {{
            background:#fff; border-radius:16px; padding:18px 20px;
            box-shadow: 0 6px 22px rgba(30,41,59,.07); border:1px solid #E6EAF4;
            margin-bottom: 4px;
        }}
        .card-title {{ font-size:15px; font-weight:800; color:{INK}; margin-bottom:2px; }}
        .card-sub {{ font-size:12px; color:{MUTED}; font-weight:500; margin-bottom:8px; }}

        /* KPI */
        .kpi {{
            background:#fff; border-radius:16px; padding:16px 18px;
            box-shadow: 0 6px 22px rgba(30,41,59,.07); border:1px solid #E6EAF4;
            display:flex; gap:14px; align-items:center; height:100%;
        }}
        .kpi-accent {{ width:6px; align-self:stretch; border-radius:6px; flex-shrink:0; }}
        .kpi-title {{ font-size:12px; color:{MUTED}; font-weight:700; }}
        .kpi-value {{ font-size:24px; font-weight:800; color:{INK}; line-height:1.15; }}
        .kpi-delta {{ font-size:12px; font-weight:700; }}
        .up {{ color:{GREEN}; }} .down {{ color:{RED}; }} .flat {{ color:{MUTED}; }}

        /* Daftar produk */
        .prod {{
            display:flex; align-items:center; gap:14px; padding:10px 12px;
            border-radius:12px; border:1px solid #EDF0F7; margin-bottom:8px; background:#FBFCFF;
        }}
        .prod-rank {{ width:22px; font-weight:800; color:{MUTED}; font-size:13px; text-align:center; }}
        .prod-icon {{
            position:relative; width:56px; height:56px; border-radius:12px; display:flex; overflow:hidden;
            align-items:center; justify-content:center; font-size:20px; font-weight:800;
            color:{MUTED}; background:#E8EDF8; flex-shrink:0; border:1px solid #E2E8F0;
        }}
        .prod-icon img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; background:#fff; }}
        .prod-body {{ flex:1; min-width:0; }}
        .prod-name {{
            font-weight:700; font-size:13.5px; color:{INK};
            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
        }}
        .prod-cat {{ font-size:11.5px; color:{MUTED}; font-weight:500; }}
        .prod-bar {{ height:6px; border-radius:6px; background:#E8EDF8; margin-top:6px; overflow:hidden; }}
        .prod-bar > div {{ height:100%; background:linear-gradient(90deg,{BLUE},#6C8BFF); border-radius:6px; }}
        .prod-val {{ text-align:right; font-weight:800; font-size:14px; color:{INK}; white-space:nowrap; }}
        .prod-val small {{ display:block; font-weight:600; color:{MUTED}; font-size:11px; }}

        /* Insight */
        .insight {{
            background:#FFF8E6; border:1px solid #F7E2A8; border-radius:12px;
            padding:10px 14px; margin-bottom:8px; font-size:13px; color:#5B4300;
        }}

        /* Tombol */
        div.stDownloadButton > button, div.stButton > button {{
            background:{YELLOW}; color:#3B2A00; font-weight:800; border:none;
            border-radius:10px; padding:10px 22px;
        }}
        div.stDownloadButton > button:hover {{ background:#E8A824; color:#3B2A00; }}

        /* Animasi koin jatuh */
        .coins-container {{ position:fixed; inset:0; pointer-events:none; z-index:0; overflow:hidden; }}
        .coin {{
            position:absolute; width:34px; height:34px; border-radius:50%;
            background: radial-gradient(circle at 35% 35%, #FCD34D, #F59E0B 60%, #B45309);
            border:2px solid #FBBF24; opacity:.5; animation: fall linear infinite;
        }}
        .coin::after {{
            content:"$"; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
            font-weight:900; font-size:17px; color:#78350F;
        }}
        @keyframes fall {{
            0% {{ transform: translateY(-60px) rotate(0deg); opacity:0; }}
            15% {{ opacity:.55; }}
            100% {{ transform: translateY(105vh) rotate(360deg); opacity:0; }}
        }}
        .coin:nth-child(1) {{ left:4%; animation-duration:7s; }}
        .coin:nth-child(2) {{ left:19%; animation-duration:9s; animation-delay:2s; }}
        .coin:nth-child(3) {{ left:35%; animation-duration:6.5s; animation-delay:1s; }}
        .coin:nth-child(4) {{ left:52%; animation-duration:8.5s; animation-delay:3s; }}
        .coin:nth-child(5) {{ left:68%; animation-duration:10s; animation-delay:.5s; }}
        .coin:nth-child(6) {{ left:82%; animation-duration:7.5s; animation-delay:2.5s; }}
        .coin:nth-child(7) {{ left:93%; animation-duration:6s; animation-delay:1.5s; }}
        </style>
        {coins}
        """,
        unsafe_allow_html=True,
    )


# =========================
# HELPER DATA
# =========================
def read_csv_bytes(data: bytes, filename: str):
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        for sep in (None, ";", ",", "\t", "|"):
            try:
                if sep is None:
                    frame = pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=encoding)
                else:
                    frame = pd.read_csv(io.BytesIO(data), sep=sep, encoding=encoding)
                if len(frame.columns) > 1 or len(frame) == 0:
                    frame.columns = [str(c).strip().replace("\ufeff", "") for c in frame.columns]
                    return frame
            except Exception as exc:
                last_error = exc
    raise ValueError(f"Gagal membaca {filename}: {last_error}")


@st.cache_data(show_spinner=False)
def get_data_options():
    options = {}
    for p in sorted(Path(".").glob("*.csv")):
        try:
            options[p.name] = read_csv_bytes(p.read_bytes(), p.name)
        except Exception:
            pass
    for zpath in sorted(Path(".").glob("*.zip")):
        try:
            with ZipFile(zpath) as zf:
                for member in zf.namelist():
                    if member.lower().endswith(".csv") and not member.endswith("/"):
                        try:
                            options[f"{zpath.name} ▸ {Path(member).name}"] = read_csv_bytes(zf.read(member), member)
                        except Exception:
                            pass
        except (BadZipFile, OSError):
            pass
    return options


def norm(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


ALIASES = {
    "date": ["orderdate", "transactiondate", "tanggaltransaksi", "tanggal", "date", "createdat", "purchasedate", "invoicedate", "timestamp"],
    "product": ["productname", "namaproduk", "produk", "product", "itemname", "namabarang", "barang", "producttitle", "sku"],
    "category": ["category", "kategori", "productcategory", "kategoriproduk", "namakategori", "categoryname", "productcategories"],
    "revenue": ["revenue", "sales", "totalprice", "totalamount", "amount", "omzet", "pendapatan", "totalpenjualan", "gmv", "total"],
    "quantity": ["quantity", "qty", "jumlah", "jumlahbarang", "unit", "units", "jumlahterjual", "kuantitas", "totalqty"],
    "unit_price": ["unitprice", "price", "harga", "hargasatuan", "sellingprice", "hargaunit"],
    "kabupaten": ["kabupaten", "kabupatenkota", "city", "kota", "district", "regency", "shippingcity", "customercity"],
    "province": ["province", "provinsi", "state", "shippingprovince"],
    "order_id": ["orderid", "transactionid", "invoiceid", "idtransaksi", "nomororder", "idorder"],
    "customer": ["customername", "namapelanggan", "pelanggan", "customer", "namacustomer", "buyer", "pembeli"],
    "discount": ["discount", "diskon", "potonganharga", "discountamount", "discountval", "potongan", "totaldiskon"],
    "status": ["orderstatus", "status", "statuspesanan", "statustransaksi", "deliverystatus"],
    "cancel_reason": ["cancelreason", "alasanpembatalan", "cancellationreason", "alasanbatal", "reason"],
}

LABELS = {
    "date": "Tanggal", "product": "Produk", "category": "Kategori", "revenue": "Omzet / Total",
    "quantity": "Jumlah", "unit_price": "Harga satuan", "kabupaten": "Kabupaten / Kota",
    "province": "Provinsi", "order_id": "ID Pesanan", "customer": "Pelanggan",
    "discount": "Diskon", "status": "Status", "cancel_reason": "Alasan batal",
}


def find_column(df, kind):
    normalized = {c: norm(c) for c in df.columns}
    aliases = [norm(x) for x in ALIASES[kind]]
    for alias in aliases:
        for col, ncol in normalized.items():
            if ncol == alias:
                return col
    for alias in aliases:
        if len(alias) >= 5:
            for col, ncol in normalized.items():
                if alias in ncol or (len(ncol) >= 5 and ncol in alias):
                    return col
    return None


def money_value(series):
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    cleaned = series.astype(str).str.strip()
    cleaned = cleaned.str.replace(r"(?i)rp|idr|usd|\$", "", regex=True)
    cleaned = cleaned.str.replace(r"[^\d,.\-]", "", regex=True)

    def parse_one(x):
        if not x or x.lower() == "nan":
            return float("nan")
        if "," in x and "." in x:
            if x.rfind(",") > x.rfind("."):
                x = x.replace(".", "").replace(",", ".")
            else:
                x = x.replace(",", "")
        elif "," in x:
            parts = x.split(",")
            x = "".join(parts) if len(parts[-1]) == 3 else ".".join(parts)
        elif "." in x:
            parts = x.split(".")
            if len(parts[-1]) == 3:
                x = "".join(parts)
        try:
            return float(x)
        except ValueError:
            return float("nan")

    return cleaned.map(parse_one)


def format_rp(value):
    if pd.isna(value):
        value = 0
    return "Rp " + f"{value:,.0f}".replace(",", ".")


def format_short(value):
    """Rp 1,2 M / 3,4 jt / 5,6 rb agar muat di kartu."""
    if pd.isna(value):
        value = 0
    a = abs(value)
    for limit, suffix in ((1e12, " T"), (1e9, " M"), (1e6, " jt"), (1e3, " rb")):
        if a >= limit:
            return "Rp " + f"{value / limit:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") + suffix
    return format_rp(value)


def format_int(value):
    return f"{value:,.0f}".replace(",", ".")


def shorten(text, n=28):
    t = str(text)
    return t if len(t) <= n else t[: n - 1] + "…"


# =========================
# FOTO PRODUK (foto asli dari Wikimedia Commons)
# =========================
IMG_BASE = "https://commons.wikimedia.org/wiki/Special:FilePath/"
IMAGE_RULES = [
    (r"tws|earbud|earphone|airpods?|in-ear", "JLab true wireless.jpg"),
    (r"headset|headphone", "Earfun wireless black headphones, September 2024 02.jpg"),
    (r"speaker", "JBL Flip 4.jpg"),
    (r"smartwatch|\bjam\b|watch|arloji", "Nilax wristwatch.jpg"),
    (r"kamera|camera|dslr|mirrorless", "Nikon DSLR camera D850.jpg"),
    (r"laptop|notebook|macbook|komputer", "Lenovo ThinkPad T410 laptop (cropped).jpg"),
    (r"\bhp\b|phone|smartphone|ponsel|iphone|android|handphone", "Android Smartphone.jpg"),
    (r"sepatu|shoe|sneaker|sandal|boots?", "Nike shoes.jpg"),
    (r"ransel|backpack", "High Sierra backpack.JPG"),
    (r"handbag|tas tangan|tote|tas wanita", "Black Microfiber Handbag.JPG"),
    (r"\btas\b|\bbag\b|koper", "High Sierra backpack.JPG"),
    (r"dompet|wallet", "Wallet.jpg"),
    (r"jaket|jacket|hoodie|sweater|coat", "Columbia Sportswear Jacket.jpg"),
    (r"celana|jeans|pants", "Denim Jeans Pant Display.JPG"),
    (r"kaos|baju|kemeja|shirt|atasan", "Men's long-sleeve T-shirt.jpg"),
    (r"kacamata|sunglasses|glasses", "Oakley sunglasses.jpg"),
    (r"parfum|perfume|kecantikan|beauty|kosmetik", "Vintage Atomizer Perfume Bottle.JPG"),
    (r"buku|book", "Stack of Books.jpg"),
]


def product_image(name, category=""):
    """URL foto sesuai jenis produk; None bila jenisnya tidak dikenali (tampil inisial)."""
    for text in (str(name).lower(), str(category).lower()):
        for pattern, filename in IMAGE_RULES:
            if re.search(pattern, text):
                return IMG_BASE + quote(filename.replace(" ", "_"), safe="()") + "?width=160"
    return None


# =========================
# KOMPONEN UI
# =========================
def page_header(title, sub):
    st.markdown(f'<div class="page-title">{title}</div><div class="page-sub">{sub}</div>', unsafe_allow_html=True)


def kpi(col, accent, title, value, delta=None):
    d = ""
    if delta is not None:
        cls = "up" if delta > 0 else ("down" if delta < 0 else "flat")
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "●")
        d = f'<div class="kpi-delta {cls}">{arrow} {abs(delta):.1f}% vs periode lalu</div>'
    col.markdown(
        f'<div class="kpi"><div class="kpi-accent" style="background:{accent}"></div>'
        f'<div><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div>{d}</div></div>',
        unsafe_allow_html=True,
    )


def card_open(title, sub=""):
    s = f'<div class="card-sub">{sub}</div>' if sub else ""
    st.markdown(f'<div class="card"><div class="card-title">{title}</div>{s}', unsafe_allow_html=True)


def card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def style_fig(fig, height=300, legend=False):
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=INK, size=12), showlegend=legend,
        legend=dict(orientation="h", y=1.12, x=0),
        hoverlabel=dict(font_family="Inter"),
    )
    fig.update_xaxes(showgrid=False, title="", linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#EEF1F8", title="", zeroline=False)
    return fig


def growth(series):
    """Pertumbuhan nilai periode terakhir vs sebelumnya."""
    s = series.dropna()
    if len(s) < 2 or s.iloc[-2] == 0:
        return None
    return (s.iloc[-1] - s.iloc[-2]) / abs(s.iloc[-2]) * 100


def product_list(frame, metric_col, n, as_money=True, sub_col=None):
    top = frame.sort_values(metric_col, ascending=False).head(n)
    if top.empty:
        st.info("Data produk tidak tersedia.")
        return
    mx = top[metric_col].max() or 1
    html = ""
    for i, (_, r) in enumerate(top.iterrows(), 1):
        img = product_image(r["_product"], r.get("_category", ""))
        img_tag = f'<img src="{img}" alt="" loading="lazy" referrerpolicy="no-referrer">' if img else ""
        pname = html_escape(str(r["_product"]))
        pcat = html_escape(str(r.get("_category", "")))
        initial = html_escape(str(r["_product"])[:1].upper())
        val = format_rp(r[metric_col]) if as_money else format_int(r[metric_col])
        sub = ""
        if sub_col:
            sub = f"<small>{sub_col[1](r[sub_col[0]])}</small>"
        pct = max(4, r[metric_col] / mx * 100)
        html += (
            f'<div class="prod"><div class="prod-rank">{i}</div>'
            f'<div class="prod-icon">{initial}{img_tag}</div>'
            f'<div class="prod-body"><div class="prod-name" title="{pname}">{pname}</div>'
            f'<div class="prod-cat">{pcat}</div>'
            f'<div class="prod-bar"><div style="width:{pct:.0f}%"></div></div></div>'
            f'<div class="prod-val">{val}{sub}</div></div>'
        )
    st.markdown(html, unsafe_allow_html=True)


# =========================
# SIDEBAR: MENU & SUMBER DATA
# =========================
PAGES = ["Ringkasan", "Produk", "Wilayah", "Diskon & Pembatalan", "Data Transaksi"]

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-avatar">AD</div><div>'
        '<div class="brand-name">Admin Workspace</div>'
        '<div class="brand-role">NusaCommerce Analytics</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">Menu</div>', unsafe_allow_html=True)
    page = st.radio("Halaman", PAGES, label_visibility="collapsed")

    st.markdown('<div class="side-label">Sumber Data</div>', unsafe_allow_html=True)
    data_options = get_data_options()
    uploaded = st.file_uploader("Unggah CSV / ZIP", type=["csv", "zip"])


inject_css()

df_raw = None
if uploaded is not None:
    try:
        if uploaded.name.lower().endswith(".zip"):
            with ZipFile(uploaded) as zf:
                csv_members = [n for n in zf.namelist() if n.lower().endswith(".csv") and not n.endswith("/")]
                if not csv_members:
                    st.error("ZIP tidak berisi file CSV.")
                    st.stop()
                member = st.sidebar.selectbox("Pilih file dalam ZIP", csv_members)
                df_raw = read_csv_bytes(zf.read(member), member)
        else:
            df_raw = read_csv_bytes(uploaded.getvalue(), uploaded.name)
    except Exception as exc:
        st.error(f"Gagal memproses file: {exc}")
        st.stop()
elif data_options:
    ranked = []
    for name, frame in data_options.items():
        score = sum(find_column(frame, k) is not None for k in ("date", "product", "category", "revenue", "quantity"))
        ranked.append((score, len(frame), name))
    ranked.sort(reverse=True)
    default_name = ranked[0][2]
    names = list(data_options.keys())
    chosen = st.sidebar.selectbox("Pilih Dataset", names, index=names.index(default_name))
    df_raw = data_options[chosen].copy()
else:
    st.warning("Silakan unggah dataset CSV/ZIP melalui sidebar untuk memulai.")
    st.stop()

if df_raw is None or df_raw.empty:
    st.error("Data kosong.")
    st.stop()

# =========================
# PEMETAAN KOLOM
# =========================
detected = {kind: find_column(df_raw, kind) for kind in ALIASES}
with st.sidebar.expander("Pemetaan Kolom", expanded=False):
    choices = ["— Tidak tersedia —"] + list(df_raw.columns)
    for kind in ALIASES:
        auto = detected.get(kind)
        idx = choices.index(auto) if auto in choices else 0
        pick = st.selectbox(LABELS[kind], choices, index=idx, key=f"map_{kind}")
        detected[kind] = None if pick == "— Tidak tersedia —" else pick

date_col, product_col, category_col = detected["date"], detected["product"], detected["category"]
revenue_col, quantity_col, city_col = detected["revenue"], detected["quantity"], detected["kabupaten"]
order_col, unit_price_col, discount_col = detected["order_id"], detected["unit_price"], detected["discount"]
status_col, cancel_reason_col, customer_col = detected["status"], detected["cancel_reason"], detected["customer"]

df = df_raw.copy()
df["_date"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True) if date_col else pd.NaT
qty_series = money_value(df[quantity_col]).fillna(1) if quantity_col else pd.Series(1, index=df.index)
if revenue_col:
    df["_revenue"] = money_value(df[revenue_col])
elif unit_price_col:
    df["_revenue"] = money_value(df[unit_price_col]) * qty_series
else:
    df["_revenue"] = 0.0
df["_revenue"] = df["_revenue"].fillna(0)
df["_quantity"] = qty_series
df["_discount"] = money_value(df[discount_col]).fillna(0) if discount_col else 0.0
df["_product"] = df[product_col].fillna("Tidak diketahui").astype(str) if product_col else "Tidak diketahui"
df["_category"] = df[category_col].fillna("Tidak diketahui").astype(str) if category_col else "Tidak diketahui"
df["_city"] = df[city_col].fillna("Tidak diketahui").astype(str) if city_col else "Tidak diketahui"
df["_status"] = df[status_col].fillna("Selesai").astype(str) if status_col else "Selesai"
df["_cancel_reason"] = df[cancel_reason_col].fillna("Tidak ada alasan").astype(str) if cancel_reason_col else "Lainnya"
df["_year"] = df["_date"].dt.year
df["_month"] = df["_date"].dt.to_period("M").dt.to_timestamp()
df["_weekday"] = df["_date"].dt.dayofweek
df["_is_cancel"] = df["_status"].str.contains("batal|cancel|dibatalkan|refund|retur|return", case=False, na=False)

# =========================
# FILTER GLOBAL (SIDEBAR)
# =========================
with st.sidebar:
    st.markdown('<div class="side-label">Filter</div>', unsafe_allow_html=True)
    years = sorted(df["_year"].dropna().astype(int).unique().tolist(), reverse=True)
    categories = sorted(df["_category"].unique().tolist())
    cities = sorted(df["_city"].unique().tolist())
    statuses = sorted(df["_status"].unique().tolist())

    selected_year = st.selectbox("Tahun", ["Semua Tahun"] + years)
    selected_category = st.selectbox("Kategori", ["Semua Kategori"] + categories)
    selected_city = st.selectbox("Kabupaten / Kota", ["Semua Wilayah"] + cities)
    selected_status = st.selectbox("Status Pesanan", ["Semua Status"] + statuses)

filtered = df.copy()
if selected_year != "Semua Tahun":
    filtered = filtered[filtered["_year"] == selected_year]
if selected_category != "Semua Kategori":
    filtered = filtered[filtered["_category"] == selected_category]
if selected_city != "Semua Wilayah":
    filtered = filtered[filtered["_city"].str.casefold() == str(selected_city).casefold()]
if selected_status != "Semua Status":
    filtered = filtered[filtered["_status"] == selected_status]

if filtered.empty:
    page_header("Dashboard E-Commerce", "Tidak ada data untuk kombinasi filter ini.")
    st.warning("Coba longgarkan filter di sidebar.")
    st.stop()

# Metrik umum
total_rev = filtered["_revenue"].sum()
total_orders = filtered[order_col].nunique() if order_col else len(filtered)
total_items = filtered["_quantity"].sum()
aov = total_rev / total_orders if total_orders else 0
cancel_rate = filtered["_is_cancel"].mean() * 100
avg_discount = filtered["_discount"].mean() if discount_col else 0

monthly = filtered.dropna(subset=["_month"]).groupby("_month").agg(
    revenue=("_revenue", "sum"),
    orders=(order_col, "nunique") if order_col else ("_revenue", "size"),
)
rev_growth = growth(monthly["revenue"]) if not monthly.empty else None
ord_growth = growth(monthly["orders"]) if not monthly.empty else None

# =========================================================
# HALAMAN 1: RINGKASAN
# =========================================================
if page == PAGES[0]:
    page_header("Ringkasan Penjualan", "Pantau omzet, pesanan, dan tren penjualan dalam satu layar.")

    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, BLUE, "Total Penjualan", format_short(total_rev), rev_growth)
    kpi(k2, YELLOW, "Jumlah Pesanan", format_int(total_orders), ord_growth)
    kpi(k3, GREEN, "Barang Terjual", format_int(total_items))
    kpi(k4, RED, "Rata-rata Nilai Pesanan", format_short(aov))
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.7, 1])
    with left:
        card_open("Ikhtisar Penjualan", "Omzet (garis) dan jumlah pesanan (batang)")
        gran = st.radio("Rentang", ["Harian", "Mingguan", "Bulanan"], index=2, horizontal=True, label_visibility="collapsed")
        freq = {"Harian": "D", "Mingguan": "W", "Bulanan": "MS"}[gran]
        ts = filtered.dropna(subset=["_date"]).set_index("_date")
        if not ts.empty:
            agg = ts.groupby(pd.Grouper(freq=freq)).agg(
                revenue=("_revenue", "sum"),
                orders=(order_col, "nunique") if order_col else ("_revenue", "size"),
            ).reset_index()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=agg["_date"], y=agg["orders"], name="Pesanan", marker_color=YELLOW, opacity=.75), secondary_y=True)
            fig.add_trace(go.Scatter(
                x=agg["_date"], y=agg["revenue"], name="Omzet", mode="lines+markers",
                line=dict(color=BLUE, width=3, shape="spline"), marker=dict(size=5),
                fill="tozeroy", fillcolor="rgba(47,91,234,.12)",
            ), secondary_y=False)
            style_fig(fig, 330, legend=True)
            fig.update_yaxes(secondary_y=True, showgrid=False)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Data tanggal tidak tersedia untuk grafik tren.")
        card_close()

    with right:
        card_open("Penjualan per Tahun")
        yearly = filtered.dropna(subset=["_year"]).groupby("_year", as_index=False)["_revenue"].sum()
        if not yearly.empty:
            yearly["_year"] = yearly["_year"].astype(int).astype(str)
            fig = px.bar(yearly, x="_year", y="_revenue", text=yearly["_revenue"].map(format_short))
            fig.update_traces(marker_color=BLUE, textposition="outside", cliponaxis=False)
            st.plotly_chart(style_fig(fig, 330), width="stretch")
        else:
            st.info("Data tahunan tidak tersedia.")
        card_close()

    b1, b2 = st.columns([1, 1.4])
    with b1:
        card_open("Wawasan Otomatis", "Ringkasan temuan dari data yang sedang difilter")
        tips = []
        tp = filtered.groupby("_product")["_revenue"].sum().sort_values(ascending=False)
        if len(tp):
            tips.append(f"Produk terlaris: <b>{shorten(tp.index[0], 40)}</b> ({format_short(tp.iloc[0])}).")
        tc = filtered.groupby("_city")["_revenue"].sum().sort_values(ascending=False)
        if len(tc):
            tips.append(f"Wilayah omzet tertinggi: <b>{tc.index[0]}</b> ({tc.iloc[0] / total_rev * 100 if total_rev else 0:.0f}% dari total).")
        if not monthly.empty:
            best = monthly["revenue"].idxmax()
            tips.append(f"Bulan terbaik: <b>{best:%B %Y}</b> ({format_short(monthly['revenue'].max())}).")
        if rev_growth is not None:
            arah = "naik" if rev_growth >= 0 else "turun"
            tips.append(f"Omzet bulan terakhir <b>{arah} {abs(rev_growth):.1f}%</b> dibanding bulan sebelumnya.")
        tips.append(f"Tingkat pembatalan: <b>{cancel_rate:.1f}%</b> dari seluruh transaksi.")
        for t in tips:
            st.markdown(f'<div class="insight">{t}</div>', unsafe_allow_html=True)
        card_close()

    with b2:
        card_open("Pesanan Terbaru", "8 transaksi terakhir pada data terfilter")
        recent = filtered.sort_values("_date", ascending=False).head(8)
        show = pd.DataFrame({
            "ID": recent[order_col].astype(str) if order_col else recent.index.astype(str),
            "Tanggal": recent["_date"].dt.strftime("%d %b %Y"),
            "Produk": recent["_product"].map(lambda x: shorten(x, 30)),
            "Wilayah": recent["_city"].map(lambda x: shorten(x, 18)),
            "Total": recent["_revenue"].map(format_rp),
            "Status": recent["_status"],
        })
        st.dataframe(show, width="stretch", hide_index=True, height=320)
        card_close()

# =========================================================
# HALAMAN 2: PRODUK
# =========================================================
elif page == PAGES[1]:
    page_header("Analisis Produk", "Produk dan kategori mana yang paling laku dan paling menguntungkan.")

    c1, c2 = st.columns([1, 1])
    metric = c1.radio("Urutkan berdasarkan", ["Omzet", "Jumlah terjual", "Jumlah pesanan"], horizontal=True)
    top_n = c2.slider("Tampilkan Top", 3, 15, 8)

    agg = filtered.groupby("_product").agg(
        omzet=("_revenue", "sum"), qty=("_quantity", "sum"),
        pesanan=(order_col, "nunique") if order_col else ("_revenue", "size"),
        _category=("_category", lambda s: s.mode().iat[0] if len(s.mode()) else ""),
    ).reset_index().rename(columns={"index": "_product"})
    if "_product" not in agg.columns:
        agg = agg.rename(columns={agg.columns[0]: "_product"})
    mcol = {"Omzet": "omzet", "Jumlah terjual": "qty", "Jumlah pesanan": "pesanan"}[metric]

    left, right = st.columns([1, 1.2])
    with left:
        card_open(f"Produk Terlaris — {metric}")
        product_list(
            agg, mcol, top_n, as_money=(mcol == "omzet"),
            sub_col=("qty", lambda v: f"{format_int(v)} terjual") if mcol != "qty" else ("omzet", lambda v: format_short(v)),
        )
        card_close()

    with right:
        card_open("Omzet per Kategori", "Klik legenda untuk menyembunyikan kategori")
        cat = filtered.groupby("_category", as_index=False)["_revenue"].sum().sort_values("_revenue", ascending=False).head(10)
        fig = px.bar(cat.sort_values("_revenue"), x="_revenue", y="_category", orientation="h",
                     color_discrete_sequence=[BLUE])
        fig.update_yaxes(ticktext=[shorten(c, 24) for c in cat.sort_values("_revenue")["_category"]],
                         tickvals=cat.sort_values("_revenue")["_category"])
        st.plotly_chart(style_fig(fig, 340), width="stretch")
        card_close()

        card_open("Harga vs Volume", "Tiap titik = satu produk; ukuran = omzet")
        sc = agg.head(80).copy()
        sc["harga_rata2"] = sc["omzet"] / sc["qty"].replace(0, 1)
        fig = px.scatter(sc, x="qty", y="harga_rata2", size="omzet", color="_category", hover_name="_product",
                         color_discrete_sequence=PALETTE, size_max=38)
        fig.update_xaxes(title="Jumlah terjual")
        fig.update_yaxes(title="Harga rata-rata")
        st.plotly_chart(style_fig(fig, 300, legend=False), width="stretch")
        card_close()

    card_open("Tabel Produk Lengkap")
    tbl = agg.sort_values(mcol, ascending=False).rename(columns={
        "_product": "Produk", "_category": "Kategori", "omzet": "Omzet", "qty": "Terjual", "pesanan": "Pesanan"})
    st.dataframe(tbl[["Produk", "Kategori", "Omzet", "Terjual", "Pesanan"]], width="stretch", hide_index=True, height=300)
    st.download_button("Unduh Tabel Produk (CSV)", tbl.to_csv(index=False).encode("utf-8-sig"), "ringkasan_produk.csv", "text/csv")
    card_close()

# =========================================================
# HALAMAN 3: WILAYAH
# =========================================================
elif page == PAGES[2]:
    page_header("Performa Wilayah", "Bandingkan omzet antar kabupaten/kota dan lihat kategori favorit tiap wilayah.")

    n_city = st.slider("Jumlah wilayah ditampilkan", 5, 20, 10)
    left, right = st.columns([1.2, 1])
    with left:
        card_open("Wilayah dengan Omzet Terbanyak")
        tc = filtered.groupby("_city", as_index=False)["_revenue"].sum().sort_values("_revenue", ascending=False).head(n_city)
        tc = tc.sort_values("_revenue")
        fig = px.bar(tc, x="_revenue", y="_city", orientation="h", color_discrete_sequence=[GREEN],
                     text=tc["_revenue"].map(format_short))
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(style_fig(fig, 420), width="stretch")
        card_close()

    with right:
        card_open("Kategori Terlaris per Wilayah")
        base = df if selected_year == "Semua Tahun" else df[df["_year"] == selected_year]
        city_list = sorted(base["_city"].unique().tolist())
        default_idx = next((i for i, c in enumerate(city_list) if "bogor" in c.lower()), 0)
        pick_city = st.selectbox("Pilih wilayah", city_list, index=default_idx)
        cd = base[base["_city"] == pick_city].groupby("_category", as_index=False)["_quantity"].sum()
        cd = cd.sort_values("_quantity", ascending=False).head(6)
        if not cd.empty:
            fig = px.pie(cd, names="_category", values="_quantity", hole=.55, color_discrete_sequence=PALETTE)
            fig.update_traces(textposition="inside", textinfo="percent")
            st.plotly_chart(style_fig(fig, 340, legend=True), width="stretch")
        else:
            st.info("Tidak ada data untuk wilayah ini.")
        card_close()

    card_open("Peta Panas: Kategori × Wilayah", "Omzet 8 wilayah teratas dan 8 kategori teratas")
    top_c = filtered.groupby("_city")["_revenue"].sum().nlargest(8).index
    top_k = filtered.groupby("_category")["_revenue"].sum().nlargest(8).index
    hm = filtered[filtered["_city"].isin(top_c) & filtered["_category"].isin(top_k)]
    if not hm.empty:
        pv = hm.pivot_table(index="_category", columns="_city", values="_revenue", aggfunc="sum", fill_value=0)
        fig = px.imshow(pv, aspect="auto", color_continuous_scale=["#EEF2FF", BLUE])
        st.plotly_chart(style_fig(fig, 340), width="stretch")
    else:
        st.info("Data tidak cukup untuk peta panas.")
    card_close()

# =========================================================
# HALAMAN 4: DISKON & PEMBATALAN
# =========================================================
elif page == PAGES[3]:
    page_header("Diskon & Pembatalan", "Seberapa besar diskon menggerus omzet dan mengapa pesanan dibatalkan.")

    disc_total = filtered["_discount"].sum()
    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, BLUE, "Total Diskon", format_short(disc_total))
    kpi(k2, YELLOW, "Rata-rata Diskon", format_short(avg_discount))
    kpi(k3, GREEN, "Diskon / Omzet", f"{(disc_total / total_rev * 100) if total_rev else 0:.1f}%")
    kpi(k4, RED, "Tingkat Pembatalan", f"{cancel_rate:.1f}%")
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        card_open("Rasio Diskon terhadap Omzet per Kategori", "Persentase, supaya skala antar kategori sebanding")
        if discount_col and (filtered["_discount"] > 0).any():
            dc = filtered.groupby("_category")[["_revenue", "_discount"]].sum()
            dc["rasio"] = dc["_discount"] / dc["_revenue"].replace(0, pd.NA) * 100
            dc = dc.dropna().sort_values("rasio", ascending=False).head(10).reset_index().sort_values("rasio")
            fig = px.bar(dc, x="rasio", y="_category", orientation="h", color_discrete_sequence=[YELLOW],
                         text=dc["rasio"].map(lambda v: f"{v:.1f}%"))
            fig.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(style_fig(fig, 340), width="stretch")
        else:
            st.info("Data diskon tidak tersedia.")
        card_close()

    with right:
        card_open("Alasan Pembatalan Terbanyak")
        canceled = filtered[filtered["_is_cancel"]]
        if not canceled.empty and cancel_reason_col:
            rs = canceled["_cancel_reason"].value_counts().head(8).reset_index()
            rs.columns = ["Alasan", "Jumlah"]
            rs = rs.sort_values("Jumlah")
            fig = px.bar(rs, x="Jumlah", y="Alasan", orientation="h", color_discrete_sequence=[RED])
            st.plotly_chart(style_fig(fig, 340), width="stretch")
        else:
            st.info("Tidak ada data pembatalan.")
        card_close()

    l2, r2 = st.columns(2)
    with l2:
        card_open("Tingkat Pembatalan per Bulan")
        mc = filtered.dropna(subset=["_month"]).groupby("_month")["_is_cancel"].mean().mul(100).reset_index()
        if not mc.empty:
            fig = px.line(mc, x="_month", y="_is_cancel", markers=True)
            fig.update_traces(line_color=RED, line_width=3)
            fig.update_yaxes(ticksuffix="%")
            st.plotly_chart(style_fig(fig, 280), width="stretch")
        card_close()
    with r2:
        card_open("Distribusi Status Pesanan")
        sd = filtered["_status"].value_counts().reset_index()
        sd.columns = ["Status", "Jumlah"]
        fig = px.pie(sd, names="Status", values="Jumlah", hole=.55, color_discrete_sequence=PALETTE)
        st.plotly_chart(style_fig(fig, 280, legend=True), width="stretch")
        card_close()

# =========================================================
# HALAMAN 5: DATA TRANSAKSI
# =========================================================
else:
    page_header("Data Transaksi", "Telusuri, cari, dan unduh data hasil filter.")

    card_open("Detail Data Penjualan")
    q = st.text_input("Cari transaksi", placeholder="Ketik nama produk, wilayah, atau ID pesanan…")
    visible = filtered.drop(columns=[c for c in filtered.columns if c.startswith("_") and c not in ("_date",)], errors="ignore")
    if q.strip():
        mask = visible.astype(str).apply(lambda col: col.str.contains(q.strip(), case=False, na=False, regex=False)).any(axis=1)
        visible = visible[mask]
    st.caption(f"{format_int(len(visible))} baris ditampilkan dari {format_int(len(df))} total.")
    st.dataframe(visible, width="stretch", height=460)
    st.download_button("Unduh Data Hasil Filter (CSV)", visible.to_csv(index=False).encode("utf-8-sig"),
                       "data_penjualan_terfilter.csv", "text/csv")
    card_close()