#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
"""
Tests for CLI schema validation.
"""

from os import path

import pytest

from mlos_bench.config.schemas import ConfigSchema

from mlos_bench.tests.config.schemas import (get_schema_test_cases,
                                             check_test_case_against_schema,
                                             check_test_case_config_with_extra_param)


# General testing strategy:
# - hand code a set of good/bad configs (useful to test editor schema checking)
# - for each config, load and validate against expected schema

TEST_CASES = get_schema_test_cases(path.join(path.dirname(__file__), "test-cases"))


# Now we actually perform all of those validation tests.

@pytest.mark.parametrize("test_case_name", sorted(TEST_CASES.by_path))
def test_cli_configs_against_schema(test_case_name: str) -> None:
    """
    Checks that the CLI config validates against the schema.
    """
    check_test_case_against_schema(TEST_CASES.by_path[test_case_name], ConfigSchema.CLI)
    if TEST_CASES.by_path[test_case_name].test_case_type != "bad":
        # Unified schema has a hard time validating bad configs, so we skip it.
        # The trouble is that tunable-values, cli, globals all look like flat dicts with minor constraints on them,
        # so adding/removing params doesn't invalidate it against all of the config types.
        check_test_case_against_schema(TEST_CASES.by_path[test_case_name], ConfigSchema.UNIFIED)


@pytest.mark.parametrize("test_case_name", sorted(TEST_CASES.by_type["good"]))
def test_cli_configs_with_extra_param(test_case_name: str) -> None:
    """
    Checks that the cli config fails to validate if extra params are present in certain places.
    """
    check_test_case_config_with_extra_param(TEST_CASES.by_type["good"][test_case_name], ConfigSchema.CLI)
    if TEST_CASES.by_path[test_case_name].test_case_type != "bad":
        # Unified schema has a hard time validating bad configs, so we skip it.
        # The trouble is that tunable-values, cli, globals all look like flat dicts with minor constraints on them,
        # so adding/removing params doesn't invalidate it against all of the config types.
        check_test_case_against_schema(TEST_CASES.by_path[test_case_name], ConfigSchema.UNIFIED)
