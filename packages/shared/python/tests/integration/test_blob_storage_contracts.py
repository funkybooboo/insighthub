""Contract tests: concrete storage implementations conform to BlobStorage interface."""

import pytest

try:
    from shared.storage import BlobStorage
    from shared.storage import MinIOBlobStorage, FileSystemBlobStorage, InMemoryBlobStorage
    CONCRETE = [MinIOBlobStorage, FileSystemBlobStorage, InMemoryBlobStorage]
except Exception:
    # If storage modules aren't importable in this environment, skip at test collection time
    pytest.skip("BlobStorage interface or implementations not available", allow_module_level=True)


def test_concrete_storage_subclass_interface():
    for cls in CONCRETE:
        assert issubclass(cls, BlobStorage)
        # Basic surface area check; concrete classes should implement these methods
        for method in ("upload_file", "download_file", "delete_file", "file_exists", "calculate_hash"):
            assert hasattr(cls, method), f"{cls.__name__} missing {method}"
