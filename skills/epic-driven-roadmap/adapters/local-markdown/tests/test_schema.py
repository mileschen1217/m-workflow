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


import dataclasses


def test_every_epicdata_field_has_consumer_or_sidecar_metadata():
    """AC-2a — no field exists without consumer or sidecar_rationale."""
    for f in dataclasses.fields(S.EpicData):
        meta = f.metadata
        has_consumer = bool(meta.get("consumer"))
        has_sidecar = bool(meta.get("sidecar_rationale"))
        assert has_consumer ^ has_sidecar, (
            f"EpicData.{f.name} must carry exactly one of consumer/sidecar_rationale; got {dict(meta)}"
        )


def test_every_phasedata_field_has_consumer_or_sidecar_metadata():
    """AC-2a — same rule for PhaseData."""
    for f in dataclasses.fields(S.PhaseData):
        meta = f.metadata
        has_consumer = bool(meta.get("consumer"))
        has_sidecar = bool(meta.get("sidecar_rationale"))
        assert has_consumer ^ has_sidecar, (
            f"PhaseData.{f.name} must carry exactly one of consumer/sidecar_rationale; got {dict(meta)}"
        )


def test_epicdata_default_construction():
    e = S.EpicData()
    assert e.schema_version == S.SCHEMA_VERSION
    assert e.slug == ""
    assert e.status == "proposed"
    assert e.started is None
    assert e.landed is None
    assert e.phases == []
    assert e.sidecar == {}


def test_phasedata_construction():
    p = S.PhaseData(n=1, title="Discovery", status="done", landed="2026-05-29")
    assert p.n == 1
    assert p.sidecar == {}
