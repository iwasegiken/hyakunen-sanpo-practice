"""百年散歩 運営ツールの見た目。サイト本体(index.html)と同じ意匠に揃える。

色・書体の定義はサイト本体と合わせてある:
  藍(深) #0f1c30 / 藍 #16283f / 金 #c9a24e / 朱 #b7412c / 生成り #f3efe4
"""

import streamlit as st

# 判子ロゴ(サイト本体のSVGと同じ意匠。2×2で「百年散歩」)
SEAL_SVG = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" class="seal">
  <rect x="6" y="6" width="88" height="88" rx="4" fill="#b7412c"/>
  <rect x="13" y="13" width="74" height="74" rx="1" fill="none" stroke="#f3efe4" stroke-width="2"/>
  <text x="31" y="42" text-anchor="middle" font-family="'Yuji Boku', serif" font-size="26" fill="#f3efe4">百</text>
  <text x="69" y="42" text-anchor="middle" font-family="'Yuji Boku', serif" font-size="26" fill="#f3efe4">年</text>
  <text x="31" y="80" text-anchor="middle" font-family="'Yuji Boku', serif" font-size="26" fill="#f3efe4">散</text>
  <text x="69" y="80" text-anchor="middle" font-family="'Yuji Boku', serif" font-size="26" fill="#f3efe4">歩</text>
</svg>
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Old+Mincho:wght@400;600&family=Noto+Sans+JP:wght@300;400;500&family=EB+Garamond:ital@0;1&family=Yuji+Boku&display=swap');

:root {
  --indigo-deep: #0f1c30;
  --indigo: #16283f;
  --gold: #c9a24e;
  --gold-soft: #9c8452;
  --vermillion: #b7412c;
  --paper: #f3efe4;
  --paper-dim: #cfd4dd;
}

/* 背景 — サイト本体と同じ、中心が少し明るい藍 */
[data-testid="stAppViewContainer"] {
  background: var(--indigo-deep);
  background-image: radial-gradient(circle at 50% 0%, var(--indigo) 0%, var(--indigo-deep) 70%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 760px; padding-top: 3.5rem; }

html, body, [data-testid="stAppViewContainer"] * {
  font-family: "Noto Sans JP", sans-serif;
}

/* config.toml の配色が効く前(再起動前)でも読めるようにしておく */
[data-testid="stAppViewContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong {
  color: var(--paper);
}

/* 題字まわり */
.brand { display: flex; align-items: center; gap: 1.1em; margin-bottom: 0.4em; }
.brand .seal {
  width: 56px; height: 56px; flex: none;
  transform: rotate(-3deg);
  filter: drop-shadow(0 0 14px rgba(183, 65, 44, 0.45));
}
.brand-text .kicker {
  font-family: "EB Garamond", serif; font-style: italic;
  letter-spacing: 0.3em; font-size: 0.7rem; color: var(--gold);
  text-transform: uppercase;
}
.brand-text h1 {
  font-family: "Zen Old Mincho", serif; font-weight: 600;
  font-size: 1.9rem; letter-spacing: 0.12em; color: var(--paper);
  margin: 0.1em 0 0;
}
.brand-sub {
  color: var(--paper-dim); font-size: 0.85rem; letter-spacing: 0.04em;
  border-top: 1px solid rgba(201, 162, 78, 0.25);
  padding-top: 1em; margin: 1.4em 0 2.4em;
  display: flex; justify-content: space-between; gap: 1em; flex-wrap: wrap;
}
.brand-sub .count { color: var(--gold); font-family: "EB Garamond", serif; font-style: italic; }

/* 見出し */
h2, h3, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {
  font-family: "Zen Old Mincho", serif !important;
  letter-spacing: 0.08em; color: var(--paper);
}

/* タブ */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 2em; border-bottom: 1px solid rgba(201,162,78,0.25); }
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family: "Zen Old Mincho", serif; letter-spacing: 0.1em; color: var(--paper-dim);
  background: transparent; padding-left: 0; padding-right: 0;
}
[data-testid="stTabs"] [aria-selected="true"] { color: var(--gold) !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--gold); }

/* フォーム — 枠線を消して余白で見せる */
[data-testid="stForm"] { border: none; padding: 0; }

/* 項目名 */
[data-testid="stWidgetLabel"] p {
  color: var(--gold) !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.12em;
  font-weight: 400 !important;
  margin-bottom: 0.35em;
}

