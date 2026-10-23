# OpenFOAM v2412 (openfoam.com) + the FoamBench evaluation scripts.
# Build from the FoamBench directory:
#     docker build -t foam-bench .
# Run:
#     docker run -it --rm foam-bench
# The OpenFOAM environment is sourced for every shell in the container.
FROM opencfd/openfoam-default:2412

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        python3 \
        python3-pip \
        python3-venv \
        libgl1 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY . /home/foam/FoamBench/
WORKDIR /home/foam/FoamBench/

RUN python3 -m venv /opt/foambench-venv \
    && /opt/foambench-venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/opt/foambench-venv/bin:${PATH}"
RUN echo 'source /usr/lib/openfoam/openfoam2412/etc/bashrc' >> /root/.bashrc

CMD ["/bin/bash", "-l"]
