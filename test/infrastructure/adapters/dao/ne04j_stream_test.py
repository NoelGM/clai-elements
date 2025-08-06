from pandas import DataFrame

from src.domain.ports.dao.data_stream import DataStream
from src.infrastructure.adapters.dao.neo4j_stream import Neo4jStream


def _build_adapter(symbols: list = None) -> DataStream:
    adapter: DataStream = Neo4jStream(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="12345678a",
        symbols=symbols
    )
    return adapter


def test_pull_without_symbols_positive():
    """
    Try a successful query to recover data from the dataset, without stipulating symbols.
    """

    # Test scenario

    adapter: DataStream = _build_adapter()

    params = {
        "main_node": "Patient",
        "secondary_node": "AllergyIntolerance",
        "filter_field": "id",
        "filter_value": "AC1743089727161",
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


def test_pull_with_symbols_positive():
    """
    Try a successful query to recover data from the dataset, stipulating symbols.
    """

    # Test scenario

    symbols: list = [
        "Patient",
        "id",
        "AllergyIntolerance",
        "text"
    ]

    adapter: DataStream = _build_adapter(symbols)

    params = {
        "main_node": "Patient",
        "secondary_node": "AllergyIntolerance",
        "filter_field": "id",
        "filter_value": "AC1743089727161",
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


def test_pull_negative():
    """
    Try a non-successful query, because AllergyIntolerance will not be enabled as allowed symbol.
    """

    # Test scenario

    symbols: list = [
        "Patient",
        "id",
        "text"
    ]

    adapter: DataStream = _build_adapter(symbols)

    params = {
        "main_node": "Patient",
        "secondary_node": "AllergyIntolerance",
        "filter_field": "id",
        "filter_value": "AC1743089727161",
        "parameters": {}
    }

    #   Expected values

    expected: dict = {
        'len': 0
    }

    #   Observation

    result: DataFrame = adapter.pull(params)

    observed: dict = {
        'len': len(result)
    }

    #   Check

    assert False not in [observed[key] == expected[key] for key in expected.keys()]


# def test_push_positive():
#
#     # Test scenario
#
#     params = {
#         "main_node": "Patient",
#     }
#
#     data = {
#         "id": "AC1743089727162",
#         "name": "John Doe",
#     }
#
#     adapter: DataStream = _build_adapter()
#
#     #   Observation
#
#     result: bool = adapter.push(data, params)
#
#     #   Check
#
#     assert result
#
#
# def test_push_negative():
#
#     # Test scenario
#
#     params = {
#         "node": "fakeNode",
#     }
#
#     data = {
#         "id": "AC1743089727162",
#         "name": "John Doe",
#     }
#
#     adapter: DataStream = _build_adapter()
#
#     #   Observation
#
#     result: bool = adapter.push(data, params)
#
#     #   Check
#
#     assert not result
