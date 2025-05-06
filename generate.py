import google.generativeai as genai
import base64
import argparse
import os
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Gemini APIキーを環境変数から取得
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_prompt():
    """プロンプトをテキストファイルから読み込む"""
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: Prompt file 'prompt.txt' not found.")
        return None

def process_single_pdf(pdf_path):
    """指定されたPDFを生成系AIで処理し、TSV形式で出力する。"""
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
        doc_data = base64.standard_b64encode(pdf_content).decode("utf-8")

        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = load_prompt()
        if prompt is None:
            return None, 0

        response = model.generate_content([
            {"mime_type": "application/pdf", "data": doc_data},
            prompt
        ])

        tsv_output = response.text

        # 質問の件数をカウント
        question_count = len(tsv_output.strip().split("\n")) - 1  # ヘッダー行を除く

        return tsv_output, question_count

    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found.")
    except Exception as e:
        print(f"Unexpected error while processing '{pdf_path}': {str(e)}")
    return None, 0

def summarize_pdfs(pdf_paths):
    total_questions = 0
    combined_tsv = ""
    header_written = False

    for pdf_path in pdf_paths:
        print(f"Processing {pdf_path}...")
        tsv_output, question_count = process_single_pdf(pdf_path)

        if tsv_output:
            lines = tsv_output.strip().split("\n")
            cleaned_lines = [line for line in lines if line.strip()]  # 空白行を除外
            combined_tsv += "\n".join(cleaned_lines[1:]) + "\n"  # データ部分を追加
            print(f"Processed {pdf_path}: {question_count} questions generated.")
            total_questions += question_count

    # 最終的なTSVを保存
    final_tsv_path = "final_output.tsv"
    with open(final_tsv_path, "w", encoding="utf-8") as final_tsv:
        final_tsv.write(combined_tsv.strip())

    print(f"Final TSV saved as '{final_tsv_path}'. Total questions generated: {total_questions}")

    # サーバーにPOSTリクエストで送信
    post_to_server(final_tsv_path)

def post_to_server(file_path):
    """生成したTSVファイルをサーバーにPOSTリクエストで送信する。"""
    url = os.getenv("SERVER_URL")
    payload = {
        "pw": os.getenv("SERVER_PASSWORD"),
        "filename": os.path.basename(file_path)
    }
    files = {
        "file": ("tsv", open(file_path, "rb"), "text/tab-separated-values")
    }

    if not url:
        print("Warning: SERVER_URL is not set in .env file. Skipping server upload.")
        return

    try:
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print("File successfully uploaded to the server.")
        else:
            print(f"Failed to upload the file. Server responded with status code {response.status_code}.")
    except Exception as e:
        print(f"An error occurred while uploading the file: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize PDFs using Google Generative AI")
    parser.add_argument("file_paths", nargs="*", type=str, help="Paths to the PDF files")

    args = parser.parse_args()

    # 引数が指定されていない場合はカレントディレクトリのPDFファイルを処理
    if not args.file_paths:
        pdf_paths = [f for f in os.listdir() if f.endswith(".pdf")]
        if not pdf_paths:
            print("Error: No PDF files found in the current directory.")
        else:
            summarize_pdfs(pdf_paths)
    else:
        summarize_pdfs(args.file_paths)

