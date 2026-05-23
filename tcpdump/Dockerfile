FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d AS builder

ARG TCPDUMP_VERSION
ARG LIBPCAP_VERSION=1.10.4

RUN apk add --no-cache \
    build-base \
    wget \
    linux-headers \
    flex \
    bison

WORKDIR /build

RUN wget https://www.tcpdump.org/release/libpcap-${LIBPCAP_VERSION}.tar.gz && \
    tar xzf libpcap-${LIBPCAP_VERSION}.tar.gz && \
    cd libpcap-${LIBPCAP_VERSION} && \
    ./configure \
        --prefix=/opt/libpcap-static \
        --disable-shared \
        --enable-static \
        CFLAGS='-O2' \
        LDFLAGS='-static' && \
    make -j$(nproc) && \
    make install

RUN wget https://www.tcpdump.org/release/${TCPDUMP_VERSION}.tar.gz && \
    tar xzf ${TCPDUMP_VERSION}.tar.gz && \
    cd ${TCPDUMP_VERSION} && \
    ./configure \
        --prefix=/opt/tcpdump-static \
        --disable-shared \
        --enable-static \
        --with-pcap=yes \
        CPPFLAGS="-I/opt/libpcap-static/include" \
        LDFLAGS="-L/opt/libpcap-static/lib -static -no-pie" \
        CFLAGS='-O2' && \
    make -j$(nproc) && \
    make install

RUN for bin in /opt/tcpdump-static/bin/*; do \
        [ -f "$bin" ] || continue; \
        file "$bin" | grep -q "statically linked" || { echo "Not static: $bin"; exit 1; }; \
    done

FROM alpine:3.21@sha256:48b0309ca019d89d40f670aa1bc06e426dc0931948452e8491e3d65087abc07d

ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" tcpuser 2>/dev/null || true && \
    adduser -D -u "$HOST_UID" -G tcpuser tcpuser 2>/dev/null || true

COPY --from=builder /opt/tcpdump-static/bin/tcpdump /usr/local/bin/tcpdump

RUN chmod 755 /usr/local/bin/tcpdump

USER tcpuser

CMD ["sh", "-c", "mkdir -p /output && cp /usr/local/bin/tcpdump /output/ && chmod 755 /output/tcpdump"]