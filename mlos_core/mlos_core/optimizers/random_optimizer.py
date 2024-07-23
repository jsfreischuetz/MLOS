#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
#
"""Contains the RandomOptimizer class."""

from typing import Optional, Tuple
from warnings import warn

import pandas as pd

from mlos_core.optimizers.observations import Observation, Suggestion
from mlos_core.optimizers.optimizer import BaseOptimizer


class RandomOptimizer(BaseOptimizer):
    """
    Optimizer class that produces random suggestions. Useful for baseline comparison
    against Bayesian optimizers.

    Parameters
    ----------
    parameter_space : ConfigSpace.ConfigurationSpace
        The parameter space to optimize.
    """

    def _register(self, *, observation: Observation) -> None:
        """
        Registers the given configs and scores.

        Doesn't do anything on the RandomOptimizer except storing configs for logging.

        Parameters
        ----------
        configs : pd.DataFrame
            Dataframe of configs / parameters. The columns are parameter names and
            the rows are the configs.

        scores : pd.DataFrame
            Scores from running the configs. The index is the same as the index of the configs.

        context : None
            Not Yet Implemented.

        metadata : None
            Not Yet Implemented.
        """
        if observation.context is not None:
            warn(
                f"Not Implemented: Ignoring context {list(observation.context.columns)}",
                UserWarning,
            )
        if observation.metadata is not None:
            warn(
                f"Not Implemented: Ignoring context {list(observation.metadata.columns)}",
                UserWarning,
            )
        # should we pop them from self.pending_observations?

    def _suggest(
        self,
        *,
        context: Optional[pd.DataFrame] = None,
    ) -> Suggestion:
        """
        Suggests a new configuration.

        Sampled at random using ConfigSpace.

        Parameters
        ----------
        context : None
            Not Yet Implemented.

        Returns
        -------
        suggestion: Suggestion
            The suggestion to evaluate.
        """
        if context is not None:
            # not sure how that works here?
            warn(f"Not Implemented: Ignoring context {list(context.columns)}", UserWarning)
        return Suggestion(
            config=pd.DataFrame(
                dict(self.optimizer_parameter_space.sample_configuration()), index=[0]
            ),
            context=context,
            metadata=None,
        )

    def register_pending(self, *, pending: Suggestion) -> None:
        raise NotImplementedError()
        # self._pending_observations.append((configs, context))
