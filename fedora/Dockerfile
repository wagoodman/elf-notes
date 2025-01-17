FROM fedora:42@sha256:19fcecbd14f2c1e887cbeb974295f5fc0e7b81e2df133e4f1b47a6f65cd11737 as base

# remove the RPM database
RUN rm -rf /usr/lib/sysimage/rpm/rpmdb.sqlite

FROM scratch
COPY --from=base / /
