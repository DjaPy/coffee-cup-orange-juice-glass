import uuid
from os import chdir
from os.path import abspath, dirname, exists, join
from typing import Optional

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy_utils import create_database, drop_database


def find_alembic_cfg(name_alembic_cfg: str = 'alembic.ini', current_path: Optional[str] = None) -> Config:
    current_path = current_path or dirname(abspath(__file__))
    if exists(join(current_path, name_alembic_cfg)):
        return Config(join(current_path, name_alembic_cfg))
    if current_path == '/':
        raise FileNotFoundError(f'{name_alembic_cfg} not found')
    return find_alembic_cfg(name_alembic_cfg, current_path=dirname(current_path))


@pytest.mark.asyncio
@pytest.fixture(scope='session')
def create_db_for_migrate(config, get_db_url):
    """
    На основе опыта Yandex
    http://www.moscowpython.ru/meetup/69/talk-from-yandex/
    """
    """
    На основе опыта Yandex
    http://www.moscowpython.ru/meetup/69/talk-from-yandex/
    """
    test_db_name = f'{uuid.uuid4().hex}_pytest'
    db_url = get_db_url('postgresql', test_db_name)

    create_database(db_url)

    try:
        yield str(db_url)
    finally:
        # engine.sync_engine.dispose()
        drop_database(db_url)


@pytest.mark.asyncio
def test_migration(create_db_for_migrate):
    """
    На основе опыта Yandex
    http://www.moscowpython.ru/meetup/69/talk-from-yandex/
    """
    current_path = dirname(abspath(__file__))
    try:
        alembic_cfg = find_alembic_cfg()
        chdir(dirname(alembic_cfg.config_file_name))
        alembic_cfg.set_main_option('sqlalchemy.url', create_db_for_migrate)
        revisions_dir = ScriptDirectory.from_config(alembic_cfg)
        # Проверяем правильность написания миграций и их отката
        for revision in reversed([revision for revision in revisions_dir.walk_revisions('base', 'heads')]):
            command.upgrade(alembic_cfg, revision.revision)
            command.downgrade(alembic_cfg, revision.down_revision or '-1')
            command.upgrade(alembic_cfg, revision.revision)

        # Проверяем правильность порядка миграций (например на раздвоение миграций)
        command.downgrade(alembic_cfg, 'base')
        command.upgrade(alembic_cfg, 'head')
    finally:
        chdir(current_path)
