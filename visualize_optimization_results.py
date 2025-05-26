"""
Script to visualize optimization results.

This script reads the optimization results from a JSON file and creates
visualizations to help understand the quality of the solution.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_results(file_path="optimization_results.json"):
    """Load optimization results from a JSON file."""
    logger.info(f"Loading results from {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None
    
    with open(file_path, "r") as f:
        results = json.load(f)
    
    # Convert string dates to datetime objects
    for assignment in results["assignments"]:
        assignment["start_time"] = datetime.fromisoformat(assignment["start_time"])
        assignment["end_time"] = datetime.fromisoformat(assignment["end_time"])
    
    logger.info(f"Loaded {len(results['assignments'])} assignments")
    return results

def create_gantt_chart(results):
    """Create a Gantt chart of the schedule."""
    logger.info("Creating Gantt chart")
    
    if not results:
        logger.error("No results to visualize")
        return
    
    assignments = results["assignments"]
    
    # Group assignments by room
    room_assignments = {}
    for assignment in assignments:
        if assignment["room_id"] not in room_assignments:
            room_assignments[assignment["room_id"]] = []
        room_assignments[assignment["room_id"]].append(assignment)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Colors for different surgeries
    colors = plt.cm.tab10.colors
    
    # Plot each room's schedule
    y_ticks = []
    y_labels = []
    
    for i, (room_id, room_assignments) in enumerate(room_assignments.items()):
        y_pos = i * 2
        y_ticks.append(y_pos)
        y_labels.append(f"Room {room_id}")
        
        for j, assignment in enumerate(room_assignments):
            start_time = assignment["start_time"]
            end_time = assignment["end_time"]
            duration = (end_time - start_time).total_seconds() / 60  # in minutes
            
            # Plot the surgery block
            ax.barh(
                y_pos,
                duration,
                left=mdates.date2num(start_time),
                height=0.8,
                color=colors[assignment["surgery_id"] % len(colors)],
                alpha=0.8,
                label=f"Surgery {assignment['surgery_id']}"
            )
            
            # Add surgery ID text
            text_x = mdates.date2num(start_time) + (mdates.date2num(end_time) - mdates.date2num(start_time)) / 2
            ax.text(
                text_x,
                y_pos,
                f"S{assignment['surgery_id']}",
                ha='center',
                va='center',
                color='white',
                fontweight='bold'
            )
    
    # Set y-axis
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)
    
    # Set x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    
    # Add grid
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    # Add labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Operating Room')
    ax.set_title('Surgery Schedule Gantt Chart')
    
    # Add legend for surgeries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig("optimization_gantt.png", dpi=300)
    logger.info("Gantt chart saved to optimization_gantt.png")
    
    # Show figure
    plt.show()

def create_utilization_chart(results):
    """Create a chart showing room utilization."""
    logger.info("Creating utilization chart")
    
    if not results:
        logger.error("No results to visualize")
        return
    
    assignments = results["assignments"]
    
    # Calculate utilization for each room
    room_utilization = {}
    
    # Find the overall schedule start and end time
    all_start_times = [assignment["start_time"] for assignment in assignments]
    all_end_times = [assignment["end_time"] for assignment in assignments]
    schedule_start = min(all_start_times)
    schedule_end = max(all_end_times)
    total_minutes = (schedule_end - schedule_start).total_seconds() / 60
    
    # Group assignments by room
    room_assignments = {}
    for assignment in assignments:
        if assignment["room_id"] not in room_assignments:
            room_assignments[assignment["room_id"]] = []
        room_assignments[assignment["room_id"]].append(assignment)
    
    # Calculate utilization for each room
    for room_id, room_assignments in room_assignments.items():
        # Calculate total surgery time
        total_surgery_minutes = sum(
            (assignment["end_time"] - assignment["start_time"]).total_seconds() / 60
            for assignment in room_assignments
        )
        
        # Calculate utilization
        utilization = (total_surgery_minutes / total_minutes) * 100
        room_utilization[room_id] = utilization
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot utilization
    rooms = list(room_utilization.keys())
    utilization_values = list(room_utilization.values())
    
    ax.bar(
        [f"Room {room_id}" for room_id in rooms],
        utilization_values,
        color='skyblue',
        alpha=0.8
    )
    
    # Add utilization values on top of bars
    for i, v in enumerate(utilization_values):
        ax.text(
            i,
            v + 1,
            f"{v:.1f}%",
            ha='center',
            va='bottom'
        )
    
    # Add average utilization line
    avg_utilization = sum(utilization_values) / len(utilization_values)
    ax.axhline(
        avg_utilization,
        color='red',
        linestyle='--',
        alpha=0.7,
        label=f'Avg: {avg_utilization:.1f}%'
    )
    
    # Add labels and title
    ax.set_xlabel('Operating Room')
    ax.set_ylabel('Utilization (%)')
    ax.set_title('Operating Room Utilization')
    
    # Add grid
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    # Set y-axis range
    ax.set_ylim(0, 110)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig("optimization_utilization.png", dpi=300)
    logger.info("Utilization chart saved to optimization_utilization.png")
    
    # Show figure
    plt.show()

def create_surgery_duration_chart(results):
    """Create a chart showing surgery durations."""
    logger.info("Creating surgery duration chart")
    
    if not results:
        logger.error("No results to visualize")
        return
    
    assignments = results["assignments"]
    
    # Calculate duration for each surgery
    surgery_durations = {}
    for assignment in assignments:
        surgery_id = assignment["surgery_id"]
        duration = (assignment["end_time"] - assignment["start_time"]).total_seconds() / 60  # in minutes
        surgery_durations[surgery_id] = duration
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot durations
    surgeries = list(surgery_durations.keys())
    duration_values = list(surgery_durations.values())
    
    ax.bar(
        [f"Surgery {surgery_id}" for surgery_id in surgeries],
        duration_values,
        color='lightgreen',
        alpha=0.8
    )
    
    # Add duration values on top of bars
    for i, v in enumerate(duration_values):
        ax.text(
            i,
            v + 5,
            f"{v:.0f} min",
            ha='center',
            va='bottom'
        )
    
    # Add labels and title
    ax.set_xlabel('Surgery')
    ax.set_ylabel('Duration (minutes)')
    ax.set_title('Surgery Durations')
    
    # Add grid
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig("optimization_durations.png", dpi=300)
    logger.info("Duration chart saved to optimization_durations.png")
    
    # Show figure
    plt.show()

def main():
    """Main function to visualize optimization results."""
    logger.info("Starting optimization results visualization...")
    
    # Load results
    results = load_results()
    
    if results:
        # Create visualizations
        create_gantt_chart(results)
        create_utilization_chart(results)
        create_surgery_duration_chart(results)
        
        logger.info("Visualization complete")
    else:
        logger.error("Failed to load results")

if __name__ == "__main__":
    main()
