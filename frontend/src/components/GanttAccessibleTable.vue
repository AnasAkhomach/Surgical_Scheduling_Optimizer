<template>
  <div class="visually-hidden">
    <table>
      <caption>Operating Room Schedule (Tabular View)</caption>
      <thead>
        <tr>
          <th scope="col">Operating Room</th>
          <th scope="col">Start Time</th>
          <th scope="col">End Time</th>
          <th scope="col">Surgery Type</th>
          <th scope="col">Patient</th>
          <th scope="col">Surgeon</th>
          <th scope="col">SDST Duration</th>
          <th scope="col">SDST Reason (Preceding Type)</th>
          <th scope="col">Conflicts</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="or in operatingRooms" :key="or.id">
          <tr v-if="getSurgeriesForOR(or.id).length === 0">
              <th scope="row">{{ or.name }}</th>
              <td colspan="8">No surgeries scheduled for this OR.</td>
          </tr>
          <tr v-for="surgery in getSurgeriesForOR(or.id)" :key="surgery.id">
            <th scope="row">{{ or.name }}</th>
            <td>{{ formatDateTime(surgery.startTime) }}</td>
            <td>{{ formatDateTime(surgery.endTime) }}</td>
            <td>{{ surgery.fullType }}</td>
            <td>{{ surgery.patientName }}</td>
            <td>{{ surgery.surgeon }}</td>
            <td>{{ surgery.sdsTime }} minutes</td>
            <td>{{ surgery.precedingType }}</td>
             <td>
                <span v-if="surgery.conflicts && surgery.conflicts.length">{{ surgery.conflicts.join(', ') }}</span>
                <span v-else>None</span>
             </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useScheduleStore } from '@/stores/scheduleStore';
import { storeToRefs } from 'pinia';

const store = useScheduleStore();
// Use visibleScheduledSurgeries from the store getter
const { operatingRooms, visibleScheduledSurgeries } = storeToRefs(store);

// Get surgeries for a specific OR within the current view, sorted by time
const getSurgeriesForOR = (orId) => {
  return visibleScheduledSurgeries.value
            .filter(s => s.orId === orId)
            .sort((a, b) => new Date(a.startTime) - new Date(b.startTime));
};

const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    // Format date and time clearly for a table
    return date.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
};
</script>

<style scoped>
/* Visually hidden class to hide content from sighted users but keep it for screen readers */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

table {
  border-collapse: collapse;
  margin-top: var(--spacing-md);
}

th, td {
  border: 1px solid var(--color-border);
  padding: var(--spacing-sm);
  text-align: left;
}

th {
  background-color: var(--color-background-soft);
  font-weight: bold;
}

caption {
  caption-side: top;
  font-weight: bold;
  margin-bottom: var(--spacing-sm);
  text-align: left;
}
</style>