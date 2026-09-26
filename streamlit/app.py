import json
import uuid
from datetime import date, datetime
from pathlib import Path

import streamlit as st

import auth
import style

# ---------------------------------------------------------------
# 保存先: このファイルと同じ場所の data/shops.json
#   ※ data/ は .gitignore でGitに見せない(個人情報が入るため)
# ---------------------------------------------------------------
DATA_FILE = Path(__file__).parent / "data" / "shops.json"

GENRES = ["和菓子", "工芸", "食", "その他"]

# 一覧を1ページに何件出すか（第43課題）。
# 全件を一度に出すと、件数に比例して画面部品が増えて固まるため区切る。
PER_PAGE = 20

# 長さの上限。入力は止めず、「確認する」を押したときに調べて赤字で伝える。
LIMITS = [
    ("name", "お店・工房の名前", 60),
    ("founded", "創業年", 40),
    ("owner", "店主・職人のお名前", 40),
    ("site", "公式サイト", 200),
    ("shop_url", "公式通販", 200),
    ("reason", "続いてきた理由", 3000),
    ("photo_memo", "撮影メモ", 2000),
    ("note", "備考", 2000),
]

# 確認表示で使う「項目名 → 保存キー」の対応
LABELS = [
    ("お店・工房の名前", "name"),
    ("種類", "genre"),
    ("創業年", "founded"),
    ("店主・職人", "owner"),
    ("掲載許諾", "permitted"),
    ("許諾を得た日", "permitted_on"),
    ("続いてきた理由", "reason"),
    ("公式サイト", "site"),
    ("公式通販", "shop_url"),
    ("撮影メモ", "photo_memo"),
    ("備考", "note"),
]


