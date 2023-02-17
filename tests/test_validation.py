import pytest

from load_atoms.validation import (
    Blueprint,
    IsBibTeX,
    IsIn,
    ListOf,
    OneOf,
    Optional,
    Required,
    RuleValidationError,
)

bob = {
    "name": "bob",
    "description": "a happy little fellow",
    "age": 42,
    "hobbies": ["coding", "reading", "writing"],
}


def test_required():
    true_rules = [
        Required("name"),  # exists
        Required("description", str),  # correct type
        Required("age", int),  # correct type
        Required("hobbies", ListOf(str)),  # correct type
        Required("age", lambda x: x > 0),  # custom validation
        Required("age", IsIn([42, 43])),  # custom validation
    ]

    false_rules = [
        Required("made_up_field"),  # doesn't exist
        Required("name", int),  # wrong type
    ]

    # test each rule individually
    for rule in true_rules:
        assert rule(bob), f"rule {rule} failed"

    for rule in false_rules:
        assert not rule(bob), f"rule {rule} should have failed"

    # test all rules together
    schema = Blueprint(*true_rules)
    schema.validate(bob)


def test_failure():
    rule = Required("name", int)
    assert not rule(bob)

    schema = Blueprint(rule)
    # assert that validation fails
    with pytest.raises(RuleValidationError):
        schema.validate(bob)
