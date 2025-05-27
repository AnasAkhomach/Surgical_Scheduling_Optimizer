<template>
  <div class="room-availability">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold">Operating Room Availability</h1>
      <div>
        <Button label="Save Changes" icon="pi pi-save" @click="saveChanges" :disabled="!hasChanges" class="mr-2" />
        <Button label="Reset" icon="pi pi-refresh" @click="resetChanges" :disabled="!hasChanges" class="p-button-secondary" />
      </div>
    </div>
    
    <AvailabilityCalendar 
      title="Operating Room Availability Calendar" 
      type="room" 
      :data="availabilityData"
      @update:data="updateAvailabilityData"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import AvailabilityCalendar from '@/components/AvailabilityCalendar.vue';

export default {
  name: 'RoomAvailability',
  components: {
    AvailabilityCalendar
  },
  setup() {
    const toast = useToast();
    const availabilityData = ref([]);
    const originalData = ref([]);
    const hasChanges = ref(false);
    
    // Mock function to load availability data
    const loadAvailabilityData = async () => {
      // In a real application, this would be an API call
      // const response = await axios.get('/api/operating-rooms/availability');
      
      // Mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockData = [
        // Mock data would go here
      ];
      
      availabilityData.value = mockData;
      originalData.value = JSON.parse(JSON.stringify(mockData)); // Deep copy
    };
    
    // Update availability data when changes are made in the calendar
    const updateAvailabilityData = (newData) => {
      availabilityData.value = newData;
      hasChanges.value = true;
    };
    
    // Save changes to the server
    const saveChanges = async () => {
      try {
        // In a real application, this would be an API call
        // await axios.post('/api/operating-rooms/availability', availabilityData.value);
        
        // Mock response for demonstration
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        originalData.value = JSON.parse(JSON.stringify(availabilityData.value)); // Deep copy
        hasChanges.value = false;
        
        toast.add({
          severity: 'success',
          summary: 'Changes Saved',
          detail: 'Operating room availability has been updated successfully',
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Save Failed',
          detail: error.message || 'An error occurred while saving changes',
          life: 3000
        });
      }
    };
    
    // Reset changes to original data
    const resetChanges = () => {
      availabilityData.value = JSON.parse(JSON.stringify(originalData.value)); // Deep copy
      hasChanges.value = false;
      
      toast.add({
        severity: 'info',
        summary: 'Changes Reset',
        detail: 'All changes have been discarded',
        life: 3000
      });
    };
    
    // Load data on component mount
    loadAvailabilityData();
    
    return {
      availabilityData,
      hasChanges,
      updateAvailabilityData,
      saveChanges,
      resetChanges
    };
  }
}
</script>
