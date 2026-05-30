"""Stdlib frontmatter parser — supported subset tests + reject tests.

Parser is a hand-rolled subset that matches EXACTLY the YAML constructs we
emit. Anything outside the subset raises SchemaValidationError.
"""
import pytest
from skills.epic_driven_roadmap.adapters.local_markdown import adapter as A
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S


def test_parse_flat_scalars():
    out = A._parse_frontmatter("schema_version: 1\nslug: demo\nstatus: active\n", slug="demo")
    assert out == {"schema_version": 1, "slug": "demo", "status": "active"}


def test_parse_empty_value_is_none():
    out = A._parse_frontmatter("started:\nlanded:\n", slug="x")
    assert out == {"started": None, "landed": None}


def test_parse_null_and_tilde():
    out = A._parse_frontmatter("a: null\nb: ~\n", slug="x")
    assert out == {"a": None, "b": None}


def test_parse_list_of_str():
    out = A._parse_frontmatter("pivots:\n  - cut concurrency\n  - drop Linear\n", slug="x")
    assert out == {"pivots": ["cut concurrency", "drop Linear"]}


def test_parse_dict_of_str():
    out = A._parse_frontmatter("meta:\n  spec: specs/x.md\n  plan: plans/x.md\n", slug="x")
    assert out == {"meta": {"spec": "specs/x.md", "plan": "plans/x.md"}}


def test_parse_quoted_scalar_keeps_string():
    out = A._parse_frontmatter('msg: "hello world"\nother: \'a b\'\n', slug="x")
    assert out == {"msg": "hello world", "other": "a b"}


def test_parse_date_stays_string():
    # The PyYAML _coerce_date workaround is gone: dates are just strings.
    out = A._parse_frontmatter("started: 2026-05-01\n", slug="x")
    assert out == {"started": "2026-05-01"}


def test_parse_int_value():
    out = A._parse_frontmatter("schema_version: 1\n", slug="x")
    assert isinstance(out["schema_version"], int)
    assert out["schema_version"] == 1


def test_reject_multiline_pipe_block():
    with pytest.raises(S.SchemaValidationError):
        A._parse_frontmatter("body: |\n  line1\n  line2\n", slug="x")


def test_reject_multiline_gt_block():
    with pytest.raises(S.SchemaValidationError):
        A._parse_frontmatter("body: >\n  line1\n  line2\n", slug="x")


def test_reject_flow_style_list():
    with pytest.raises(S.SchemaValidationError):
        A._parse_frontmatter("pivots: [a, b]\n", slug="x")


def test_reject_flow_style_dict():
    with pytest.raises(S.SchemaValidationError):
        A._parse_frontmatter("meta: {a: b}\n", slug="x")


def test_reject_anchor():
    with pytest.raises(S.SchemaValidationError):
        A._parse_frontmatter("a: &x foo\nb: *x\n", slug="x")


def test_reject_nested_list_in_list():
    with pytest.raises(S.SchemaValidationError):
        A._parse_frontmatter("items:\n  - - nested\n", slug="x")


def test_emit_roundtrip_scalar():
    fm = {"schema_version": 1, "slug": "demo", "status": "active"}
    text = A._emit_frontmatter(fm)
    assert A._parse_frontmatter(text, slug="demo") == fm


def test_emit_roundtrip_list():
    fm = {"pivots": ["a", "b"]}
    text = A._emit_frontmatter(fm)
    assert A._parse_frontmatter(text, slug="x") == fm


def test_emit_roundtrip_dict():
    fm = {"meta": {"k1": "v1", "k2": "v2"}}
    text = A._emit_frontmatter(fm)
    assert A._parse_frontmatter(text, slug="x") == fm


def test_emit_roundtrip_none():
    fm = {"started": None, "landed": None}
    text = A._emit_frontmatter(fm)
    assert A._parse_frontmatter(text, slug="x") == fm
