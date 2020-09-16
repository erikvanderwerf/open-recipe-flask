import logging
from pathlib import Path
from typing import Iterator, Callable

from openrecipeflask.item import Item
from openrecipeflask.orf_item import OrfItem
from openrecipeflask.repo import Repository

logger = logging.getLogger('orf.indexer')


async def reindex(repo_factory: Callable[[], Repository], parent_dir: Path) -> None:
    """Index the given parent into

    :param repo_factory: Factory to instantiate Repositories. Multiple Repository instances may
        be in use simultaneously.
    :param parent_dir: Directory to begin index on.
    """
    if not parent_dir.is_dir():
        raise ValueError('parent_dir must be a directory')
    for file in _walk(parent_dir):
        await index_file(repo_factory(), file)


def _walk(path_dir: Path) -> Iterator[Path]:
    for node in path_dir.iterdir():
        if node.is_dir():
            yield from _walk(node)
        else:
            yield node


async def index_file(repo: Repository, file_path: Path):
    item: Item = OrfItem.from_path(file_path)

    with repo as conn:
        logger.info(f'Indexing file: {item} for {conn}')
        index = conn.index
        if item.index not in index:
            logger.info(f'Adding {item} to index.')
            index.insert(item.index, link_to_file=file_path)
        print('\n'.join(conn.iterdump()))
        conn.commit()
