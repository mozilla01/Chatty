FROM redis
RUN redis -p 6379:6379 -d redis:5