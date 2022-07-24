# Based on https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-13-docker-deploy/
FROM python:3.8

# create the app user
RUN addgroup --system app && adduser --system --group app

WORKDIR /app/

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0

COPY ./app /app
RUN pip install -r requirements.txt
RUN chmod +x run.sh

ENV PYTHONPATH=/app

# chown all the files to the app user
RUN chown -R app:app $HOME

# change to the app user
# Switch to a non-root user, which is recommended by Heroku.
USER app

# Run the run script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Uvicorn
# CMD ["./run.sh"]
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8001", "app:app", "--reload"]