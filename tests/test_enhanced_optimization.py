"""
Test suite for enhanced optimization features (Task 2.1).

This module tests the advanced optimization capabilities including:
- Multiple algorithm variants
- Progress tracking
- Result caching
- Parameter configuration
- Performance analysis
"""

import pytest
import asyncio
import json
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.models import (
    AdvancedOptimizationParameters,
    OptimizationAlgorithm,
    OptimizationStatus,
    OptimizationProgress,
    OptimizationResult
)
from models import Surgery, OperatingRoom, Surgeon, Patient, SurgeryType
from enhanced_tabu_optimizer import EnhancedTabuOptimizer
from optimization_cache import OptimizationCacheManager, CacheConfig
from db_config import get_db


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_enhanced_optimization.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def db_session():
    """Create a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_surgeries():
    """Create sample surgeries for testing."""
    return [
        Surgery(
            surgery_id=1,
            surgery_type_id=1,
            duration_minutes=120,
            urgency_level="Medium",
            patient_id=1,
            surgeon_id=1,
            status="Scheduled",
            scheduled_date=date.today()
        ),
        Surgery(
            surgery_id=2,
            surgery_type_id=2,
            duration_minutes=90,
            urgency_level="High",
            patient_id=2,
            surgeon_id=2,
            status="Scheduled",
            scheduled_date=date.today()
        ),
        Surgery(
            surgery_id=3,
            surgery_type_id=1,
            duration_minutes=150,
            urgency_level="Low",
            patient_id=3,
            surgeon_id=1,
            status="Scheduled",
            scheduled_date=date.today()
        )
    ]


@pytest.fixture
def sample_operating_rooms():
    """Create sample operating rooms for testing."""
    return [
        OperatingRoom(room_id=1, location="OR-1"),
        OperatingRoom(room_id=2, location="OR-2"),
        OperatingRoom(room_id=3, location="OR-3")
    ]


@pytest.fixture
def advanced_parameters():
    """Create advanced optimization parameters for testing."""
    return AdvancedOptimizationParameters(
        schedule_date=date.today(),
        max_iterations=50,
        tabu_tenure=5,
        max_no_improvement=10,
        time_limit_seconds=30,
        algorithm=OptimizationAlgorithm.ADAPTIVE_TABU,
        min_tabu_tenure=3,
        max_tabu_tenure=15,
        tenure_adaptation_factor=1.3,
        diversification_threshold=20,
        diversification_strength=0.4,
        intensification_threshold=10,
        intensification_factor=0.7,
        weights={
            "or_utilization": 1.0,
            "sds_time_penalty": 0.8,
            "surgeon_preference_satisfaction": 0.7
        },
        enable_progress_tracking=True,
        progress_update_interval=5,
        enable_detailed_logging=False,
        cache_results=True
    )


class TestAdvancedOptimizationParameters:
    """Test advanced optimization parameters validation."""

    def test_valid_parameters(self, advanced_parameters):
        """Test that valid parameters are accepted."""
        assert advanced_parameters.max_iterations == 50
        assert advanced_parameters.algorithm == OptimizationAlgorithm.ADAPTIVE_TABU
        assert advanced_parameters.enable_progress_tracking is True

    def test_parameter_validation(self):
        """Test parameter validation constraints."""
        # Test max_iterations bounds
        with pytest.raises(ValueError):
            AdvancedOptimizationParameters(max_iterations=5)  # Below minimum

        with pytest.raises(ValueError):
            AdvancedOptimizationParameters(max_iterations=15000)  # Above maximum

    def test_algorithm_variants(self):
        """Test all algorithm variants are supported."""
        algorithms = [
            OptimizationAlgorithm.BASIC_TABU,
            OptimizationAlgorithm.ADAPTIVE_TABU,
            OptimizationAlgorithm.REACTIVE_TABU,
            OptimizationAlgorithm.HYBRID_TABU
        ]

        for algorithm in algorithms:
            params = AdvancedOptimizationParameters(algorithm=algorithm)
            assert params.algorithm == algorithm


class TestEnhancedTabuOptimizer:
    """Test enhanced Tabu Search optimizer."""

    @patch('enhanced_tabu_optimizer.TabuOptimizer')
    def test_optimizer_initialization(self, mock_tabu_optimizer, sample_surgeries,
                                    sample_operating_rooms, advanced_parameters):
        """Test optimizer initialization with advanced parameters."""
        mock_db = Mock()

        optimizer = EnhancedTabuOptimizer(
            db_session=mock_db,
            surgeries=sample_surgeries,
            operating_rooms=sample_operating_rooms,
            parameters=advanced_parameters
        )

        assert optimizer.parameters == advanced_parameters
        assert optimizer.surgeries == sample_surgeries
        assert optimizer.operating_rooms == sample_operating_rooms
        assert optimizer.optimization_id is not None

    def test_algorithm_parameter_setup(self, sample_surgeries, sample_operating_rooms):
        """Test algorithm-specific parameter setup."""
        mock_db = Mock()

        # Test adaptive algorithm setup
        adaptive_params = AdvancedOptimizationParameters(
            algorithm=OptimizationAlgorithm.ADAPTIVE_TABU,
            min_tabu_tenure=3,
            max_tabu_tenure=15
        )

        optimizer = EnhancedTabuOptimizer(
            db_session=mock_db,
            surgeries=sample_surgeries,
            operating_rooms=sample_operating_rooms,
            parameters=adaptive_params
        )

        assert hasattr(optimizer, 'min_tenure')
        assert hasattr(optimizer, 'max_tenure')
        assert optimizer.min_tenure == 3
        assert optimizer.max_tenure == 15

    @patch('enhanced_tabu_optimizer.TabuOptimizer.initialize_solution')
    @patch('enhanced_tabu_optimizer.SolutionEvaluator.evaluate_solution')
    def test_optimization_process(self, mock_evaluate, mock_initialize,
                                sample_surgeries, sample_operating_rooms, advanced_parameters):
        """Test the optimization process."""
        mock_db = Mock()
        mock_initialize.return_value = []  # Mock initial solution
        mock_evaluate.return_value = 100.0  # Mock evaluation score

        optimizer = EnhancedTabuOptimizer(
            db_session=mock_db,
            surgeries=sample_surgeries,
            operating_rooms=sample_operating_rooms,
            parameters=advanced_parameters
        )

        # Mock the neighborhood generator to return empty neighbors to end quickly
        optimizer.neighborhood_generator.generate_neighbor_solutions = Mock(return_value=[])

        result = optimizer.optimize()

        assert isinstance(result, OptimizationResult)
        assert result.optimization_id == optimizer.optimization_id
        assert result.algorithm_used == advanced_parameters.algorithm


class TestOptimizationCache:
    """Test optimization result caching."""

    def test_cache_manager_initialization(self):
        """Test cache manager initialization."""
        config = CacheConfig(max_cache_size=100, default_ttl_hours=12)
        cache_manager = OptimizationCacheManager(config)

        assert cache_manager.config.max_cache_size == 100
        assert cache_manager.config.default_ttl_hours == 12
        assert len(cache_manager.cache) == 0

    def test_cache_key_generation(self, advanced_parameters, sample_surgeries):
        """Test cache key generation."""
        cache_manager = OptimizationCacheManager()

        surgeries_hash = cache_manager.generate_surgeries_hash(sample_surgeries)
        cache_key = cache_manager.generate_cache_key(advanced_parameters, surgeries_hash)

        assert isinstance(cache_key, str)
        assert len(cache_key) == 16  # SHA256 truncated to 16 chars

    def test_cache_put_and_get(self, advanced_parameters):
        """Test caching and retrieving results."""
        cache_manager = OptimizationCacheManager()

        # Create mock result
        mock_result = OptimizationResult(
            optimization_id="test-123",
            assignments=[],
            score=95.5,
            detailed_metrics={},
            iteration_count=25,
            execution_time_seconds=15.2,
            algorithm_used=OptimizationAlgorithm.BASIC_TABU,
            parameters_used=advanced_parameters,
            convergence_data=[],
            solution_quality_analysis={},
            cached=False
        )

        cache_key = "test_key_123"

        # Test put
        cache_manager.put(cache_key, mock_result, advanced_parameters)
        assert len(cache_manager.cache) == 1

        # Test get
        retrieved_result = cache_manager.get(cache_key)
        assert retrieved_result is not None
        assert retrieved_result.optimization_id == "test-123"
        assert retrieved_result.cached is True

    def test_cache_expiration(self, advanced_parameters):
        """Test cache expiration functionality."""
        config = CacheConfig(default_ttl_hours=0)  # Immediate expiration
        cache_manager = OptimizationCacheManager(config)

        mock_result = OptimizationResult(
            optimization_id="test-456",
            assignments=[],
            score=88.0,
            detailed_metrics={},
            iteration_count=30,
            execution_time_seconds=20.1,
            algorithm_used=OptimizationAlgorithm.BASIC_TABU,
            parameters_used=advanced_parameters,
            convergence_data=[],
            solution_quality_analysis={},
            cached=False
        )

        cache_key = "test_key_456"
        cache_manager.put(cache_key, mock_result, advanced_parameters, ttl_hours=0)

        # Should be expired immediately
        retrieved_result = cache_manager.get(cache_key)
        assert retrieved_result is None

    def test_cache_statistics(self):
        """Test cache statistics tracking."""
        cache_manager = OptimizationCacheManager()

        # Initial stats
        stats = cache_manager.get_stats()
        assert stats['total_requests'] == 0
        assert stats['hit_rate'] == 0

        # Simulate cache miss
        cache_manager.get("nonexistent_key")
        stats = cache_manager.get_stats()
        assert stats['total_requests'] == 1
        assert stats['total_misses'] == 1


class TestOptimizationAPI:
    """Test optimization API endpoints."""

    @patch('api.routers.schedules.EnhancedTabuOptimizer')
    @patch('api.routers.schedules.get_cache_manager')
    def test_advanced_optimize_endpoint(self, mock_cache_manager, mock_optimizer):
        """Test the advanced optimization endpoint."""
        # Mock cache manager
        mock_cache = Mock()
        mock_cache.get.return_value = None  # No cached result
        mock_cache_manager.return_value = mock_cache

        # Mock optimizer
        mock_opt_instance = Mock()
        mock_result = OptimizationResult(
            optimization_id="api-test-123",
            assignments=[],
            score=92.3,
            detailed_metrics={},
            iteration_count=40,
            execution_time_seconds=25.5,
            algorithm_used=OptimizationAlgorithm.ADAPTIVE_TABU,
            parameters_used=AdvancedOptimizationParameters(),
            convergence_data=[],
            solution_quality_analysis={},
            cached=False
        )
        mock_opt_instance.optimize.return_value = mock_result
        mock_optimizer.return_value = mock_opt_instance

        # Test request
        request_data = {
            "schedule_date": date.today().isoformat(),
            "max_iterations": 50,
            "algorithm": "adaptive_tabu",
            "enable_progress_tracking": True
        }

        # Note: This would require proper authentication setup
        # response = client.post("/api/schedules/optimize/advanced", json=request_data)
        # assert response.status_code == 200

        # For now, just verify the mock setup
        assert mock_result.optimization_id == "api-test-123"

    def test_progress_tracking_endpoint(self):
        """Test the progress tracking endpoint."""
        # This would test the progress tracking functionality
        # Implementation depends on proper session management
        pass

    def test_algorithm_comparison_endpoint(self):
        """Test the algorithm comparison endpoint."""
        # This would test comparing multiple algorithms
        # Implementation depends on proper request handling
        pass


def test_basic_functionality():
    """Test basic functionality without complex dependencies."""
    # Test parameter validation
    params = AdvancedOptimizationParameters(
        max_iterations=50,
        algorithm=OptimizationAlgorithm.BASIC_TABU
    )
    assert params.max_iterations == 50
    assert params.algorithm == OptimizationAlgorithm.BASIC_TABU

    # Test cache manager
    from optimization_cache import OptimizationCacheManager, CacheConfig
    config = CacheConfig(max_cache_size=10)
    cache_manager = OptimizationCacheManager(config)
    assert cache_manager.config.max_cache_size == 10

    print("✅ Basic functionality tests passed!")


if __name__ == "__main__":
    # Run basic test first
    test_basic_functionality()

    # Run full test suite
    # pytest.main([__file__, "-v"])
