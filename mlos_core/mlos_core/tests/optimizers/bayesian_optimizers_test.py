#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
"""
Tests for Bayesian Optimizers.
"""

from typing import Optional, Type

import ConfigSpace as CS
import pandas as pd
import pytest
from mlos_core.optimizers import BaseOptimizer, OptimizerType
from mlos_core.optimizers.bayesian_optimizers import BaseBayesianOptimizer


@pytest.mark.filterwarnings("error:Not Implemented")
@pytest.mark.parametrize(
    ("optimizer_class", "kwargs"),
    [
        *[(member.value, {}) for member in OptimizerType if not member == OptimizerType.SMAC],
    ],
)
def test_context_not_implemented_warning(
    configuration_space: CS.ConfigurationSpace,
    optimizer_class: Type[BaseOptimizer],
    kwargs: Optional[dict],
) -> None:
    """
    Make sure we raise warnings for the functionality that has not been implemented yet.
    """
    if kwargs is None:
        kwargs = {}
<<<<<<< HEAD
    optimizer = optimizer_class(parameter_space=configuration_space, **kwargs)
    suggestion, _ = optimizer.suggest()
    scores = pd.DataFrame({"score": [1]})
=======
    optimizer = optimizer_class(
        parameter_space=configuration_space,
        optimization_targets=['score'],
        **kwargs
    )
    suggestion = optimizer.suggest()
    scores = pd.DataFrame({'score': [1]})
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec
    context = pd.DataFrame([["something"]])

    with pytest.raises(UserWarning):
<<<<<<< HEAD
        optimizer.register(suggestion, scores["score"], context=context)
=======
        optimizer.register(suggestion, scores, context=context)
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec

    with pytest.raises(UserWarning):
        optimizer.suggest(context=context)

    if isinstance(optimizer, BaseBayesianOptimizer):
        with pytest.raises(UserWarning):
            optimizer.surrogate_predict(suggestion, context=context)
