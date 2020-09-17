import os
from pathlib import Path

from flask import Flask, json, Response, logging

from openrecipeflask.identifier import OrfIdentifier
from openrecipeflask.item import json_index_serializer, json_meta_serializer
from openrecipeflask.repo import Repository

SERVE_DIR = 'serve'
ORF_DIR = Path(os.path.join(SERVE_DIR, 'orf'))
DB_PATH = Path(os.path.join(SERVE_DIR, 'db.sqlite'))

app = Flask('open-recipe-flask')
logger = logging.create_logger(app)


@app.route('/index')
def index():
    with Repository(DB_PATH) as conn:
        item_indices = conn.index.list()
    return json.dumps(list(json_index_serializer(idx) for idx in item_indices))


@app.route('/meta/<path:path>')
def meta(path: str):
    with Repository(DB_PATH) as conn:
        item = conn.item.by_identifier(OrfIdentifier.from_url(path))
    return json.dumps(json_meta_serializer(item.meta))


@app.route('/item/<path:path>')
def item(path: str):
    with Repository(DB_PATH) as r:
        pass
    return Response(

    )


if __name__ == '__main__':
    app.run(debug=True)
