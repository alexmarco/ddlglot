"""DDLGlot exception hierarchy."""

from __future__ import annotations


class DDLGlotError(Exception):
    """Base exception for all DDLGlot errors."""


class ValidationError(DDLGlotError):
    """Base class for validation errors."""


class DialectValidationError(ValidationError):
    """Raised when DDL is invalid for a specific dialect."""

    def __init__(self, message: str, dialect: str | None = None) -> None:
        self.dialect = dialect
        super().__init__(message)


class SchemaValidationError(ValidationError):
    """Raised when schema definition is invalid."""


class ASTBuildError(DDLGlotError):
    """Raised when AST construction fails."""


class UnsupportedDialectError(DDLGlotError):
    """Raised when dialect is not supported."""

    def __init__(self, dialect: str) -> None:
        self.dialect = dialect
        super().__init__(f"Unsupported dialect: {dialect}")


class PartitionByExpressionError(DialectValidationError):
    """Raised when PARTITIONED BY expression is used where not supported."""

    def __init__(self, dialect: str) -> None:
        self.dialect = dialect
        super().__init__(
            f"PARTITIONED BY with expressions is not supported in {dialect}. "
            "Use a generated column instead."
        )


class UnsupportedFeatureError(DialectValidationError):
    """Raised when a feature is not supported by the dialect."""

    def __init__(self, feature: str, dialect: str, suggestion: str | None = None) -> None:
        self.dialect = dialect
        self.feature = feature
        msg = f"Feature '{feature}' is not supported in {dialect}."
        if suggestion:
            msg += f" {suggestion}"
        super().__init__(msg)


class InvalidPropertyError(DialectValidationError):
    """Raised when a property value is invalid for the dialect."""

    def __init__(self, property_name: str, dialect: str, valid_values: str) -> None:
        self.dialect = dialect
        self.property_name = property_name
        super().__init__(
            f"Invalid value for property '{property_name}' in {dialect}. "
            f"Valid values: {valid_values}."
        )
