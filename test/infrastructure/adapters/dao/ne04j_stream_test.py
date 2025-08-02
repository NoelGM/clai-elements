from pandas import DataFrame

from src.domain.ports.dao.data_stream import DataStream
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

adapter: DataStream = Neo4jStream(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678a"
)


def test_pull():

    # Test scenario

    params = {
        "node": "Patient",
        "identifier": "AC1743089727161",
        "topic": "AllergyIntolerance",
        "field": "id",
        "parameters": {}
    }

    #   Expected values

    expected: dict = {
        'len': 2
    }

    #   Observation

    result: DataFrame = adapter.pull(params)

    observed: dict = {
        'len': len(result)
    }

    #   Check

    assert False not in [observed[key] == expected[key] for key in expected.keys()]


def test_push_positive():

    # Test scenario

    params = {
        "node": "Patient",
    }

    data = {
        "id": "AC1743089727162",
        "name": "John Doe",
    }

    #   Observation

    result: bool = adapter.push(data, params)

    #   Check

    assert result


def test_push_negative():

    # Test scenario

    params = {
        "node": "fakeNode",
    }

    data = {
        "id": "AC1743089727162",
        "name": "John Doe",
    }

    #   Observation

    result: bool = adapter.push(data, params)

    #   Check

    assert not result
