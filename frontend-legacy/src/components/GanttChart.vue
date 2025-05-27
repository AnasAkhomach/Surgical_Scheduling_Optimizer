<template>
  <div class="gantt-chart">
    <div class="placeholder">
      <h3>Gantt Chart Placeholder</h3>
      <p>The DHTMLX Gantt library is not installed. This is a placeholder for the Gantt chart.</p>

      <div class="timeline">
        <div class="timeline-header">
          <div class="timeline-header-cell" v-for="hour in timelineHours" :key="hour">
            {{ formatHour(hour) }}
          </div>
        </div>

        <div class="timeline-body">
          <div v-for="(group, groupIndex) in groupedTasks" :key="groupIndex" class="timeline-group">
            <div class="timeline-group-header">{{ group.name }}</div>

            <div v-for="(task, taskIndex) in group.tasks" :key="taskIndex" class="timeline-row">
              <div class="timeline-task-info">
                {{ task.text }}
              </div>

              <div class="timeline-task-container">
                <div
                  class="timeline-task"
                  :style="getTaskStyle(task)"
                  @click="onTaskClick(task)"
                >
                  {{ task.text }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';

export default {
  name: 'GanttChart',
  props: {
    tasks: {
      type: Array,
      required: true
    },
    links: {
      type: Array,
      default: () => []
    },
    readonly: {
      type: Boolean,
      default: false
    },
    scales: {
      type: Array,
      default: () => [
        { unit: 'hour', step: 1, format: '%H:%i' }
      ]
    },
    columns: {
      type: Array,
      default: () => [
        { name: 'text', label: 'Surgery', tree: true, width: '200' },
        { name: 'start_date', label: 'Start Time', align: 'center', width: '140' },
        { name: 'duration', label: 'Duration', align: 'center', width: '60' }
      ]
    }
  },
  emits: ['task-updated', 'task-clicked', 'task-double-clicked', 'link-created', 'link-updated', 'link-deleted'],
  setup(props, { emit }) {
    // Generate hours for the timeline (8:00 to 18:00)
    const timelineHours = computed(() => {
      return Array.from({ length: 11 }, (_, i) => i + 8);
    });

    // Format hour for display
    const formatHour = (hour) => {
      return `${hour}:00`;
    };

    // Group tasks by parent
    const groupedTasks = computed(() => {
      const groups = [];
      const tasksByParent = {};

      // Group tasks by parent
      props.tasks.forEach(task => {
        if (!task.parent || task.parent === 0) {
          // This is a root task or group
          if (task.type === 'project') {
            groups.push({
              id: task.id,
              name: task.text,
              tasks: []
            });
          }
        } else {
          // This is a child task
          if (!tasksByParent[task.parent]) {
            tasksByParent[task.parent] = [];
          }
          tasksByParent[task.parent].push(task);
        }
      });

      // Assign tasks to groups
      groups.forEach(group => {
        if (tasksByParent[group.id]) {
          group.tasks = tasksByParent[group.id];
        }
      });

      return groups;
    });

    // Calculate task position and width based on start time and duration
    const getTaskStyle = (task) => {
      const startHour = new Date(task.start_date).getHours();
      const startMinutes = new Date(task.start_date).getMinutes();
      const durationHours = task.duration;

      // Calculate position as percentage of the timeline
      const startPosition = ((startHour - 8) + (startMinutes / 60)) / 10 * 100;
      const width = (durationHours / 10) * 100;

      return {
        left: `${startPosition}%`,
        width: `${width}%`,
        backgroundColor: getTaskColor(task)
      };
    };

    // Get color based on task type or other properties
    const getTaskColor = (task) => {
      if (task.type === 'project') {
        return '#42A5F5';
      } else {
        return '#66BB6A';
      }
    };

    // Handle task click
    const onTaskClick = (task) => {
      emit('task-clicked', { id: task.id, task, event: null });
    };

    return {
      timelineHours,
      formatHour,
      groupedTasks,
      getTaskStyle,
      onTaskClick
    };
  }
}
</script>

<style scoped>
.gantt-chart {
  width: 100%;
  height: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.placeholder {
  padding: 16px;
  height: 600px;
  overflow: auto;
}

.placeholder h3 {
  margin-top: 0;
  margin-bottom: 8px;
}

.placeholder p {
  margin-bottom: 16px;
}

.timeline {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.timeline-header {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.timeline-header-cell {
  flex: 1;
  padding: 8px;
  text-align: center;
  font-weight: bold;
  border-right: 1px solid #e0e0e0;
}

.timeline-body {
  display: flex;
  flex-direction: column;
}

.timeline-group {
  margin-bottom: 16px;
}

.timeline-group-header {
  padding: 8px;
  font-weight: bold;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.timeline-row {
  display: flex;
  height: 40px;
  border-bottom: 1px solid #e0e0e0;
}

.timeline-task-info {
  width: 200px;
  padding: 8px;
  border-right: 1px solid #e0e0e0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-task-container {
  flex: 1;
  position: relative;
}

.timeline-task {
  position: absolute;
  height: 24px;
  top: 8px;
  border-radius: 4px;
  padding: 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 12px;
  line-height: 24px;
  cursor: pointer;
  color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
}
</style>
