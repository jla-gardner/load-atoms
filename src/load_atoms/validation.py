import inspect
import string
from dataclasses import asdict, field, make_dataclass

from load_atoms.util import lpad


class RuleValidationError(Exception):
    pass


class Rule:
    def is_valid(self, data) -> bool:
        """
        check if the data is valid according to the rule
        """
        raise NotImplementedError()

    def _describe(self, content="") -> str:
        """
        describe the rule
        """
        return f"{self.__class__.__name__}({content})"

    def __repr__(self, indent=0) -> str:
        return lpad(self._describe(), indent=indent)

    def validate(self, data) -> None:
        """
        validate the data according to the rule

        Raises:
            ValidationError: if the data is not valid
        """

        if not self.is_valid(data):
            raise RuleValidationError(f"Rule {self} failed on {data}")

    def __call__(self, data):
        return self.is_valid(data)


class IsInstance(Rule):
    """
    check if the data is an instance of the given class

    Usage:
    >>> rule = IsInstance(str)
    >>> rule("hello")
    True
    >>> rule(1)
    False
    """

    def __init__(self, cls):
        self.cls = cls

    def is_valid(self, data):
        return isinstance(data, self.cls)

    def _describe(self):
        # return super()._describe(self.cls.__name__)
        return self.cls.__name__


class MultiRule(Rule):
    def __init__(self, *rules: Rule):
        rules = [convert_from_shorthand(rule) for rule in rules]
        self.rules = rules

    def apply_rules(self, data):
        passes = [rule for rule in self.rules if rule(data)]
        failures = [rule for rule in self.rules if not rule(data)]
        return passes, failures

    def _describe(self):
        parts = ",\n".join(rule.__repr__(indent=4) for rule in self.rules)
        return super()._describe(f"(\n{parts}\n)")

    def is_valid(self, data) -> bool:
        try:
            self.validate(data)
            return True
        except RuleValidationError:
            return False


class AllOf(MultiRule):
    def validate(self, data):
        passes, failures = self.apply_rules(data)
        if len(failures) == 0:
            return

        raise RuleValidationError(
            f"Rule {self} failed on {data}.\n"
            f" {len(failures)} rules failed:\n"
            + "\n".join(f" - {rule}" for rule in failures)
        )


class Blueprint(AllOf):
    def dataclass(self):
        fields = []

        for rule in self.rules:
            if not isinstance(rule, FieldValidator):
                continue

            if isinstance(rule.validator, IsInstance):
                cls = rule.validator.cls
            else:
                cls = any

            if isinstance(rule, Required):
                fields.append((rule.field, cls))

            elif isinstance(rule, Optional):
                fields.append((rule.field, cls, field(default=None)))

            else:
                raise ValueError(f"Unknown field validator {rule}")

        fields.append(("_blueprint", MultiRule, field(default=self)))

        def validate(self):
            dictionary = asdict(self)
            dictionary.pop("_blueprint")
            self._blueprint.validate(dictionary)

        cls = make_dataclass(
            "AutoValidatedDataclass", fields, namespace={"validate": validate}
        )
        return cls


class OneOf(MultiRule):
    def validate(self, data):
        passes, failures = self.apply_rules(data)
        if len(passes) == 1:
            return

        raise RuleValidationError(
            f"Rule {self} failed on {data}.\n"
            f"More than one rule passed:\n" + "\n".join(f" - {rule}" for rule in passes)
        )


class AnyOf(MultiRule):
    def validate(self, data):
        passes, failures = self.apply_rules(data)
        if len(passes) >= 1:
            return

        raise RuleValidationError(
            f"Rule {self} failed on {data}.\n" f"No rules passed.\n"
        )


class ListOf(Rule):
    """
    check if the data is a list of valid items

    Usage:
    >>> rule = ListOf(IsInstance(int))
    >>> rule([1, 2, 3])
    True
    >>> rule([1, "hello", 3])
    False
    >>> rule = ListOf(str)  # shorthand for ListOf(IsInstance(str))
    >>> rule(["hello", "world"])
    True
    """

    def __init__(self, validator: Rule):
        self.validator = convert_from_shorthand(validator)

    def is_valid(self, data):
        if not isinstance(data, list):
            return False
        for item in data:
            if not self.validator(item):
                return False
        return True

    def _describe(self):
        # return super()._describe(self.validator)
        return f"[{self.validator}]"


def convert_from_shorthand(validator):
    if validator is any:
        return lambda data: data is not None
    if validator in (str, int, float, list, dict):
        return IsInstance(validator)
    if isinstance(validator, type):
        return IsInstance(validator)
    if isinstance(validator, list):
        assert len(validator) == 1
        return ListOf(validator[0])
    # test if is a lambda function:
    if hasattr(validator, "__name__") and validator.__name__ == "<lambda>":
        return Lambda(validator)
    return validator


class FieldValidator(Rule):
    def __init__(self, field, validator=None):
        self.field = field
        if validator is None:
            validator = any
        self.validator = convert_from_shorthand(validator)

    def _describe(self):
        content = f"{self.field!r}"
        if self.validator is not None:
            content += f", {self.validator}"
        return super()._describe(content)


class Required(FieldValidator):
    """
    check if the data has the given field

    Usage:
    >>> rule = Required("name")
    >>> rule({"name": "hello"})
    True
    >>> rule({"name": 1})
    False
    >>> rule = Required("name", str)
    >>> rule({"name": "hello"})
    True
    >>> rule({"name": 1})
    False
    """

    def is_valid(self, data):
        if self.field not in data:
            return False
        if self.validator is not None:
            return self.validator(data[self.field])
        return True


class Optional(FieldValidator):
    """
    check if the data has the given field

    Usage:
    >>> rule = Optional("name")
    >>> rule({"name": "hello"})
    True
    >>> rule({"name": 1})
    False
    >>> rule = Optional("name", str)
    >>> rule({"name": "hello"})
    True
    >>> rule({"name": 1})
    False
    """

    def is_valid(self, data):
        # rule passes if the field is not present
        if self.field not in data:
            return True
        # but if it is present, it must be valid
        if self.validator is not None:
            return self.validator(data[self.field])
        return True


class IsIn(Rule):
    """
    check if the data is in the given iterable

    Usage:
    >>> rule = IsIn({"hello", "world"})
    >>> rule("hello")
    True
    >>> rule("foo")
    False
    """

    def __init__(self, options):
        self.options = options

    def is_valid(self, data):
        return data in self.options

    def _describe(self) -> str:
        return super()._describe(self.options)


class Mapping(Rule):
    def __init__(self, keys, values):
        self.keys_rule = convert_from_shorthand(keys)
        self.values_rule = convert_from_shorthand(values)

    def is_valid(self, data):
        if not isinstance(data, dict):
            return False
        for key, value in data.items():
            if not self.keys_rule(key):
                return False
            if not self.values_rule(value):
                return False
        return True

    def _describe(self):
        return super()._describe(f"{self.keys_rule} -> {self.values_rule}")


class BibTeX(Rule):
    def is_valid(self, data):
        data = data.strip()
        return data.startswith("@") and data.endswith("}")


class FileHash(Rule):
    def is_valid(self, data):
        if not isinstance(data, str):
            return False
        if len(data) != 12:
            return False
        return all(c in string.hexdigits for c in data)


class Lambda(Rule):
    def __init__(self, func):
        self.func = func

    def is_valid(self, data) -> bool:
        return self.func(data)

    def _describe(self):
        # get the code of the lambda function using inspect
        return inspect.getsource(self.func)
