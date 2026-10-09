"""Concord - Streamlit demo. Run: streamlit run app.py"""
import json, re, tempfile
from pathlib import Path
import streamlit as st
from concord.schema import DOC_TYPES, DOC_LABELS
from concord.letter import build_letter
from concord.i18n import LANGS, SEV, CHECK, t, doc_label, finding_text

ROOT = Path(__file__).parent
st.set_page_config(page_title="Concord", page_icon=str(ROOT / "assets" / "favicon-32.png"), layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, .stApp, .stMarkdown, button, input, label { font-family: 'IBM Plex Sans', system-ui, sans-serif !important; }
.stApp { background:#EEF2F9; color:#0E1B3D; }
header[data-testid="stHeader"] { background:transparent; height:0; }
.block-container { padding-top:1.5rem; max-width:1360px; }
.cc-head { background:#0E1B3D; border-radius:10px; padding:14px 24px; margin-bottom:8px;
           display:flex; align-items:center; gap:20px; flex-wrap:wrap; }
.cc-head svg { height:34px; width:auto; display:block; }
.cc-head span { color:#A9B6D3; font-size:15px; }
h2, h3 { color:#0E1B3D !important; letter-spacing:-0.01em; }
[data-testid="stWidgetLabel"] p { color:#0E1B3D !important; font-weight:600; font-size:15px; }
[data-testid="stFileUploaderDropzone"] { background:#F7F9FC; border:1.5px dashed #A7B2C6; border-radius:10px; }
[data-testid="stFileUploaderDropzone"] small, [data-testid="stFileUploaderDropzone"] span { color:#4A5670; }
.stTabs [data-baseweb="tab"] p { font-size:15px; font-weight:600; color:#4A5670; }
.stTabs [aria-selected="true"] p { color:#0E1B3D; }
.stButton button { height:44px; padding:0 20px; border-radius:6px; font-weight:600; }
.stButton button[kind="primary"] { background:#1F45C9; border:0; color:#fff; }
.stButton button[kind="primary"]:hover { background:#18379F; }
.stButton button[kind="secondary"] { background:#FFFFFF; border:1px solid #A7B2C6; color:#0E1B3D; }
.stButton button:disabled { background:#C9D3E6 !important; color:#4A5670 !important; }
.cc-count { font-family:'IBM Plex Mono',monospace; font-size:32px; font-weight:500; line-height:1.1; }
.cc-badge { font-size:12px; font-weight:600; padding:2px 8px; border-radius:4px; }
.error { background:#FBE3D2; color:#9A3412; } .warn { background:#FCEFC7; color:#7A5200; } .ok { background:#E2F0E8; color:#1E6B4A; }
.cc-table { width:100%; border-collapse:collapse; background:#fff; border:1px solid #D5DCE8; border-radius:8px; }
.cc-table th { text-align:left; font-weight:400; color:#4A5670; font-size:13px; background:#F2F5FA; padding:8px 12px; }
.cc-table td { padding:10px 12px; border-top:1px solid #E6EAF2; color:#0E1B3D; }
.cc-val { font-family:'IBM Plex Mono',monospace; padding:2px 6px; border-radius:4px; }
.cc-val.bad { background:#FBE3D2; color:#9A3412; }
.cc-meta { color:#4A5670; font-size:13px; }
[data-testid="stHorizontalBlock"]:has([data-testid="stButtonGroup"]) {
  margin-top:56px; padding-top:16px; padding-bottom:24px; border-top:1px solid #D5DCE8; }
[data-testid="stColumn"]:has([data-testid="stButtonGroup"]) [data-testid="stVerticalBlock"] { align-items:flex-end; }
[data-testid="stButtonGroup"] button { min-height:26px; height:26px; padding:0 9px; font-size:12px;
  background:transparent; border-color:#D5DCE8; color:#4A5670; }
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[kind*="Active"] {
  color:#0E1B3D; background:#FFFFFF; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
_mark = (ROOT / "assets" / "concord-lockup-dark.svg").read_text()
_mark = re.sub(r'<rect[^>]*/>', '', _mark, count=1)          # drop the navy backdrop rect
_mark = re.sub(r'\s(width|height)="[^"]*"', '', _mark.split('>', 1)[0]) + '>' + _mark.split('>', 1)[1]
if "lang" not in st.session_state:
    qp = st.query_params.get("lang", "az")
    st.session_state.lang = qp if qp in LANGS else "az"
if st.session_state.get("lang_pick") is None:          # first run, or the pick was cleared
    st.session_state.lang_pick = st.session_state.lang
L = st.session_state.lang
st.query_params["lang"] = L                            # keeps the language on reload and in shared links


def _on_lang():
    v = st.session_state.lang_pick
    if v is None:                                      # clicking the active option must not clear it
        st.session_state.lang_pick = st.session_state.lang
    else:
        st.session_state.lang = v
st.markdown(f'<div class="cc-head">{_mark}<span>{t("tagline", L)}</span></div>', unsafe_allow_html=True)


def unit_en(v):
    return v.replace(" kq", " kg")


def unit(v):
    return v.replace(" kq", {"az": " kq", "en": " kg", "ru": " кг"}[L]) if isinstance(v, str) else v


def run_pipeline(files: dict):
    from concord.extract import extract
    from concord.compare import check
    docs = []
    with st.status(t("reading", L), expanded=True) as s:
        for k, up in files.items():
            st.write(t("reading_one", L, doc=doc_label(k, L)))
            with tempfile.NamedTemporaryFile(suffix=Path(up.name).suffix, delete=False) as f:
                f.write(up.getvalue()); p = Path(f.name)
            d = extract(p, k); d["_source_file"] = up.name; docs.append(d)
        s.update(label=t("comparing", L))
        res = check(docs, use_ai=True)
        s.update(label=t("done", L), state="complete", expanded=False)
    res["docs"] = docs
    return res


tab_up, tab_res = st.tabs([t("tab_upload", L), t("tab_result", L)])
with tab_up:
    st.subheader(t("upload_title", L))
    st.caption(t("upload_hint", L))
    cols = st.columns(4)
    files = {}
    for c, k in zip(cols, DOC_TYPES):
        with c:
            up = st.file_uploader(doc_label(k, L), type=["pdf", "png", "jpg", "jpeg"], key=k)
            if up: files[k] = up
    b1, b2, _ = st.columns([1, 1.6, 9], gap="small")
    if b1.button(t("check", L), type="primary", disabled=len(files) < 2):
        try:
            st.session_state.result = run_pipeline(files)
            st.success(t("done_go", L))
        except Exception as e:
            st.error(t("failed", L, e=e))
    if b2.button(t("sample", L)):
        st.session_state.result = json.loads((ROOT / "demo" / "sample_result.json").read_text())
        st.success(t("sample_go", L))

with tab_res:
    res = st.session_state.get("result")
    if not res:
        st.info(t("empty", L))
    else:
        c = res["counts"]
        m1, m2, m3, _ = st.columns([1, 1, 1, 4])
        m1.markdown(f'<div class="cc-count" style="color:#9A3412">{c["error"]}</div><div class="cc-meta">{t("n_error", L)}</div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="cc-count" style="color:#7A5200">{c["warn"]}</div><div class="cc-meta">{t("n_warn", L)}</div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="cc-count" style="color:#1E6B4A">{len(res["passed"]) + c["ok"]}</div><div class="cc-meta">{t("n_ok", L)}</div>', unsafe_allow_html=True)
        st.write("")
        f_tab, l_tab, d_tab = st.tabs([t("tab_findings", L), t("tab_letter", L), t("tab_data", L)])
        with f_tab:
            for f in res["findings"]:
                ft = finding_text(f, L)
                sev = SEV[f["severity"]][L]
                with st.expander(f"{sev} · {ft['title']}", expanded=f["severity"] == "error"):
                    st.markdown(f'<span class="cc-badge {f["severity"]}">{sev}</span> '
                                f'<span class="cc-meta">{ft["field"]}</span>', unsafe_allow_html=True)
                    st.write(ft["summary"])
                    rows = "".join(f'<tr><td>{doc_label(r["doc_key"], L) if r.get("doc_key") else r["doc"]}</td>'
                                   f'<td><span class="cc-val {"bad" if r.get("bad") else ""}">{unit(r["value"])}</span></td>'
                                   f'<td class="cc-meta">{r["where"]}</td></tr>' for r in f["rows"])
                    st.markdown(f'<table class="cc-table"><tr><th>{t("col_doc", L)}</th><th>{t("col_value", L)}</th>'
                                f'<th>{t("col_where", L)}</th></tr>{rows}</table>', unsafe_allow_html=True)
                    a, b = st.columns(2)
                    a.markdown(f'<div class="cc-meta">{t("who", L)}</div><b>{ft["checker"]}</b>', unsafe_allow_html=True)
                    b.markdown(f'<div class="cc-meta">{t("fix", L)}</div><b>{unit(ft["fix"])}</b>', unsafe_allow_html=True)
            if res["passed"]:
                st.markdown(f"**{t('passed', L)}** " + " ".join(
                    f'<span class="cc-badge ok">{CHECK.get(p, {}).get(L, p)}</span>' for p in res["passed"]), unsafe_allow_html=True)
        with l_tab:
            docs = res.get("docs", [])
            awb = next((d.get("awb_no") for d in docs if d.get("awb_no")), "[AWB]")
            shipper = next((d.get("shipper_name") for d in docs if d.get("shipper_name")), "[SHIPPER]")
            letter = build_letter(res["findings"], awb, shipper)
            st.code(unit_en(letter) if letter else t("no_letter", L), language=None)
            st.caption(t("letter_note", L))
        with d_tab:
            st.json(res.get("docs", []))

_, foot = st.columns([12, 2])
with foot:
    st.segmented_control("Language", list(LANGS), format_func=lambda k: LANGS[k],
                         key="lang_pick", on_change=_on_lang, label_visibility="collapsed")
