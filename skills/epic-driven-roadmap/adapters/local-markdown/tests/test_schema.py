"""Schema foundation tests — SCHEMA_VERSION + typed errors + sidecar tag shape."""
import pytest
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S


def test_schema_version_is_one():
    assert S.SCHEMA_VERSION == 1


def test_status_literal_members():
    assert set(S.STATUS_VALUES) == {
        "proposed", "active", "paused", "done", "cancelled",
    }


def test_typed_errors_carry_required_attrs():
    err = S.SchemaValidationError(field="status", slug="x", schema_version=1, reason="missing")
    assert err.field == "status"
    assert err.slug == "x"
    assert err.schema_version == 1
    assert err.reason == "missing"

    err2 = S.SchemaVersionMismatch(found=99, expected=1)
    assert err2.found == 99 and err2.expected == 1

    err3 = S.CanonicalSerialisationError(field="phases", backend="local-markdown")
    assert err3.field == "phases" and err3.backend == "local-markdown"

    err4 = S.SidecarUnstorableError(field="weird", backend="local-markdown", reason="oversize")
    assert err4.reason == "oversize"

    err5 = S.StructuralHostMissingError(field="open_questions")
    assert err5.field == "open_questions"

    err6 = S.EpicNotFound(slug="missing-slug")
    assert err6.slug == "missing-slug"

    err7 = S.AdapterNotFoundError(selector="nonexistent")
    assert err7.selector == "nonexistent"

    err8 = S.AdapterInternalError(cause="boom")
    assert err8.cause == "boom"


def test_validate_sidecar_value_accepts_tagged_shapes():
    assert S.validate_sidecar_value("hello") is None
    assert S.validate_sidecar_value(["a", "b"]) is None
    assert S.validate_sidecar_value({"k": "v"}) is None


def test_validate_sidecar_value_rejects_untagged():
    for bad in (1, 1.5, True, None, ["a", 1], {"k": 1}, {1: "v"}, ("a",)):
        with pytest.raises(S.SidecarUnstorableError):
            S.validate_sidecar_value(bad)
