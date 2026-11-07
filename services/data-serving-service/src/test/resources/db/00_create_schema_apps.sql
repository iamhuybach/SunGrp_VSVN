-- Chạy trước gld_srv_serve.pg.sql trong container test (docker-entrypoint-initdb.d, thứ tự theo tên file).
-- Schema apps do phía dữ liệu sở hữu; file DDL của repo không tạo schema nên test tạo ở đây.
CREATE SCHEMA IF NOT EXISTS apps;
