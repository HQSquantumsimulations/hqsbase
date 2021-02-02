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
"""Provides general HQS config class.

Supports simple creation, saving and loading of configs
for all HQS projects

"""

from typing import Optional, KeysView, List
from typing import TypeVar, Generic, Any, Union, Dict, cast, Callable, Sequence
import importlib
import yaml
import json
import os
from copy import copy, deepcopy
from hqsbase.qonfig import (
    Empty,
    IncompleteQonfigError,
    NotQonfigurableError,
)
from hqsbase.calculator import CalculatorComplex, CalculatorFloat
import pandas as pd
import re
empty = Empty()

T = TypeVar('T')

OptionalEmpty = Union[Optional[T], Empty]


class Qonfig(Generic[T]):
    r"""General HQS config class.

    Supports simple creation, saving and loading of configs for all
    HQS python projects.

    Qonfig can be used to configure Python classes that are "aware" of Qonfig.
    These classes shoud have from_qonfig and to_qonfig methods.
    Classes need to provide a _qonfig_defaults_dict.
    The _qonfig_defaults_dict contains all keys that need to be set to initialize the calls.
    For each key _qonfig_defaults_dict contains a dict of the form:
    {'doc':..., 'default':...}, where:
    (1) doc contains the documentation of the key and can be accessed via get_doc and print_doc
        in the Qonfig.
    (2) default is the default value for the key. The special class Empty() from the Qonfig
        module signals there is no default value (needs to be set manually before to_instance).

    _requirements is a optional dict for classes that can be configured with Qonfig. Its entries
    have the form:
    key: {'requirement': lambda expression, 'doc': doc}, where:
    (1) the lambda_expression takes Qonfig[key] as an argument and returns True if the requirement
        is met.
    (2) doc documents the requirement.

    _qonfig_never_receives_values is an optional bool value for classes that can be configured with
    Qonfig. When _qonfig_never_receives_values is set to True the Qonfig will not be updated
    recursively with values from the parent Qonfig.

    Note:
        For Method docstrings see QonfigBase class.

    """

    @classmethod
    def from_dict(cls, config_dictionary: dict) -> 'Qonfig[T]':
        r"""Load a (partial) Qonfig from a dictionary.

        Args:
            config_dictionary: Dictionary version of the config

        Returns:
            Qonfig[T]

        Raises:
            ImportError: Could not find class. Try importing corresponding module
        """
        # Process qonfig_name to import class of Qonfig and raise error
        # when import fails
        spl = config_dictionary['qonfig_name'].rsplit('.', 1)
        if len(spl) == 1:
            class_type = globals().get(spl[0], None)
            if class_type is None:
                error_msg = (
                    'Could not find class {}. Try importing corresponding module'.format(spl[0]))
                raise ImportError(error_msg)
        elif len(spl) == 2:
            temporary_import = importlib.import_module(spl[0])
            class_type = getattr(temporary_import, spl[1], None)
            if class_type is None:
                error_msg = 'Could not import {}.'.format(spl)
                raise ImportError(error_msg)
        # Create new Qonfig for class
        return_config = cls(class_type)
        # Setting items in dict as items in Qonfig
        for key in [key for key in return_config.keys() if key in config_dictionary.keys()]:
            # Code path when the value of config_dictionary[key] defines a Qonfig
            if (isinstance(config_dictionary[key], dict)
                    and 'qonfig_name' in config_dictionary[key].keys()):
                try:
                    return_config[key] = Qonfig.from_dict(
                        config_dictionary[key])
                except NotQonfigurableError:
                    return_config[key] = config_dictionary[key]
            elif (isinstance(config_dictionary[key], dict)
                    and config_dictionary[key].get('is_calculator_complex', False)):
                return_config[key] = CalculatorComplex.from_pair(
                    config_dictionary[key]['real'], config_dictionary[key]['imag'])
            # Code path for list recursion if item is a list containing dicts
            # defining a Qonfig, create the Qonfigs in the list
            elif (isinstance(config_dictionary[key], list)
                  and any([(isinstance(d, dict) and ('qonfig_name' in d.keys()))
                           for d in config_dictionary[key]])):
                config_list: List[Any] = list()
                for d in config_dictionary[key]:
                    if isinstance(d, dict) and ('qonfig_name' in d.keys()):
                        try:
                            config_list.append(Qonfig.from_dict(d))
                        except NotQonfigurableError:
                            config_list.append(d)
                    elif isinstance(d, dict) and d.get('is_calculator_complex', False):
                        config_list.append(CalculatorComplex.from_pair(d['real'], d['imag']))
                    else:
                        config_list.append(d)
                return_config[key] = config_list
            elif config_dictionary[key] == "<empty 'Empty'>":
                return_config[key] = empty
            else:
                return_config[key] = config_dictionary[key]
        return return_config

    @classmethod
    def load_yaml(cls, filename: str) -> 'Qonfig[T]':
        r"""Load a (partial) Qonfig from a yaml file.

        Args:
            filename: location of yaml file

        Returns:
            Qonfig[T]
        """
        with open(filename, 'r') as infile:
            loaded = cls.from_yaml(infile.read())  # NOQA
        return loaded

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'Qonfig[T]':
        r"""Load a (partial) Qonfig from a yaml file.

        Args:
            yaml_str: yaml in string form

        Returns:
            Qonfig[T]
        """
        loaded = yaml.load(yaml_str, Loader=yaml.FullLoader)  # NOQA
        return cls.from_dict(loaded)

    @classmethod
    def load_json(cls, filename: str) -> 'Qonfig[T]':
        r"""Load a (partial) Qonfig from a json file.

        Args:
            filename: location of json file

        Returns:
            Qonfig[T]
        """
        with open(filename, 'r') as infile:
            loaded = cls.from_json(infile.read())
        return loaded

    @classmethod
    def from_json(cls, json_str: str) -> 'Qonfig[T]':
        r"""Load a (partial) Qonfig from a json file.

        Args:
            json_str: json in string form

        Returns:
            Qonfig[T]
        """
        loaded = json.loads(json_str)
        return cls.from_dict(loaded)

    def __init__(self, class_type: type,
                 *args,
                 parent: Optional["Qonfig"] = None,
                 receives_values: bool = True,
                 **kwargs) -> None:
        """Initialize Qonfig class.

        Args:
            class_type: The Python class for which we want to create a config object
            parent: The parent Qonfig node in the tree structure of the complete Qonfig
            receives_values: If True, a value set in the Qonfig parent will be propagated
                             recursively to this Qonfig and all its child Qonfigs
            args: Additional positional arguments
            kwargs: Additional keyword arguments

        Raises:
            NotQonfigurableError: Class can not be configured
        """
        self._values: Dict[str, Any] = dict()
        self._defaults: Dict[str, Any] = dict()
        self._docs: Dict[str, Any] = dict()
        self._requirements: Dict[str, Any] = dict()
        self._parent: "Optional[Qonfig]" = parent
        self._receives_values = receives_values
        self._class_type = class_type
        self._class_name = class_type.__name__
        self._class_module = class_type.__module__
        if self._class_module != '__main__':
            self._qonfig_name = '{}.{}'.format(self._class_module, self._class_name)
        else:
            self._qonfig_name = '{}'.format(self._class_name)

        if hasattr(self._class_type, '_qonfig_defaults_dict'):
            self._config_aware_class_init()
        else:
            raise NotQonfigurableError(class_type=class_type)

    # Methods that make class dict()-like

    def __eq__(self, other: object) -> bool:
        """Return True when self and other are equal.

        Args:
            other: Other object the Qonfig is compared to

        Returns:
            bool
        """
        if not isinstance(other, self.__class__):
            return False
        if self._class_type is not other._class_type:
            return False
        return self._values == other._values

    def __repr__(self) -> str:
        """Return unique representation of Qonfig.

        Returns:
            str
        """
        string = json.dumps(
            self.to_dict(enforce_yaml_compatible=True),
            ensure_ascii=False, indent=2)
        return string

    def __str__(self) -> str:
        """Return string representation of Qonfig.

        Returns:
            str
        """
        string = 'Qonfig[{}]'.format(self._qonfig_name)
        return string

    def __getitem__(self, key: str) -> Any:
        """Implement getitem magic method for Qonfig.

        Args:
            key: Key of the requested value

        Returns:
            value (Any): Value for the key

        Raises:
            KeyError: Key not in Qonfig keys
            TypeError: Qonfig only supports str keys
        """
        if type(key) is not str:
            raise TypeError("Qonfig only supports str keys")
        if key in ['name', 'qonfig_name']:
            return self._qonfig_name
        if key not in self._values.keys():
            raise KeyError("Key {} not in Qonfig keys".format(key))
        return self._values[key]

    def __copy__(self) -> "Qonfig[T]":
        """Implement copy operation.

        Returns:
            Qonfig[T]
        """
        return_instance: "Qonfig[T]" = Qonfig(class_type=self._class_type,
                                              parent=self.parent)
        for key in self.keys():
            if (hasattr(self._values[key], '__iter__')
                and any([isinstance(subval, Qonfig)
                         for subval in self._values[key]])):
                tmp_list = list()
                for _, subval in enumerate(self._values[key]):
                    tmp_list.append(copy(subval))
                return_instance._values[key] = tmp_list
            else:
                return_instance._values[key] = copy(self[key])

        return return_instance

    def __deepcopy__(self, memodict: Optional[dict] = None) -> "Qonfig[T]":
        """Implement deepcopy operation.

        Args:
            memodict: Memodict used by Python's deepcopy mechanisms

        Returns:
            Qonfig[T]
        """
        if memodict is None:
            memodict = dict()
        return_instance: "Qonfig[T]" = Qonfig(class_type=self._class_type,
                                              parent=None)
        for key in self.keys():
            if (hasattr(self._values[key], '__iter__')
                and any([isinstance(subval, Qonfig)
                         for subval in self._values[key]])):
                tmp_list = list()
                for _, subval in enumerate(self._values[key]):
                    tmp_list.append(deepcopy(subval, memodict))
                return_instance._values[key] = tmp_list
            else:
                return_instance._values[key] = deepcopy(self[key], memodict)
        return return_instance

    def __setitem__(self, key: str, value: Any) -> None:
        """Implement setitem magic method for Qonfig.

        Args:
            key: Key of value that is set
            value: New value

        Raises:
            TypeError: Qonfig only supports str keys
        """
        if type(key) is not str:
            raise TypeError("Qonfig only supports str keys")
        if key not in self.keys():
            self.propagate_value(key, value)
        else:
            self._values[key] = copy(value)
            if isinstance(value, Qonfig):
                self._values[key].parent = self
            elif (hasattr(self._values[key], '__iter__')
                  and any([isinstance(subval, Qonfig)
                           for subval in self._values[key]])):
                for subval in [sv for sv in self._values[key] if isinstance(sv, Qonfig)]:
                    subval.parent = self
            if self._receives_values:
                self.propagate_value(key, copy(value))

    def keys(self) -> KeysView[str]:
        """Return str keys of the Qonfig.

        Returns:
            KeysView[str]
        """
        return self._defaults.keys()

    def get(self, key: str, *args) -> Any:
        """Implement dict-like get function.

        This returns self[key] for key in keys and default otherwise.

        Args:
            key: key of the returned value
            args: Optional positional arguments, maximum length 1
                  If not empty first value will be returned as defaults
                  when key not in keys

        Returns:
            value (Any)

        Raises:
            KeyError: Key not in Qonfig keys
        """
        if (key in self._values.keys()):
            return self._values[key]
        elif len(args) == 1:
            return args[0]
        else:
            raise KeyError("Key {} not in Qonfig keys".format(key))

    def print_doc(self, key: str) -> None:
        """Print the documentation for a certain Qonfig key.

        Args:
            key: key of the printed value
        """
        print(self.get_doc(key))

    def get_doc(self, key: str) -> str:
        """Get the documentation for a certain Qonfig key.

        Args:
            key: key of the returned value

        Returns:
            str
        """
        return self._docs[key]

    def _ipython_key_completions_(self) -> List[str]:
        """Implement autocomplete of key access when in iPython mode.

        Returns:
            List[str]
        """
        return list(self._values.keys())

    @property
    def qonfig_name(self) -> str:
        r"""Special property qonfig_name getter.

        This is not set dynamically and has special behaviour for Qonfig of an abstract class.

        Setter:
            value (str): New qonfig_name

        Returns:
            str
        """
        return self._qonfig_name

    @property
    def parent(self) -> Optional["Qonfig"]:
        """The parent Qonfig node in the tree structure of the complete Qonfig.

        Setter:
            value (Optional[Qonfig]): New value of parent

        Returns:
            Optional[Qonfig]
        """
        return self._parent

    @parent.setter
    def parent(self, value: Optional["Qonfig"]) -> None:
        if isinstance(value, Qonfig) or value is None:
            self._parent = value
        else:
            raise TypeError(
                'Only a Qonfig can be the parent of a Qonfig')

    @property
    def root(self) -> "Qonfig":
        """The root Qonfig of the Qonfig tree.

        Returns:
            Optional[Qonfig]
        """
        if self.parent is None:
            return self
        return self.parent.root

    @property
    def receives_values(self) -> bool:
        """If True, values will be propagated along Qonfig tree.

        A value set in the Qonfig parent will be propagated recursively
        to this Qonfig and all its child Qonfigs.

        Setter:
            value (bool): New value of receives_values

        Returns:
            bool
        """
        return self._receives_values and not self._never_receives_values

    @receives_values.setter
    def receives_values(self, value: bool) -> None:
        self._receives_values = bool(value)

    def to_instance(self, no_copy: bool = False) -> T:
        """Return Instance of class configured in the Qonfig.

        Args:
            no_copy: Don't copy elements in Qonfig on instance creation
                     (Use when a reference to an object should be passed
                     instead of a copy of the object)

        Returns:
            instance (T): Instance of the python class configured by Qonfig

        Raises:
            IncompleteQonfigError: Incomplete Qonfig can not create a class
            NotQonfigurableError: Class can not be configured
        """
        if self.is_valid is True:
            init_function = cast(Callable, getattr(self._class_type, 'from_qonfig', None))
            if init_function is None:
                raise NotQonfigurableError()
            if no_copy or self._never_receives_values:
                return init_function(config=self)
            else:
                return init_function(config=copy(self))

        else:
            raise IncompleteQonfigError("Incomplete Qonfig can not create a class")

    def _config_aware_class_init(self) -> None:
        r"""Initialize class that can be configured with Qonfig.

        Raises:
            NotQonfigurableError: Class can not be configured
        """
        # Set special keys 'qonfig_name' and 'type'
        class_qonfig_defaults_dict = cast(Dict[str, Dict[str, Any]], getattr(
            self._class_type, '_qonfig_defaults_dict', None))
        class_requirements = cast(Dict[str, Any], getattr(self._class_type, '_requirements', None))
        self._never_receives_values = getattr(
            self._class_type, '_qonfig_never_receives_values', False)
        defaults_dict: Dict[str, Any] = dict()
        if class_qonfig_defaults_dict is None:
            raise NotQonfigurableError()
        for key in class_qonfig_defaults_dict.keys():
            self._docs[key] = class_qonfig_defaults_dict[key]['doc']
            self._defaults[key] = empty
            defaults_dict[key] = class_qonfig_defaults_dict[key]['default']
        if class_requirements is not None:
            for key in class_requirements.keys():
                self._requirements[key] = copy(class_requirements[key])
        self._populate_defaults_from_dict_like(dict_like=defaults_dict)
        self._populate_values_from_defaults()

    def _populate_values_from_defaults(self) -> None:
        for key in self._defaults.keys():
            self._values[key] = self._defaults[key]
        if not self._never_receives_values:
            self.propagate_all()

    def _populate_defaults_from_dict_like(self,
                                          dict_like: Dict[str, Any]) -> None:
        for key in self.keys():
            if (isinstance(dict_like[key], dict)
                    and ('qonfig_name' in dict_like[key].keys())):
                try:
                    self._defaults[key] = Qonfig.from_dict(dict_like[key])
                except NotQonfigurableError:
                    self._defaults[key] = copy(dict_like[key])
            elif (isinstance(dict_like[key], list)
                    and any([(isinstance(d, dict) and ('qonfig_name' in d.keys()))
                             for d in dict_like[key]])):
                config_list: List[Any] = list()
                for d in dict_like[key]:
                    if isinstance(d, dict) and ('qonfig_name' in d.keys()):
                        try:
                            config_list.append(Qonfig.from_dict(d))
                        except NotQonfigurableError:
                            config_list.append(d)
                    else:
                        config_list.append(d)
                self._defaults[key] = config_list
            else:
                self._defaults[key] = copy(dict_like[key])

    def propagate_value(self, key: str, value: Any) -> None:
        r"""Propagate a key value pair recursively.

        Propagate to all Qonfig instances that are part of the Qonfig instance self.

        Args:
            key: Key of the value that is set
            value: Value that is set
        """
        for k in self.keys():
            if (isinstance(self._values[k], Qonfig)
                    and self._values[k].receives_values is True):
                if key in self._values[k].keys():
                    self._values[k][key] = value
                self._values[k].propagate_value(key, value)
            elif (hasattr(self._values[k], '__iter__')
                  and any([isinstance(subval, Qonfig)
                           for subval in self._values[k]])):
                for subval in [subval for subval in self._values[k]
                               if isinstance(subval, Qonfig)]:
                    if subval.receives_values and key in subval.keys():
                        subval[key] = value
                    subval.propagate_value(key, value)

    def _propagate_overwrites(self, key: str, specific_class: type, value: Any) -> None:
        r"""Propagate overwrite values.

        Function that propagates class specific overwrites along the Qonfig tree.
        It can overwrite the value of the Qonfig of specific classes compared, deviating
        from the normal value propagated down the tree.
        Standard use case: An attibute of one class needs to default to None, but
        for some use cases an attibute with the same qonfig_name of another class is actually
        set in the Qonfig.

        Args:
            key: the key that is set
            specific_class: The class for which the key is set, all other classes are
                not affected
            value: The value that is set

        Warning:
            Normally this function is only used by Qonfig internally and should
            not be needed otherwise. Only use when you know what you are doing.
        """
        for k in self.keys():
            if (isinstance(self._values[k], Qonfig)
                    and self._values[k].receives_values is True
                    and issubclass(self._values[k]._class_type, specific_class)):
                if key in self._values[k].keys():
                    self._values[k][key] = value
                self._values[k]._propagate_overwrites(key, specific_class, value)
            elif (hasattr(self._values[k], '__iter__')
                  and any([isinstance(subval, Qonfig)
                           for subval in self._values[k]])):
                for subval in [subval for subval in self._values[k]
                               if isinstance(subval, Qonfig)]:
                    if subval.receives_values and issubclass(subval._class_type, specific_class):
                        if key in subval.keys():
                            subval[key] = value
                        subval._propagate_overwrites(key, specific_class, value)

    def propagate_all(self) -> None:
        r"""Propagate all values.

        Function that propagates all values in the Qonfig and all
        class specific defaults along the Qonfig.
        """
        if not self._never_receives_values:
            for k in self.keys():
                self.propagate_value(k, self._values[k])

    @property
    def is_complete(self) -> bool:
        """True when all values in the Qonfig are set.

        Returns:
            bool
        """
        complete = True
        if not self._never_receives_values:
            for key in self.keys():
                if isinstance(self._values[key], Empty):
                    complete = False
                if (isinstance(self._values[key], Qonfig)
                        and self._values[key].is_complete is False):
                    complete = False
                elif(hasattr(self._values[key], '__iter__')
                     and any([isinstance(subval, Qonfig)
                              for subval in self._values[key]])):
                    for subval in [sv for sv in self._values[key] if isinstance(sv, Qonfig)]:
                        if subval.is_complete is False:
                            complete = False
                            break
                if complete is False:
                    break
        return complete

    @property
    def meets_requirements(self) -> bool:
        """True when Qonfig values meet all requirements defined in class.

        Returns:
            bool
        """
        requ = True
        if not self._never_receives_values:
            for key in self.keys():
                if (isinstance(self._values[key], Qonfig)
                        and self._values[key].meets_requirements is False):
                    requ = False
                elif(hasattr(self._values[key], '__iter__')
                     and any([isinstance(subval, Qonfig)
                              for subval in self._values[key]])):
                    for subval in [sv for sv in self._values[key] if isinstance(sv, Qonfig)]:
                        if subval.meets_requirements is False:
                            requ = False
                            break
                if requ is False:
                    break
            for key in self._requirements.keys():
                if requ is False:
                    break
                requ = self._requirements[key]['requirement'](self)
        return requ

    @property
    def is_valid(self) -> bool:
        """Is valid when Qonfig is complete and meets all requirements.

        Returns:
            bool
        """
        valid = self.is_complete and self.meets_requirements
        return valid

    @property
    def violated_requirements(self) -> dict:
        """Return recursive list of requirements that are not met in the Qonfig tree.

        Returns:
            dict
        """
        violated_requirements = dict()
        if not self._never_receives_values:
            for key in self.keys():
                if (isinstance(self._values[key], Qonfig)
                        and self._values[key].meets_requirements is False):
                    violated_requirements[key] = self._values[key].violated_requirements
                elif (hasattr(self._values[key], '__iter__')
                      and any([isinstance(subval, Qonfig)
                               for subval in self._values[key]])):
                    for cs, subval in enumerate(
                            [sv for sv in self._values[key] if isinstance(sv, Qonfig)]):
                        if (subval.meets_requirements is False):
                            violated_requirements['{}_{}'.format(key, cs)] = (
                                subval.violated_requirements)
            for key in self._requirements.keys():
                if self._requirements[key]['requirement'](self) is False:
                    violated_requirements[key] = self._requirements[key]['doc']
        return violated_requirements

    @property
    def missing_values(self) -> dict:
        """Return a recursive list of keys of missing values.

        Returns:
            dict
        """
        missing_dict: Dict[str, Any] = dict()
        if not self._never_receives_values:
            for key in self.keys():
                if isinstance(self._values[key], Empty):
                    missing_dict[key] = key
                if (isinstance(self._values[key], Qonfig)
                        and self._values[key].is_complete is False):
                    missing_dict[key] = self._values[key].missing_values
                elif (hasattr(self._values[key], '__iter__')
                      and any([isinstance(subval, Qonfig)
                               for subval in self._values[key]])):
                    for cs, subval in enumerate(self._values[key]):
                        if (isinstance(subval, Qonfig) and subval.is_complete is False):
                            missing_dict['{}_{}'.format(key, cs)] = (
                                subval.missing_values)
                        else:
                            missing_dict['{}_{}'.format(key, cs)] = '{}_{}'.format(key, cs)
        return missing_dict

    def to_dict(self, enforce_yaml_compatible: bool = False) -> Dict[str, Any]:
        r"""Return the current (partial) configuration in dictionary format.

        Args:
            enforce_yaml_compatible: Make sure all dict entries can be dumped to
                                     yaml even if they can't be reconstructed (default False)

        Returns:
            Dict[str, Any]
        """
        return_dict: Dict[str, Any]
        return_dict = dict()
        return_dict['qonfig_name'] = str(self._qonfig_name)
        for key in self.keys():
            if isinstance(self._values[key], Qonfig):
                return_dict[key] = self._values[key].to_dict(enforce_yaml_compatible)
            elif (hasattr(self._values[key], '__iter__')
                  and any([isinstance(subval, Qonfig)
                           for subval in self._values[key]])):
                tmp_list = list()
                for _, subval in enumerate(self._values[key]):
                    if isinstance(subval, Qonfig):
                        tmp_list.append(subval.to_dict(enforce_yaml_compatible))
                    else:
                        tmp_list.append(subval)
                return_dict[key] = tmp_list
            elif isinstance(self._values[key], Empty):
                return_dict[key] = repr(empty)
            else:
                if enforce_yaml_compatible:
                    return_dict[key] = enforce_yaml(copy(self._values[key]))
                else:
                    return_dict[key] = copy(self._values[key])
        return return_dict

    def save_to_yaml(self, filename: str, overwrite: bool = False) -> None:
        r"""Save the current (partial) configuration in yaml form.

        Args:
            filename: Location of yaml file
            overwrite: Overwrite yaml file if it already exits (default False)

        Raises:
            IOError: File already exists
        """
        file_name = os.path.expanduser(filename)
        if not (file_name.endswith('.yaml') or file_name.endswith('.yml')):
            file_name += ".yaml"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        if not os.path.exists(file_name):
            with open(file_name, 'w') as outfile:
                outfile.write(self.to_yaml())
        elif overwrite is True:
            with open(file_name, 'w') as outfile:
                outfile.write(self.to_yaml())
        else:
            raise IOError("File {} already exists".format(file_name))

    def to_yaml(self) -> str:
        r"""Return the current (partial) configuration in yaml form.

        Returns:
            str
        """
        return yaml.dump(
            self.to_dict(enforce_yaml_compatible=True),
            default_flow_style=False, allow_unicode=True)

    def save_to_json(self, filename: str, overwrite: bool = False,
                     indent: Optional[int] = 2) -> None:
        r"""Save the current (partial) configuration in json form.

        Args:
            filename: Location of json file
            overwrite: Overwrite json file if it already exits (default False)
            indent: The indent of the json output, default 2, set to None for most
                    compact (memory efficient) representation

        Raises:
            IOError: File already exists
        """
        file_name = os.path.expanduser(filename)
        if not (file_name.endswith('.json')):
            file_name += ".json"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        if not os.path.exists(file_name):
            with open(file_name, 'w') as outfile:
                outfile.write(self.to_json(indent=indent))
        elif overwrite is True:
            with open(file_name, 'w') as outfile:
                outfile.write(self.to_json(indent=indent))
        else:
            raise IOError("File {} already exists".format(file_name))

    def to_json(self,
                indent: Optional[int] = 2) -> str:
        r"""Return the current (partial) configuration in json form.

        Args:
            indent: The indent of the json output, default 2, set to None for most
                    compact (memory efficient) representation

        Returns:
            str
        """
        return json.dumps(
            self.to_dict(enforce_yaml_compatible=True),
            indent=indent, ensure_ascii=False)

    def to_pd_series(self, valid_check: bool = True,
                     excluded_keys: Optional[Sequence[str]] = None,
                     enforce_yaml_compatible: bool = True) -> pd.Series:
        r"""Return the current configuration in dictionary format

        Args:
            valid_check: Do not return pandas.Series if Qonfig is not valid
            excluded_keys: List of keys not included in pd.Series.
                           Accepts Python regular expressions as excluded key wildcards
            enforce_yaml_compatible: Make sure all dict entries can be dumped to
                                     yaml even if they can't be reconstructed (default False)

        Returns:
            series (pd.Series): Pandas series representation

        Raises:
            IncompleteQonfigError: Incomplete Qonfigs can not be exported to pd.Series
        """
        if excluded_keys is None:
            excluded_keys = list()
        if self.is_valid is False and valid_check is True:
            raise IncompleteQonfigError("Incomplete Qonfigs can not be exported to pd.Series")
        series = pd.Series()
        series['qonfig_name'] = str(self.qonfig_name)
        for key in self.keys():
            if any(re.fullmatch(excluded, key) is not None for excluded in excluded_keys):
                continue
            if isinstance(self._values[key], Qonfig):
                subseries = self._values[key].to_pd_series(
                    valid_check,
                    excluded_keys,
                    enforce_yaml_compatible)
                subseries = subseries.add_prefix(key + '_')
                series = series.append(subseries)
            elif (hasattr(self._values[key], '__iter__')
                  and all([isinstance(subval, Qonfig)
                           for subval in self._values[key]])):
                for cs, subval in enumerate(self._values[key]):
                    subseries = subval.to_pd_series(
                        valid_check,
                        excluded_keys,
                        enforce_yaml_compatible)
                    subseries = subseries.add_prefix('{}_{}_'.format(key, cs))
                    series = series.append(subseries)
            else:
                if enforce_yaml_compatible:
                    series[key] = enforce_yaml(copy(self._values[key]))
                else:
                    series[key] = copy(self._values[key])
        for key in series.keys():
            if any(re.fullmatch(excluded, key) is not None for excluded in excluded_keys):
                del series[key]
        return series


def enforce_yaml(value: Any) -> Union[Empty, dict, list, tuple, None, str]:
    """Convert value to yaml compatible form.

    Args:
        value: Value that is cast to yaml compatible form

    Returns:
        Union[empty, dict, list, tuple]
    """
    if hasattr(value, 'keys') and hasattr(value, '__getitem__'):
        return_dict = dict()
        for key in value.keys():
            return_dict[key] = enforce_yaml(value[key])
        return return_dict
    elif isinstance(value, list):
        return_list = list()
        for subval in value:
            return_list.append(enforce_yaml(subval))
        return return_list
    elif isinstance(value, tuple):
        return_list = list()
        for subval in value:
            return_list.append(enforce_yaml(subval))
        return tuple(return_list)
    elif value.__class__.__module__ == 'builtins':
        return value
    elif value.__class__.__module__ == 'numpy':
        return value.tolist()
    elif value is None:
        return None
    elif isinstance(value, CalculatorComplex):
        return value.to_dict()
    elif isinstance(value, CalculatorFloat):
        return value.value
    else:
        return repr(empty)
