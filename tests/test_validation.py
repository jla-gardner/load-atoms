import pytest

from load_atoms.validation import (
    AnyOf,
    BibTeX,
    Blueprint,
    FileHash,
    IsIn,
    ListOf,
    Mapping,
    OneOf,
    Optional,
    Required,
    Rule,
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


def test_optional():
    true_rules = [
        Optional("name"),  # exists
        Optional("description", str),  # correct type
        Optional("age", int),  # correct type
        Optional("hobbies", ListOf(str)),  # correct type
        Optional("age", lambda x: x > 0),  # custom validation
        Optional("age", IsIn([42, 43])),  # custom validation
    ]

    false_rules = [
        Optional("made_up_field"),  # doesn't exist
        Optional("name", int),  # wrong type
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


def test_mapping():
    rule = Mapping(str, any)
    assert rule.is_valid(bob), "Bob is a mapping from string to any"
    assert not rule.is_valid(42), "42 is not a mapping"

    # test validation on values fails
    rule = Mapping(str, int)
    assert not rule.is_valid(bob), "Bob is not a mapping from string to int"

    # test validation on keys fails
    rule = Mapping(int, any)
    assert not rule.is_valid(bob), "Bob is not a mapping from int to any"

    # test validation on more complex rules
    extra_test = {"name": "bob", "hobby": "coding"}
    rule = Mapping(str, lambda x: len(x) > 2)
    assert rule.is_valid(
        extra_test
    ), "extra_test is a valid mapping from string to string of length > 2"


def test_bibtex():
    bibtex = "@misc{bob, author = {Bob}, title = {A happy little fellow}}"
    assert BibTeX().is_valid(bibtex)

    # test that validation fails
    with pytest.raises(RuleValidationError):
        BibTeX().validate("this is not bibtext")


def test_file_hash():
    assert FileHash().is_valid("c9dcec505f4d"), "c9dcec505f4d is a valid hash"
    assert not FileHash().is_valid("00000000000000000"), "hash is too long"
    assert not FileHash().is_valid("00000000000"), "hash is too short"
    assert not FileHash().is_valid("hello there"), "hash contains invalid characters"
    assert not FileHash().is_valid(42), "hash is not a string"


def test_one_of():
    rule = OneOf(Required("name"), Required("age"))
    assert not rule.is_valid(bob), "both of these fields exist - should fail"

    rule = OneOf(Required("name"), Required("made_up_field"))
    assert rule(bob), "one of these fields exists - should pass"


def test_any_of():
    rule = AnyOf(Required("name"), Required("age"))
    assert rule(bob), "both of these fields exist - should pass"

    rule = AnyOf(Required("name"), Required("made_up_field"))
    assert rule(bob), "one of these fields exists - should pass"

    rule = AnyOf(Required("made_up_field"), Required("made_up_field_2"))
    assert not rule(bob), "neither of these fields exist - should fail"


def test_optional():
    assert Optional("made_up_field", str).is_valid(
        bob
    ), "made_up_field doesn't exist on bob, so an optional rule should pass"

    assert Optional("name", str).is_valid(
        bob
    ), "name exists on bob, so an optional rule should pass"

    assert not Optional("name", int).is_valid(
        bob
    ), "name exists on bob, but is the wrong type, so an optional rule should fail"


def test_rule_impl():
    with pytest.raises(NotImplementedError):
        Rule().is_valid("hello")


def test_lambda():
    rule = lambda x: x > 0
    assert rule(42), "42 is greater than 0"
    assert not rule(-42), "-42 is not greater than 0"

    assert "lambda" in str(rule), "str should contain lambda"
