# Copyright (c) 2023-2026 Datalayer, Inc.
#
# BSD 3-Clause License

FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml LICENSE README.md ./
COPY earthdata_mcp_server/ earthdata_mcp_server/

RUN pip install --no-cache-dir .

EXPOSE 4040

# stdio by default; `start --transport streamable-http` serves /mcp on 4040.
ENTRYPOINT ["earthdata-mcp-server"]
CMD ["start"]
