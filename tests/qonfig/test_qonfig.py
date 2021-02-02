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
"""Test Qonfig for configuring Python classes"""
import pytest
import sys
import numpy as np
import cmath
import hqsbase
from hqsbase.calculator import (
    CalculatorFloat,
    CalculatorComplex
)
from typing import Optional
from hqsbase import qonfig
from hqsbase.qonfig import Qonfig
import yaml


class unrelated_class(object):
    pass


class simple_class_aware(object):

    _qonfig_defaults_dict = {
        'key1': {'doc': 'documentation for key1', 'default': CalculatorFloat(1)},
        'key2': {'doc': 'documentation for key2', 'default': CalculatorComplex(1j)},
    }

    def __init__(self, key1=CalculatorFloat(1), key2=CalculatorComplex(1j)) -> None:
        """Initialize simple_class_aware class

        Args:
            key1: documentation for key1
            key2: documentation for key2
        """
        self.key1 = CalculatorFloat(key1)
        self.key2 = CalculatorComplex(key2)

    @classmethod
    def from_qonfig(cls, config: Qonfig['simple_class_aware']) -> 'simple_class_aware':
        return cls(key1=config['key1'], key2=config['key2'])

    def to_qonfig(self) -> 'Qonfig[simple_class_aware]':
        config: Qonfig['simple_class_aware'] = Qonfig(self.__class__)
        config['key1'] = self.key1
        config['key2'] = self.key2
        return config


class no_propagation_class_aware(object):

    _qonfig_defaults_dict = {
        'key1': {'doc': 'documentation for key1', 'default': CalculatorFloat(1)},
        'key2': {'doc': 'documentation for key2', 'default': CalculatorComplex(1j)},
    }
    _qonfig_never_receives_values = True

    def __init__(self, key1=CalculatorFloat(1), key2=CalculatorComplex(1j)) -> None:
        """Initialize no_propagation_class_aware class

        Args:
            key1: documentation for key1
            key2: documentation for key2
        """
        self.key1 = CalculatorFloat(key1)
        self.key2 = CalculatorComplex(key2)

    @classmethod
    def from_qonfig(cls, config: Qonfig['simple_class_aware']) -> 'no_propagation_class_aware':
        return cls(key1=config['key1'], key2=config['key2'])

    def to_qonfig(self) -> 'Qonfig[no_propagation_class_aware]':
        config: Qonfig['no_propagation_class_aware'] = Qonfig(self.__class__)
        config['key1'] = self.key1
        config['key2'] = self.key2
        return config


class class_aware(object):

    _qonfig_defaults_dict = {
        'super_key1': {'doc': 'documentation for simple class aware', 'default': Qonfig(simple_class_aware)},
        'key2': {'doc': 'documentation for key2', 'default': qonfig.empty},
        'key3': {'doc': 'documentation for key3', 'default': 'test'},
    }
    _requirements = {
        'super_key1': {'requirement': lambda x: x['super_key1']['key1'] == 3,
                       'doc': "It is required that super_key1['key1'] is 3 "},
    }

    def __init__(self, super_key1, key2, key3, **kwargs):
        """Initialize no_propagation_class_aware class

        Args:
            super_key1: documentation for super_key1
            key2: documentation for key2
            key3: documentation for key3
            kwargs: Additional keyword arguments
        """
        self.super_key1 = super_key1
        self.key2 = key2
        self.key3 = key3

    @classmethod
    def from_qonfig(cls, config: Qonfig['class_aware']) -> 'class_aware':
        return cls(super_key1=config['super_key1'], key2=config['key2'], key3=config['key3'])

    def to_qonfig(self) -> 'Qonfig[class_aware]':
        config: Qonfig['class_aware'] = Qonfig(self.__class__)
        config['super_key1'] = self.super_key1
        config['key2'] = self.key2
        config['key3'] = self.key2
        return config


