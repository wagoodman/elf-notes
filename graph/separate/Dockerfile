FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y build-essential binutils jq && apt-get clean

RUN mkdir /patched_bins /patched_libs

# patch binaries with accurate metadata
RUN echo '{"name": "make", "type": "deb", "version": "4.3-4", "license": "GPL-3.0-or-later", "purl": "pkg:deb/ubuntu/gmake@4.3-4"}' \
    | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/bin/make /patched_bins/make

RUN echo '{"name": "strip", "type": "deb", "version": "2.38-4ubuntu2", "license": "GPL-3.0-or-later", "purl": "pkg:deb/ubuntu/binutils@2.38-4ubuntu2"}' \
    | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/bin/strip /patched_bins/strip

RUN echo '{"name": "cp", "type": "deb", "version": "9.1-0ubuntu1", "license": "GPL-3.0-or-later", "purl": "pkg:deb/ubuntu/coreutils@9.1-0ubuntu1"}' \
    | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/bin/cp /patched_bins/cp

RUN echo '{"name": "mv", "type": "deb", "version": "9.1-0ubuntu1", "license": "GPL-3.0-or-later", "purl": "pkg:deb/ubuntu/coreutils@9.1-0ubuntu1"}' \
    | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/bin/mv /patched_bins/mv

# patch libraries with accurate metadata
RUN cp /usr/lib/ld-linux-aarch64.so.1 \
    /usr/lib/aarch64-linux-gnu/libc.so.6 \
    /usr/lib/aarch64-linux-gnu/libbfd-2.38-system.so \
    /usr/lib/aarch64-linux-gnu/libselinux.so.1 \
    /usr/lib/aarch64-linux-gnu/libacl.so.1 \
    /usr/lib/aarch64-linux-gnu/libattr.so.1 \
    /patched_libs/

# /usr/lib/aarch64-linux-gnu/libz.so.1 \
# /usr/lib/aarch64-linux-gnu/libpcre2-8.so.0 \

# RUN echo '{"name": "ld-linux-aarch64", "type": "deb", "version": "2.35-0ubuntu3.1", "license": "LGPL-2.1-or-later", "purl": "pkg:deb/ubuntu/libc6@2.35-0ubuntu3.1"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/ld-linux-aarch64.so.1 /patched_libs/ld-linux-aarch64.so.1

# RUN echo '{"name": "libc6", "type": "deb", "version": "2.35-0ubuntu3.1", "license": "LGPL-2.1-or-later", "purl": "pkg:deb/ubuntu/libc6@2.35-0ubuntu3.1"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libc.so.6 /patched_libs/libc.so.6

# RUN echo '{"name": "libbfd", "type": "deb", "version": "2.38-4ubuntu2", "license": "GPL-3.0-or-later", "purl": "pkg:deb/ubuntu/binutils@2.38-4ubuntu2"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libbfd-2.38-system.so /patched_libs/libbfd-2.38-system.so

# RUN echo '{"name": "libz", "type": "deb", "version": "1.2.11.dfsg-2ubuntu2", "license": "Zlib", "purl": "pkg:deb/ubuntu/zlib1g@1.2.11.dfsg-2ubuntu2"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libz.so.1 /patched_libs/libz.so.1

# RUN echo '{"name": "libselinux", "type": "deb", "version": "3.3-1build2", "license": "GPL-2.0-or-later", "purl": "pkg:deb/ubuntu/libselinux1@3.3-1build2"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libselinux.so.1 /patched_libs/libselinux.so.1

# RUN echo '{"name": "libacl", "type": "deb", "version": "2.3.1-1", "license": "LGPL-2.1-or-later", "purl": "pkg:deb/ubuntu/libacl1@2.3.1-1"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libacl.so.1 /patched_libs/libacl.so.1

# RUN echo '{"name": "libattr", "type": "deb", "version": "1.6.0-1build1", "license": "LGPL-2.1-or-later", "purl": "pkg:deb/ubuntu/libattr1@1.6.0-1build1"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libattr.so.1 /patched_libs/libattr.so.1

# RUN echo '{"name": "libpcre2", "type": "deb", "version": "10.39-3build1", "license": "BSD-3-Clause", "purl": "pkg:deb/ubuntu/libpcre2-8-0@10.39-3build1"}' \
#     | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly /usr/lib/aarch64-linux-gnu/libpcre2-8.so.0 /patched_libs/libpcre2-8.so.0

# Stage 2: Create minimal scratch image with patched binaries and libraries
FROM scratch

COPY --from=builder /patched_bins /bin/
COPY --from=builder /patched_libs /lib/
