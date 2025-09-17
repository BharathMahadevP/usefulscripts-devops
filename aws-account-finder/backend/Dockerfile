# official Python runtime as a parent image
FROM python:3-alpine3.22

# Update system packages to address vulnerabilities
#RUN apk update && apk upgrade --no-cache

# Set the working directory in the container
WORKDIR /backend

# Create a non root user to run the application
RUN adduser -D -h /backend appuser && chown -R appuser:appuser /backend

# Copy the requirements file into the container at /backend
COPY --chown=appuser:appuser requirements.txt /backend

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /backend
COPY --chown=appuser:appuser . .

# Expose port 5001 for the API
EXPOSE 5001

# Switch to non-root user
USER appuser

# Command to run the application
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "5001"]