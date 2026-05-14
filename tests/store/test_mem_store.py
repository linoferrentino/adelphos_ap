######################################################
#
# Adelphos AP: the fractal trust network
#
# Activity Pub implementation
#
# © 2025-26 Lino Ferrentino
# lino.ferrentino@gmail.com
#
# This is free software. Licensed with GPL version 3
#
######################################################
#

import pytest
from app.store.MemoryStore import MemoryStore
from app.store.SqliteStore import SqliteStore

@pytest.fixture(params = ['mem', 'sqlite'])
def mem_1(request):

    if request.param == 'mem':
        db = MemoryStore()
    else:
        db = SqliteStore()

    return db


def test_set_get(mem_1):
    mem_1.set('a', 'val-a')
    val_a = mem_1.get('a')
    assert val_a == 'val-a'

    has_a = mem_1.has_key('a')
    assert has_a == True


def test_set_rollback(mem_1):

    mem_1.set('a', 'val-a')
    mem_1.rollback()
    with pytest.raises(KeyError):
        val_a = mem_1.get('a')

    val_a = mem_1.has_key('a')
    assert val_a == False


def test_set_commit_set_rollback(mem_1):

    mem_1.set('a', 'val-a')
    mem_1.commit()

    val_a = mem_1.get('a')
    assert val_a == 'val-a'

    mem_1.set('a', 'second-val')
    val_a = mem_1.get('a')
    assert val_a == 'second-val'

    mem_1.rollback()

    val_a = mem_1.get('a')
    assert val_a == 'val-a'


def test_set_commit_delete_rollback(mem_1):

    mem_1.set('a', 'val-a')
    mem_1.commit()

    val_a = mem_1.get('a')
    assert val_a == 'val-a'

    mem_1.delete('a')
    with pytest.raises(KeyError):
        val_a = mem_1.get('a')

    mem_1.rollback()
    val_a = mem_1.get('a')
    assert val_a == 'val-a'



