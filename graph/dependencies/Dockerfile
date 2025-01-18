FROM ubuntu:22.04 as builder

RUN apt-get update && apt-get install -y \
    build-essential \
    libgd-dev \
    zlib1g-dev \
    libbz2-dev \
    python3

WORKDIR /build
COPY src src
COPY Makefile.build ./Makefile
COPY *.py .

RUN make static show find-libs write-notes

FROM scratch

COPY --from=builder /build/image-creator /image-creator
COPY --from=builder /build/evidence.txt /evidence.txt
COPY --from=builder /build/symbols.txt /symbols.txt
COPY --from=builder /build/pkg.txt /pkg.txt
COPY --from=builder /build/libs.json /libs.json
COPY --from=builder /build/notes.json /notes.json

ENTRYPOINT ["/image-creator"]
