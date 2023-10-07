# ベースイメージを指定
FROM python:3.11.3

# ワーキングディレクトリを設定
WORKDIR /app

# 必要なファイルをコピー
COPY . .

# 依存関係をインストール
RUN pip install -r requirements.txt
RUN pip install protobuf

# 環境変数を設定 (必要に応じて)
ENV USER_AGENT="Your User Agent String"

# コンテナ起動時に実行するコマンドを指定
CMD ["python", "src/app.py"]
