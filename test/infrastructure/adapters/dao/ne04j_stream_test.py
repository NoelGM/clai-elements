from pandas import DataFrame

from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream

adapter: Neo4jStream = Neo4jStream(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678a"
)


def test_pull():

    # Test scene

    pull_params = {
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

    result: DataFrame = adapter.pull(pull_params)

    observed: dict = {
        'len': len(result)
    }

    #   Check

    assert False not in [observed[key] == expected[key] for key in expected.keys()]


def test_push_positive():

    push_params = {
        "node": "Patient",
    }

    data = {
        "id": "AC1743089727162",
        "name": "John Doe",
    }

    result: bool = adapter.push(data, push_params)

    assert result
