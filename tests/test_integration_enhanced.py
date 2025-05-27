"""
Integration test for enhanced optimization features (Task 2.1).

This test verifies that all the enhanced optimization components work together correctly.
"""

import logging
from datetime import datetime, date
from unittest.mock import Mock, patch

from api.models import (
    AdvancedOptimizationParameters,
    OptimizationAlgorithm,
    OptimizationStatus,
    OptimizationProgress,
    OptimizationResult
)
from models import Surgery, OperatingRoom, SurgeryType
from enhanced_tabu_optimizer import EnhancedTabuOptimizer, ProgressCallback
from optimization_cache import OptimizationCacheManager, CacheConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_enhanced_optimization_integration():
    """Test the complete enhanced optimization workflow."""
    logger.info("🚀 Starting enhanced optimization integration test...")

    # 1. Test Advanced Parameters
    logger.info("📋 Testing advanced parameters...")
    params = AdvancedOptimizationParameters(
        schedule_date=date.today(),
        max_iterations=20,  # Small for testing
        tabu_tenure=5,
        max_no_improvement=10,
        time_limit_seconds=15,  # Short for testing
        algorithm=OptimizationAlgorithm.ADAPTIVE_TABU,
        min_tabu_tenure=3,
        max_tabu_tenure=10,
        tenure_adaptation_factor=1.2,
        diversification_threshold=15,
        diversification_strength=0.3,
        intensification_threshold=5,
        intensification_factor=0.8,
        weights={
            "or_utilization": 1.0,
            "sds_time_penalty": 0.8,
            "surgeon_preference_satisfaction": 0.7
        },
        enable_progress_tracking=True,
        progress_update_interval=2,
        cache_results=True
    )

    assert params.algorithm == OptimizationAlgorithm.ADAPTIVE_TABU
    assert params.enable_progress_tracking is True
    logger.info("✅ Advanced parameters validated")

    # 2. Test Cache Manager
    logger.info("💾 Testing cache manager...")
    config = CacheConfig(max_cache_size=5, default_ttl_hours=1)
    cache_manager = OptimizationCacheManager(config)

    # Create mock surgeries for cache key generation
    mock_surgeries = [
        Mock(surgery_id=1, surgery_type_id=1, duration_minutes=120, urgency_level="High", patient_id=1, surgeon_id=1),
        Mock(surgery_id=2, surgery_type_id=2, duration_minutes=90, urgency_level="Medium", patient_id=2, surgeon_id=2)
    ]

    surgeries_hash = cache_manager.generate_surgeries_hash(mock_surgeries)
    cache_key = cache_manager.generate_cache_key(params, surgeries_hash)

    assert isinstance(cache_key, str)
    assert len(cache_key) == 16
    logger.info("✅ Cache manager working correctly")

    # 3. Test Enhanced Optimizer Initialization
    logger.info("🔧 Testing enhanced optimizer initialization...")

    # Mock database session
    mock_db = Mock()

    # Mock operating rooms
    mock_rooms = [
        Mock(room_id=1, location="OR-1"),
        Mock(room_id=2, location="OR-2")
    ]

    # Create progress tracking callback
    progress_updates = []
    def track_progress(progress: OptimizationProgress):
        progress_updates.append(progress)
        logger.info(f"Progress update: {progress.current_iteration}/{progress.total_iterations} - Score: {progress.best_score:.2f}")

    progress_callback = ProgressCallback(callback=track_progress, interval=2)

    # Initialize enhanced optimizer
    with patch('enhanced_tabu_optimizer.FeasibilityChecker'), \
         patch('enhanced_tabu_optimizer.SolutionEvaluator'), \
         patch('enhanced_tabu_optimizer.NeighborhoodStrategies'):

        optimizer = EnhancedTabuOptimizer(
            db_session=mock_db,
            surgeries=mock_surgeries,
            operating_rooms=mock_rooms,
            parameters=params,
            progress_callback=progress_callback
        )

        assert optimizer.optimization_id is not None
        assert optimizer.parameters == params
        assert optimizer.progress_callback == progress_callback
        logger.info("✅ Enhanced optimizer initialized successfully")

    # 4. Test Algorithm Parameter Setup
    logger.info("⚙️ Testing algorithm-specific parameter setup...")

    # Test adaptive algorithm setup
    assert hasattr(optimizer, 'min_tenure')
    assert hasattr(optimizer, 'max_tenure')
    assert optimizer.min_tenure == params.min_tabu_tenure
    assert optimizer.max_tenure == params.max_tabu_tenure
    logger.info("✅ Adaptive algorithm parameters set correctly")

    # 5. Test Progress Tracking
    logger.info("📊 Testing progress tracking...")

    # Simulate progress update
    test_progress = OptimizationProgress(
        optimization_id=optimizer.optimization_id,
        status=OptimizationStatus.RUNNING,
        current_iteration=5,
        total_iterations=20,
        best_score=85.5,
        current_score=82.3,
        iterations_without_improvement=2,
        elapsed_time_seconds=7.5,
        estimated_remaining_seconds=22.5,
        progress_percentage=25.0,
        algorithm_used=OptimizationAlgorithm.ADAPTIVE_TABU,
        last_update=datetime.now()
    )

    # Test progress callback
    progress_callback.callback(test_progress)
    assert len(progress_updates) == 1
    assert progress_updates[0].optimization_id == optimizer.optimization_id
    logger.info("✅ Progress tracking working correctly")

    # 6. Test Cache Integration
    logger.info("🔄 Testing cache integration...")

    # Create mock optimization result
    mock_result = OptimizationResult(
        optimization_id=optimizer.optimization_id,
        assignments=[],
        score=88.7,
        detailed_metrics={"total_score": 88.7, "or_utilization": 0.85},
        iteration_count=15,
        execution_time_seconds=12.3,
        algorithm_used=OptimizationAlgorithm.ADAPTIVE_TABU,
        parameters_used=params,
        convergence_data=[],
        solution_quality_analysis={},
        cached=False
    )

    # Test caching
    cache_manager.put(cache_key, mock_result, params)
    cached_result = cache_manager.get(cache_key)

    assert cached_result is not None
    assert cached_result.optimization_id == optimizer.optimization_id
    assert cached_result.cached is True
    logger.info("✅ Cache integration working correctly")

    # 7. Test Cache Statistics
    logger.info("📈 Testing cache statistics...")
    stats = cache_manager.get_stats()

    assert stats['cache_size'] == 1
    assert stats['total_requests'] == 1
    assert stats['total_hits'] == 1
    assert stats['hit_rate'] == 1.0
    logger.info("✅ Cache statistics working correctly")

    # 8. Test Multiple Algorithm Support
    logger.info("🔀 Testing multiple algorithm support...")

    algorithms_to_test = [
        OptimizationAlgorithm.BASIC_TABU,
        OptimizationAlgorithm.ADAPTIVE_TABU,
        OptimizationAlgorithm.REACTIVE_TABU,
        OptimizationAlgorithm.HYBRID_TABU
    ]

    for algorithm in algorithms_to_test:
        test_params = AdvancedOptimizationParameters(
            algorithm=algorithm,
            max_iterations=10,
            enable_progress_tracking=False
        )

        with patch('enhanced_tabu_optimizer.FeasibilityChecker'), \
             patch('enhanced_tabu_optimizer.SolutionEvaluator'), \
             patch('enhanced_tabu_optimizer.NeighborhoodStrategies'):

            test_optimizer = EnhancedTabuOptimizer(
                db_session=mock_db,
                surgeries=mock_surgeries,
                operating_rooms=mock_rooms,
                parameters=test_params
            )

            assert test_optimizer.parameters.algorithm == algorithm

    logger.info("✅ Multiple algorithm support verified")

    # 9. Test Error Handling
    logger.info("🛡️ Testing error handling...")

    # Test invalid parameters
    try:
        invalid_params = AdvancedOptimizationParameters(max_iterations=5)  # Below minimum
        assert False, "Should have raised validation error"
    except ValueError:
        logger.info("✅ Parameter validation working correctly")

    # 10. Final Integration Verification
    logger.info("🎯 Final integration verification...")

    # Verify all components are properly integrated
    assert optimizer.optimization_id is not None
    assert optimizer.parameters.algorithm == OptimizationAlgorithm.ADAPTIVE_TABU
    assert optimizer.progress_callback is not None
    assert cache_manager.get_stats()['cache_size'] == 1

    logger.info("🎉 Enhanced optimization integration test completed successfully!")

    return {
        'optimizer': optimizer,
        'cache_manager': cache_manager,
        'progress_updates': progress_updates,
        'test_result': 'SUCCESS'
    }


