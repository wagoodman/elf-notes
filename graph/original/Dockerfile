FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y build-essential binutils jq && apt-get clean

RUN mkdir /patched_bins /patched_libs

RUN cp /usr/lib/ld-linux-aarch64.so.1 \
    /usr/lib/aarch64-linux-gnu/libc.so.6 \
    /usr/lib/aarch64-linux-gnu/libbfd-2.38-system.so \
    /usr/lib/aarch64-linux-gnu/libselinux.so.1 \
    /usr/lib/aarch64-linux-gnu/libacl.so.1 \
    /usr/lib/aarch64-linux-gnu/libattr.so.1 \
    /usr/bin/strip \
    /usr/bin/make \
    /usr/bin/cp \
    /usr/bin/mv \
    /patched_libs/

RUN cp /usr/bin/strip \
    /usr/bin/make \
    /usr/bin/cp \
    /usr/bin/mv \
    /patched_bins/

FROM scratch

COPY --from=builder /patched_bins /bin/
COPY --from=builder /patched_libs /lib/
