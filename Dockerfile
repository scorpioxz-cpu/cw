# Use the official Python 3.11 image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8501
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "HKStockTelegramCSV2.py", "--server.headless", "true", "--server.port", "8501"]