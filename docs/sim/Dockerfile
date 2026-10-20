# Simulation environment for the RLCM test structures: openEMS with its Python
# interface, the gds2openEMS workflow and ngspice.
#
#   docker build -t rlcm-sim docs/sim
#
# The base image is pinned by digest and the Python packages by version. The
# Debian packages come from trixie at build time; ngspice is pinned because
# docs/sim/README.md quotes its version.
FROM debian:trixie@sha256:d07d1b51c39f51188e60be9b64e6bf769fa94e187f092bc32b91305cfa34ba5a

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential git cmake ca-certificates \
        libhdf5-dev libtinyxml-dev libboost-all-dev libcgal-dev libvtk9-dev \
        python3-dev python3-venv python3-pip \
        ngspice=44.2+ds-1 \
    && rm -rf /var/lib/apt/lists/*

ARG OPENEMS_TAG=v0.37.0-rc3
RUN git clone --recursive --depth 1 --branch ${OPENEMS_TAG} \
        https://github.com/thliebig/openEMS-Project.git /src/openEMS-Project \
    && cd /src/openEMS-Project \
    && ./update_openEMS.sh /opt/openEMS --disable-GUI --python --skip-dep-check \
        --python-venv-mode venv --python-venv-dir /opt/venv \
    ; status=$?; cat /src/openEMS-Project/build_*.log | tail -n 60; exit $status

ENV PATH=/opt/venv/bin:/opt/openEMS/bin:$PATH \
    LD_LIBRARY_PATH=/opt/openEMS/lib

# What gds2openEMS imports, at the versions the results in results/ were made with.
RUN pip install --no-cache-dir gdspy==1.6.13 shapely==2.2.0 numpy==2.5.3 h5py==3.16.0

# Volker Mühlhaus's GDS to openEMS workflow, pinned to the commit that was used.
ARG GDS2OPENEMS_COMMIT=551deea7b3a89d904086d7a4d06d5133b2b4f186
# --no-deps leaves out PySide6, which only its stack editor needs.
RUN git clone https://github.com/VolkerMuehlhaus/gds2openEMS.git /opt/gds2openEMS \
    && git -C /opt/gds2openEMS checkout ${GDS2OPENEMS_COMMIT} \
    && pip install --no-cache-dir --no-deps /opt/gds2openEMS
