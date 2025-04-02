# Copyright (c) 2023-2024 Datalayer, Inc.
#
# BSD 3-Clause License

FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY LICENSE LICENSE
COPY README.md README.md
COPY earthdata_mcp_server/* earthdata_mcp_server/

RUN pip install -e .

CMD ["python", "-m", "earthdata_mcp_server.server"]
