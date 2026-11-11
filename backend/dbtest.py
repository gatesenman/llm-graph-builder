"""Neo4j connectivity / insert performance smoke test.

Connection settings are read from the environment (see example.env):

    NEO4J_URI          e.g. neo4j+s://xxxxxxxx.databases.neo4j.io
    NEO4J_USERNAME     e.g. neo4j
    NEO4J_PASSWORD
    NEO4J_DATABASE     optional; driver default if unset

This script deletes all nodes in the target database before running the
timed insert test. Do not point it at a database you care about.

Usage:
    export NEO4J_URI=...
    export NEO4J_USERNAME=neo4j
    export NEO4J_PASSWORD=...
    python dbtest.py
"""

from __future__ import annotations

import os
import sys
import time

REQUIRED_ENV = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")

# Query used by the timed insert loop.
QUERY = "CREATE (n:Person {id: $id, name: $name})"
NUM_OPERATIONS = 1000


def load_config() -> dict:
    """Load Neo4j settings from the environment. Exit 2 if any are missing."""
    missing = [key for key in REQUIRED_ENV if not os.environ.get(key)]
    if missing:
        print(
            "Missing required environment variables: "
            + ", ".join(missing)
            + "\nSet them (placeholders are documented in example.env) and rerun."
            "\nDo not hard-code credentials in this file.",
            file=sys.stderr,
        )
        sys.exit(2)
    return {
        "name": os.environ.get("NEO4J_NAME", "Neo4j"),
        "uri": os.environ["NEO4J_URI"],
        "user": os.environ["NEO4J_USERNAME"],
        "password": os.environ["NEO4J_PASSWORD"],
        "database": os.environ.get("NEO4J_DATABASE") or None,
    }


def create_driver(uri: str, user: str, password: str):
    from neo4j import GraphDatabase

    return GraphDatabase.driver(uri, auth=(user, password))


def clear_database(driver, database: str | None = None) -> None:
    with driver.session(database=database) if database else driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


def performance_test(driver, query: str, num_operations: int, database: str | None = None) -> float:
    with driver.session(database=database) if database else driver.session() as session:
        start_time = time.time()
        for i in range(num_operations):
            session.run(query, parameters={"id": i, "name": f"name_{i}"})
        end_time = time.time()
    return end_time - start_time


def dbtest_main() -> None:
    config = load_config()
    print(f"Testing {config['name']}...")

    driver = create_driver(config["uri"], config["user"], config["password"])
    try:
        clear_database(driver, config["database"])
        elapsed_time = performance_test(
            driver, QUERY, NUM_OPERATIONS, config["database"]
        )
    finally:
        driver.close()

    print(f"{config['name']} completed in {elapsed_time:.4f} seconds")
    print("\nPerformance Test Results:")
    print(f"{config['name']}: {elapsed_time:.4f} seconds")


if __name__ == "__main__":
    dbtest_main()
