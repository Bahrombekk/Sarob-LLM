FROM sarob-jupyter
USER root
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw
RUN pip install --no-cache-dir playwright fastapi uvicorn && playwright install --with-deps chromium && chmod -R a+rx /opt/pw
COPY browser_server.py /app/browser_server.py
USER 1000
WORKDIR /app
CMD ["uvicorn","browser_server:app","--host","0.0.0.0","--port","8097"]
