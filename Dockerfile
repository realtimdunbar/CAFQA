# Use the official Miniconda base image
FROM continuumio/miniconda3

# Set environment variables
ENV PATH /opt/conda/bin:$PATH

# Create a new Conda environment
COPY environment.yml environment.yml
RUN conda env create -f environment.yml
RUN conda init

# Activate the Conda environment
SHELL ["conda", "activate", "mycondaenv"]

# Copy your project files into the container
COPY . /app
WORKDIR /app

# Install additional dependencies if needed
# RUN pip install -r requirements.txt

# Command to run your Python project (adjust as needed)
CMD ["python",  "/example/H2/h2.py"]