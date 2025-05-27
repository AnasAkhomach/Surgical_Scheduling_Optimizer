"""
WebSocket Progress Callback for Task 3.1.

This module provides real-time optimization progress streaming via WebSocket.
Integrates with the optimization engine to broadcast progress updates to connected clients.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Create a base ProgressCallback class since enhanced_tabu_optimizer might not be available
class ProgressCallback:
    """Base progress callback class."""

    async def on_iteration_complete(self, iteration: int, current_score: float, best_score: float, **kwargs):
        """Called when an optimization iteration completes."""
        pass

    async def on_phase_change(self, phase: str, **kwargs):
        """Called when optimization phase changes."""
        pass

    async def on_optimization_start(self, **kwargs):
        """Called when optimization starts."""
        pass

    async def on_optimization_complete(self, final_score: float, total_iterations: int, **kwargs):
        """Called when optimization completes."""
        pass

    async def on_optimization_error(self, error: Exception, **kwargs):
        """Called when optimization encounters an error."""
        pass
from websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class WebSocketProgressCallback(ProgressCallback):
    """
    Progress callback that broadcasts optimization progress via WebSocket.

    Extends the base ProgressCallback to provide real-time updates to connected clients.
    """

    def __init__(
        self,
        optimization_id: str,
        user_id: int,
        total_iterations: int,
        update_interval: int = 10
    ):
        """
        Initialize WebSocket progress callback.

        Args:
            optimization_id: Unique optimization session ID
            user_id: User who started the optimization
            total_iterations: Total number of planned iterations
            update_interval: How often to send updates (every N iterations)
        """
        super().__init__()
        self.optimization_id = optimization_id
        self.user_id = user_id
        self.total_iterations = total_iterations
        self.update_interval = update_interval

        # Progress tracking
        self.start_time = time.time()
        self.last_update_time = time.time()
        self.last_update_iteration = 0
        self.best_score_history = []
        self.current_phase = "initialization"

        # Performance metrics
        self.iterations_per_second = 0.0
        self.estimated_completion_time = None

        logger.info(f"WebSocket progress callback initialized for optimization {optimization_id}")

    async def on_iteration_complete(
        self,
        iteration: int,
        current_score: float,
        best_score: float,
        **kwargs
    ):
        """
        Called when an optimization iteration completes.

        Args:
            iteration: Current iteration number
            current_score: Score of current solution
            best_score: Best score found so far
            **kwargs: Additional optimization data
        """
        try:
            # Update progress tracking
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            # Calculate performance metrics
            if iteration > 0:
                self.iterations_per_second = iteration / elapsed_time
                if self.iterations_per_second > 0:
                    remaining_iterations = self.total_iterations - iteration
                    self.estimated_completion_time = remaining_iterations / self.iterations_per_second

            # Track best score history
            self.best_score_history.append({
                "iteration": iteration,
                "score": best_score,
                "timestamp": current_time
            })

            # Send update if interval reached
            if iteration % self.update_interval == 0 or iteration == self.total_iterations:
                await self._send_progress_update(
                    iteration, current_score, best_score, elapsed_time, **kwargs
                )

                self.last_update_time = current_time
                self.last_update_iteration = iteration

        except Exception as e:
            logger.error(f"Error in WebSocket progress callback: {e}")

    async def on_phase_change(self, phase: str, **kwargs):
        """
        Called when optimization phase changes.

        Args:
            phase: New optimization phase
            **kwargs: Additional phase data
        """
        try:
            self.current_phase = phase

            # Send phase change update
            await self._send_progress_update(
                self.last_update_iteration,
                kwargs.get("current_score", 0),
                kwargs.get("best_score", 0),
                time.time() - self.start_time,
                phase_changed=True,
                **kwargs
            )

            logger.info(f"Optimization {self.optimization_id} entered phase: {phase}")

        except Exception as e:
            logger.error(f"Error handling phase change: {e}")

    async def on_optimization_start(self, **kwargs):
        """
        Called when optimization starts.

        Args:
            **kwargs: Optimization start data
        """
        try:
            self.current_phase = "starting"

            await websocket_manager.broadcast_optimization_progress(
                user_id=self.user_id,
                optimization_id=self.optimization_id,
                progress_percentage=0.0,
                current_iteration=0,
                total_iterations=self.total_iterations,
                time_elapsed=0.0,
                status="starting",
                phase=self.current_phase
            )

            logger.info(f"Optimization {self.optimization_id} started")

        except Exception as e:
            logger.error(f"Error handling optimization start: {e}")

    async def on_optimization_complete(
        self,
        final_score: float,
        total_iterations: int,
        **kwargs
    ):
        """
        Called when optimization completes.

        Args:
            final_score: Final optimization score
            total_iterations: Total iterations completed
            **kwargs: Additional completion data
        """
        try:
            elapsed_time = time.time() - self.start_time
            self.current_phase = "completed"

            await websocket_manager.broadcast_optimization_progress(
                user_id=self.user_id,
                optimization_id=self.optimization_id,
                progress_percentage=100.0,
                current_iteration=total_iterations,
                total_iterations=self.total_iterations,
                current_score=final_score,
                best_score=final_score,
                time_elapsed=elapsed_time,
                status="completed",
                phase=self.current_phase
            )

            # Send completion notification
            await websocket_manager.broadcast_system_notification(
                notification_type="optimization_complete",
                title="Optimization Complete",
                message=f"Schedule optimization completed with score {final_score:.2f}",
                severity="success",
                target_users=[self.user_id]
            )

            logger.info(f"Optimization {self.optimization_id} completed with score {final_score}")

        except Exception as e:
            logger.error(f"Error handling optimization completion: {e}")

    async def on_optimization_error(self, error: Exception, **kwargs):
        """
        Called when optimization encounters an error.

        Args:
            error: The error that occurred
            **kwargs: Additional error data
        """
        try:
            elapsed_time = time.time() - self.start_time
            self.current_phase = "error"

            await websocket_manager.broadcast_optimization_progress(
                user_id=self.user_id,
                optimization_id=self.optimization_id,
                progress_percentage=0.0,
                current_iteration=self.last_update_iteration,
                total_iterations=self.total_iterations,
                time_elapsed=elapsed_time,
                status="failed",
                phase=self.current_phase
            )

            # Send error notification
            await websocket_manager.broadcast_system_notification(
                notification_type="optimization_error",
                title="Optimization Failed",
                message=f"Schedule optimization failed: {str(error)}",
                severity="error",
                target_users=[self.user_id]
            )

            logger.error(f"Optimization {self.optimization_id} failed: {error}")

        except Exception as e:
            logger.error(f"Error handling optimization error: {e}")

    async def _send_progress_update(
        self,
        iteration: int,
        current_score: float,
        best_score: float,
        elapsed_time: float,
        phase_changed: bool = False,
        **kwargs
    ):
        """
        Send progress update via WebSocket.

        Args:
            iteration: Current iteration
            current_score: Current solution score
            best_score: Best score so far
            elapsed_time: Time elapsed since start
            phase_changed: Whether this is a phase change update
            **kwargs: Additional update data
        """
        try:
            # Calculate progress percentage
            progress_percentage = min((iteration / self.total_iterations) * 100, 100.0)

            # Determine status
            status = "running"
            if iteration >= self.total_iterations:
                status = "completed"
            elif phase_changed:
                status = "phase_change"

            await websocket_manager.broadcast_optimization_progress(
                user_id=self.user_id,
                optimization_id=self.optimization_id,
                progress_percentage=progress_percentage,
                current_iteration=iteration,
                total_iterations=self.total_iterations,
                current_score=current_score,
                best_score=best_score,
                time_elapsed=elapsed_time,
                estimated_time_remaining=self.estimated_completion_time,
                status=status,
                phase=self.current_phase
            )

        except Exception as e:
            logger.error(f"Error sending progress update: {e}")

    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get a summary of optimization progress.

        Returns:
            Dict containing progress summary
        """
        elapsed_time = time.time() - self.start_time

        return {
            "optimization_id": self.optimization_id,
            "user_id": self.user_id,
            "current_phase": self.current_phase,
            "last_iteration": self.last_update_iteration,
            "total_iterations": self.total_iterations,
            "elapsed_time": elapsed_time,
            "iterations_per_second": self.iterations_per_second,
            "estimated_completion_time": self.estimated_completion_time,
            "best_score_history": self.best_score_history[-10:],  # Last 10 scores
            "start_time": self.start_time
        }


def create_websocket_progress_callback(
    optimization_id: str,
    user_id: int,
    total_iterations: int,
    update_interval: int = 10
) -> WebSocketProgressCallback:
    """
    Factory function to create a WebSocket progress callback.

    Args:
        optimization_id: Unique optimization session ID
        user_id: User who started the optimization
        total_iterations: Total number of planned iterations
        update_interval: How often to send updates (every N iterations)

    Returns:
        WebSocketProgressCallback instance
    """
    return WebSocketProgressCallback(
        optimization_id=optimization_id,
        user_id=user_id,
        total_iterations=total_iterations,
        update_interval=update_interval
    )
