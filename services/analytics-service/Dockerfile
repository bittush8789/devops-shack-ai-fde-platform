FROM php:8.3-cli-alpine
RUN apk add --no-cache postgresql-dev libpq \
    && docker-php-ext-install pdo_pgsql
WORKDIR /app
COPY router.php .
EXPOSE 8087
CMD ["php", "-S", "0.0.0.0:8087", "router.php"]
