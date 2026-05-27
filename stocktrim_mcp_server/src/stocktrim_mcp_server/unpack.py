"""Unpack decorator for flattening Pydantic models into tool parameters.

This module provides a decorator that allows tools to use Pydantic models for
validation while exposing flattened parameters to the MCP protocol, working around
Claude Code's parameter serialization issues with nested objects.

Usage:
    from typing import Annotated
    from pydantic import BaseModel, Field
    from stocktrim_mcp_server.unpack import Unpack, unpack_pydantic_params

    class MyRequest(BaseModel):
        name: str = Field(..., description="Item name")
        limit: int = Field(10, description="Max results")

    @unpack_pydantic_params
    async def my_tool(
        request: Annotated[MyRequest, Unpack()],
        context: Context
    ) -> MyResponse:
        # request is a MyRequest instance with validated fields
        ...

The decorator transforms the function signature so FastMCP sees individual
parameters (name, limit) instead of a nested request object, while the function
body still receives a properly validated Pydantic model instance.

Runtime dispatch (Strategy C, GH #116)
--------------------------------------
The wrapper accepts both call shapes:

1. **Flat-kwargs path** (FastMCP path): the wrapper is invoked with the model's
   fields as individual kwargs (e.g. ``code="WIDGET-001"``). The wrapper
   reconstructs the Pydantic model and forwards it to the wrapped function.
2. **Positional-model path** (in-process / legacy path): the wrapper is invoked
   with a single positional ``BaseModel`` instance whose type matches one of the
   ``Unpack()`` annotations (e.g. ``await tool(MyRequest(...), ctx)``). The
   wrapper forwards the model instance straight through, preserving the
   ergonomic test-call convention that pre-dates the flattening machinery.

The legacy ``{"request": {<flat_fields>}}`` wrapper shape is no longer accepted.
Calls that still send the wrapper raise ``TypeError`` immediately, naming the
model's flat fields so clients can fix their payloads.
"""

from __future__ import annotations

import functools
import inspect
import logging
from collections.abc import Callable
from typing import Annotated, Any, cast, get_args, get_origin, get_type_hints

from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

logger = logging.getLogger(__name__)


class Unpack:
    """Marker class to indicate a Pydantic model should be unpacked into flat parameters.

    Use with typing.Annotated to mark which parameters should be unpacked:
        request: Annotated[MyRequest, Unpack()]
    """

    pass


def _try_positional_model_dispatch(
    args: tuple[Any, ...],
    unpack_mapping: dict[str, tuple[type[BaseModel], list[str]]],
) -> str | None:
    """Detect the legacy positional-model call shape.

    Returns the original parameter name (e.g. ``"request"``) when ``args[0]`` is
    a ``BaseModel`` instance matching one of the unpacked parameter types — that
    tells the wrapper to forward the model straight through to the wrapped
    function instead of running flat-kwargs reconstruction.

    Returns ``None`` when the call should go through the flat-kwargs path.
    """
    if not args:
        return None
    candidate = args[0]
    if not isinstance(candidate, BaseModel):
        return None
    for original_param_name, (model_class, _field_names) in unpack_mapping.items():
        if isinstance(candidate, model_class):
            return original_param_name
    return None


def _descriptive_field_info(field_info: FieldInfo) -> FieldInfo:
    """Clone a ``FieldInfo`` keeping only the descriptive metadata.

    The synthetic ``inspect.Parameter`` carries the default value separately via
    ``Parameter.default`` — so when we embed ``FieldInfo`` in the parameter's
    ``Annotated`` chain, we must strip ``default`` and ``default_factory`` from
    the cloned ``FieldInfo`` (otherwise Pydantic raises
    ``TypeError: cannot specify both default and default_factory`` when it
    re-derives the field during schema generation).

    We preserve ``description``, validation constraints (``metadata``),
    ``examples``, ``title``, ``alias``, etc. — everything the emitted JSON
    schema cares about.
    """
    # Copy all explicitly-set attributes EXCEPT default/default_factory/annotation.
    # FieldInfo._attributes_set tracks which kwargs were explicitly passed by the
    # caller (vs defaulted), so this is the right source of truth for "what does
    # the user care about preserving".
    excluded = {"default", "default_factory", "annotation"}
    attrs = {k: v for k, v in field_info._attributes_set.items() if k not in excluded}
    descriptive = FieldInfo(**attrs)
    # Carry over constraint validators (Ge/Le/MinLen/etc.). Pydantic stores
    # numeric/string constraints on ``FieldInfo.metadata`` rather than in
    # ``_attributes_set``, so an attribute-copy alone loses them.
    if field_info.metadata:
        descriptive.metadata = list(field_info.metadata)
    return descriptive


