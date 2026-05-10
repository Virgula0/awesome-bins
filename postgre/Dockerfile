FROM alpine:3.19 AS builder

ARG PG_VERSION=16.1

RUN apk add --no-cache build-base openssl-dev openssl-libs-static wget linux-headers

WORKDIR /build

RUN wget https://ftp.postgresql.org/pub/source/v${PG_VERSION}/postgresql-${PG_VERSION}.tar.gz \
    && tar xzf postgresql-${PG_VERSION}.tar.gz \
    && cd postgresql-${PG_VERSION} \
    && ./configure \
        --prefix=/opt/pg-static \
        --without-readline \
        --without-zlib \
        --without-icu \
        --disable-shared \
        --with-openssl \
        CFLAGS='-std=c17' \
        LDFLAGS='-static -no-pie' \
    && sed -i 's/^all: /all-orig: /' src/interfaces/libpq/Makefile \
    && echo 'all: libpq.a' >> src/interfaces/libpq/Makefile \
    && make -C src/port \
    && make -C src/common \
    && make -C src/fe_utils \
    && make -C src/interfaces/libpq libpq.a \
    && make -C src/bin \
    && make -C src/bin install \
    && echo "=== Static binary check ===" \
    && for bin in /opt/pg-static/bin/*; do \
         printf "%s: " "$(basename $bin)"; \
         file "$bin" | grep -q "statically linked" \
           && echo "OK (static)" \
           || { echo "FAILED (not static) - $(file $bin)"; exit 1; }; \
       done

FROM alpine:3.19

ARG HOST_UID=1000
ARG HOST_GID=1000

RUN addgroup -g "$HOST_GID" pguser 2>/dev/null || true \
    && adduser -D -u "$HOST_UID" -G pguser pguser 2>/dev/null || true

COPY --from=builder /opt/pg-static/bin/ /pg-bins/
RUN chmod -R 755 /pg-bins/

USER pguser

CMD ["sh", "-c", "mkdir -p /output && cp -r /pg-bins/. /output/ && chmod -R 755 /output"]