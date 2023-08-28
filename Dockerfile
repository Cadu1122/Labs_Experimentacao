FROM python:3.11

COPY projeto_1 /app/projeto_1
COPY resources /app/resources

CMD [ "pip", "install", "-r", "requirements.txt" ]

ENV GITHUB_AUTH_TOKEN=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
ENV DEFAULT_QUANTITY_OF_REPOSITORIES_TO_FETCH=50
ENV TOTAL_QUANTITY_OF_REPOSITORIES=1_000
ENV PERSIT_GRAPQHL_QUERIES=1