def _reconstruct_models(
    kwargs: dict[str, Any],
    unpack_mapping: dict[str, tuple[type[BaseModel], list[str]]],
) -> dict[str, Any]:
    """Collect flat kwargs into Pydantic model instances per the unpack mapping.

    Shared by both the async and sync wrappers so the two stay in lockstep.
    """
    # Defense for the #116 symptom shape: if a caller still sends the legacy
    # wrapper name (e.g. ``request={...}`` or ``request="<json string>"``),
    # reject with a clear error pointing at the flat fields. Without this,
    # the wrapper would silently discard the wrapped payload and call the
    # underlying function with model defaults — a confusing partial success.
    for original_param_name, (model_class, _field_names) in unpack_mapping.items():
        if original_param_name in kwargs and not isinstance(
            kwargs[original_param_name], model_class
        ):
            flat_fields = ", ".join(model_class.model_fields.keys())
            raise TypeError(
                f"Unexpected wrapped argument '{original_param_name}'. The tool "
                f"expects flat keyword arguments matching "
                f"{model_class.__name__} fields: {flat_fields}. The legacy "
                f"{{'request': {{...}}}} wrapper shape was removed in 0.16.0; "
                f"see CHANGELOG and #116."
            )

    reconstructed_kwargs = dict(kwargs)

    for original_param_name, (model_class, field_names) in unpack_mapping.items():
        # Collect fields for this model
        model_data: dict[str, Any] = {}
        for field_name in field_names:
            if field_name in reconstructed_kwargs:
                model_data[field_name] = reconstructed_kwargs.pop(field_name)

        # Build and validate the model. Re-raise Pydantic validation errors
        # unchanged so callers see the field-level diagnostics.
        try:
            model_instance = model_class(**model_data)
        except ValidationError:
            raise

        reconstructed_kwargs[original_param_name] = model_instance

    return reconstructed_kwargs


