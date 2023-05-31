import pytest
import random
import string
from docarray import DocList, BaseDoc
from docarray.typing import NdArray
from vectordb import HNSWVectorDB
import numpy as np


class MyDoc(BaseDoc):
    text: str
    embedding: NdArray[128]


@pytest.fixture()
def docs_to_index():
    return DocList[MyDoc](
        [MyDoc(text="".join(random.choice(string.ascii_lowercase) for _ in range(5)), embedding=np.random.rand(128))
         for _ in range(2000)])


@pytest.mark.parametrize('call_method', ['docs', 'inputs', 'positional'])
def test_hnswlib_vectordb_batch(docs_to_index, call_method, tmpdir):
    query = docs_to_index[:10]
    indexer = HNSWVectorDB[MyDoc](workspace=str(tmpdir))
    if call_method == 'docs':
        indexer.index(docs=docs_to_index)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.index(inputs=docs_to_index)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.index(docs_to_index)
        resp = indexer.search(query)
    assert len(resp) == len(query)
    for res in resp:
        assert len(res.matches) == 10
        assert res.id == res.matches[0].id
        assert res.text == res.matches[0].text
        assert res.scores[0] < 0.001  # some precision issues, should be 0.0


@pytest.mark.parametrize('call_method', ['docs', 'inputs', 'positional'])
def test_hnswlib_vectordb_single_query(docs_to_index, call_method, tmpdir):
    query = docs_to_index[100]
    indexer = HNSWVectorDB[MyDoc](workspace=str(tmpdir))
    if call_method == 'docs':
        indexer.index(docs=docs_to_index)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.index(inputs=docs_to_index)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.index(docs_to_index)
        resp = indexer.search(query)
    assert len(resp.matches) == 10
    assert resp.id == resp.matches[0].id
    assert resp.text == resp.matches[0].text
    assert resp.scores[0] < 0.001  # some precision issues, should be 0.0


@pytest.mark.parametrize('call_method', ['docs', 'inputs', 'positional'])
def test_hnswlib_vectordb_delete(docs_to_index, call_method, tmpdir):
    query = docs_to_index[0]
    delete = MyDoc(id=query.id, text='', embedding=np.random.rand(128))
    indexer = HNSWVectorDB[MyDoc](workspace=str(tmpdir))
    if call_method == 'docs':
        indexer.index(docs=docs_to_index)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.index(inputs=docs_to_index)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.index(docs_to_index)
        resp = indexer.search(query)

    assert len(resp.matches) == 10
    assert resp.id == resp.matches[0].id
    assert resp.text == resp.matches[0].text
    assert resp.scores[0] < 0.001  # some precision issues, should be 0.0

    if call_method == 'docs':
        indexer.delete(docs=delete)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.delete(docs=delete)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.delete(docs=delete)
        resp = indexer.search(query)

    assert len(resp.matches) == 10
    assert resp.id != resp.matches[0].id
    assert resp.text != resp.matches[0].text


@pytest.mark.parametrize('call_method', ['docs', 'inputs', 'positional'])
def test_hnswlib_vectordb_udpate_text(docs_to_index, call_method, tmpdir):
    query = docs_to_index[0]
    update = MyDoc(id=query.id, text=query.text + '_changed', embedding=query.embedding)
    indexer = HNSWVectorDB[MyDoc](workspace=str(tmpdir))
    if call_method == 'docs':
        indexer.index(docs=docs_to_index)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.index(inputs=docs_to_index)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.index(docs_to_index)
        resp = indexer.search(query)

    assert len(resp.matches) == 10
    assert resp.id == resp.matches[0].id
    assert resp.text == resp.matches[0].text
    assert resp.scores[0] < 0.001  # some precision issues, should be 0.0

    if call_method == 'docs':
        indexer.update(docs=update)
        resp = indexer.search(docs=query)
    elif call_method == 'inputs':
        indexer.update(inputs=update)
        resp = indexer.search(inputs=query)
    elif call_method == 'positional':
        indexer.update(update)
        resp = indexer.search(inputs=query)

    assert len(resp.matches) == 10
    assert resp.scores[0] < 0.001
    assert resp.id == resp.matches[0].id
    assert resp.matches[0].text == resp.text + '_changed'
