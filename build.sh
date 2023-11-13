#!/bin/bash
python -m sphinx -b html . _build/mo-book 
# cd _build/
# rsync -av mo-book/ kinsta-staging:~/public/mo-book
# rsync -av mo-book/ kinsta:~/public/mo-book