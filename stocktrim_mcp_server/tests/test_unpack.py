"""Tests for the ``unpack`` decorator.

Covers the three behaviors that GH #116 either introduced or relied on:

1. ``Field(description=...)`` is preserved on synthesized parameters via
   ``Annotated`` metadata. Locked in so the side-fix doesn't regress.
2. Strategy C runtime dispatch — positional ``BaseModel`` calls forward
   straight through to the wrapped function, flat kwargs reconstruct the
   model.
3. Legacy wrapper rejection — the pre-#116 ``{"request": {...}}`` shape
   raises a clear ``TypeError`` naming the expected flat fields.
"""

from __future__ import annotations

import inspect
from typing import Annotated, get_args, get_origin

import pytest
from pydantic import BaseModel, Field, ValidationError
from pydantic.fields import FieldInfo

from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params


class _SampleRequest(BaseModel):
    """Request model used to probe the decorator's behavior."""

    name: str = Field(description="The thing's name")
    limit: int = Field(default=10, description="Cap on results", ge=1, le=100)
    tags: list[str] = Field(default_factory=list, description="Optional tags")


# ---------------------------------------------------------------------------
# 1. Description preservation
# ---------------------------------------------------------------------------


def test_field_description_preserved_on_synthesized_parameter() -> None:
    """The synthesized ``inspect.Parameter`` should carry ``description`` via Annotated.

    Before the #116 fix, the decorator constructed parameters with the bare
    ``field_info.annotation`` and dropped ``FieldInfo`` metadata. FastMCP's
    emitted JSON schema therefore had no field descriptions. After the fix,
    the parameter's annotation is ``Annotated[ann, FieldInfo(description=…)]``
    so descriptions reach the schema.
    """

    @unpack_pydantic_params
    async def fn(
        request: Annotated[_SampleRequest, Unpack()],
    ) -> None: ...

    sig = inspect.signature(fn)
    name_param = sig.parameters["name"]

    # The annotation should be Annotated[str, FieldInfo(description="The thing's name")]
    assert get_origin(name_param.annotation) is Annotated
    annotated_args = get_args(name_param.annotation)
    assert annotated_args[0] is str
    field_infos = [a for a in annotated_args[1:] if isinstance(a, FieldInfo)]
    assert field_infos, (
        f"No FieldInfo in synthesized parameter metadata: {annotated_args}"
    )
    assert field_infos[0].description == "The thing's name"


def test_field_constraints_preserved_on_synthesized_parameter() -> None:
    """``ge``/``le`` constraints should survive flattening.

    The wrapper passes the cloned ``FieldInfo`` through ``Annotated`` so
    Pydantic re-derives the validators from it during schema generation.
    """

    @unpack_pydantic_params
    async def fn(
        request: Annotated[_SampleRequest, Unpack()],
    ) -> None: ...

    sig = inspect.signature(fn)
    limit_param = sig.parameters["limit"]
    annotated_args = get_args(limit_param.annotation)
    field_infos = [a for a in annotated_args[1:] if isinstance(a, FieldInfo)]
    fi = field_infos[0]
    assert fi.description == "Cap on results"
    # ge=1, le=100 come through as constraint metadata on FieldInfo.
    # Pydantic exposes them via .metadata as a list of validator dataclasses.
    constraint_reprs = [repr(m) for m in fi.metadata]
    joined = " ".join(constraint_reprs)
    assert "Ge" in joined or "ge" in joined, (
        f"Expected Ge constraint in metadata, got: {constraint_reprs}"
    )


# ---------------------------------------------------------------------------
# 2. Strategy C dispatch
# ---------------------------------------------------------------------------


async def test_positional_model_dispatch_forwards_unchanged() -> None:
    """``await fn(SampleRequest(...), ctx)`` should bypass flat reconstruction.

    This is the legacy in-process path used by workflow tests.
    """
    received: list[_SampleRequest] = []

    @unpack_pydantic_params
    async def fn(
        request: Annotated[_SampleRequest, Unpack()],
        ctx: object = None,
    ) -> None:
        received.append(request)

    payload = _SampleRequest(name="hello", limit=5, tags=["a"])
    await fn(payload, ctx=object())
    assert received == [payload]
    # The forwarded instance is the same object (not a reconstruction).
    assert received[0] is payload


async def test_flat_kwargs_reconstruct_model() -> None:
    """Flat kwargs should reconstruct a model instance and forward it."""
    received: list[_SampleRequest] = []

    @unpack_pydantic_params
    async def fn(
        request: Annotated[_SampleRequest, Unpack()],
        ctx: object = None,
    ) -> None:
        received.append(request)

    await fn(name="hello", limit=7, ctx=object())
    assert len(received) == 1
    assert received[0].name == "hello"
    assert received[0].limit == 7
    assert received[0].tags == []


async def test_flat_kwargs_validation_error_mentions_field() -> None:
    """When flat kwargs fail validation, the error names the offending field."""

    @unpack_pydantic_params
    async def fn(
        request: Annotated[_SampleRequest, Unpack()],
        ctx: object = None,
    ) -> None: ...

    # ``limit`` has ``ge=1`` — sending 0 should produce a field-level error.
    with pytest.raises(ValidationError) as exc_info:
        await fn(name="x", limit=0, ctx=object())
    assert "limit" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 3. Legacy wrapper shape rejection
# ---------------------------------------------------------------------------


async def test_legacy_request_wrapper_raises_clear_error() -> None:
    """``request=<any non-model value>`` (the #116 symptom) raises a clear ``TypeError``.

    The legacy ``{"request": {...}}`` wrapper shape was removed in 0.16.0 —
    both dict and string payloads under the ``request`` key are rejected
    immediately, naming the model's flat fields so callers can fix their
    payloads. See CHANGELOG (mcp v0.16.0) and #116.
    """

    @unpack_pydantic_params
    async def fn(
        request: Annotated[_SampleRequest, Unpack()],
        ctx: object = None,
    ) -> None: ...

    # String payload (the original #116 symptom shape).
    with pytest.raises(TypeError) as exc_info:
        await fn(request='{"name": "broken"}', ctx=object())
    msg = str(exc_info.value)
    # Error should mention the flat field names so the user knows what to send.
    assert "name" in msg
    assert "limit" in msg

    # Dict payload — previously splatted by the transitional fallback,
    # now rejected with the same clear error.
    with pytest.raises(TypeError) as exc_info:
        await fn(request={"name": "legacy", "limit": 3}, ctx=object())
    msg = str(exc_info.value)
    assert "name" in msg
    assert "limit" in msg
