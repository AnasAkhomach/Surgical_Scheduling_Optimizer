# This file will contain the core Tabu Search algorithm logic.
import time
import copy
import logging
from tabu_list import TabuList
from datetime import datetime, timedelta # Added for placeholder times
from feasibility_checker import FeasibilityChecker # Import FeasibilityChecker

logger = logging.getLogger(__name__)

class TabuSearchCore:
    def __init__(self, solution_evaluator, neighborhood_generator, initial_solution_assignments, feasibility_checker):
        """
        Initializes the TabuSearchCore.
        Args:
            solution_evaluator: An instance of SolutionEvaluator.
            neighborhood_generator: An instance of NeighborhoodStrategies.
            initial_solution_assignments: The initial set of surgery assignments (list of dicts).
            feasibility_checker: An instance of FeasibilityChecker.
        """
        self.solution_evaluator = solution_evaluator
        self.neighborhood_generator = neighborhood_generator
        self.feasibility_checker = feasibility_checker # Store FeasibilityChecker instance
        logger.info(f"TabuSearchCore __init__: Received initial_solution_assignments with {len(initial_solution_assignments)} items: {initial_solution_assignments}")
        self.initial_solution_assignments = copy.deepcopy(initial_solution_assignments)
        logger.info(f"TabuSearchCore __init__: Stored self.initial_solution_assignments (deep copied) with {len(self.initial_solution_assignments)} items: {self.initial_solution_assignments}")
        logger.info(f"TabuSearchCore __init__: id(self.initial_solution_assignments) after deepcopy: {id(self.initial_solution_assignments)}")
        logger.info("TabuSearchCore initialized.")

    def _perturb_solution(self, solution_assignments, perturbation_factor):
        """Helper method to perturb a solution for intensification/diversification."""
        # This is a placeholder. Actual implementation would depend on the solution structure
        # and desired perturbation strength. Could involve random swaps, shifts, etc.
        perturbed_solution = copy.deepcopy(solution_assignments)
        num_to_perturb = int(len(perturbed_solution) * perturbation_factor)
        if num_to_perturb == 0 and len(perturbed_solution) > 0:
            num_to_perturb = 1 # Perturb at least one if possible

        # Example: Randomly change a small number of assignments (very basic)
        # A more sophisticated perturbation would use neighborhood moves.
        # For now, this is a conceptual placeholder.
        # In a real scenario, you might use self.neighborhood_generator to apply a few random moves.
        logger.info(f"Perturbing solution: {num_to_perturb} elements (conceptual). Factor: {perturbation_factor}")
        # for _ in range(num_to_perturb):
        #     if not perturbed_solution: break
        #     idx_to_change = random.randint(0, len(perturbed_solution) - 1)
            # Modify perturbed_solution[idx_to_change] in some meaningful way
        return perturbed_solution

    def _apply_intensification(self, current_solution_assignments, best_solution_assignments, intensification_params, tabu_list, placeholder_start_time, placeholder_end_time):
        """Applies intensification strategies."""
        if intensification_params and intensification_params.get("type") == "restart_from_best":
            logger.info(f"INTENSIFICATION: Restarting search around new best solution. Perturbing solution.")
            # Perturb the best solution to restart search in its vicinity
            perturbed_best_solution = self._perturb_solution(best_solution_assignments, intensification_params.get("perturbation_factor", 0.05))
            # Check feasibility before accepting the perturbed solution
            if self.feasibility_checker.is_feasible(perturbed_best_solution):
                current_solution_assignments = perturbed_best_solution
                current_score = self.solution_evaluator.evaluate_solution(current_solution_assignments, placeholder_start_time, placeholder_end_time)
                logger.info(f"Intensification: Restarted with perturbed best solution. New current score: {current_score}")
                if intensification_params.get("reset_tabu_list_on_intensify", True):
                    tabu_list.clear()
                    logger.info("Intensification: Tabu list cleared.")
                return current_solution_assignments, current_score
            else:
                logger.warning("Intensification: Perturbed best solution was infeasible. Skipping intensification restart.")
        return current_solution_assignments, self.solution_evaluator.evaluate_solution(current_solution_assignments, placeholder_start_time, placeholder_end_time) # Return original if not intensified

    def _apply_diversification(self, current_solution_assignments, diversification_params, tabu_list, placeholder_start_time, placeholder_end_time):
        """Applies diversification strategies."""
        diversification_type = diversification_params.get("type")
        logger.info(f"DIVERSIFICATION: Triggered. Type: {diversification_type}")
        if diversification_type == "random_restart":
            logger.info("DIVERSIFICATION: Performing random restart.")
            # This requires NeighborhoodStrategies to have a method to generate a completely random (but valid) initial solution.
            # For now, we'll re-initialize from the original initial solution as a basic form of restart.
            # A true random restart would be more effective.
            # random_solution = self.neighborhood_generator.generate_random_solution() # Ideal
            if hasattr(self.neighborhood_generator, 'initialize_solution_randomly'):
                 # Assuming initialize_solution_randomly can generate a diverse feasible solution
                current_solution_assignments = self.neighborhood_generator.initialize_solution_randomly()
            else:
                logger.warning("Diversification: 'initialize_solution_randomly' not found in neighborhood_generator. Re-initializing from initial problem solution as fallback.")
                current_solution_assignments = copy.deepcopy(self.initial_solution_assignments) # Fallback

            if not self.feasibility_checker.is_feasible(current_solution_assignments):
                logger.error("Diversification: Randomly generated/re-initialized solution is infeasible. This should not happen.")
                # Fallback to a known good state or handle error appropriately
                current_solution_assignments = copy.deepcopy(self.initial_solution_assignments) # Safest fallback

            current_score = self.solution_evaluator.evaluate_solution(current_solution_assignments, placeholder_start_time, placeholder_end_time)
            if diversification_params.get("reset_tabu_list_on_diversify", True):
                tabu_list.clear()
                logger.info("Diversification: Tabu list cleared for random restart.")
            return current_solution_assignments, current_score, True # Return True to indicate diversification reset iterations_without_improvement
        elif diversification_type == "increase_tabu_tenure":
            increase_factor = diversification_params.get("factor", 1.5)
            duration = diversification_params.get("duration_iterations", 10)
            tabu_list.increase_all_tenures(factor=increase_factor, duration=duration) # Assuming TabuList supports temporary increase
            logger.info(f"DIVERSIFICATION: Temporarily increasing all tabu tenures by factor {increase_factor} for {duration} iterations.")
        # Add other diversification strategies here
        return current_solution_assignments, self.solution_evaluator.evaluate_solution(current_solution_assignments, placeholder_start_time, placeholder_end_time), False # Return False if iterations_without_improvement not reset

    def search(
        self,
        max_iterations=100,
        tabu_tenure=10,
        max_iterations_without_improvement_ratio=0.25,
        time_limit_seconds=None,
        aspiration_criteria_config=None, # New parameter for aspiration criteria configuration
        intensification_params=None, # Parameters for intensification strategies
        diversification_params=None  # Parameters for diversification strategies
    ):
        """Main Tabu Search optimization loop."""
        # Example intensification_params: {"type": "restart_from_best", "perturbation_factor": 0.1}
        # Example diversification_params: {"type": "random_restart", "reset_tabu_list": True, "perturbation_strength": "medium"}
        # Example diversification_params: {"type": "increase_tabu_tenure", "factor": 1.5, "duration_iterations": 10}

        # Default aspiration criteria: aspire if better than global best
        # Example: aspiration_criteria_config = {"type": "global_best_improvement"}
        # Example: aspiration_criteria_config = {"type": "current_best_improvement"}
        # Example: aspiration_criteria_config = {"type": "component_improvement", "component_name": "sds_time_penalty", "threshold_factor": 0.1}
        if aspiration_criteria_config is None:
            aspiration_criteria_config = {"type": "global_best_improvement"}

        logger.info(
            "Starting Tabu Search with parameters: max_iterations=%s, tabu_tenure=%s, max_iterations_without_improvement_ratio=%s, time_limit_seconds=%s, aspiration_criteria_config=%s",
            max_iterations,
            tabu_tenure,
            max_iterations_without_improvement_ratio,
            time_limit_seconds,
            aspiration_criteria_config,
            intensification_params,
            diversification_params
        )

        logger.info(f"TabuSearchCore search(): id(self.initial_solution_assignments) at start of search: {id(self.initial_solution_assignments)}")
        logger.info(f"TabuSearchCore search(): Type of self.initial_solution_assignments: {type(self.initial_solution_assignments)}")
        logger.info(f"TabuSearchCore search(): Checking self.initial_solution_assignments with {len(self.initial_solution_assignments) if self.initial_solution_assignments is not None and isinstance(self.initial_solution_assignments, list) else 'N/A or not a list'} items: {self.initial_solution_assignments}")
        if not self.initial_solution_assignments or not isinstance(self.initial_solution_assignments, list):
            logger.error("Cannot run Tabu Search: initial solution is empty, not provided, or not a list.")
            return None, -float('inf')

        current_solution_assignments = copy.deepcopy(self.initial_solution_assignments)
        best_solution_assignments = copy.deepcopy(current_solution_assignments)

        # Placeholder schedule times for now - these should ideally be derived from the actual schedule's span
        # or a predefined operational window for the entire scheduling period.
        placeholder_start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        placeholder_end_time = placeholder_start_time + timedelta(days=1) # Assuming a 24-hour window for evaluation context

        current_score = self.solution_evaluator.evaluate_solution(current_solution_assignments, placeholder_start_time, placeholder_end_time)
        best_score = current_score # Initialize best_score with the score of the initial solution
        logger.info(f"Initial solution score: {best_score}")

        # Initialize TabuList with default min and max tenures.
        # These can be tuned. `tabu_tenure` from params is used as default_max_tenure.
        default_min_tabu_tenure = max(1, tabu_tenure // 2)
        tabu_list = TabuList(
            default_max_tenure=tabu_tenure,
            default_min_tenure=default_min_tabu_tenure
        )
        logger.info(f"TabuList initialized with default_max_tenure={tabu_tenure}, default_min_tenure={default_min_tabu_tenure}")

        iterations_without_improvement = 0
        max_iterations_without_improvement = max(
            1, int(max_iterations * max_iterations_without_improvement_ratio)
        )

        # For frequency-based tenure, we might need to track move frequencies.
        # move_frequency_tracker = {} # Example placeholder

        start_time_process = time.process_time()

        for iteration in range(max_iterations):
            logger.info("Iteration %d/%d. Current best score: %s. Tabu list size: %d",
                        iteration + 1, max_iterations, best_score, len(tabu_list.tabu_items) if hasattr(tabu_list, 'tabu_items') else 0)

            # Decrement tenures at the start of the iteration.
            tabu_list.decrement_tenure()

            # Generate neighbor solutions using the NeighborhoodStrategies instance.
            # Pass the tabu_list so the neighborhood generator can optionally use it (e.g., to avoid generating known tabu moves).
            # The core loop will still perform the definitive tabu check and aspiration criteria.
            neighbor_solutions_info = self.neighborhood_generator.generate_neighbor_solutions(
                current_solution_assignments,
                tabu_list # Pass the tabu_list to the neighborhood generator
            )

            if not neighbor_solutions_info:
                logger.info("No neighbors generated by the strategy (or all were filtered by it). Stopping search.")
                break

            best_neighbor_assignments = None
            best_neighbor_score = -float("inf")
            best_neighbor_move_attribute = None # The attribute of the move to be made tabu

            for neighbor_info in neighbor_solutions_info:
                neighbor_assignments = neighbor_info["assignments"]
                # 'move' should be a hashable representation of the change (e.g., (type, item1, item2, new_val))
                move_attribute = neighbor_info["move"]

                # First, check if the generated neighbor is feasible
                # The `is_feasible` method now expects SurgeryRoomAssignment objects.
                # We assume neighbor_assignments are already in this format or compatible.
                # The `check_db_too` parameter in `is_feasible` defaults to True, which is generally desired here.
                if not self.feasibility_checker.is_feasible(neighbor_assignments):
                    logger.debug(f"Neighbor generated by move {move_attribute} is INFEASIBLE. Skipping evaluation.")
                    continue # Skip to the next neighbor
                else:
                    logger.debug(f"Neighbor generated by move {move_attribute} is FEASIBLE. Proceeding to evaluation.")

                # Evaluate the neighbor solution
                score = self.solution_evaluator.evaluate_solution(neighbor_assignments, placeholder_start_time, placeholder_end_time)

                is_tabu_now = tabu_list.is_tabu(move_attribute)
                aspirated_by_global_best = score > best_score
                aspirated_by_current_improvement = score > current_score

                is_aspirated = False
                if is_tabu_now:
                    if aspiration_criteria_config.get("type") == "global_best_improvement" and aspirated_by_global_best:
                        is_aspirated = True
                        logger.info(f"Aspiration (global_best_improvement): Tabu move {move_attribute} with score {score} is better than global best {best_score}.")
                    elif aspiration_criteria_config.get("type") == "current_best_improvement" and aspirated_by_current_improvement:
                        is_aspirated = True
                        logger.info(f"Aspiration (current_best_improvement): Tabu move {move_attribute} with score {score} is better than current score {current_score}.")
                    # Placeholder for component-based aspiration
                    # elif aspiration_criteria_config.get("type") == "component_improvement":
                    #     # This would require SolutionEvaluator to return component scores
                    #     # and then compare specific components.
                    #     # Example: if solution_evaluator.get_component_score(neighbor_assignments, component_name) < solution_evaluator.get_component_score(current_solution_assignments, component_name) * (1 - threshold_factor):
                    #     # is_aspirated = True
                    #     logger.debug("Component-based aspiration check (placeholder).")
                        pass # Add more sophisticated aspiration logic here if needed

                if not is_tabu_now or is_aspirated:
                    if score > best_neighbor_score:
                        best_neighbor_assignments = neighbor_assignments
                        best_neighbor_score = score
                        best_neighbor_move_attribute = move_attribute
                        if is_aspirated:
                            logger.info(
                                "Aspiration criteria met for move %s (score: %s). Tabu overridden. (Global best was: %s)",
                                move_attribute, score, best_score
                            )
                    # If not improving, but not tabu (or aspirated), it's a candidate to escape local optima.
                    # The current logic correctly picks the best among non-tabu/aspirated neighbors.
                else:
                    logger.debug(f"Move {move_attribute} is tabu (tenure: {tabu_list.get_tenure(move_attribute)}) and does not meet aspiration. Score: {score}")

            if best_neighbor_assignments is None:
                logger.info("No suitable (non-tabu or aspirated) neighbor found in this iteration. Stopping search.")
                break

            # Update current solution to the best neighbor found
            current_solution_assignments = best_neighbor_assignments
            current_score = best_neighbor_score # Update current_score

            # Add the *attribute* of the chosen move to the tabu list
            if best_neighbor_move_attribute is not None:
                # The TabuList's add method now handles randomized tenure by default if tenure is not specified.
                tabu_list.add(best_neighbor_move_attribute)
                # move_frequency_tracker[best_neighbor_move_attribute] = move_frequency_tracker.get(best_neighbor_move_attribute, 0) + 1 # Example frequency tracking
            else:
                # This case should ideally not happen if a neighbor was selected.
                logger.warning("Best neighbor was selected, but its move attribute is None. Cannot add to tabu list.")

            # Update global best solution if current neighbor is better
            if best_neighbor_score > best_score:
                best_solution_assignments = copy.deepcopy(best_neighbor_assignments)
                best_score = best_neighbor_score
                logger.info(
                    "New global best solution found with score: %s at iteration %d",
                    best_score, iteration + 1
                )
                iterations_without_improvement = 0 # Reset counter

                # --- Intensification Phase ---
                if intensification_params:
                    current_solution_assignments, current_score = self._apply_intensification(
                        current_solution_assignments,
                        best_solution_assignments,
                        intensification_params,
                        tabu_list,
                        placeholder_start_time,
                        placeholder_end_time
                    )

            else:
                iterations_without_improvement += 1

            # --- Diversification Phase ---
            # Trigger diversification if no improvement for a certain ratio of max_iterations_without_improvement
            # Ensure diversification_params is not None before trying to access its properties
            trigger_ratio = 0.75 # Default trigger ratio
            if diversification_params and "trigger_ratio" in diversification_params:
                trigger_ratio = diversification_params["trigger_ratio"]

            if diversification_params and iterations_without_improvement >= max_iterations_without_improvement * trigger_ratio:
                current_solution_assignments, current_score, diversified = self._apply_diversification(
                    current_solution_assignments,
                    diversification_params,
                    tabu_list,
                    placeholder_start_time,
                    placeholder_end_time
                )
                if diversified: # If diversification led to a reset (e.g., random_restart)
                    iterations_without_improvement = 0 # Reset counter

            # Adaptive tenure adjustment (example - can be more sophisticated)
            if iteration % 10 == 0: # Every 10 iterations
                # Example: Randomly adjust tenure slightly for some moves, or based on frequency
                # tabu_list.update_tenure_randomly(factor=0.1) # Hypothetical method
                # Or, adjust based on search progress (e.g., if stuck, increase tenure)
                if iterations_without_improvement > max_iterations_without_improvement / 2:
                    # tabu_list.increase_all_tenures(factor=1.1) # Hypothetical
                    logger.debug("Considering increasing tabu tenures due to lack of improvement.")
                pass # Placeholder for more advanced adaptive tenure logic

            # Check for stopping criteria
            if iterations_without_improvement >= max_iterations_without_improvement:
                logger.info(
                    "Stopping early: No improvement in best solution for %d iterations (threshold: %d).",
                    iterations_without_improvement, max_iterations_without_improvement
                )
                break

            if time_limit_seconds is not None:
                elapsed_time = time.process_time() - start_time_process
                if elapsed_time >= time_limit_seconds:
                    logger.info(
                        "Stopping early: Time limit of %d seconds reached. Elapsed: %.2fs.",
                        time_limit_seconds, elapsed_time
                    )
                    break

        elapsed_total_time = time.process_time() - start_time_process
        logger.info("Tabu Search finished. Total iterations: %d. Total time: %.2fs. Best score: %s", iteration +1, elapsed_total_time, best_score)
        return best_solution_assignments, best_score