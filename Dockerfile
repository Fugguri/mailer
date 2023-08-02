FROM python

COPY . /bot

WORKDIR /bot

EXPOSE 8001

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]