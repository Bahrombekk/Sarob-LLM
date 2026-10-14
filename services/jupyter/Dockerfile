FROM local/vllm-cu130-nightly-pandas:latest
RUN pip install --no-cache-dir jupyter_server ipykernel openpyxl python-docx xlsxwriter matplotlib reportlab pypdf tabulate
RUN useradd -m -u 1000 sarob || true
WORKDIR /workspace
ENTRYPOINT []
USER 1000
CMD ["jupyter","server","--ip=0.0.0.0","--port=8888","--no-browser","--ServerApp.root_dir=/workspace","--ServerApp.allow_origin=*"]
