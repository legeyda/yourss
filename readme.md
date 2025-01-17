Generate rss/atom-feed from any media source (e.g. youtube playlist).

See it working at [https://yourss.legeyda.com/]

docker build -t yourss . --progress=plain && docker run --rm --name yourss -p 8000:8000 yourss