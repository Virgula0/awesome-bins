FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d AS builder

ARG NETCAT_VERSION=0.7.1

RUN apk add --no-cache \
    build-base \
    wget \
    automake

WORKDIR /build

RUN wget https://downloads.sourceforge.net/project/netcat/netcat/${NETCAT_VERSION}/netcat-${NETCAT_VERSION}.tar.gz \
    && tar xzf netcat-${NETCAT_VERSION}.tar.gz \
    && cd netcat-${NETCAT_VERSION} \
    # config.guess bundled with netcat 0.7.1 is from 2003; replace with
    # current versions from Alpine's automake package for broad arch support
    && cp "$(automake --print-libdir)/config.guess" . \
    && cp "$(automake --print-libdir)/config.sub" . \
    && ./configure \
        --prefix=/opt/netcat-static \
        CFLAGS='-O2' \
        LDFLAGS='-static -no-pie' \
    && make \
    && make install \
    \
    && echo "=== Static binary check ===" \
    && file /opt/netcat-static/bin/netcat | grep -q "statically linked" \
    && echo "OK (static)" \
    || { echo "FAILED (not static) - $(file /opt/netcat-static/bin/netcat)"; exit 1; }

FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d
ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" ncuser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G ncuser ncuser 2>/dev/null || true

COPY --from=builder /opt/netcat-static/bin/ /netcat-bins/
RUN chmod -R 755 /netcat-bins/

USER ncuser
CMD ["sh", "-c", "mkdir -p /output && cp -r /netcat-bins/. /output/ && chmod -R 755 /output"]