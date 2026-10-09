"""Concord - Streamlit demo. Run: streamlit run app.py"""
import json, tempfile
from pathlib import Path
import streamlit as st
from concord.schema import DOC_TYPES, DOC_LABELS
from concord.letter import build_letter

ROOT = Path(__file__).parent
st.set_page_config(page_title="Concord", page_icon=str(ROOT / "assets" / "favicon-32.png"), layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
.stApp { background: #EEF2F9; color: #0E1B3D; }
.cc-head { background:#0E1B3D; margin:-1rem -1rem 1.5rem; padding:14px 32px; display:flex; align-items:center; gap:12px; }
.cc-head span { color:#A9B6D3; font-size:14px; }
.cc-count { font-family:'IBM Plex Mono',monospace; font-size:32px; font-weight:500; line-height:1.1; }
.cc-badge { font-size:12px; font-weight:600; padding:2px 8px; border-radius:4px; }
.error { background:#FBE3D2; color:#9A3412; } .warn { background:#FCEFC7; color:#7A5200; } .ok { background:#E2F0E8; color:#1E6B4A; }
.cc-table { width:100%; border-collapse:collapse; background:#fff; border:1px solid #D5DCE8; border-radius:8px; }
.cc-table th { text-align:left; font-weight:400; color:#4A5670; font-size:13px; background:#F2F5FA; padding:8px 12px; }
.cc-table td { padding:10px 12px; border-top:1px solid #E6EAF2; }
.cc-val { font-family:'IBM Plex Mono',monospace; padding:2px 6px; border-radius:4px; }
.cc-val.bad { background:#FBE3D2; color:#9A3412; }
.cc-meta { color:#4A5670; font-size:13px; }
.stButton button[kind="primary"] { background:#1F45C9; border:0; }
.stButton button[kind="primary"]:hover { background:#18379F; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
logo = (ROOT / "assets" / "concord-lockup-dark.svg").read_text()
st.markdown(f'<div class="cc-head"><div style="height:36px">{logo.replace("<svg", "<svg height=36", 1)}</div>'
            f'<span>Yük sənədlərinin avtomatik tutuşdurulması</span></div>', unsafe_allow_html=True)

LABEL = {"error": "Xəta", "warn": "Yoxlanmalı", "ok": "Uyğun"}


def run_pipeline(files: dict):
    from concord.extract import extract
    from concord.compare import check
    docs = []
    with st.status("Sənədlər oxunur...", expanded=True) as s:
        for t, up in files.items():
            st.write(f"{DOC_LABELS[t]} oxunur")
            with tempfile.NamedTemporaryFile(suffix=Path(up.name).suffix, delete=False) as f:
                f.write(up.getvalue()); p = Path(f.name)
            d = extract(p, t); d["_source_file"] = up.name; docs.append(d)
        s.update(label="Tutuşdurulur...")
        res = check(docs, use_ai=True)
        s.update(label="Hazırdır", state="complete", expanded=False)
    res["docs"] = docs
    return res


tab_up, tab_res = st.tabs(["Yüklə", "Nəticə"])
with tab_up:
    st.subheader("Yükün sənədlərini əlavə edin")
    st.caption("PDF, skan və ya telefon şəkli. Ən azı 2 sənəd lazımdır.")
    cols = st.columns(4)
    files = {}
    for c, t in zip(cols, DOC_TYPES):
        with c:
            up = st.file_uploader(DOC_LABELS[t], type=["pdf", "png", "jpg", "jpeg"], key=t)
            if up: files[t] = up
    b1, b2, _ = st.columns([1, 1, 4])
    if b1.button("Yoxla", type="primary", disabled=len(files) < 2):
        try:
            st.session_state.result = run_pipeline(files)
            st.success("Hazırdır. 'Nəticə' tab-ına keçin.")
        except Exception as e:
            st.error(f"Yoxlama alınmadı: {e}. Sənədi yenidən yükləyin və ya nümunə yükü açın.")
    if b2.button("Nümunə yükü aç"):
        st.session_state.result = json.loads((ROOT / "demo" / "sample_result.json").read_text())
        st.success("Nümunə yük yükləndi. 'Nəticə' tab-ına keçin.")

with tab_res:
    res = st.session_state.get("result")
    if not res:
        st.info("Hələ nəticə yoxdur. Sənəd yükləyin və ya nümunə yükü açın.")
    else:
        c = res["counts"]
        m1, m2, m3, _ = st.columns([1, 1, 1, 4])
        m1.markdown(f'<div class="cc-count" style="color:#9A3412">{c["error"]}</div><div class="cc-meta">xəta</div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="cc-count" style="color:#7A5200">{c["warn"]}</div><div class="cc-meta">yoxlanmalı</div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="cc-count" style="color:#1E6B4A">{len(res["passed"]) + c["ok"]}</div><div class="cc-meta">uyğun</div>', unsafe_allow_html=True)
        st.write("")
        f_tab, l_tab, d_tab = st.tabs(["Uyğunsuzluqlar", "Düzəliş məktubu", "Çıxarılan data"])
        with f_tab:
            for f in res["findings"]:
                with st.expander(f"{LABEL[f['severity']]} · {f['title']}", expanded=f["severity"] == "error"):
                    st.markdown(f'<span class="cc-badge {f["severity"]}">{LABEL[f["severity"]]}</span> '
                                f'<span class="cc-meta">{f["field"]}</span>', unsafe_allow_html=True)
                    st.write(f["summary"])
                    rows = "".join(f'<tr><td>{r["doc"]}</td><td><span class="cc-val {"bad" if r.get("bad") else ""}">{r["value"]}</span></td>'
                                   f'<td class="cc-meta">{r["where"]}</td></tr>' for r in f["rows"])
                    st.markdown(f'<table class="cc-table"><tr><th>Sənəd</th><th>Dəyər</th><th>Harada</th></tr>{rows}</table>', unsafe_allow_html=True)
                    a, b = st.columns(2)
                    a.markdown(f'<div class="cc-meta">Kim aşkarladı</div><b>{f["checker"]}</b>', unsafe_allow_html=True)
                    b.markdown(f'<div class="cc-meta">Təklif olunan düzəliş</div><b>{f["fix"]}</b>', unsafe_allow_html=True)
            if res["passed"]:
                st.markdown("**Uyğun gələn yoxlamalar:** " + " ".join(f'<span class="cc-badge ok">{p}</span>' for p in res["passed"]), unsafe_allow_html=True)
        with l_tab:
            docs = res.get("docs", [])
            awb = next((d.get("awb_no") for d in docs if d.get("awb_no")), "[AWB]")
            shipper = next((d.get("shipper_name") for d in docs if d.get("shipper_name")), "[SHIPPER]")
            letter = build_letter(res["findings"], awb, shipper)
            st.code(letter or "Xəta yoxdur, məktub lazım deyil.", language=None)
            st.caption("Yalnız xəta statuslu bəndlər daxil edilir. Yoxlanmalı bəndlər brokerin təsdiqini gözləyir.")
        with d_tab:
            st.json(res.get("docs", []))
