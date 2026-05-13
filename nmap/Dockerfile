FROM alpine:3.19 AS builder

ARG NMAP_VERSION=7.99SVN

RUN apk add --no-cache \
    build-base \
    git \
    linux-headers \
    autoconf

WORKDIR /build

RUN git clone https://github.com/nmap/nmap.git \
    && cd nmap \
    && ./configure \
        --prefix=/opt/NMAP-static \
        # --with-pcap=null \
        CFLAGS='-O2' \
        LDFLAGS='-static -no-pie' \
    && make \
    # needed install for moving in /opt/NMPA-static
    && make install \
    \
    # Verify static linking
    && echo "=== Static binary check ===" \
    && for bin in /opt/NMAP-static/bin/*; do \
        [ -f "$bin" ] || continue; \
        printf "%s: " "$(basename "$bin")"; \
        file "$bin" | grep -q "statically linked" \
            && echo "OK (static)" \
            || { echo "FAILED (not static) - $bin"; exit 1; }; \
    done \
    && cp -r scripts /opt/NMAP-static/bin/.


FROM alpine:3.19

ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" ncuser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G ncuser ncuser 2>/dev/null || true

COPY --from=builder /opt/NMAP-static/bin/ /NMAP-bins/
RUN chmod -R 755 /NMAP-bins/

USER ncuser
CMD ["sh", "-c", "mkdir -p /output && cp -r /NMAP-bins/. /output/ && chmod -R 755 /output"]