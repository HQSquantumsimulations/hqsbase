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
"""Testing Calculator class"""
import pytest
import sys
import numpy as np
import numpy.testing as npt
from hqsbase import calculator


@pytest.mark.parametrize("initial", [
    (1, 1, ),
    ('a', 'sign(a)'),
    (-1, -1,),
    (2, 1, ),
    (-3, -1,),
    (0, 1, ),
])
def test_float_sign(initial):
    t = calculator.float_sign(initial[0])
    assert t == initial[1]


@pytest.mark.parametrize("initial", [
    (0, np.pi/2),
    (1, 0),
    (-1, np.pi,),
    ('a', 'acos(a)', ),
])
def test_float_acos(initial):
    t = calculator.float_acos(initial[0])
    assert t.isclose(initial[1])


if __name__ == '__main__':
    pytest.main(sys.argv)
