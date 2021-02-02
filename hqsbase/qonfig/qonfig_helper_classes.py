"""Helper Classes for Qonfig.

Provides classes that hold special meaning when used as values in one
of the internal dicts of the Qonfig class
"""
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

from typing import Optional, Sequence


class IncompleteQonfigError(Exception):
    """Special Error for incomplete qonfig"""

    def __init__(self, message: str,
                 class_type: Optional[type] = None,
                 missing_values: Optional[Sequence[str]] = None) -> None:
        r"""Initialize IncompleteQonfigError.

        Args:
            message: Error message
            class_type: Type of the class configured by qonfig raising exception
            missing_values: Values missing from qonfig
        """
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.class_type = class_type
        self.missing_values = missing_values


class NotQonfigurableError(Exception):
    """Special Error for creating a qonfig for a class that is not qonfig aware"""

    def __init__(self, message: str = "Class can not be configured by Qonfig",
                 class_type: Optional[type] = None,
                 ) -> None:
        r"""Initialize NotQonfigurableError.

        Args:
            message: Error message
            class_type: Type of the class configured by qonfig raising exception
        """
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.class_type = class_type


class Empty(object):
    r"""Empty class, used when a value is not set in Qonfig"""

    def __init__(self) -> None:
        """Initialize empty class."""
        pass

    def __eq__(self, other: object) -> bool:
        """Return True when self and other are equal.

        Args:
            other: Compared objects, needs to be empty to return True

        Returns:
            bool
        """
        if other.__class__ == self.__class__:
            return True
        else:
            return False

    def __repr__(self) -> str:
        """Representation of empty.

        Returns:
            str
        """
        return "<empty 'Empty'>"

    def __str__(self) -> str:
        """String of empty.

        Returns:
            str
        """
        return "empty"


empty = Empty()
