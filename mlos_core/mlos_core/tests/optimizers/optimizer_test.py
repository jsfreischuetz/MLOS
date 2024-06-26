#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
"""
Tests for Bayesian Optimizers.
"""

import logging
from copy import deepcopy
from typing import List, Optional, Type

import ConfigSpace as CS
import numpy as np
<<<<<<< HEAD
import numpy.typing as npt
import pandas as pd
import pytest
=======
import ConfigSpace as CS

>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec
from mlos_core.optimizers import (
    BaseOptimizer,
    ConcreteOptimizer,
    OptimizerFactory,
    OptimizerType,
)
from mlos_core.optimizers.bayesian_optimizers import (
    BaseBayesianOptimizer,
    SmacOptimizer,
)
from mlos_core.spaces.adapters import SpaceAdapterType
from mlos_core.tests import SEED, get_all_concrete_subclasses

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)


@pytest.mark.parametrize(
    ("optimizer_class", "kwargs"),
    [
        *[(member.value, {}) for member in OptimizerType],
    ],
)
def test_create_optimizer_and_suggest(
    configuration_space: CS.ConfigurationSpace,
    optimizer_class: Type[BaseOptimizer],
    kwargs: Optional[dict],
) -> None:
    """
    Test that we can create an optimizer and get a suggestion from it.
    """
    if kwargs is None:
        kwargs = {}
    optimizer = optimizer_class(
        parameter_space=configuration_space,
        optimization_targets=['score'],
        **kwargs
    )
    assert optimizer is not None

    assert optimizer.parameter_space is not None

    suggestion, context = optimizer.suggest()
    assert suggestion is not None

    myrepr = repr(optimizer)
    assert myrepr.startswith(optimizer_class.__name__)

    # pending not implemented
    with pytest.raises(NotImplementedError):
        optimizer.register_pending(suggestion, context)


@pytest.mark.parametrize(
    ("optimizer_class", "kwargs"),
    [
        *[(member.value, {}) for member in OptimizerType],
    ],
)
def test_basic_interface_toy_problem(
    configuration_space: CS.ConfigurationSpace,
    optimizer_class: Type[BaseOptimizer],
    kwargs: Optional[dict],
) -> None:
    """
    Toy problem to test the optimizers.
    """
    # pylint: disable=too-many-locals
    max_iterations = 20
    if kwargs is None:
        kwargs = {}
    if optimizer_class == OptimizerType.SMAC.value:
        # SMAC sets the initial random samples as a percentage of the max iterations, which defaults to 100.
        # To avoid having to train more than 25 model iterations, we set a lower number of max iterations.
        kwargs["max_trials"] = max_iterations * 2

<<<<<<< HEAD
    def objective(x: pd.Series) -> npt.ArrayLike:  # pylint: disable=invalid-name
        ret: npt.ArrayLike = (6 * x - 2) ** 2 * np.sin(12 * x - 4)
        return ret
=======
    def objective(x: pd.Series) -> pd.DataFrame:
        return pd.DataFrame({"score": (6 * x - 2)**2 * np.sin(12 * x - 4)})
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec

    # Emukit doesn't allow specifying a random state, so we set the global seed.
    np.random.seed(SEED)
    optimizer = optimizer_class(
        parameter_space=configuration_space,
        optimization_targets=['score'],
        **kwargs
    )

    with pytest.raises(ValueError, match="No observations"):
        optimizer.get_best_observations()

    with pytest.raises(ValueError, match="No observations"):
        optimizer.get_observations()

    for _ in range(max_iterations):
        suggestion, context = optimizer.suggest()
        assert isinstance(suggestion, pd.DataFrame)
<<<<<<< HEAD
        assert (suggestion.columns == ["x", "y", "z"]).all()
=======
        assert set(suggestion.columns) == {'x', 'y', 'z'}
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec
        # check that suggestion is in the space
        configuration = CS.Configuration(
            optimizer.parameter_space, suggestion.iloc[0].to_dict()
        )
        # Raises an error if outside of configuration space
        configuration.is_valid_configuration()
<<<<<<< HEAD
        observation = objective(suggestion["x"])
        assert isinstance(observation, pd.Series)
        optimizer.register(suggestion, observation, context)

    best_observation = optimizer.get_best_observation()
    assert isinstance(best_observation, pd.DataFrame)
    assert (best_observation.columns == ["x", "y", "z", "score"]).all()

    all_observations = optimizer.get_observations()
    assert isinstance(all_observations, pd.DataFrame)
    assert all_observations.shape == (20, 4)
    assert (all_observations.columns == ["x", "y", "z", "score"]).all()

    # It would be better to put this into bayesian_optimizer_test but then we'd have to refit the model
    if isinstance(optimizer, BaseBayesianOptimizer):
        pred_best = optimizer.surrogate_predict(best_observation[["x", "y", "z"]])
        assert pred_best.shape == (1,)

        pred_all = optimizer.surrogate_predict(all_observations[["x", "y", "z"]])
