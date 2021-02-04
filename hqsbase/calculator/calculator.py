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
"""Calculator functions handling HQS symbolic values"""
from hqsbase.calculator import CalculatorFloat, IntoCalculatorFloat
from hqsbase.calculator import CalculatorComplex, IntoCalculatorComplex


def complex_isclose(val: IntoCalculatorComplex,
                    comparison: IntoCalculatorComplex,
                    rtol: float = 1e-05,
                    atol: float = 1e-08) -> bool:
    """Complex is_close comparison of CalculatorComplexs handling real and imaginary parts.

    Args:
        val: complex value
        comparison: value that is compared to
        rtol: Relative tolerance for numpy comparison
        atol: Absolute tolerance for numpy comparison

    Returns:
        bool

    """
    value = CalculatorComplex(val)
    return value.isclose(comparison, rtol, atol)


def float_sign(val: IntoCalculatorFloat) -> CalculatorFloat:
    """Return sign of value.

    Args:
        val: float value

    Returns:
        CalculatorFloat
    """
    value = CalculatorFloat(val)
    return value.sign()


def float_atan2(a: IntoCalculatorFloat, b: IntoCalculatorFloat) -> CalculatorFloat:
    """Return atan2 of two CalculatorFloats.

    Args:
        a: first argument
        b: second argument

    Returns:
        CalculatorFloat
    """
    a_cf = CalculatorFloat(a)
    return a_cf.atan2(b)


def float_acos(val: IntoCalculatorFloat) -> CalculatorFloat:
    """Return acos of value.

    Args:
        val: float value

    Returns:
        CalculatorFloat
    """
    value = CalculatorFloat(val)
    return value.acos()


def float_sin(val: IntoCalculatorFloat) -> CalculatorFloat:
    """Return sine of value.

    Args:
        val: float value

    Returns:
        CalculatorFloat
    """
    value = CalculatorFloat(val)
    return value.sin()