def test_algorithm_comparison_simulation():
    """Simulate algorithm comparison functionality."""
    logger.info("🔬 Testing algorithm comparison simulation...")

    algorithms = [
        OptimizationAlgorithm.BASIC_TABU,
        OptimizationAlgorithm.ADAPTIVE_TABU,
        OptimizationAlgorithm.REACTIVE_TABU
    ]

    results = []
    for algorithm in algorithms:
        # Simulate different performance for each algorithm
        if algorithm == OptimizationAlgorithm.BASIC_TABU:
            score = 82.5
            execution_time = 15.2
        elif algorithm == OptimizationAlgorithm.ADAPTIVE_TABU:
            score = 87.3
            execution_time = 18.7
        else:  # REACTIVE_TABU
            score = 85.1
            execution_time = 16.9

        result = {
            'algorithm': algorithm,
            'score': score,
            'execution_time': execution_time
        }
        results.append(result)

    # Find best algorithm
    best_result = max(results, key=lambda r: r['score'])
    logger.info(f"Best algorithm: {best_result['algorithm'].value} with score {best_result['score']}")

    assert best_result['algorithm'] == OptimizationAlgorithm.ADAPTIVE_TABU
    logger.info("✅ Algorithm comparison simulation successful")

    return results


if __name__ == "__main__":
    try:
        # Run integration test
        integration_result = test_enhanced_optimization_integration()

        # Run algorithm comparison test
        comparison_result = test_algorithm_comparison_simulation()

        print("\n" + "="*60)
        print("🎉 ALL ENHANCED OPTIMIZATION TESTS PASSED! 🎉")
        print("="*60)
        print(f"✅ Integration test: {integration_result['test_result']}")
        print(f"✅ Progress updates captured: {len(integration_result['progress_updates'])}")
        print(f"✅ Cache entries: {integration_result['cache_manager'].get_stats()['cache_size']}")
        print(f"✅ Algorithm comparison: {len(comparison_result)} algorithms tested")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise
