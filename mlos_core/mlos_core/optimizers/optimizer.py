#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
"""
Contains the BaseOptimizer abstract class.
"""

import collections
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple, Union

import ConfigSpace
import numpy as np
import numpy.typing as npt
import pandas as pd

from mlos_core.util import config_to_dataframe
from mlos_core.spaces.adapters.adapter import BaseSpaceAdapter


class BaseOptimizer(metaclass=ABCMeta):
    """
    Optimizer abstract base class defining the basic interface.
    """

    def __init__(self, *,
                 parameter_space: ConfigSpace.ConfigurationSpace,
                 optimization_targets: Optional[Union[str, List[str]] = None,
                 space_adapter: Optional[BaseSpaceAdapter] = None):
        """
        Create a new instance of the base optimizer.

        Parameters
        ----------
        parameter_space : ConfigSpace.ConfigurationSpace
            The parameter space to optimize.
        optimization_targets : List[str]
            The names of the optimization targets to minimize.
        space_adapter : BaseSpaceAdapter
            The space adapter class to employ for parameter space transformations.
        """
        self.parameter_space: ConfigSpace.ConfigurationSpace = parameter_space
        self.optimizer_parameter_space: ConfigSpace.ConfigurationSpace = \
            parameter_space if space_adapter is None else space_adapter.target_parameter_space

        if space_adapter is not None and space_adapter.orig_parameter_space != parameter_space:
            raise ValueError("Given parameter space differs from the one given to space adapter")

        self._optimization_targets = optimization_targets
        self._space_adapter: Optional[BaseSpaceAdapter] = space_adapter
        self._observations: List[Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]] = []
        self._has_context: Optional[bool] = None
        self._pending_observations: List[Tuple[pd.DataFrame, Optional[pd.DataFrame]]] = []
        self.delayed_config: Optional[pd.DataFrame] = None
        self.delayed_context: Optional[pd.DataFrame] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(space_adapter={self.space_adapter})"

    @property
    def space_adapter(self) -> Optional[BaseSpaceAdapter]:
        """Get the space adapter instance (if any)."""
        return self._space_adapter

    def register(self, configurations: pd.DataFrame, scores: pd.DataFrame,
                 context: Optional[pd.DataFrame] = None) -> None:
        """Wrapper method, which employs the space adapter (if any), before registering the configurations and scores.

        Parameters
        ----------
        configurations : pd.DataFrame
            Dataframe of configurations / parameters. The columns are parameter names and the rows are the configurations.
        scores : pd.DataFrame
            Scores from running the configurations. The index is the same as the index of the configurations.

        context : pd.DataFrame
            Not Yet Implemented.
        """
        # Do some input validation.
        if type(self._optimization_targets) is str:
            assert self._optimization_targets in scores.columns, "Mismatched optimization targets."
        if type(self._optimization_targets) is list:
            assert set(scores.columns) >= set(self._optimization_targets), "Mismatched optimization targets."
        assert self._has_context is None or self._has_context ^ (context is None), \
            "Context must always be added or never be added."
        assert len(configurations) == len(scores), \
            "Mismatched number of configurations and scores."
        if context is not None:
            assert len(configurations) == len(context), \
                "Mismatched number of configurations and context."
        assert configurations.shape[1] == len(self.parameter_space.values()), \
            "Mismatched configuration shape."
        self._observations.append((configurations, scores, context))
        self._has_context = context is not None

        if self._space_adapter:
            configurations = self._space_adapter.inverse_transform(configurations)
            assert configurations.shape[1] == len(self.optimizer_parameter_space.values()), \
                "Mismatched configuration shape after inverse transform."
        return self._register(configurations, scores, context)

    @abstractmethod
    def _register(self, configurations: pd.DataFrame, scores: pd.DataFrame,
                  context: Optional[pd.DataFrame] = None) -> None:
        """Registers the given configurations and scores.

        Parameters
        ----------
        configurations : pd.DataFrame
            Dataframe of configurations / parameters. The columns are parameter names and the rows are the configurations.
        scores : pd.DataFrame
            Scores from running the configurations. The index is the same as the index of the configurations.

        context : pd.DataFrame
            Not Yet Implemented.
        """
        pass    # pylint: disable=unnecessary-pass # pragma: no cover

    def suggest(
        self, context: Optional[pd.DataFrame] = None, defaults: bool = False
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Wrapper method, which employs the space adapter (if any), after suggesting a new configuration.

        Parameters
        ----------
        context : pd.DataFrame
            Not Yet Implemented.
        defaults : bool
            Whether or not to return the default config instead of an optimizer guided one.
            By default, use the one from the optimizer.

        Returns
        -------
        configuration : pd.DataFrame
            Pandas dataframe with a single row. Column names are the parameter names.

        context : pd.DataFrame
            Pandas dataframe with a single row containing the context.
            Column names are the budget, seed, and instance of the evaluation, if valid.
        """
        if defaults:
            self.delayed_config, self.delayed_context = self._suggest(context)

            configuration: pd.DataFrame = config_to_dataframe(
                self.parameter_space.get_default_configuration()
            )
            context = self.delayed_context
            if self.space_adapter is not None:
                configuration = self.space_adapter.inverse_transform(configuration)
        else:
            if self.delayed_config is None:
                configuration, context = self._suggest(context)
            else:
                configuration, context = self.delayed_config, self.delayed_context
                self.delayed_config, self.delayed_context = None, None
            assert len(configuration) == 1, \
                "Suggest must return a single configuration."
            assert set(configuration.columns).issubset(set(self.optimizer_parameter_space)), \
                "Optimizer suggested a configuration that does not match the expected parameter space."
        if self._space_adapter:
            configuration = self._space_adapter.transform(configuration)
            assert set(configuration.columns).issubset(set(self.parameter_space)), \
                "Space adapter produced a configuration that does not match the expected parameter space."
        return configuration, context

    @abstractmethod
    def _suggest(
        self, context: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """Suggests a new configuration.

        Parameters
        ----------
        context : pd.DataFrame
            Not Yet Implemented.

        Returns
        -------
        configuration : pd.DataFrame
            Pandas dataframe with a single row. Column names are the parameter names.
        """
        pass    # pylint: disable=unnecessary-pass # pragma: no cover

    @abstractmethod
    def register_pending(self, configurations: pd.DataFrame,
                         context: Optional[pd.DataFrame] = None) -> None:
        """Registers the given configurations as "pending".
        That is it say, it has been suggested by the optimizer, and an experiment trial has been started.
        This can be useful for executing multiple trials in parallel, retry logic, etc.

        Parameters
        ----------
        configurations : pd.DataFrame
            Dataframe of configurations / parameters. The columns are parameter names and the rows are the configurations.
        context : pd.DataFrame
            Not Yet Implemented.
        """
        pass    # pylint: disable=unnecessary-pass # pragma: no cover

    def get_observations(self) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Returns the observations as a triplet of DataFrames (config, score, context).

        Returns
        -------
        observations : Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]
            A triplet of (config, score, context) DataFrames of observations.
        """
        if len(self._observations) == 0:
            raise ValueError("No observations registered yet.")
        configs = pd.concat([config for config, _, _ in self._observations]).reset_index(drop=True)
        scores = pd.concat([score for _, score, _ in self._observations]).reset_index(drop=True)
        contexts = pd.concat([pd.DataFrame() if context is None else context
                              for _, _, context in self._observations]).reset_index(drop=True)
        return (configs, scores, contexts if len(contexts.columns) > 0 else None)

    def get_best_observations(self, n_max: int = 1) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Get the N best observations so far as a triplet of DataFrames (config, score, context).
        Default is N=1. The columns are ordered in ASCENDING order of the optimization targets.
        The function uses `pandas.DataFrame.nsmallest(..., keep="first")` method under the hood.

        Parameters
        ----------
        n_max : int
            Maximum number of best observations to return. Default is 1.

        Returns
        -------
        observations : Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]
            A triplet of best (config, score, context) DataFrames of best observations.
        """
        if len(self._observations) == 0:
            raise ValueError("No observations registered yet.")
        (configs, scores, contexts) = self.get_observations()
        idx = scores.nsmallest(n_max, columns=self._optimization_targets, keep="first").index
        return (configs.loc[idx], scores.loc[idx],
                None if contexts is None else contexts.loc[idx])

    def cleanup(self) -> None:
        """
        Remove temp files, release resources, etc. after use. Default is no-op.
        Redefine this method in optimizers that require cleanup.
        """

    def _from_1hot(self, config: npt.NDArray) -> pd.DataFrame:
        """
        Convert numpy array from one-hot encoding to a DataFrame
        with categoricals and ints in proper columns.
        """
        df_dict = collections.defaultdict(list)
        for i in range(config.shape[0]):
            j = 0
            for param in self.optimizer_parameter_space.values():
                if isinstance(param, ConfigSpace.CategoricalHyperparameter):
                    for (offset, val) in enumerate(param.choices):
                        if config[i][j + offset] == 1:
                            df_dict[param.name].append(val)
                            break
                    j += len(param.choices)
                else:
                    val = config[i][j]
                    if isinstance(param, ConfigSpace.UniformIntegerHyperparameter):
                        val = int(val)
                    df_dict[param.name].append(val)
                    j += 1
        return pd.DataFrame(df_dict)

    def _to_1hot(self, config: Union[pd.DataFrame, pd.Series]) -> npt.NDArray:
        """
        Convert pandas DataFrame to one-hot-encoded numpy array.
        """
        n_cols = 0
        n_rows = config.shape[0] if config.ndim > 1 else 1
        for param in self.optimizer_parameter_space.values():
            if isinstance(param, ConfigSpace.CategoricalHyperparameter):
                n_cols += len(param.choices)
            else:
                n_cols += 1
        one_hot = np.zeros((n_rows, n_cols), dtype=np.float32)
        for i in range(n_rows):
            j = 0
            for param in self.optimizer_parameter_space.values():
                if config.ndim > 1:
                    assert isinstance(config, pd.DataFrame)
                    col = config.columns.get_loc(param.name)
                    assert isinstance(col, int)
                    val = config.iloc[i, col]
                else:
                    assert isinstance(config, pd.Series)
                    col = config.index.get_loc(param.name)
                    assert isinstance(col, int)
                    val = config.iloc[col]
                if isinstance(param, ConfigSpace.CategoricalHyperparameter):
                    offset = param.choices.index(val)
                    one_hot[i][j + offset] = 1
                    j += len(param.choices)
                else:
                    one_hot[i][j] = val
                    j += 1
        return one_hot
