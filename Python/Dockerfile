FROM python:3.9-slim

# Set environment variable for MS SQL Server ODBC driver
ENV ACCEPT_EULA=Y

# Update apt-get and install dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl gcc g++ gnupg unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql18 mssql-tools

# Add MS SQL tools to the PATH
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile \
    && echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Copy application files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Clean up unnecessary files to reduce image size
RUN apt-get -y clean

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]