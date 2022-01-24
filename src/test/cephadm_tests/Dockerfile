FROM quay.io/ceph/daemon-base:latest-master-devel

COPY ./src/ceph-volume/ceph_volume /usr/lib/python3.6/site-packages/ceph_volume
COPY ./src/cephadm/cephadm /usr/sbin/cephadm
COPY ./src/pybind/mgr/ /usr/share/ceph/mgr
COPY ./src/python-common/ceph /usr/lib/python3.6/site-packages/ceph
COPY ./monitoring/grafana/dashboards /etc/grafana/dashboards/ceph-dashboard
COPY ./monitoring/prometheus/alerts /etc/prometheus/ceph

