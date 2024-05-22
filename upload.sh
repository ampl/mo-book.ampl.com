#!/bin/bash
cd "`dirname "$0"`"
set -ex
source venv/bin/activate
python -m sphinx -b html . _build/mo-book 
rsync -av --delete _build/mo-book/ kinsta-staging:/www/amplnewsitestaging_483/public/mo-book
rsync -av --delete _build/mo-book/ kinsta:/www/amplnewsitestaging_483/public/mo-book
