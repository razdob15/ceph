#!/bin/bash

test "$(command -v dnf)" && PKG_MGR=dnf || PKG_MGR=apt

CONTAINER_BINARY=podman

pushd ../../../
"${CONTAINER_BINARY}" build -t 192.168.100.10:5000/ceph:ceph-testing -f src/test/cephadm_tests/Dockerfile .
popd

echo "$PKG_MGR"
