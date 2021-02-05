"""Setup file for HQSBase"""
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
from setuptools import find_packages, setup
import os
path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(path, 'README.md')) as file:
    readme = file.read()

# obtain current version
__version__ = None
with open(os.path.join(path, 'hqsbase/__version__.py')) as f:
    lines = f.readlines()
__version__ = lines[-1].strip().split("'")[1].strip()

License = 'Apache-2.0'

install_requires = [
    'h5py',
    'pandas',
    'pytest',
    'tables',
    'pyyaml',
    'qoqo_calculator_pyo3>=0.1.5'
]

setup(name='hqsbase',
      description='HQS base utility package',
      version=__version__,
      long_description=readme,
      packages=find_packages(exclude=('docs')),
      author='HQS Quantum Simulations GmbH',
      author_email='info@quantumsimulations.de',
      url='https://quantumsimulations.de',
      license=License,
      install_requires=install_requires,
      )
