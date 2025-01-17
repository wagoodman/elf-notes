FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    binutils \
    elfutils

COPY src src

RUN gcc -static src/demo.c -o demo

# add the JSON payload as a package note to the binary. The payload should approimate what is descrived here https://systemd.io/ELF_PACKAGE_METADATA/ (there are some differences);
# we use 'noload' to prevent the note from being loaded into memory at runtime and 'readonly' to prevent the note from being modified if it is inadvertently loaded.
RUN echo '{"name": "alex", "version": "v1.2.3", "type": "deb", "license": "MIT", "purl": "pkg:generic/alex@1.2.3"}' \
    | objcopy --add-section .note.package=/dev/stdin --set-section-flags .note.package=noload,readonly ./demo

FROM scratch

COPY --from=builder /demo /demo

CMD ["/demo"]
