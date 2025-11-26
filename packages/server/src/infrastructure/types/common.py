"""Common type aliases used across the application."""

# Metadata dictionary for storing arbitrary key-value pairs
MetadataDict = dict[str, str | int | float | bool | None]

# Filter dictionary for querying with conditions
FilterDict = dict[str, str | int | float | bool | None | list[str | int | float]]

# Primitive values
PrimitiveValue = str | int | float | bool | None
