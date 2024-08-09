# Use Python 3.11 Buster as the base image
FROM python:3.11-buster

# Set environment variables
# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Create a non-root user and group
# -g 1001: Set group ID to 1001
# -u 1001: Set user ID to 1001
# -m: Create home directory
RUN groupadd -g 1001 appgroup && useradd -u 1001 -g appgroup -m appuser

# Set the working directory in the container
WORKDIR /home/app

# Copy the necessary files into the container
COPY app.py /home/app/app.py
COPY models.py /home/app/models.py
COPY requirements.txt /home/app/requirements.txt
COPY calibration_files /home/app/calibration_files

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Change ownership of the application files to the non-root user
RUN chown -R appuser:appgroup /home/app

# Switch to the non-root user for security
USER appuser

# Command to run the application
CMD ["python", "app.py"]