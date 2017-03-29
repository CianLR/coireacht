FROM python:3.6-alpine
RUN pip install Flask requests
COPY . /app
WORKDIR /app
ENTRYPOINT ["python"]
CMD ["app.py"]
EXPOSE 4321
