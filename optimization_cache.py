"""
Optimization result caching system for Task 2.1.

This module provides caching functionality for optimization results to improve
performance and avoid redundant computations.
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict

from api.models import (
    AdvancedOptimizationParameters,
    OptimizationResult,
    OptimizationCache
)

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for optimization cache."""
    max_cache_size: int = 1000
    default_ttl_hours: int = 24
    cleanup_interval_hours: int = 6
    enable_compression: bool = True


class OptimizationCacheManager:
    """
    Manager for optimization result caching.
    
    Features:
    - Parameter-based cache keys
    - TTL-based expiration
    - LRU eviction
    - Cache statistics
    - Compression support
    """
    
    def __init__(self, config: CacheConfig = None):
        """
        Initialize cache manager.
        
        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self.cache: Dict[str, OptimizationCache] = {}
        self.access_times: Dict[str, datetime] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_requests': 0
        }
        
        logger.info(f"Cache manager initialized with max size: {self.config.max_cache_size}")
    
    def generate_cache_key(self, parameters: AdvancedOptimizationParameters, surgeries_hash: str) -> str:
        """
        Generate a cache key based on optimization parameters and data.
        
        Args:
            parameters: Optimization parameters
            surgeries_hash: Hash of surgery data
            
        Returns:
            Cache key string
        """
        # Create a normalized parameter dict for hashing
        param_dict = {
            'schedule_date': parameters.schedule_date.isoformat() if parameters.schedule_date else None,
            'max_iterations': parameters.max_iterations,
            'tabu_tenure': parameters.tabu_tenure,
            'max_no_improvement': parameters.max_no_improvement,
            'algorithm': parameters.algorithm.value,
            'weights': parameters.weights or {},
            'diversification_threshold': parameters.diversification_threshold,
            'intensification_threshold': parameters.intensification_threshold,
            'surgeries_hash': surgeries_hash
        }
        
        # Sort keys for consistent hashing
        param_str = json.dumps(param_dict, sort_keys=True)
        cache_key = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        
        logger.debug(f"Generated cache key: {cache_key}")
        return cache_key
    
    def generate_surgeries_hash(self, surgeries: List[Any]) -> str:
        """
        Generate a hash for the surgery data.
        
        Args:
            surgeries: List of surgery objects
            
        Returns:
            Hash string representing the surgery data
        """
        surgery_data = []
        for surgery in surgeries:
            surgery_info = {
                'surgery_id': surgery.surgery_id,
                'surgery_type_id': surgery.surgery_type_id,
                'duration_minutes': surgery.duration_minutes,
                'urgency_level': surgery.urgency_level,
                'patient_id': surgery.patient_id,
                'surgeon_id': surgery.surgeon_id
            }
            surgery_data.append(surgery_info)
        
        # Sort by surgery_id for consistent hashing
        surgery_data.sort(key=lambda x: x['surgery_id'])
        data_str = json.dumps(surgery_data, sort_keys=True)
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[OptimizationResult]:
        """
        Retrieve optimization result from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached optimization result or None if not found/expired
        """
        self.stats['total_requests'] += 1
        
        if cache_key not in self.cache:
            self.stats['misses'] += 1
            logger.debug(f"Cache miss for key: {cache_key}")
            return None
        
        cached_item = self.cache[cache_key]
        
        # Check if expired
        if datetime.now() > cached_item.expires_at:
            logger.debug(f"Cache entry expired for key: {cache_key}")
            self._remove(cache_key)
            self.stats['misses'] += 1
            return None
        
        # Update access time and hit count
        self.access_times[cache_key] = datetime.now()
        cached_item.hit_count += 1
        self.stats['hits'] += 1
        
        logger.debug(f"Cache hit for key: {cache_key}")
        
        # Mark result as cached
        result = cached_item.result
        result.cached = True
        
        return result
    
    def put(
        self, 
        cache_key: str, 
        result: OptimizationResult, 
        parameters: AdvancedOptimizationParameters,
        ttl_hours: Optional[int] = None
    ):
        """
        Store optimization result in cache.
        
        Args:
            cache_key: Cache key
            result: Optimization result to cache
            parameters: Parameters used for optimization
            ttl_hours: Time to live in hours (uses default if None)
        """
        # Check cache size and evict if necessary
        if len(self.cache) >= self.config.max_cache_size:
            self._evict_lru()
        
        # Calculate expiration time
        ttl = ttl_hours or self.config.default_ttl_hours
        expires_at = datetime.now() + timedelta(hours=ttl)
        
        # Create cache entry
        cache_entry = OptimizationCache(
            cache_key=cache_key,
            parameters_hash=self._hash_parameters(parameters),
            result=result,
            created_at=datetime.now(),
            expires_at=expires_at,
            hit_count=0
        )
        
        # Store in cache
        self.cache[cache_key] = cache_entry
        self.access_times[cache_key] = datetime.now()
        
        logger.debug(f"Cached result for key: {cache_key}, expires: {expires_at}")
    
    def invalidate(self, cache_key: str):
        """
        Invalidate a specific cache entry.
        
        Args:
            cache_key: Cache key to invalidate
        """
        if cache_key in self.cache:
            self._remove(cache_key)
            logger.debug(f"Invalidated cache entry: {cache_key}")
    
    def invalidate_by_date(self, schedule_date):
        """
        Invalidate all cache entries for a specific schedule date.
        
        Args:
            schedule_date: Date to invalidate
        """
        keys_to_remove = []
        for key, cache_entry in self.cache.items():
            if (cache_entry.result.parameters_used.schedule_date and 
                cache_entry.result.parameters_used.schedule_date == schedule_date):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._remove(key)
        
        logger.info(f"Invalidated {len(keys_to_remove)} cache entries for date: {schedule_date}")
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        now = datetime.now()
        expired_keys = [
            key for key, cache_entry in self.cache.items()
            if now > cache_entry.expires_at
        ]
        
        for key in expired_keys:
            self._remove(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        hit_rate = (self.stats['hits'] / self.stats['total_requests'] 
                   if self.stats['total_requests'] > 0 else 0)
        
        return {
            'cache_size': len(self.cache),
            'max_cache_size': self.config.max_cache_size,
            'hit_rate': hit_rate,
            'total_hits': self.stats['hits'],
            'total_misses': self.stats['misses'],
            'total_requests': self.stats['total_requests'],
            'evictions': self.stats['evictions']
        }
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_times.clear()
        logger.info("Cache cleared")
    
    def _remove(self, cache_key: str):
        """Remove a cache entry."""
        if cache_key in self.cache:
            del self.cache[cache_key]
        if cache_key in self.access_times:
            del self.access_times[cache_key]
    
    def _evict_lru(self):
        """Evict least recently used cache entry."""
        if not self.access_times:
            return
        
        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        self._remove(lru_key)
        self.stats['evictions'] += 1
        
        logger.debug(f"Evicted LRU cache entry: {lru_key}")
    
    def _hash_parameters(self, parameters: AdvancedOptimizationParameters) -> str:
        """Generate hash for parameters."""
        param_dict = {
            'max_iterations': parameters.max_iterations,
            'tabu_tenure': parameters.tabu_tenure,
            'algorithm': parameters.algorithm.value,
            'weights': parameters.weights or {}
        }
        
        param_str = json.dumps(param_dict, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> OptimizationCacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = OptimizationCacheManager()
    return _cache_manager


def configure_cache(config: CacheConfig):
    """Configure the global cache manager."""
    global _cache_manager
    _cache_manager = OptimizationCacheManager(config)
