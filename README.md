# SSL Expiry Checker (Python, Standard Library)

`targets.txt` に書いたドメインのTLS/SSL証明書を取得し、有効期限（残日数）を一覧表示するツールです。
証明書更新忘れによる障害を事前に検知する目的で作成しました。

## Features
- ドメイン一覧（`targets.txt`）から証明書の有効期限を取得
- 残日数とステータスを表示（OK / WARN / EXPIRED / ERROR）
- 監視ツール等に組み込みやすい終了コード（0 / 1 / 2）
- 追加インストール不要（標準ライブラリのみ）

## Files
- `ssl_expiry_check.py` : メインスクリプト
- `targets.txt` : チェック対象（1行に1ドメイン、`#` コメント可）
- `.gitignore` : Git管理外設定

## Requirements
- Python 3.10+（動作確認: Python 3.12）

## Usage
```powershell
python .\ssl_expiry_check.py .\targets.txt --warn-days 30

```
## Example Output

```text
HOST                           DAYS_LEFT  STATUS  EXPIRES_UTC / ERROR
------------------------------------------------------------------------------------------
google.com                            58  OK     2026-04-27T08:36:41+00:00
example.com                           75  OK     2026-05-14T18:57:50+00:00
