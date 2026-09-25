"""ログインの担当。

■ 方針: 合言葉(パスワード)そのものは、どこにも保存しない。

  保存するのは「塩 + 合言葉」を一方通行で変換した結果(ハッシュ)と、その塩だけ。
  ログインのときは、入力された合言葉に同じ塩を混ぜて同じ計算をし、
  保存してある結果と一致するかを比べる。

  塩(salt)は人ごとに違うデタラメな文字列。秘密ではなく、ファイルに丸見えで
  書いてある。役割は「秘密を守る」ことではなく「使い回しを禁じる」こと:
    - 世界共通の対応表(sakura → d41dc638...)が使えなくなる
    - 同じ合言葉の人が同じ値にならない

■ 断り書き
  ここで使っているSHA-256は「学習のための実装」。
  本物のサービスでは、総当たりに時間がかかるよう設計された
  bcrypt / Argon2 といった専用の仕組みを使う。
  百年散歩の取材ノートを本当に世界へ公開するときは作り直すこと。
"""

import hashlib
import hmac
import json
import os
from pathlib import Path

# data/ は .gitignore でGit管理外。合言葉の情報をGitHubへ出さないため。
USERS_FILE = Path(__file__).parent / "data" / "users.json"

# 空欄・異常入力で落ちないための決まり(第16課題)
MIN_PASSWORD = 4   # 合言葉は4文字以上
MAX_NAME = 30      # お名前は30文字まで


def _load_users():
    if not USERS_FILE.exists():
        return {}
    try:
        return json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # ファイルが壊れていても落ちない。空として扱う。
        return {}


def _save_users(users):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(
        json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _to_hash(password, salt):
    """PowerShellで手で試したのと同じ計算。sha256(塩 + 合言葉)。"""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def register(username, password):
    """新しく登録する。(成功したか, 画面に出す言葉) を返す。"""
    name = (username or "").strip()
    password = password or ""

    if not name:
        return False, "お名前を入力してください"
    if len(name) > MAX_NAME:
        return False, f"お名前は{MAX_NAME}文字までにしてください"
    if not password:
        return False, "合言葉を入力してください"
    if len(password) < MIN_PASSWORD:
        return False, f"合言葉は{MIN_PASSWORD}文字以上にしてください"

    users = _load_users()
    if name in users:
        return False, "そのお名前はすでに使われています"

    salt = os.urandom(16).hex()          # 人ごとに違うデタラメな塩を作る
    users[name] = {
        "salt": salt,
        "hash": _to_hash(password, salt),
    }
    # ここで password という変数は捨てられる。ファイルに書くのは salt と hash だけ。
    _save_users(users)
    return True, f"「{name}」を登録しました"


def verify(username, password):
    """合言葉が合っているかを確かめる。合っていればTrue。"""
    name = (username or "").strip()
    password = password or ""
    if not name or not password:
        return False

    user = _load_users().get(name)
    if not user:
        return False

    # compare_digest は、違うと分かった時点で止めずに最後まで比べる。
    # 途中で止めると、答えが返るまでの時間の差から合言葉を推測されうるため。
    return hmac.compare_digest(user["hash"], _to_hash(password, user["salt"]))
