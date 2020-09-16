import os

from flask import Flask, json, Response, logging

from openrecipeflask.repo import Repository
from openrecipeflask.orf_item import OrfItem


SERVE_DIR = 'serve'
ORF_DIR = os.path.join(SERVE_DIR, 'orf')
DB_PATH = os.path.join(SERVE_DIR, 'db.sqlite')

app = Flask('open-recipe-flask')
logger = logging.create_logger(app)


def pathdir(path):
    return (os.path.join(path, filename) for filename in os.listdir(path))


@app.route('/index')
def index():
    idx = []
    for path in pathdir(ORF_DIR):
        try:
            m = OrfItem.from_path(path).meta
        except KeyError:
            logger.error(f'Skipping {path}.', exc_info=True)
            continue
        idx.append({'id': m['identity'], 'name': m['name'], 'ver': m['version']})
    return json.dumps(idx)


@app.route('/meta/<path:path>')
def meta(path: str):
    path = os.path.sep.join(path.split('/'))
    return OrfItem.from_path(os.path.join(SERVE_DIR, path)).meta


@app.route('/item/<path:path>')
def item(path: str):
    with Repository(DB_PATH) as r:
        pass
    return Response(

    )


if __name__ == '__main__':
    app.run(debug=True)
