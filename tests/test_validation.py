import pytest

from load_atoms.validation import (
    BibTeX,
    Blueprint,
    FileHash,
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


def test_bibtext():
    bibtext = "@misc{bob, author = {Bob}, title = {A happy little fellow}}"
    assert BibTeX().is_valid(bibtext)

    # test that validation fails
    with pytest.raises(RuleValidationError):
        BibTeX().validate("this is not bibtext")


def test_file_hash():
    assert FileHash().is_valid("c9dcec505f4d"), "c9dcec505f4d is a valid hash"
    assert not FileHash().is_valid("00000000000000000"), "hash is too long"
    assert not FileHash().is_valid("00000000000"), "hash is too short"
    assert not FileHash().is_valid("hello there"), "hash contains invalid characters"


def test_one_of():
    rule = OneOf(Required("name"), Required("age"))
    assert not rule.is_valid(bob), "both of these fields exist - should fail"

    rule = OneOf(Required("name"), Required("made_up_field"))
    assert rule(bob), "one of these fields exists - should pass"


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
