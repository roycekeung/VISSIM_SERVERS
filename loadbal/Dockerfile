
FROM python:3.7-alpine

LABEL maintainer="royce"

# Upgrade pip
RUN pip install --upgrade pip --user 

# - copy src files
COPY . /user/src/loadbal

# # Move the requirements file into the image
COPY requirements.txt ./user/src/loadbal  
RUN pip install --no-cache-dir -r ./user/src/loadbal/requirements.txt --user 

# Remove the requirements file - this is no longer needed
RUN rm /user/src/loadbal/requirements.txt

# Set it as the working directory
WORKDIR /user/src/loadbal 


ADD init.sh /init.sh
RUN chmod +x /init.sh

### start run python
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5400"]





