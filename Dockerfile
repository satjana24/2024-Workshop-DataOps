# Use Python 3.8 as the base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /workspace

# Install required packages and clean up in a single layer
RUN apt-get update -y && \
   apt-get install -y wget unzip gcc python3-dev nano && \
   # Install Terraform
   wget https://releases.hashicorp.com/terraform/1.0.5/terraform_1.0.5_linux_amd64.zip && \
   unzip terraform_1.0.5_linux_amd64.zip -d /usr/local/bin/ && \
   rm terraform_1.0.5_linux_amd64.zip && \
   # Install Google Cloud SDK
   wget https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz && \
   tar zxvf google-cloud-sdk.tar.gz && \
   ./google-cloud-sdk/install.sh -q && \
   rm google-cloud-sdk.tar.gz && \
   # Clean up
   apt-get autoremove -y && \
   rm -rf /var/lib/apt/lists/*

# Add Google Cloud SDK to the PATH
ENV PATH $PATH:/workspace/google-cloud-sdk/bin

# Copy requirements files
COPY requirements.txt /workspace/
COPY setup.py /workspace/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
   pip install --no-cache-dir -e .

# Copy the rest of the application
COPY . /workspace/

# Set environment variable for Google Cloud auth
ARG GOOGLE_APPLICATION_CREDENTIALS
ENV GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS:-"/workspace/stately-gist-435602-u9-e7d9d76c1b6d.json"}

# Command to run when the container starts
CMD ["sh", "-c", "terraform init && terraform apply -auto-approve && python main_pipeline.py"]