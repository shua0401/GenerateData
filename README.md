# PDF Question Generator

PDFファイルから学生向けの質問と回答を自動生成するツールです。Google Gemini APIを使用して、授業資料（PDF）の内容を分析し、想定される質問と回答をTSV形式で出力します。

## 機能

- PDFファイルの読み込みと解析
- Gemini APIを使用した質問生成
- TSV形式での出力
- 複数PDFファイルの一括処理
- サーバーへの自動アップロード

## 必要条件

- Python 3.7以上
- Google Gemini APIキー

## インストール

1. リポジトリをクローン:
2. 必要なパッケージをインストール:
3. 環境変数の設定:

## 使用方法

1. 単一のPDFファイルを処理:
```bash
python generate.py path/to/your/file.pdf
```

2. 複数のPDFファイルを処理:
```bash
python generate.py file1.pdf file2.pdf file3.pdf
```

3. カレントディレクトリの全PDFファイルを処理:
```bash
python generate.py
```

## 出力

- 生成された質問と回答は`final_output.tsv`ファイルに保存されます
- TSVファイルは自動的にサーバーにアップロードされます

## ライセンス

MIT License
