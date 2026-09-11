FROM ruby:3.3-alpine
RUN apk add --no-cache build-base libpq-dev
WORKDIR /app
COPY Gemfile Gemfile.lock ./
RUN bundle install
COPY . .
EXPOSE 8086
CMD ["bundle", "exec", "ruby", "app.rb"]