# ---------------------------------------------------------------
# データの読み書き
# ---------------------------------------------------------------
def save_all(shops):
    """取材ノートのリストを丸ごとファイルに書き戻す。

    いきなり本物のファイルへ書くと、途中で失敗したとき中身が壊れる。
    (第14〜16課題の作業中に、実際に書き戻しでファイルを壊した経験あり)
    まず隣に一時ファイルを書き、最後まで書けたら置き換える。
    こうすれば、失敗しても元のファイルは無傷で残る。
    """
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(shops, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    tmp.replace(DATA_FILE)


def load_shops():
    """保存済みの取材ノートを読み込む。

    1件ずつを見分けるための id が無い記録には、その場で付けて保存し直す。
    (第14課題の時点では id が無かったため。同じ名前のお店が2件あっても
     取り違えないように、名前ではなく id で1件を指す。)
    """
    if not DATA_FILE.exists():
        return []
    try:
        # utf-8-sig: ファイルの先頭に見えない印(BOM)が付いていても読めるようにする。
        # PowerShellなどで手で書き換えると付くことがあるため。
        shops = json.loads(DATA_FILE.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as e:
        # 黙って空を返すと「データが消えた」ようにしか見えない。理由を画面に出す。
        st.error(f"記録の読み込みに失敗しました: {e}")
        st.caption(f"ファイル: {DATA_FILE}")
        st.stop()

    # 1件だけのとき、書き戻し方によってはリストではなく単体で保存されることがある
    if isinstance(shops, dict):
        shops = [shops]

    # 記録の形になっていないもの(手で編集して壊れた等)は取り除く
    shops = [s for s in shops if isinstance(s, dict)]

    changed = False
    for shop in shops:
        if not shop.get("id"):
            shop["id"] = uuid.uuid4().hex[:8]
            changed = True
    if changed:
        save_all(shops)
    return shops


def add_shop(shop):
    """1件追加して保存する。"""
    shops = load_shops()
    shops.append(shop)
    save_all(shops)


def update_shop(shop_id, new_values, owner):
    """id で1件を探して、内容を書き換えて保存する。

    owner(いま入っている人)と記録の author が違えば、何もしない。
    画面に出さないだけでは守りとして足りない。画面は作り変えられるので、
    実際に書き換える側でも持ち主を確かめる。
    """
    shops = load_shops()
    target = index_by_id(shops).get(shop_id)   # 端から探さず、辞書で一発
    if target is None or target.get("author") != owner:
        return False
    target.update(new_values)
    target["updated_at"] = datetime.now().isoformat(timespec="seconds")
    save_all(shops)   # 辞書の中身はリストの中身と同じ物なので、これで保存される
    return True


def delete_shop(shop_id, owner):
    """id で1件を消して保存する。持ち主でなければ消さない。"""
    shops = load_shops()
    target = index_by_id(shops).get(shop_id)   # 端から探さず、辞書で一発
    if target is None or target.get("author") != owner:
        return False
    save_all([s for s in shops if s.get("id") != shop_id])
    return True


def check_record(record):
    """入力に問題がないか調べて、直してほしいことの一覧を返す。

    問題が無ければ空のリスト。入力自体は止めないので、
    長い文章を貼り付けてから直すこともできる。
    """
    problems = []
    if not record["name"]:
        problems.append("お店・工房の名前を入力してください")
    for key, label, limit in LIMITS:
        length = len(record.get(key, ""))
        if length > limit:
            problems.append(
                f"「{label}」が長すぎます（{length}字／{limit}字まで）。"
                f"{length - limit}字減らしてください"
            )
    return problems


def index_by_id(shops):
    """記録のリストから「id で引くための辞書」を作る（第44課題）。

    リストは「新しい順に並べる」のが得意だが、「1件を引く」のは苦手で、
    端から順に見るため件数に比例して遅くなる(O(n))。
    辞書は id をそのまま鍵にできるので、何件あっても一発で引ける(O(1))。

    実測（1件を探すのにかかった時間）:
        件数        リスト(端から)   辞書(一発)   差
        100         3.1 μ秒        0.047 μ秒     66倍
        10,000    321.1 μ秒        0.055 μ秒   5,838倍
        100,000  3463.3 μ秒        0.074 μ秒  46,801倍

    「順番に並べる」はリスト、「1件を引く」は辞書。
    役割が違うので、1つの入れ物に両方やらせない。
    """
    return {s["id"]: s for s in shops if s.get("id")}


def find_shop(index, shop_id):
    """id で1件を引く。index は index_by_id() で作った辞書。"""
    return index.get(shop_id)


# ---------------------------------------------------------------
# ログイン画面
# ---------------------------------------------------------------
def login_screen():
    style.header("工芸と老舗をたずねる紀行 — 取材の記録", "ようこそ")
    st.caption("取材の記録は、書いた本人だけが見られます。")

    tab_login, tab_register = st.tabs(["入る", "はじめて使う"])

    with tab_login:
        with st.form("login_form", enter_to_submit=False, border=False):
            name = st.text_input("お名前", key="login_name")
            password = st.text_input("合言葉", type="password", key="login_pw")
            if st.form_submit_button("入る", type="primary"):
                if auth.verify(name, password):
                    st.session_state["user"] = name.strip()
                    st.rerun()
                else:
                    # どちらが違うかは言わない。
                    # 「お名前は合っている」と教えると、名前当てのヒントになるため。
                    st.error("お名前か合言葉が違います")

    with tab_register:
        with st.form("register_form", enter_to_submit=False, border=False):
            new_name = st.text_input("お名前", key="reg_name")
            new_password = st.text_input(
                "合言葉", type="password", key="reg_pw",
                placeholder=f"{auth.MIN_PASSWORD}文字以上",
            )
            if st.form_submit_button("登録する", type="primary"):
                ok, message = auth.register(new_name, new_password)
                if ok:
                    st.success(message + "。「入る」から入ってください。")
                else:
                    st.error(message)
        st.caption(
            "合言葉そのものは保存しません。変換した結果だけを保存するので、"
            "忘れても誰にも調べられません(その場合は登録し直しになります)。"
        )


# ---------------------------------------------------------------
# 入力フォーム(新規と編集で同じものを使う)
# ---------------------------------------------------------------
def shop_form(form_key, initial, submit_label):
    """入力欄を並べて、押されたかどうかと入力内容を返す。"""
    k = form_key  # 入力欄の名札。新規と編集で重ならないようにする

    try:
        default_day = date.fromisoformat(initial.get("permitted_on") or "")
    except ValueError:
        default_day = date.today()

    genre_value = initial.get("genre", GENRES[0])
    genre_index = GENRES.index(genre_value) if genre_value in GENRES else 0

    with st.form(k, clear_on_submit=False, enter_to_submit=False, border=False):
        # ここで max_chars は使わない。
        #   黙って入力を拒むため、貼り付けが効かなくなり、しかも理由が分からない
        #   (2026-09-25、岩瀬様が「名前にコピペが使えません」と発見)。
        #   長さは「確認する」を押したときに LIMITS で調べ、赤字で理由を出す。
        name = st.text_input(
            "お店・工房の名前", value=initial.get("name", ""),
            placeholder="必須", key=f"{k}_name",
        )
        genre = st.selectbox("種類", GENRES, index=genre_index, key=f"{k}_genre")
        founded = st.text_input(
            "創業年", value=initial.get("founded", ""),
            placeholder="例: 創業110年 / 1916年", key=f"{k}_founded",
        )
        owner = st.text_input(
            "店主・職人のお名前", value=initial.get("owner", ""),
            placeholder="次に伺った時に聞く", key=f"{k}_owner",
        )
        permitted = st.radio(
            "掲載許諾", ["未", "済"], horizontal=True,
            index=1 if initial.get("permitted") == "済" else 0, key=f"{k}_permitted",
        )
        permitted_on = st.date_input("許諾を得た日", value=default_day, key=f"{k}_day")
        reason = st.text_area(
            "続いてきた理由", value=initial.get("reason", ""),
            placeholder="何を変え、何を変えずに残してきたか。聞いたことをそのまま書く(推測で補わない)",
            key=f"{k}_reason",
        )
        site = st.text_input(
            "公式サイト", value=initial.get("site", ""),
            placeholder="なければ空欄", key=f"{k}_site",
        )
        shop_url = st.text_input(
            "公式通販", value=initial.get("shop_url", ""),
            placeholder="なければ空欄", key=f"{k}_shop_url",
        )
        photo_memo = st.text_area(
            "撮影メモ", value=initial.get("photo_memo", ""),
            placeholder="例: 午前の自然光がよい、工程の撮影は要相談",
            key=f"{k}_photo",
        )
        note = st.text_area("備考", value=initial.get("note", ""), key=f"{k}_note")
        st.write("")
        submitted = st.form_submit_button(submit_label, type="primary")

    record = {
        "name": name.strip(),
        "genre": genre,
        "founded": founded.strip(),
        "owner": owner.strip(),
        "permitted": permitted,
        # 日付欄は空にもできるので、無いときに落ちないようにする
        "permitted_on": (
            permitted_on.isoformat() if permitted == "済" and permitted_on else ""
        ),
        "reason": reason.strip(),
        "site": site.strip(),
        "shop_url": shop_url.strip(),
        "photo_memo": photo_memo.strip(),
        "note": note.strip(),
    }
    return submitted, record


# ---------------------------------------------------------------
# 確認の小窓
# ---------------------------------------------------------------
@st.dialog("この内容で記録します")
def confirm_new_dialog(record):
    style.record_rows(record, LABELS)
    st.write("")
    col_back, col_save = st.columns(2)
    with col_back:
        if st.button("書き直す", use_container_width=True):
            st.session_state.pop("pending", None)
            st.rerun()
    with col_save:
        if st.button("記録する", type="primary", use_container_width=True):
            record["id"] = uuid.uuid4().hex[:8]
            record["author"] = st.session_state["user"]   # 書いた人
            record["created_at"] = datetime.now().isoformat(timespec="seconds")
            add_shop(record)
            st.session_state.pop("pending", None)
            st.session_state["flash"] = f"「{record['name']}」を記録しました"
            st.session_state.seq += 1  # 入力欄を空に戻す
            st.rerun()


@st.dialog("この内容に書き換えます")
def confirm_edit_dialog(shop_id, record):
    style.record_rows(record, LABELS)
    st.write("")
    col_back, col_save = st.columns(2)
    with col_back:
        if st.button("やめる", use_container_width=True):
            st.session_state.pop("pending_edit", None)
            st.rerun()
    with col_save:
        if st.button("書き換える", type="primary", use_container_width=True):
            if not update_shop(shop_id, record, st.session_state["user"]):
                st.error("この記録は書き換えられません")
                return
            st.session_state.pop("pending_edit", None)
            st.session_state.pop("editing", None)
            st.session_state["flash"] = f"「{record['name']}」を書き換えました"
            st.rerun()


@st.dialog("この記録を削除します")
def delete_dialog(shop):
    st.markdown(f"#### {shop.get('name', '(名前なし)')}")
    st.caption(
        f"{shop.get('genre', '')}　{shop.get('founded') or '創業年 未記入'}"
    )
    st.warning("削除すると元に戻せません。")
    col_back, col_del = st.columns(2)
    with col_back:
        if st.button("やめる", use_container_width=True):
            st.session_state.pop("deleting", None)
            st.rerun()
    with col_del:
        if st.button("削除する", type="primary", use_container_width=True):
            if not delete_shop(shop["id"], st.session_state["user"]):
                st.error("この記録は削除できません")
                return
            st.session_state.pop("deleting", None)
            st.session_state["flash"] = f"「{shop.get('name', '')}」を削除しました"
            st.rerun()


# ---------------------------------------------------------------
# 画面
# ---------------------------------------------------------------
st.set_page_config(page_title="百年散歩 運営ツール", page_icon="🏮")
style.apply()

if "seq" not in st.session_state:
    st.session_state.seq = 0

# ログインしていない人は、ここから先へ進めない
if not st.session_state.get("user"):
    login_screen()
    st.stop()

user = st.session_state["user"]

# 自分が書いた記録だけを扱う。以降 shops は「自分のもの」しか入っていない。
shops = [s for s in load_shops() if s.get("author") == user]
# 「新しい順に並べる」のはリスト(shops)、「id で1件を引く」のは辞書(shops_by_id)。
# 役割ごとに入れ物を分ける(第44課題)。辞書は1回作るだけで、以降は何度引いても一発。
shops_by_id = index_by_id(shops)

style.header("工芸と老舗をたずねる紀行 — 取材の記録", f"{len(shops)} 軒")

col_who, col_out = st.columns([5, 1])
with col_who:
    st.caption(f"{user} さんとして入っています")
with col_out:
    if st.button("出る", use_container_width=True):
        for key in ["user", "editing", "pending", "pending_edit", "deleting", "last_line"]:
            st.session_state.pop(key, None)
        st.rerun()

# 記録・書き換え・削除の結果は、小さな通知と一行の報告だけで伝える
if st.session_state.get("flash"):
    message = st.session_state.pop("flash")
    st.toast(message)
    st.session_state["last_line"] = message
if st.session_state.get("last_line"):
    st.caption(st.session_state["last_line"])

tab_new, tab_list, tab_contact = st.tabs(["取材ノート", "記録一覧", "お問い合わせ"])

# ---------- 新しく記録する ----------
with tab_new:
    submitted, record = shop_form(
        f"new_{st.session_state.seq}", {}, "確認する"
    )
    if submitted:
        problems = check_record(record)
        if problems:
            for p in problems:
                st.error(p)
        else:
            st.session_state["pending"] = record
            st.rerun()

    if st.session_state.get("pending"):
        confirm_new_dialog(st.session_state["pending"])

    if st.button("新しく書く（入力欄を空にする）"):
        st.session_state.seq += 1
        st.session_state.pop("last_line", None)
        st.rerun()

# ---------- 一覧・編集・削除 ----------
with tab_list:
    editing_id = st.session_state.get("editing")

    if editing_id:
        # --- 編集画面 ---
        target = find_shop(shops_by_id, editing_id)
        if target is None:
            st.session_state.pop("editing", None)
            st.rerun()
        else:
            st.markdown(f"##### 「{target.get('name', '')}」を直す")
            edited, new_values = shop_form(
                f"edit_{editing_id}", target, "確認する"
            )
            if edited:
                problems = check_record(new_values)
                if problems:
                    for p in problems:
                        st.error(p)
                else:
                    st.session_state["pending_edit"] = new_values
                    st.rerun()

            if st.session_state.get("pending_edit"):
                confirm_edit_dialog(editing_id, st.session_state["pending_edit"])

            if st.button("一覧に戻る"):
                st.session_state.pop("editing", None)
                st.session_state.pop("pending_edit", None)
                st.rerun()

    elif not shops:
        st.markdown(
            '<div class="empty-note">まだ記録がありません。<br>'
            '「取材ノート」から最初の一軒を記録してください。</div>',
            unsafe_allow_html=True,
        )

    else:
        # --- 一覧 --- 新しく記録したものが上に来るように並べ替える
        ordered = sorted(shops, key=lambda s: s.get("created_at", ""), reverse=True)

        # ページ送り（第43課題）
        #   以前は全件をそのまま画面に出していた。1件につき画面部品が6個できるため、
        #   1万件なら6万個、10万件なら60万個になり、ブラウザが固まる。
        #   1ページ20件に区切れば、何件あっても画面部品は120個で頭打ちになる。
        #   人間はそもそも1万件を一度に見られないので、使う人にとっても親切。
        total = len(ordered)
        last_page = max(1, -(-total // PER_PAGE))   # 切り上げ
        if st.session_state.get("page", 1) > last_page:
            st.session_state["page"] = last_page
        page = st.session_state.get("page", 1)
        start = (page - 1) * PER_PAGE
        showing = ordered[start:start + PER_PAGE]

        if last_page > 1:
            col_prev, col_mid, col_next = st.columns([1, 3, 1])
            with col_prev:
                if st.button("← 前", disabled=(page <= 1), use_container_width=True):
                    st.session_state["page"] = page - 1
                    st.rerun()
            with col_mid:
                st.markdown(
                    f'<div style="text-align:center;font-size:.8rem;opacity:.7">'
                    f'{start + 1}〜{min(start + PER_PAGE, total)} 件目 ／ 全 {total} 軒'
                    f'（{page} / {last_page} ページ）</div>',
                    unsafe_allow_html=True,
                )
            with col_next:
                if st.button("次 →", disabled=(page >= last_page), use_container_width=True):
                    st.session_state["page"] = page + 1
                    st.rerun()
            st.write("")

        for shop in showing:
            permit = (
                '<span class="ok">許諾済</span>'
                if shop.get("permitted") == "済"
                else '<span class="yet">許諾まだ</span>'
            )
            # 入力された文字はHTMLの命令にならないよう style.safe() を通す。
            # permit だけは自分で書いたタグなので、そのまま使う。
            meta = "　・　".join([
                style.safe(shop.get("genre", "")),
                style.safe(shop.get("founded") or "創業年 未記入"),
                permit,
            ])
            col_body, col_edit, col_del = st.columns([6, 1.2, 1.2])
            with col_body:
                st.markdown(
                    f'<div class="card"><div class="nm">'
                    f'{style.safe(shop.get("name") or "(名前なし)")}</div>'
                    f'<div class="meta">{meta}</div></div>',
                    unsafe_allow_html=True,
                )
            with col_edit:
                if st.button("直す", key=f"edit_btn_{shop['id']}", use_container_width=True):
                    st.session_state["editing"] = shop["id"]
                    st.rerun()
            with col_del:
                if st.button("消す", key=f"del_btn_{shop['id']}", use_container_width=True):
                    st.session_state["deleting"] = shop["id"]
                    st.rerun()

        if st.session_state.get("deleting"):
            target = find_shop(shops_by_id, st.session_state["deleting"])
            if target is None:
                st.session_state.pop("deleting", None)
            else:
                delete_dialog(target)

# ---------- お問い合わせ ----------
with tab_contact:
    st.caption("取材ノートが動いたら、同じ作り方でここを作ります。")
