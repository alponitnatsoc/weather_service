# Running the pytthon container
FROM python:3.7-alpine

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# add app
COPY . /usr/src/app

# run server
CMD ["python","app.py"]