=======
        observation = objective(suggestion['x'])
        assert isinstance(observation, pd.DataFrame)
        optimizer.register(suggestion, observation)

    (best_config, best_score, best_context) = optimizer.get_best_observations()
    assert isinstance(best_config, pd.DataFrame)
    assert isinstance(best_score, pd.DataFrame)
    assert best_context is None
    assert set(best_config.columns) == {'x', 'y', 'z'}
    assert set(best_score.columns) == {'score'}
    assert best_config.shape == (1, 3)
    assert best_score.shape == (1, 1)
    assert best_score.score.iloc[0] < -5

    (all_configs, all_scores, all_contexts) = optimizer.get_observations()
    assert isinstance(all_configs, pd.DataFrame)
    assert isinstance(all_scores, pd.DataFrame)
    assert all_contexts is None
    assert set(all_configs.columns) == {'x', 'y', 'z'}
    assert set(all_scores.columns) == {'score'}
    assert all_configs.shape == (20, 3)
    assert all_scores.shape == (20, 1)

    # It would be better to put this into bayesian_optimizer_test but then we'd have to refit the model
    if isinstance(optimizer, BaseBayesianOptimizer):
        pred_best = optimizer.surrogate_predict(best_config)
        assert pred_best.shape == (1,)

        pred_all = optimizer.surrogate_predict(all_configs)
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec
        assert pred_all.shape == (20,)


@pytest.mark.parametrize(
    ("optimizer_type"),
    [
        # Enumerate all supported Optimizers
        # *[member for member in OptimizerType],
        *list(OptimizerType),
    ],
)
def test_concrete_optimizer_type(optimizer_type: OptimizerType) -> None:
    """
    Test that all optimizer types are listed in the ConcreteOptimizer constraints.
    """
    assert optimizer_type.value in ConcreteOptimizer.__constraints__  # type: ignore[attr-defined]  # pylint: disable=no-member


@pytest.mark.parametrize(
    ("optimizer_type", "kwargs"),
    [
        # Default optimizer
        (None, {}),
        # Enumerate all supported Optimizers
        *[(member, {}) for member in OptimizerType],
        # Optimizer with non-empty kwargs argument
    ],
)
def test_create_optimizer_with_factory_method(
    configuration_space: CS.ConfigurationSpace,
    optimizer_type: Optional[OptimizerType],
    kwargs: Optional[dict],
) -> None:
    """
    Test that we can create an optimizer via a factory.
    """
    if kwargs is None:
        kwargs = {}
    if optimizer_type is None:
        optimizer = OptimizerFactory.create(
            parameter_space=configuration_space,
            optimization_targets=['score'],
            optimizer_kwargs=kwargs,
        )
    else:
        optimizer = OptimizerFactory.create(
            parameter_space=configuration_space,
            optimization_targets=['score'],
            optimizer_type=optimizer_type,
            optimizer_kwargs=kwargs,
        )
    assert optimizer is not None

    assert optimizer.parameter_space is not None

    suggestion, _ = optimizer.suggest()
    assert suggestion is not None

    if optimizer_type is not None:
        myrepr = repr(optimizer)
        assert myrepr.startswith(optimizer_type.value.__name__)


@pytest.mark.parametrize(
    ("optimizer_type", "kwargs"),
    [
        # Enumerate all supported Optimizers
        *[(member, {}) for member in OptimizerType],
        # Optimizer with non-empty kwargs argument
        (
            OptimizerType.SMAC,
            {
                # Test with default config.
                "use_default_config": True,
                # 'n_random_init': 10,
            },
        ),
    ],
)
def test_optimizer_with_llamatune(
    optimizer_type: OptimizerType, kwargs: Optional[dict]
) -> None:
    """
    Toy problem to test the optimizers with llamatune space adapter.
    """
    # pylint: disable=too-complex,disable=too-many-statements,disable=too-many-locals
    num_iters = 50
    if kwargs is None:
        kwargs = {}

    def objective(point: pd.DataFrame) -> pd.DataFrame:
        # Best value can be reached by tuning an 1-dimensional search space
<<<<<<< HEAD
        ret: pd.Series = np.sin(point["x"] * point["y"])
        assert ret.hasnans is False
