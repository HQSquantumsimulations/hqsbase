# Copyright © 2019-2021 HQS Quantum Simulations GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.
"""Calculator

.. autosummary::
    :toctree: generated/

    CalculatorFloat
    CalculatorComplex
    Calculator
    float_atan2
    float_sign
    float_acos
    float_sin
    complex_isclose
    parse_string

"""

from typing import Union

from qoqo_calculator_pyo3 import (
    parse_string,
    Calculator
)

from qoqo_calculator_pyo3 import (
    CalculatorFloat,
)

from qoqo_calculator_pyo3 import (
    CalculatorComplex,
)
IntoCalculatorFloat = Union[str, float, CalculatorFloat]

IntoCalculatorComplex = Union[complex, CalculatorComplex]

# Ignoring one lint here to avoid cyclic import
from .calculator import (  # noqa: E402
    complex_isclose,
    float_atan2,
    float_sign,
    float_acos,
    float_sin
)