def test_simple_aware_init():
    config = Qonfig(simple_class_aware)
    assert config['name'] == 'test_qonfig.simple_class_aware'
    assert config.qonfig_name == 'test_qonfig.simple_class_aware'
    assert config['key1'] == 1
    assert config['key2'] == 1j
    instance = config.to_instance()
    assert instance.key1 == 1
    assert instance.key2 == 1j
    instance.key1 = 2
    instance.key2 = CalculatorComplex(2j)
    config2 = instance.to_qonfig()
    assert config2['name'] == 'test_qonfig.simple_class_aware'
    assert config2.qonfig_name == 'test_qonfig.simple_class_aware'
    assert config2['key1'] == 2
    assert config2['key2'] == 2j


def test_simple_aware_failing():
    config = Qonfig(simple_class_aware)
    with pytest.raises(KeyError):
        a = config['key3']
    config['key1'] = qonfig.empty
    with pytest.raises(qonfig.IncompleteQonfigError):
        config.to_instance()
    assert config.missing_values == {'key1': 'key1'}
    with pytest.raises(qonfig.NotQonfigurableError):
        config2 = Qonfig(unrelated_class)


def test_simple_to_dict():
    config = Qonfig(simple_class_aware)
    simple_dict = {'qonfig_name': 'test_qonfig.simple_class_aware',
                   'key1': CalculatorFloat(1), 'key2': CalculatorComplex(1j)}
    assert simple_dict == config.to_dict()


def test_simple_doc():
    config = Qonfig(simple_class_aware)
    assert config.get_doc('key1') == 'documentation for key1'
    assert config.get_doc('key2') == 'documentation for key2'


def test_simple_yaml():
    config = Qonfig(simple_class_aware)
    simple_dict = {'qonfig_name': 'test_qonfig.simple_class_aware',
                   'key1': 1, 'key2': {'is_calculator_complex': True, 'real': 0, 'imag': 1}}
    simple_yaml = "key1: 1.0\nkey2:\n  imag: 1.0\n  is_calculator_complex: true\n  real: 0.0\nqonfig_name: test_qonfig.simple_class_aware\n"
    assert simple_dict == config.to_dict(enforce_yaml_compatible=True)
    test_yaml = yaml.dump(
        config.to_dict(enforce_yaml_compatible=True), default_flow_style=False, allow_unicode=True)
    assert test_yaml == simple_yaml
    config2 = Qonfig.from_dict(simple_dict)
    assert config == config2


def test_aware_serialisation_yaml():
    config = Qonfig(class_aware)
    config['key1'] = 3
    yaml_str = config.to_yaml()
    config2 = Qonfig.from_yaml(yaml_str)
    assert config == config2


def test_aware_serialisation_json():
    config = Qonfig(class_aware)
    config['key1'] = 3
    json_str = config.to_json()
    config2 = Qonfig.from_json(json_str)
    assert config == config2


def test_aware_init():
    config = Qonfig(class_aware)
    assert config['name'] == 'test_qonfig.class_aware'
    assert not config.is_valid
    assert not config.is_complete
    assert not config.meets_requirements
    assert config.violated_requirements == {'super_key1': "It is required that super_key1['key1'] is 3 "}
    config['key2'] = CalculatorComplex(10j)
    assert not config.is_valid
    assert config.is_complete
    assert config['super_key1']['key2'] == 10j
    # test propagation
    config['key1'] = 3
    assert config['super_key1']['key1'] == 3
    assert config.is_valid


def test_aware_do_dict():
    config = Qonfig(class_aware)
    config['key1'] = 3
    simple_dict = {
        'qonfig_name': 'test_qonfig.class_aware',
        'super_key1': {
            'key1': 3,
            'key2': "<empty 'Empty'>",
            'qonfig_name': 'test_qonfig.simple_class_aware',
        },
        'key2': "<empty 'Empty'>",
        'key3': 'test'
    }
    test_dict = config.to_dict(enforce_yaml_compatible=True)
    assert test_dict == simple_dict
    config2 = Qonfig.from_dict(test_dict)
    assert config == config2


def test_no_propagation():
    config = Qonfig(class_aware)
    config['super_key1'] = Qonfig(no_propagation_class_aware)
    assert config['super_key1']['key2'] == 1j
    config['key2'] = 3
    assert config['key2'] == 3
    assert config['super_key1']['key2'] == 1j


if __name__ == "__main__":
    pytest.main(sys.argv)
