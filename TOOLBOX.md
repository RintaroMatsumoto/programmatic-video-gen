# TOOLBOX — programmatic-video-gen

セッション開始時に目を通す実装ノート。試行錯誤で掴んだ事実と、その出典を
恒久化するための場所。記述は「何を／なぜ／どう」の順で。

---

## 1. Remotion 運用規約

### 1.1 アセット参照は `staticFile()` を必ず経由する

- `public/` 配下に置いたファイルは `staticFile("ukiyoe/kanagawa_wave/original.jpg")`
  で参照する。生の相対パスを `<Img src="..." />` に渡すと、Remotion Studio
  プレビューでは通っても `remotion render` のバンドルで解決できず
  「Cannot find module」で失敗する。
- `public/` はリポジトリルート直下固定。`remotion.config.ts` で
  `Config.setPublicDir()` を書き換えた場合のみ別位置。

出典：[Remotion docs — staticFile()](https://www.remotion.dev/docs/staticfile)

### 1.2 JSON インポートは `as unknown as <Type>` で通す

strict TS だと `import data from "./scene.json"` は推論が広すぎて
`UkiyoeData` に代入できない。`tsconfig.json` で `resolveJsonModule: true` を
有効にした上で、Root.tsx 側で

```ts
{registerUkiyoe("kanagawa_wave", kanagawaWave as unknown as UkiyoeData)}
```

と二段キャストする。単純な `as UkiyoeData` だと TS2352 で蹴られる。
スキーマ一致は `generate_script.py` 側が保証する前提。

### 1.3 `durationInFrames` はデータから計算、決め打ちしない

シーン JSON の `duration` (秒) × `fps` の合計で求める。
`computeUkiyoeDuration(data, fps)` ヘルパが `UkiyoeAnimation.tsx` にあるので
Root.tsx からはそれを呼ぶだけ。ハードコードすると尺ミスマッチで末尾が
黒フレームになる／音声が切れる。

### 1.4 レンダリングは必ず `--frames=0-299` で 10 秒プレビューしてから

- フル 4 分のレンダーは CPU なら 60〜90 分かかる。
- まず `npx remotion render UkiyoeKanagawaWave output/preview.mp4 --frames=0-299`
  （= 10 秒）でカメラと字幕タイミングを確認。本番はそのあと。
- Remotion Studio (`npx remotion studio`) でプレビューするのが一番速い。
  スクラブで任意フレームに飛べる。

出典：[Remotion docs — remotion render CLI](https://www.remotion.dev/docs/cli/render)

### 1.5 Ken Burns のオフセット式

`KenBurns.tsx` は `transform-origin` を注視点 (fx, fy) に合わせた上で
以下を同時適用する：

```
offsetX = (0.5 - fx) * width  * (zoom - 1)
offsetY = (0.5 - fy) * height * (zoom - 1)
transform: translate(offsetX, offsetY) scale(zoom)
```

意味：`transform-origin` 自体は注視点に固定。`scale` で広がる分を
画面中央側に戻すことで、拡大中心が画面中央に来る。
fx=0.5, fy=0.5（中央注視）なら offset=0 となり普通の中央ズーム。

この式を崩すと注視点がフレーム外へ飛ぶ。触るときは
`(0.5, 0.5)` と `(0.3, 0.3)` の両方でプレビューして挙動を確認すること。

### 1.6 `concurrency` はデフォルト 1 に落としている

`remotion.config.ts` で `Config.setConcurrency(1)` としている。
Remotion 4.x は既定で CPU コア数ぶんの Chromium を立ち上げるが、
Windows + 4K 画像では RAM がすぐ 16GB を超える。初期値は 1 にし、
本当に必要なときだけ `Config.setConcurrency(2)` 以上に上げる。

出典：[Remotion docs — config/concurrency](https://www.remotion.dev/docs/config#setconcurrency)

---

## 2. VOICEVOX 運用

### 2.1 話者 ID とデフォルト

`synthesize_narration.py` のデフォルトは `speaker=16`（九州そら・ノーマル）。
シーンごとに変えたい場合は scene JSON の該当シーンに `"speaker": 3` の
ように書く。script も引数 `--speaker <id>` で一括上書き可能。

よく使う ID（VOICEVOX 0.14 以降で安定している範囲）：

| ID | 話者               | 用途メモ                 |
| -- | ------------------ | ------------------------ |
| 1  | 四国めたん ノーマル | 明るめ、女性寄り          |
| 3  | ずんだもん ノーマル | キャラ立ち、軽い解説向き  |
| 8  | 春日部つむぎ ノーマル | 落ち着き、ナレーション向き |
| 13 | 青山龍星 ノーマル   | 男性、ニュース調          |
| 16 | 九州そら ノーマル  | 低め女性、解説・本プラグイン既定 |

正規の ID 一覧は engine の `GET /speakers` から取得する。将来のバージョンで
変わる可能性があるので、固有値をコード深くに埋めない。

出典：[VOICEVOX engine API](https://voicevox.github.io/voicevox_engine/api/)

### 2.2 エンジンが落ちたらスクリプトは中断、擬似音声は生成しない

`synthesize_narration.py` は起動時に `/version` を叩いて到達性を確認する。
落ちていれば `return 2` で中断。無音 WAV でも合成音もどきでも返さない。
VOICEVOX が必須である以上、品質の違う音声を混ぜる方が害が大きいため。

### 2.3 `speedScale` / `prePhonemeLength` は手で調整している

既定で `speedScale=0.96`（気持ちゆっくり）、`prePhonemeLength=0.2`、
`postPhonemeLength=0.3` を `audio_query` レスポンスに上書きしてから
`/synthesis` に投げている。これはナレーション用。キャラ物にしたい場合は
`speedScale=1.0`、プリ/ポストを 0 に戻す。

---

## 3. FFmpeg / Windows 環境

### 3.1 FFmpeg は PATH に通っていないと Remotion が audio を失う

Remotion は音声をミックスするときに内蔵 ffmpeg を使うが、
`synthesize_narration.py` が生成した WAV のサンプリングレートが
コンポジションと揃わないケースで、システム ffmpeg に fallback する。
どちらにせよ **FFmpeg 6+ を PATH に通しておくのが最小構成**。

確認：

```
ffmpeg -version
```

出典：[Remotion docs — audio](https://www.remotion.dev/docs/audio)

### 3.2 Python は `py` ランチャ推奨（Windows）

`python` だと Microsoft Store のスタブが呼ばれて無言で終了する PC がある。
README・skill の手順はすべて `py scripts\ukiyoe\...` で揃えてある。
macOS / Linux なら `python3` に置換。

出典：[PEP 397 — Python launcher for Windows](https://peps.python.org/pep-0397/)

### 3.3 バックスラッシュとスラッシュ

- Python コード内のパスは `pathlib.Path` で組む（`os.sep` を意識しない）。
- shell コマンドとして提示するときは Windows を想定して `\` を使う
  （README 例：`py scripts\ukiyoe\_healthcheck.py`）。
- POSIX 環境でも `py` を `python3` に読み替えれば通る。

---

## 4. Claude API 呼び出し

### 4.1 既定モデルは `claude-sonnet-4-6`

`generate_script.py` と `translate_subtitles.py` は
`CLAUDE_MODEL` 環境変数で上書き可能。既定は `claude-sonnet-4-6`。
Opus を使いたいときは `.env` に

```
CLAUDE_MODEL=claude-opus-4-6
```

を追加。翻訳・脚本生成は Sonnet で十分な品質が出る。Opus を無闇に使うと
コストが 5〜10 倍になるので、脚本の質に不満が出るまでは Sonnet 固定。

### 4.2 Claude 応答から JSON を取り出す防御コード

`generate_script.py` は以下の順で堅く取る：

1. `content[0].text.strip()` で生テキスト取得
2. 先頭が ` ``` ` ならコードフェンスを剥がす
3. `json.loads()` で parse
4. 失敗したら `out/claude_raw_<name>.txt` にダンプして `return 3`

ダンプ先があるので debug はその生ファイルを見に行けばよい。LLM の出力を
そのまま信じて parse 成功前提で進めると、ほぼ例外で落ちる。

---

## 5. Python スクリプトの `REPO` 解決規約

すべての `scripts/ukiyoe/*.py` は自ファイル位置からリポジトリルートを
解決する：

```python
REPO = Path(__file__).resolve().parent.parent.parent
```

`scripts/ukiyoe/xxx.py` → `parent = ukiyoe/` → `parent.parent = scripts/` →
`parent.parent.parent = repo root`。

**だから scripts は `scripts/ukiyoe/` 配下でなければならない**。
`scripts/` 直下に置くと `REPO` が狂って `public/` や `src/` を
見失い、`[error] metadata not found` で止まる。

---

## 6. 開発サイクル

- コードを触る前に該当箇所の ADR／このファイルを読む。「何を調べたか」を
  まず確認する。
- 試行錯誤で何かを発見したら、**その場で**この TOOLBOX に追記する。
- 出典 URL は必須。「たぶんこう」は書かない。検証できないものは
  「演繹（根拠 A／B／C）」と明記する。

---

## 7. git 運用（Windows マウント + Linux サンドボックス）

FreelanceAutoPilot の道具箱 §3／§6 で検証済みのパターンに揃えている。
要旨：**commit/push は Desktop Commander（cmd）経由で実行し、
Claude のサンドボックス（Linux）からは基本 touch しない**。

### 7.1 実行環境の使い分け

| 操作                         | 使うツール                 | 理由 |
| --------------------------- | ------------------------- | --- |
| 読み取り (Read/Grep/Glob)    | Cowork file tools         | 高速・確実 |
| 参照系 bash (git log/diff)   | サンドボックス bash         | 高速・副作用なし |
| ファイル作成・編集            | Cowork file tools          | 直接書き込み |
| `git add` / `git commit`    | Desktop Commander (cmd)   | 認証と ACL がこちら側 |
| `git push` / `git tag`      | Desktop Commander (cmd)   | 同上 |
| `gh issue` / `gh pr`        | Desktop Commander → .py 経由 | 引数分割・日本語問題回避 |

### 7.2 push は HTTPS 直打ちで

remote が何に設定されていても、URL 直指定でやる方が事故が少ない：

```
cd /d C:\Users\GoldRush\Documents\MyProject\ClaudePlugins\programmatic-video-gen
git push https://github.com/RintaroMatsumoto/programmatic-video-gen.git main
```

認証は GitHub CLI (`gh auth`) のキーリング経由。`~/.ssh/id_ed25519` は
存在しない前提（FA §3 で 2026-04-07 に確認済み）。ssh-agent / ssh-add は不要。

### 7.3 日本語を含むコミットメッセージ

Windows cmd から直接 `-m "件名"` で日本語を渡すと cp932 で化ける、または
エスケープ地獄に入る。**ユーザーに .bat を渡して実行させるのは禁止**
（FA 道具箱 §9 — ユーザーはコマンド実行しない。Claude が DC で回す）。

確立された手順：

1. `_commit_msg.txt` を Cowork の Write ツールで UTF-8 書き出し
   （件名 1 行 → 空行 → 本文の多行）。
2. DC で cmd セッションを開き、リポジトリに `cd /d`。
3. `git add -A`
   `git reset HEAD _commit_msg.txt`（メッセージ自体は commit に含めない）
4. `git commit -F _commit_msg.txt`
5. `git push https://github.com/<user>/<repo>.git main`
6. `del _commit_msg.txt`（後始末）
7. タグを切るなら `git tag vX.Y.Z && git push https://.../<repo>.git vX.Y.Z`

この 7 ステップを DC 側の同一 cmd セッションで続けて叩くだけで通る。
CRLF 警告は Windows 側では無害（LF → CRLF 変換するだけ）。

Co-Authored-By を付けるなら `_commit_msg.txt` の末尾に空行 2 行を挟んで
`Co-Authored-By: Name <email@example.com>` を足す。

### 7.4 落とし穴集（FA §2 から関連分を抜粋）

- **CRLF ゴースト diff**：サンドボックス bash で `git status --short` が
  全ファイルを `M` で埋めたらこれ。`git diff` は見かけ上壊滅的でも、
  Windows 側から `git add -A` すれば「変更なし」で通るので慌てない。
- **`unable to unlink ... Operation not permitted`**：Windows マウントの
  ファイルに対し、サンドボックス git が unlink/rename を要する操作を
  するとこれ。commit/push をサンドボックスから試みない限り踏まない。
- **`git format` 文字列が cmd の `%` 処理で壊れる**：`--oneline` か
  `.bat` 経由で回避。直接 cmd に `--pretty=format:%H` は書かない。
- **Python one-liner が cmd.exe で壊れる**：必ず `.py` に書き出してから
  `py <file>.py` で実行。`sys.stdout.reconfigure(encoding='utf-8')` を
  冒頭に入れる。
- **PowerShell に `gh`/`git` が PATH にない場合がある**：shell は `cmd` を優先。

出典：[../FreelanceAutoPilot/docs/TOOLBOX.md](../../FreelanceAutoPilot/docs/TOOLBOX.md)
§2, §3, §6（複数セッションで再現・検証済み）。

---

## 8. 参考リンク集

- [Remotion docs](https://www.remotion.dev/docs/)
- [Remotion config reference](https://www.remotion.dev/docs/config)
- [Remotion staticFile](https://www.remotion.dev/docs/staticfile)
- [VOICEVOX engine API](https://voicevox.github.io/voicevox_engine/api/)
- [VOICEVOX product site](https://voicevox.hiroshiba.jp/)
- [FFmpeg official builds](https://ffmpeg.org/download.html)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
