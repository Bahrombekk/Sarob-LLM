FROM sarob-jupyter
USER root
RUN pip install --no-cache-dir "python-telegram-bot[job-queue]==21.10" ddgs beautifulsoup4 psycopg2-binary
COPY sarob_bot.py /app/sarob_bot.py
USER 1000
WORKDIR /app
CMD ["python3", "-u", "/app/sarob_bot.py"]
