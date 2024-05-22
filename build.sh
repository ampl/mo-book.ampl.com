#!/bin/bash
set -ex
source venv/bin/activate
python -m sphinx -b html . _build/mo-book 
# rsync -av _build/mo-book/ kinsta-staging:~/public/mo-book
# rsync -av _build/mo-book/ kinsta:~/public/mo-book