/* 入力欄 — 下線だけの和風 */
[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"],
[data-testid="stSelectbox"] .react-aria-ComboBox > div,
[data-testid="stDateInput"] div[data-baseweb="input"],
[data-testid="stDateInputField"] {
  background: rgba(243, 239, 228, 0.03) !important;
  border: none !important;
  border-bottom: 1px solid rgba(201, 162, 78, 0.35) !important;
  border-radius: 2px 2px 0 0 !important;
  box-shadow: none !important;
  transition: border-color 0.25s ease, background 0.25s ease;
}
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stDateInputField"]:focus-within,
[data-testid="stSelectbox"] .react-aria-ComboBox > div:focus-within {
  border-bottom-color: var(--gold) !important;
  background: rgba(243, 239, 228, 0.07) !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {
  color: var(--paper) !important;
  font-size: 0.98rem !important;
  background: transparent !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
  color: rgba(207, 212, 221, 0.35) !important;
  font-size: 0.85rem;
}

/* ラジオ */
[data-testid="stRadio"] label p { color: var(--paper-dim) !important; font-size: 0.9rem !important; }

/* ボタン */
[data-testid="stBaseButton-primaryFormSubmit"],
[data-testid="stBaseButton-primary"] {
  background: var(--vermillion) !important;
  border: 1px solid var(--vermillion) !important;
  color: var(--paper) !important;
  font-family: "Zen Old Mincho", serif !important;
  letter-spacing: 0.18em;
  border-radius: 2px !important;
  box-shadow: 0 0 18px rgba(183, 65, 44, 0.25);
}
[data-testid="stBaseButton-secondaryFormSubmit"],
[data-testid="stBaseButton-secondary"] {
  background: transparent !important;
  border: 1px solid rgba(201, 162, 78, 0.45) !important;
  color: var(--gold) !important;
  font-family: "Zen Old Mincho", serif !important;
  letter-spacing: 0.18em;
  border-radius: 2px !important;
}
[data-testid="stBaseButton-secondary"]:hover,
[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
  border-color: var(--gold) !important;
  background: rgba(201, 162, 78, 0.08) !important;
}

/* 確認ダイアログ */
[data-testid="stDialog"] div[role="dialog"] {
  background: var(--indigo) !important;
  border: 1px solid rgba(201, 162, 78, 0.3);
  border-radius: 3px;
}
[data-testid="stDialog"] h2 {
  font-family: "Zen Old Mincho", serif !important;
  letter-spacing: 0.12em; color: var(--gold) !important; font-size: 1.1rem !important;
}

/* 確認ダイアログの中の一覧 */
.rec-row {
  display: flex; gap: 1.2em; padding: 0.45em 0;
  border-bottom: 1px solid rgba(201, 162, 78, 0.12);
  font-size: 0.9rem;
}
.rec-row .k {
  color: var(--gold); flex: 0 0 9.5em; letter-spacing: 0.06em; font-size: 0.8rem;
  padding-top: 0.15em;
}
.rec-row .v { color: var(--paper); white-space: pre-wrap; }
.rec-row .v.empty { color: rgba(207, 212, 221, 0.3); }

/* 記録一覧のカード */
.card {
  border-bottom: 1px solid rgba(201, 162, 78, 0.15);
  padding: 0.7em 0 0.55em;
}
.card .nm {
  font-family: "Zen Old Mincho", serif;
  font-size: 1.02rem; letter-spacing: 0.06em; color: var(--paper);
}
.card .meta {
  font-size: 0.74rem; color: var(--paper-dim); opacity: 0.75;
  letter-spacing: 0.04em; margin-top: 0.15em;
}
.card .meta .ok { color: var(--gold); }
.card .meta .yet { color: rgba(207, 212, 221, 0.45); }
.empty-note {
  color: var(--gold-soft); font-size: 0.85rem;
  border: 1px dashed rgba(201, 162, 78, 0.3);
  border-radius: 3px; padding: 2em 1em; text-align: center;
}

/* 注意書き */
[data-testid="stCaptionContainer"] p { color: var(--gold-soft) !important; font-size: 0.75rem !important; }
</style>
"""


def apply():
    """CSSを読み込んで、題字を描く。"""
    st.markdown(CSS, unsafe_allow_html=True)


def _compact(html):
    """字下げと改行を取り除く。

    Markdownは行頭に4つ以上の空白があると「コード」と解釈してしまい、
    HTMLがそのまま文字として表示される。それを避けるため1行にまとめる。
    """
    return "".join(line.strip() for line in html.splitlines())


def header(subtitle, count_text):
    html = (
        f'<div class="brand">{_compact(SEAL_SVG)}'
        f'<div class="brand-text">'
        f'<div class="kicker">Hyakunen Sanpo</div>'
        f"<h1>百年散歩 運営ツール</h1>"
        f"</div></div>"
        f'<div class="brand-sub"><span>{safe(subtitle)}</span>'
        f'<span class="count">{safe(count_text)}</span></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def safe(text):
    """入力された文字を、HTMLの「命令」ではなく「ただの文字」として扱う。

    この画面はHTMLを自分で組み立てて描いているため、入力に <b> や <img> が
    混ざるとタグとして解釈されてしまう(第38課題で学んだXSSと同じ形)。
    < > & " を別の書き方に置き換えて、見たままの文字として表示させる。
    """
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def record_rows(rec, labels):
    """記録の内容を、項目名つきの行で描く。"""
    rows = []
    for label, key in labels:
        value = rec.get(key, "")
        cls = "v" if value else "v empty"
        shown = safe(value) if value else "—"
        rows.append(
            f'<div class="rec-row"><div class="k">{safe(label)}</div>'
            f'<div class="{cls}">{shown}</div></div>'
        )
    st.markdown("".join(rows), unsafe_allow_html=True)
