from unittest.mock import Mock
from cache import get_cached_url, set_cached_url, delete_cached_url


def test_cache_operations(mocker):
    mock_redis = Mock()
    mocker.patch("cache.redis_client", mock_redis)

    # Test set and get
    set_cached_url("abc123", "http://example.com")
    mock_redis.set.assert_called_with("abc123", "http://example.com")

    mock_redis.get.return_value = b"http://example.com"
    result = get_cached_url("abc123")
    assert result == b"http://example.com"

    # Test delete
    delete_cached_url("abc123")
    mock_redis.delete.assert_called_with("abc123")
