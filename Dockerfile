FROM nixos/nix:latest AS builder

COPY . /tmp/build
WORKDIR /tmp/build

RUN nix \
    --extra-experimental-features "nix-command flakes" \
    --option filter-syscalls false \
    build

RUN mkdir /tmp/nix-store-closure
RUN cp -R $(nix-store -qR result/) /tmp/nix-store-closure

FROM alpine:3.22.1
RUN apk add --no-cache curl
EXPOSE 7999

WORKDIR /

# Copy Nix Closure
COPY --from=builder /tmp/nix-store-closure /nix/store
COPY --from=builder /tmp/build/result /

HEALTHCHECK --interval=60s --timeout=5s --start-period=20s --retries=5 CMD curl -f http://0.0.0.0:7999/health || exit 1
ENTRYPOINT ["/main"]