=======
        ret = pd.DataFrame({"score": np.sin(point.x * point.y)})
        assert ret.score.hasnans is False
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec
        return ret

    input_space = CS.ConfigurationSpace(seed=1234)
    # Add two continuous inputs
    input_space.add_hyperparameter(
        CS.UniformFloatHyperparameter(name="x", lower=0, upper=3)
    )
    input_space.add_hyperparameter(
        CS.UniformFloatHyperparameter(name="y", lower=0, upper=3)
    )

    # Initialize an optimizer that uses LlamaTune space adapter
    space_adapter_kwargs = {
        "num_low_dims": 1,
        "special_param_values": None,
        "max_unique_values_per_param": None,
    }

    # Make some adjustments to the kwargs for the optimizer and LlamaTuned
    # optimizer for debug/testing.

    # if optimizer_type == OptimizerType.SMAC:
    #    # Allow us to override the number of random init samples.
    #    kwargs['max_ratio'] = 1.0
    optimizer_kwargs = deepcopy(kwargs)
    llamatune_optimizer_kwargs = deepcopy(kwargs)
    # if optimizer_type == OptimizerType.SMAC:
    #    optimizer_kwargs['n_random_init'] = 20
    #    llamatune_optimizer_kwargs['n_random_init'] = 10

    llamatune_optimizer: BaseOptimizer = OptimizerFactory.create(
        parameter_space=input_space,
        optimization_targets=['score'],
        optimizer_type=optimizer_type,
        optimizer_kwargs=llamatune_optimizer_kwargs,
        space_adapter_type=SpaceAdapterType.LLAMATUNE,
        space_adapter_kwargs=space_adapter_kwargs,
    )
    # Initialize an optimizer that uses the original space
    optimizer: BaseOptimizer = OptimizerFactory.create(
        parameter_space=input_space,
        optimization_targets=['score'],
        optimizer_type=optimizer_type,
        optimizer_kwargs=optimizer_kwargs,
    )
    assert optimizer is not None
    assert llamatune_optimizer is not None
    assert (
        optimizer.optimizer_parameter_space
        != llamatune_optimizer.optimizer_parameter_space
    )

    llamatune_n_random_init = 0
    opt_n_random_init = int(kwargs.get("n_random_init", 0))
    if optimizer_type == OptimizerType.SMAC:
        assert isinstance(optimizer, SmacOptimizer)
        assert isinstance(llamatune_optimizer, SmacOptimizer)
        opt_n_random_init = optimizer.n_random_init
        llamatune_n_random_init = llamatune_optimizer.n_random_init

    for i in range(num_iters):
        # Place to set a breakpoint for when the optimizer is done with random init.
        if llamatune_n_random_init and i > llamatune_n_random_init:
            _LOG.debug("LlamaTuned Optimizer is done with random init.")
        if opt_n_random_init and i >= opt_n_random_init:
            _LOG.debug("Optimizer is done with random init.")

        # loop for optimizer
        suggestion, context = optimizer.suggest()
        observation = objective(suggestion)
        optimizer.register(suggestion, observation, context)

        # loop for llamatune-optimizer
        suggestion, context = llamatune_optimizer.suggest()
        _x, _y = suggestion["x"].iloc[0], suggestion["y"].iloc[0]
        assert _x == pytest.approx(_y, rel=1e-3) or _x + _y == pytest.approx(
            3.0, rel=1e-3
        )  # optimizer explores 1-dimensional space
        observation = objective(suggestion)
        llamatune_optimizer.register(suggestion, observation, context)

    # Retrieve best observations
    best_observation = optimizer.get_best_observations()
    llamatune_best_observation = llamatune_optimizer.get_best_observations()

<<<<<<< HEAD
    for best_obv in (best_observation, llamatune_best_observation):
        assert isinstance(best_obv, pd.DataFrame)
        assert (best_obv.columns == ["x", "y", "score"]).all()

    # LlamaTune's optimizer score should better (i.e., lower) than plain optimizer's one, or close to that
    assert (
        best_observation["score"].iloc[0] > llamatune_best_observation["score"].iloc[0]
        or best_observation["score"].iloc[0] + 1
        > llamatune_best_observation["score"].iloc[0]
    )

    # Retrieve and check all observations
    for all_obvs in (
        optimizer.get_observations(),
        llamatune_optimizer.get_observations(),
    ):
        assert isinstance(all_obvs, pd.DataFrame)
        assert all_obvs.shape == (num_iters, 3)
        assert (all_obvs.columns == ["x", "y", "score"]).all()
=======
    for (best_config, best_score, best_context) in (best_observation, llamatune_best_observation):
        assert isinstance(best_config, pd.DataFrame)
        assert isinstance(best_score, pd.DataFrame)
        assert best_context is None
        assert set(best_config.columns) == {'x', 'y'}
        assert set(best_score.columns) == {'score'}

    (best_config, best_score, _context) = best_observation
    (llamatune_best_config, llamatune_best_score, _context) = llamatune_best_observation

    # LlamaTune's optimizer score should better (i.e., lower) than plain optimizer's one, or close to that
    assert best_score.score.iloc[0] > llamatune_best_score.score.iloc[0] or \
        best_score.score.iloc[0] + 1e-3 > llamatune_best_score.score.iloc[0]

    # Retrieve and check all observations
    for (all_configs, all_scores, all_contexts) in (
            optimizer.get_observations(), llamatune_optimizer.get_observations()):
        assert isinstance(all_configs, pd.DataFrame)
        assert isinstance(all_scores, pd.DataFrame)
        assert all_contexts is None
        assert set(all_configs.columns) == {'x', 'y'}
        assert set(all_scores.columns) == {'score'}
        assert len(all_configs) == num_iters
        assert len(all_scores) == num_iters
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec

    # .surrogate_predict method not currently implemented if space adapter is employed
    if isinstance(llamatune_optimizer, BaseBayesianOptimizer):
        with pytest.raises(NotImplementedError):
