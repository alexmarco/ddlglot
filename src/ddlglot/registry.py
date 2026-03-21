"""Plugin registry for DDLGlot variants."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

VariantFactory = Callable[..., Any]


_REGISTRY: dict[str, type] = {}


def register_variant(name: str) -> Callable[[type], type]:
    """Decorator to register a variant builder.

    Usage:
        @register_variant("spark_delta")
        class SparkDeltaBuilder(CreateBuilder):
            ...

    Args:
        name: The variant name (e.g., "spark_delta", "hive").

    Returns:
        Decorator function.
    """

    def decorator(cls: type) -> type:
        _REGISTRY[name] = cls
        return cls

    return decorator


def get_variant(name: str) -> type:
    """Get a registered variant by name.

    Args:
        name: The variant name.

    Returns:
        The variant builder class.

    Raises:
        ValueError: If variant is not registered.
    """
    if name not in _REGISTRY:
        raise ValueError(f"Variant '{name}' is not registered. Available: {list_variants()}")
    return _REGISTRY[name]


def create_variant(name: str, kind: str = "TABLE") -> Any:
    """Create a variant builder by name.

    Args:
        name: The variant name.
        kind: The DDL kind ("TABLE", "VIEW", etc.).

    Returns:
        A new instance of the variant builder.
    """
    variant_cls = get_variant(name)
    return variant_cls(kind)


def list_variants() -> list[str]:
    """List all registered variant names.

    Returns:
        List of registered variant names.
    """
    return list(_REGISTRY.keys())


def is_registered(name: str) -> bool:
    """Check if a variant is registered.

    Args:
        name: The variant name.

    Returns:
        True if registered, False otherwise.
    """
    return name in _REGISTRY


def clear_registry() -> None:
    """Clear all registered variants. Useful for testing."""
    _REGISTRY.clear()


def _get_registry() -> dict[str, type]:
    """Get the internal registry dict. For testing purposes only."""
    return _REGISTRY
