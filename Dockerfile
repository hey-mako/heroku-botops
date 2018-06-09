FROM python:3.6.5-jessie
WORKDIR /srv
COPY requirements.txt .
COPY setup.py .
RUN pip install --no-cache-dir --requirement requirements.txt
COPY . .
EXPOSE 4567
CMD ["flask", "run"]
