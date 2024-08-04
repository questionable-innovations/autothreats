FROM rust:1.77-bookworm AS builder
WORKDIR /app
COPY svg-service/dummy.rs .
COPY svg-service/Cargo.lock .
COPY svg-service/Cargo.toml .
RUN sed -i 's#src/main.rs#dummy.rs#' Cargo.toml
RUN cargo build --release
RUN sed -i 's#dummy.rs#src/main.rs#' Cargo.toml
COPY svg-service/src/ src/
RUN cargo build --release

FROM debian:bookworm
RUN apt update && apt install inkscape texlive-full -y
COPY assets/* /usr/share/fonts/
RUN fc-cache -f -v
WORKDIR /app
COPY --from=builder /app/target/release/svg-service svg-service

ENTRYPOINT /app/svg-service

