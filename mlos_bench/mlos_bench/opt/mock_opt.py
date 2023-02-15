"""
Mock optimizer for OS Autotune.
"""

import random
import logging
from typing import Tuple

from ..environment.status import Status
from ..environment.tunable import TunableGroups

from .base_opt import Optimizer

_LOG = logging.getLogger(__name__)


class MockOptimizer(Optimizer):
    """
    Mock optimizer to test the Environment API.
    """

    def __init__(self, tunables: TunableGroups, config: dict):
        super().__init__(tunables, config)
        self._best_config = None
        self._best_score = None

    _FUNC_RANDOM = {
        "categorical": lambda tunable: random.choice(tunable.categorical_values),
        "float": lambda tunable: random.uniform(*tunable.range),
        "int": lambda tunable: random.randint(*tunable.range),
    }

    def suggest(self) -> TunableGroups:
        """
        Generate the next (random) suggestion.
        """
        tunables = self._tunables.copy()
        for (tunable, _group) in tunables:
            tunable.value = self._FUNC_RANDOM[tunable.type](tunable)
        _LOG.info("Iteration %d :: Suggest: %s", self._iter, tunables)
        return tunables

    def register(self, tunables: TunableGroups, status: Status, score: float):
        _LOG.info("Iteration %d :: Register: %s = %s score: %s",
                  self._iter, tunables, status, score)
        if status == Status.SUCCEEDED and (
                self._best_score is None or score < self._best_score):
            self._best_score = score
            self._best_config = tunables.copy()
        self._iter += 1

    def get_best_observation(self) -> Tuple[float, TunableGroups]:
        return (self._best_score, self._best_config)
