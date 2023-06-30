
FROM python:3.7-alpine

LABEL maintainer="royce"

WORKDIR /

# Upgrade pip
RUN pip install --upgrade pip --user 

# - copy src files
COPY receiver.py /user/src/messageque/receiver.py

# # Move the requirements file into the image
COPY requirements.txt ./user/src/messageque  
RUN pip install --no-cache-dir -r ./user/src/messageque/requirements.txt --user 

# Remove the requirements file - this is no longer needed
RUN rm /user/src/messageque/requirements.txt

# Set it as the working directory
WORKDIR /user/src/messageque 


# Define default command
CMD ["python", "receiver.py"]