def unpack_pydantic_params(func: Callable) -> Callable:
    """Decorator that unpacks Pydantic model parameters into individual fields.

    This decorator scans the function signature for parameters annotated with
    Annotated[ModelClass, Unpack()], extracts the Pydantic model fields, and
    creates a new function that accepts those fields as individual parameters.

    At runtime, the individual parameters are collected and used to construct
    the Pydantic model instance, which is then passed to the original function.

    Each synthesized parameter preserves the original ``FieldInfo`` (description,
    ge, le, etc.) via ``Annotated[annotation, field_info]`` so FastMCP's emitted
    schema retains the documentation that Pydantic produced from the model.

    The runtime wrapper accepts two call shapes (Strategy C, GH #116):

    1. **Flat kwargs** (FastMCP path) — the typical case.
    2. **Single positional ``BaseModel``** (in-process path) — when the wrapped
       function is invoked positionally with a model instance whose type matches
       one of the unpack-mapped models, the model is forwarded straight through
       to the wrapped function. This preserves the
       ``await tool(MyRequest(...), ctx)`` idiom used throughout the workflow
       test suite.

    The legacy ``{"request": {<flat_fields>}}`` wrapper shape is no longer
    accepted; calls using it raise ``TypeError`` naming the expected flat
    fields. See CHANGELOG (mcp v0.16.0) and #116.

    Args:
        func: The function to decorate. Should have at least one parameter
            annotated with Annotated[BaseModel, Unpack()].

    Returns:
        A wrapped function with flattened parameters that reconstructs the
        Pydantic model at runtime.

    Raises:
        TypeError: If the unpacked parameter is not a Pydantic BaseModel subclass.
        ValidationError: If the collected parameters don't pass Pydantic validation.

    Example:
        @unpack_pydantic_params
        async def search_products(
            request: Annotated[SearchProductsRequest, Unpack()],
            context: Context
        ) -> SearchProductsResponse:
            # request is a validated SearchProductsRequest instance
            return await search_impl(request, context)

        # FastMCP sees: search_products(search_query: str, context: Context)
        # Function receives: request=SearchProductsRequest(search_query="...")
    """
    sig = inspect.signature(func)
    new_params = []
    unpack_mapping: dict[str, tuple[type[BaseModel], list[str]]] = {}

    # Get type hints to resolve string annotations (from __future__ import annotations).
    # Forward references that can't be resolved at decoration time raise NameError
    # — fall back to raw annotations only in that case. Any other exception (e.g.,
    # a malformed annotation) indicates a programming error that should surface
    # rather than silently disable Unpack() detection, which would cause the tool
    # to register with the wrong (wrapped-model) schema.
    try:
        type_hints = get_type_hints(func, include_extras=True)
    except NameError:
        logger.warning(
            "unpack_pydantic_params: get_type_hints() raised NameError for %s; "
            "falling back to raw annotations. Unpack() detection may be skipped "
            "for parameters with unresolved forward references.",
            getattr(func, "__qualname__", func),
        )
        type_hints = {}

    # Track if we've added any KEYWORD_ONLY params
    # If we have, all subsequent params must also be KEYWORD_ONLY
    has_keyword_only = False

    # Scan parameters to find ones marked with Unpack()
    for param_name, param in sig.parameters.items():
        # Use resolved type hint if available, otherwise use raw annotation
        annotation = type_hints.get(param_name, param.annotation)

        # Check if this is Annotated[SomeModel, Unpack()]
        if get_origin(annotation) is Annotated:
            args = get_args(annotation)
            if len(args) >= 2 and any(isinstance(arg, Unpack) for arg in args[1:]):
                # Found an unpacked parameter
                model_class = args[0]

                if not (
                    inspect.isclass(model_class) and issubclass(model_class, BaseModel)
                ):
                    raise TypeError(
                        f"Parameter '{param_name}' with Unpack() must be a Pydantic BaseModel, "
                        f"got {model_class}"
                    )

                # Extract fields from the Pydantic model
                # Store fields to add them in correct order later
                unpacked_fields = []
                for field_name, field_info in model_class.model_fields.items():
                    # Preserve Field() metadata (description, ge, le, examples, etc.)
                    # by wrapping the base annotation in Annotated[..., field_info_copy].
                    # We strip default/default_factory from the cloned FieldInfo
                    # because the synthetic Parameter expresses the default
                    # separately via Parameter.default — Pydantic would otherwise
                    # refuse to merge both expressions.
                    # Without this preservation, FastMCP's emitted schema would
                    # drop descriptions, losing UX parity with the wrapped-model
                    # tools that produced descriptions naturally (#116).
                    field_annotation: Any = field_info.annotation
                    if field_annotation is not None:
                        descriptive = _descriptive_field_info(field_info)
                        field_annotation = Annotated[field_annotation, descriptive]

                    # Handle default values - convert PydanticUndefined to inspect.Parameter.empty
                    if field_info.default is not PydanticUndefined:
                        field_default = field_info.default
                    elif field_info.default_factory:
                        field_default = field_info.default_factory()
                    else:
                        field_default = inspect.Parameter.empty

                    # Use KEYWORD_ONLY to avoid parameter ordering issues
                    # This allows unpacked params to work with other params like Context
                    new_param = inspect.Parameter(
                        name=field_name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        default=field_default,
                        annotation=field_annotation,
                    )
                    unpacked_fields.append(new_param)

                # Add all unpacked fields
                new_params.extend(unpacked_fields)
                has_keyword_only = True

                # Remember this mapping for runtime reconstruction
                unpack_mapping[param_name] = (
                    model_class,
                    list(model_class.model_fields.keys()),
                )
                continue

        # Keep non-unpacked parameters, but if we've added KEYWORD_ONLY params
        # before this, we need to make this KEYWORD_ONLY too
        if has_keyword_only and param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            new_params.append(param.replace(kind=inspect.Parameter.KEYWORD_ONLY))
        else:
            new_params.append(param)

    # Create new signature with flattened parameters
    new_sig = sig.replace(parameters=new_params)

    # Create wrapper function that reconstructs models at runtime
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Strategy C: if called positionally with a matching BaseModel
        # instance, forward straight to the wrapped function. This keeps
        # the in-process `await tool(Request(...), ctx)` idiom working.
        if _try_positional_model_dispatch(args, unpack_mapping) is not None:
            return await func(*args, **kwargs)

        reconstructed_kwargs = _reconstruct_models(kwargs, unpack_mapping)
        return await func(*args, **reconstructed_kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Strategy C: positional-model passthrough (see async_wrapper).
        if _try_positional_model_dispatch(args, unpack_mapping) is not None:
            return func(*args, **kwargs)

        reconstructed_kwargs = _reconstruct_models(kwargs, unpack_mapping)
        return func(*args, **reconstructed_kwargs)

    # Choose wrapper based on whether original function is async
    wrapper = async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

    # Update wrapper signature to show flattened parameters. We cast to Any
    # because `__signature__` is an opt-in attribute on callables — the type
    # checker correctly doesn't infer it on a generic Callable, but
    # `inspect.signature()` honors it at runtime.
    cast("Any", wrapper).__signature__ = new_sig

    # CRITICAL: Also update __annotations__ so get_type_hints() sees the flattened params
    # This is required for FastMCP's ParsedFunction.from_function() to work correctly
    new_annotations = {}
    for param_name, param in new_sig.parameters.items():
        if param.annotation != inspect.Parameter.empty:
            new_annotations[param_name] = param.annotation
    if new_sig.return_annotation != inspect.Signature.empty:
        new_annotations["return"] = new_sig.return_annotation
    wrapper.__annotations__ = new_annotations

    return wrapper


__all__ = ["Unpack", "unpack_pydantic_params"]
