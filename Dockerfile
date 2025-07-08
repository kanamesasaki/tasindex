# ベースイメージとしてNode.jsのLTSバージョンを使用 (Astroのため)
FROM node:lts-bullseye

# --- 必要なパッケージのインストール ---
# aptパッケージリストを更新し、Python3, pip, SQLite3クライアント、git等をインストール
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    python3 \
    python3-pip \
    sqlite3 \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# --- Microsoft Core Fonts (Arial含む) のインストール ---
RUN echo "deb http://deb.debian.org/debian/ bullseye contrib" >> /etc/apt/sources.list

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    ttf-mscorefonts-installer \
    fontconfig \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN fc-cache -f -v

# --- Pythonパッケージ ---
# (オプション) もしデータ投入スクリプトで使うライブラリがあればここで追加
# COPY requirements.txt /tmp/py-requirements.txt
# RUN pip3 install --no-cache-dir -r /tmp/py-requirements.txt
RUN pip3 install bibtexparser matplotlib pandas seaborn

# --- Node.js グローバルパッケージ ---
# (オプション) 必要であればnpmでグローバルインストールするものを指定
# RUN npm install -g pnpm

# --- 作業ディレクトリ設定 ---
WORKDIR /workspace

# (Dockerfileはここまで)