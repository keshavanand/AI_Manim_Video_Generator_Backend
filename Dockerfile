FROM python:3.12
WORKDIR /app

RUN apt-get update -o Acquire::ForceIPv4=true && \
    apt-get install -y -o Acquire::ForceIPv4=true \
        pkg-config \
        libcairo2-dev \
        libpango1.0-dev \
        ffmpeg \
        libgl1 && \
    rm -rf /var/lib/apt/lists/*

# RUN apt update && apt install -y \
#     texlive-full \
#     && apt clean

RUN apt update && apt install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-latex-extra \
    dvipng \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
