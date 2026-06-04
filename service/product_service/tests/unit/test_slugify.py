from app.infrastructure.slugify import slugify


def test_slugify_basic():
    assert slugify("Gaming PC") == "gaming-pc"


def test_slugify_cyrillic_stripped():
    assert slugify("Игровой ПК") == ""


def test_slugify_mixed():
    assert slugify("RTX 4060 Gaming") == "rtx-4060-gaming"


def test_slugify_special_chars():
    assert slugify("hello!!! world???") == "hello-world"


def test_slugify_multiple_spaces():
    assert slugify("a  b   c") == "a-b-c"
