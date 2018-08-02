FROM python:3.6.5-jessie
WORKDIR /srv
COPY setup.py .
COPY requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt
COPY . .
EXPOSE 8080
ENTRYPOINT ["/srv/scripts/run_worker.sh"]
CMD ["src"]
