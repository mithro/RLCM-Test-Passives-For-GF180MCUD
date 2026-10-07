# Simulation environment for the RLCM test structures: openEMS with its Python
# interface, the gds2openEMS workflow, KLayout and ngspice.
#
#   docker build -t rlcm-sim docs/sim
FROM debian:trixie

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential git cmake ca-certificates \
        libhdf5-dev libtinyxml-dev libboost-all-dev libcgal-dev libvtk9-dev \
        python3-dev python3-venv python3-pip \
        klayout ngspice \
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

RUN pip install --no-cache-dir gdspy shapely numpy scipy matplotlib scikit-rf klayout

# Volker Mühlhaus's GDS to openEMS workflow, pinned to the commit that was used.
ARG GDS2OPENEMS_COMMIT=551deea7b3a89d904086d7a4d06d5133b2b4f186
# --no-deps leaves out PySide6, which only its stack editor needs.
RUN git clone https://github.com/VolkerMuehlhaus/gds2openEMS.git /opt/gds2openEMS \
    && git -C /opt/gds2openEMS checkout ${GDS2OPENEMS_COMMIT} \
    && pip install --no-cache-dir --no-deps /opt/gds2openEMS
