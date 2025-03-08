# Use Python 3.9 as base image
FROM python:3.9

# Set working directory in container
WORKDIR /app

# Copy bot files to the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]