<<<<<<< HEAD
            llamatune_optimizer.surrogate_predict(
                llamatune_best_observation[["x", "y"]]
            )
=======
            llamatune_optimizer.surrogate_predict(llamatune_best_config)
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec


# Dynamically determine all of the optimizers we have implemented.
# Note: these must be sorted.
optimizer_subclasses: List[Type[BaseOptimizer]] = get_all_concrete_subclasses(
    BaseOptimizer, pkg_name="mlos_core"  # type: ignore[type-abstract]
)
assert optimizer_subclasses


@pytest.mark.parametrize(("optimizer_class"), optimizer_subclasses)
def test_optimizer_type_defs(optimizer_class: Type[BaseOptimizer]) -> None:
    """
    Test that all optimizer classes are listed in the OptimizerType enum.
    """
    optimizer_type_classes = {member.value for member in OptimizerType}
    assert optimizer_class in optimizer_type_classes


@pytest.mark.parametrize(
    ("optimizer_type", "kwargs"),
    [
        # Default optimizer
        (None, {}),
        # Enumerate all supported Optimizers
        *[(member, {}) for member in OptimizerType],
        # Optimizer with non-empty kwargs argument
    ],
)
def test_mixed_numerics_type_input_space_types(
    optimizer_type: Optional[OptimizerType], kwargs: Optional[dict]
) -> None:
    """
    Toy problem to test the optimizers with mixed numeric types to ensure that original dtypes are retained.
    """
    max_iterations = 10
    if kwargs is None:
        kwargs = {}

    def objective(point: pd.DataFrame) -> pd.DataFrame:
        # mix of hyperparameters, optimal is to select the highest possible
        return pd.DataFrame({"score": point["x"] + point["y"]})

    input_space = CS.ConfigurationSpace(seed=SEED)
    # add a mix of numeric datatypes
    input_space.add_hyperparameter(
        CS.UniformIntegerHyperparameter(name="x", lower=0, upper=5)
    )
    input_space.add_hyperparameter(
        CS.UniformFloatHyperparameter(name="y", lower=0.0, upper=5.0)
    )

    if optimizer_type is None:
        optimizer = OptimizerFactory.create(
            parameter_space=input_space,
            optimization_targets=['score'],
            optimizer_kwargs=kwargs,
        )
    else:
        optimizer = OptimizerFactory.create(
            parameter_space=input_space,
            optimization_targets=['score'],
            optimizer_type=optimizer_type,
            optimizer_kwargs=kwargs,
        )

    with pytest.raises(ValueError, match="No observations"):
        optimizer.get_best_observations()

    with pytest.raises(ValueError, match="No observations"):
        optimizer.get_observations()

    for _ in range(max_iterations):
        suggestion, context = optimizer.suggest()
        assert isinstance(suggestion, pd.DataFrame)
        assert (suggestion.columns == ["x", "y"]).all()
        # Check suggestion values are the expected dtype
        assert isinstance(suggestion["x"].iloc[0], np.integer)
        assert isinstance(suggestion["y"].iloc[0], np.floating)
        # Check that suggestion is in the space
        test_configuration = CS.Configuration(
            optimizer.parameter_space, suggestion.astype("O").iloc[0].to_dict()
        )
        # Raises an error if outside of configuration space
        test_configuration.is_valid_configuration()
        # Test registering the suggested configuration with a score.
        observation = objective(suggestion)
<<<<<<< HEAD
        assert isinstance(observation, pd.Series)
        optimizer.register(suggestion, observation, context)
=======
        assert isinstance(observation, pd.DataFrame)
        optimizer.register(suggestion, observation)
>>>>>>> c7a4823b22855ccc9b9083495b48e95a48b779ec

    (best_config, best_score, best_context) = optimizer.get_best_observations()
    assert isinstance(best_config, pd.DataFrame)
    assert isinstance(best_score, pd.DataFrame)
    assert best_context is None

    (all_configs, all_scores, all_contexts) = optimizer.get_observations()
    assert isinstance(all_configs, pd.DataFrame)
    assert isinstance(all_scores, pd.DataFrame)
    assert all_contexts is None
