FROM node:20-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install "fastmcp<3"

WORKDIR /app
COPY --link server.py /app/server.py

ENV WORKSPACE_ROOT=/workspace
RUN mkdir -p /workspace

EXPOSE 7860
CMD ["python3", "/app/server.py"]
