"""Multi-level caching system for performance optimization."""

import hashlib
import json
import logging
import time
from typing import Any, Optional, Union, Dict
from pathlib import Path
import streamlit as st

# Caching libraries
try:
    import diskcache as dc
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheManager:
    """Multi-level cache manager with fallback strategies."""
    
    def __init__(self, cache_dir: Optional[str] = None, redis_url: Optional[str] = None):
        """Initialize cache manager with multiple storage backends."""
        self.cache_dir = Path(cache_dir or "cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache levels
        self.memory_cache = {}  # Level 1: In-memory
        self.disk_cache = None  # Level 2: Disk-based
        self.redis_cache = None  # Level 3: Redis (optional)
        
        # Initialize disk cache
        if DISKCACHE_AVAILABLE:
            try:
                self.disk_cache = dc.Cache(str(self.cache_dir / "disk_cache"))
                logger.info("Disk cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize disk cache: {str(e)}")
        
        # Initialize Redis cache (optional)
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_cache = redis.from_url(redis_url, decode_responses=True)
                self.redis_cache.ping()  # Test connection
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {str(e)}")
                self.redis_cache = None
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0,
            'redis_hits': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with multi-level fallback."""
        cache_key = self._normalize_key(key)
        
        # Level 1: Memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if not self._is_expired(entry):
                self.stats['hits'] += 1
                self.stats['memory_hits'] += 1
                logger.debug(f"Cache hit (memory): {cache_key}")
                return entry['value']
            else:
                del self.memory_cache[cache_key]
        
        # Level 2: Disk cache
        if self.disk_cache:
            try:
                entry = self.disk_cache.get(cache_key)
                if entry and not self._is_expired(entry):
                    # Promote to memory cache
                    self.memory_cache[cache_key] = entry
                    self.stats['hits'] += 1
                    self.stats['disk_hits'] += 1
                    logger.debug(f"Cache hit (disk): {cache_key}")
                    return entry['value']
            except Exception as e:
                logger.warning(f"Disk cache get error: {str(e)}")
        
        # Level 3: Redis cache
        if self.redis_cache:
            try:
                entry_json = self.redis_cache.get(cache_key)
                if entry_json:
                    entry = json.loads(entry_json)
                    if not self._is_expired(entry):
                        # Promote to memory and disk cache
                        self.memory_cache[cache_key] = entry
                        if self.disk_cache:
                            self.disk_cache.set(cache_key, entry)
                        self.stats['hits'] += 1
                        self.stats['redis_hits'] += 1
                        logger.debug(f"Cache hit (Redis): {cache_key}")
                        return entry['value']
            except Exception as e:
                logger.warning(f"Redis cache get error: {str(e)}")
        
        # Cache miss
        self.stats['misses'] += 1
        logger.debug(f"Cache miss: {cache_key}")
        return default
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in all available cache levels."""
        cache_key = self._normalize_key(key)
        
        entry = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        
        success = False
        
        # Level 1: Memory cache
        try:
            self.memory_cache[cache_key] = entry
            success = True
            logger.debug(f"Cache set (memory): {cache_key}")
        except Exception as e:
            logger.warning(f"Memory cache set error: {str(e)}")
        
        # Level 2: Disk cache
        if self.disk_cache:
            try:
                self.disk_cache.set(cache_key, entry, expire=ttl)
                logger.debug(f"Cache set (disk): {cache_key}")
            except Exception as e:
                logger.warning(f"Disk cache set error: {str(e)}")
        
        # Level 3: Redis cache
        if self.redis_cache:
            try:
                entry_json = json.dumps(entry)
                self.redis_cache.setex(cache_key, ttl, entry_json)
                logger.debug(f"Cache set (Redis): {cache_key}")
            except Exception as e:
                logger.warning(f"Redis cache set error: {str(e)}")
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete key from all cache levels."""
        cache_key = self._normalize_key(key)
        success = False
        
        # Remove from memory
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            success = True
        
        # Remove from disk
        if self.disk_cache:
            try:
                self.disk_cache.delete(cache_key)
            except Exception as e:
                logger.warning(f"Disk cache delete error: {str(e)}")
        
        # Remove from Redis
        if self.redis_cache:
            try:
                self.redis_cache.delete(cache_key)
            except Exception as e:
                logger.warning(f"Redis cache delete error: {str(e)}")
        
        return success
    
    def clear(self) -> bool:
        """Clear all cache levels."""
        try:
            # Clear memory
            self.memory_cache.clear()
            
            # Clear disk
            if self.disk_cache:
                self.disk_cache.clear()
            
            # Clear Redis
            if self.redis_cache:
                self.redis_cache.flushdb()
            
            logger.info("All caches cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 2),
            'memory_size': len(self.memory_cache),
            'disk_available': self.disk_cache is not None,
            'redis_available': self.redis_cache is not None
        }
    
    def cleanup_expired(self) -> int:
        """Remove expired entries from memory cache."""
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self.memory_cache.items():
            if self._is_expired(entry, current_time):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    def _normalize_key(self, key: str) -> str:
        """Normalize cache key for consistency."""
        # Create a hash for very long keys
        if len(key) > 250:
            return hashlib.sha256(key.encode()).hexdigest()
        return key.replace(' ', '_').lower()
    
    def _is_expired(self, entry: Dict[str, Any], current_time: Optional[float] = None) -> bool:
        """Check if cache entry is expired."""
        if current_time is None:
            current_time = time.time()
        
        return (current_time - entry['timestamp']) > entry['ttl']


class StreamlitCacheManager:
    """Streamlit-specific cache manager using session state."""
    
    def __init__(self):
        """Initialize Streamlit cache manager."""
        if 'cache_manager' not in st.session_state:
            st.session_state.cache_manager = CacheManager()
        
        self.cache = st.session_state.cache_manager
    
    def cache_file_content(self, file_hash: str, content: str, ttl: int = 1800) -> bool:
        """Cache processed file content."""
        return self.cache.set(f"file_content_{file_hash}", content, ttl)
    
    def get_cached_file_content(self, file_hash: str) -> Optional[str]:
        """Get cached file content."""
        return self.cache.get(f"file_content_{file_hash}")
    
    def cache_html_output(self, content_hash: str, html: str, ttl: int = 3600) -> bool:
        """Cache generated HTML output."""
        return self.cache.set(f"html_output_{content_hash}", html, ttl)
    
    def get_cached_html_output(self, content_hash: str) -> Optional[str]:
        """Get cached HTML output."""
        return self.cache.get(f"html_output_{content_hash}")
    
    def cache_style_preview(self, style_hash: str, preview: str, ttl: int = 7200) -> bool:
        """Cache style preview."""
        return self.cache.set(f"style_preview_{style_hash}", preview, ttl)
    
    def get_cached_style_preview(self, style_hash: str) -> Optional[str]:
        """Get cached style preview."""
        return self.cache.get(f"style_preview_{style_hash}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for display."""
        return self.cache.get_stats()


def generate_content_hash(content: Union[str, bytes]) -> str:
    """Generate hash for content caching."""
    if isinstance(content, str):
        content = content.encode('utf-8')
    return hashlib.sha256(content).hexdigest()[:16]


def generate_style_hash(style_config) -> str:
    """Generate hash for style configuration."""
    if hasattr(style_config, 'model_dump'):
        config_str = json.dumps(style_config.model_dump(), sort_keys=True)
    elif hasattr(style_config, 'dict'):  # Fallback for older Pydantic versions
        config_str = json.dumps(style_config.dict(), sort_keys=True)
    else:
        config_str = str(style_config)
    return hashlib.sha256(config_str.encode()).hexdigest()[:16]


# Global cache instance for Streamlit
@st.cache_resource
def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    return CacheManager()