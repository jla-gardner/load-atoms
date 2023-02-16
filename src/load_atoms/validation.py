class Validator:
    def __init__(self, *rules):
        self.rules = list(rules)

    def add_rule(self, rule):
        self.rules.append(rule)

    def validate(self, data):
        for rule in self.rules:
            passes = rule(data)
            if not passes:
                raise ValueError(f"Validation failed: {rule}")

    def is_valid(self, data):
        try:
            self.validate(data)
        except ValueError:
            return False
        return True

    def __repr__(self) -> str:
        return f"Validator({', '.join(str(rule) for rule in self.rules)})"

    def __call__(self, thing) -> bool:
        return self.is_valid(thing)


class IsInstance:
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, data):
        return isinstance(data, self.cls)

    def __repr__(self):
        return f"IsInstance({self.cls.__name__})"


class ListOf:
    def __init__(self, validator):
        self.validator = validator

    def __call__(self, data):
        if not isinstance(data, list):
            return False
        for item in data:
            if not self.validator(item):
                return False
        return True

    def __repr__(self):
        return f"ListOf({self.validator})"


class Required:
    def __init__(self, field, validator=None):
        self.field = field
        if validator is not None:
            if validator in (str, int, float, list, dict):
                validator = IsInstance(validator)
        self.validator = validator

    def __call__(self, data):
        if self.field not in data:
            return False
        if self.validator is not None:
            return self.validator(data[self.field])
        return True

    def __repr__(self):
        if self.validator is None:
            return f'Required("{self.field}")'
        return f'Required("{self.field}", {self.validator})'


class Optional:
    def __init__(self, field, validator=None):
        self.field = field
        if validator is not None:
            if validator in (str, int, float, list, dict):
                validator = IsInstance(validator)
        self.validator = validator

    def __call__(self, data):
        if self.field not in data:
            return True
        if self.validator is not None:
            return self.validator(data[self.field])
        return True

    def __repr__(self):
        if self.validator is None:
            return f'Optional("{self.field}")'
        return f'Optional("{self.field}", {self.validator})'


class OneOf:
    def __init__(self, *rules):
        self.rules = rules

    def __call__(self, data):
        for rule in self.rules:
            if rule(data):
                return True
        return False

    def __repr__(self):
        return f"OneOf({', '.join(map(str, self.rules))})"


class In:
    def __init__(self, values, *more_values):
        self.values = [*values, *more_values]

    def __call__(self, data):
        return data in self.values

    def __repr__(self):
        return f"In({', '.join(map(str, self.values))})"


class IsBibTeX:
    def __call__(self, data):
        if not isinstance(data, str):
            return False
        data = data.strip()
        return data.startswith("@") and data.endswith("}")

    def __repr__(self):
        return "IsBibTeX()"


class HasFields:
    def __init__(self, *fields):
        self.fields = fields

    def __call__(self, data):
        for field in self.fields:
            if field not in data:
                return False
        return True

    def __repr__(self):
        return f"HasFields({', '.join(map(str, self.fields))})"
