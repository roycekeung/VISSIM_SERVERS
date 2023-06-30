
FROM python:3.7-alpine
# FROM python:3.7

LABEL maintainer="royce"

# # Working directory is / by default. We explictly state it here for posterity
# WORKDIR /

# Upgrade pip
RUN pip install --upgrade --user pip

# - copy src files
COPY . /user/src/storage

# # Move the requirements file into the image
COPY requirements.txt ./user/src/storage  
RUN pip install --no-cache-dir -r ./user/src/storage/requirements.txt --user 

# Remove the requirements file - this is no longer needed
RUN rm /user/src/storage/requirements.txt

# Set it as the working directory
WORKDIR /user/src/storage 

### start run python
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5500"]
