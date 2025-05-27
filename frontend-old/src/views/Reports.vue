<template>
  <div class="reports">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold">Reports</h1>
    </div>
    
    <div class="grid">
      <div class="col-12 md:col-4">
        <Card class="h-full">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-calendar text-primary mr-2"></i>
              <span>Schedule Report</span>
            </div>
          </template>
          <template #content>
            <div class="p-fluid">
              <div class="field">
                <label for="scheduleDate">Date</label>
                <Calendar id="scheduleDate" v-model="scheduleReportParams.date" dateFormat="yy-mm-dd" class="w-full" />
              </div>
              <div class="field">
                <label for="scheduleFormat">Format</label>
                <Dropdown id="scheduleFormat" v-model="scheduleReportParams.format" :options="reportFormats" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <div class="field">
                <label for="scheduleIncludeDetails">Include Details</label>
                <div class="p-field-checkbox">
                  <Checkbox id="scheduleIncludeDetails" v-model="scheduleReportParams.includeDetails" :binary="true" />
                  <label for="scheduleIncludeDetails" class="ml-2">Include surgery details</label>
                </div>
              </div>
              <Button label="Generate Report" icon="pi pi-file-pdf" @click="generateScheduleReport" :loading="loading.schedule" class="w-full" />
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-4">
        <Card class="h-full">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-chart-bar text-primary mr-2"></i>
              <span>Utilization Report</span>
            </div>
          </template>
          <template #content>
            <div class="p-fluid">
              <div class="field">
                <label for="utilizationDateRange">Date Range</label>
                <Dropdown id="utilizationDateRange" v-model="utilizationReportParams.dateRange" :options="dateRanges" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <div class="field">
                <label for="utilizationResourceType">Resource Type</label>
                <Dropdown id="utilizationResourceType" v-model="utilizationReportParams.resourceType" :options="resourceTypes" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <div class="field">
                <label for="utilizationFormat">Format</label>
                <Dropdown id="utilizationFormat" v-model="utilizationReportParams.format" :options="reportFormats" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <Button label="Generate Report" icon="pi pi-file-pdf" @click="generateUtilizationReport" :loading="loading.utilization" class="w-full" />
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-4">
        <Card class="h-full">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-user text-primary mr-2"></i>
              <span>Surgeon Performance Report</span>
            </div>
          </template>
          <template #content>
            <div class="p-fluid">
              <div class="field">
                <label for="performanceDateRange">Date Range</label>
                <Dropdown id="performanceDateRange" v-model="performanceReportParams.dateRange" :options="dateRanges" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <div class="field">
                <label for="performanceSurgeon">Surgeon</label>
                <Dropdown id="performanceSurgeon" v-model="performanceReportParams.surgeonId" :options="surgeons" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <div class="field">
                <label for="performanceFormat">Format</label>
                <Dropdown id="performanceFormat" v-model="performanceReportParams.format" :options="reportFormats" optionLabel="label" optionValue="value" class="w-full" />
              </div>
              <Button label="Generate Report" icon="pi pi-file-pdf" @click="generatePerformanceReport" :loading="loading.performance" class="w-full" />
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <div class="mt-4">
      <Card>
        <template #title>
          <div class="flex align-items-center">
            <i class="pi pi-clock text-primary mr-2"></i>
            <span>Scheduled Reports</span>
          </div>
        </template>
        <template #content>
          <DataTable :value="scheduledReports" responsiveLayout="scroll" class="p-datatable-sm">
            <Column field="name" header="Report Name"></Column>
            <Column field="type" header="Type"></Column>
            <Column field="frequency" header="Frequency"></Column>
            <Column field="recipients" header="Recipients">
              <template #body="slotProps">
                {{ slotProps.data.recipients.join(', ') }}
              </template>
            </Column>
            <Column field="nextRun" header="Next Run">
              <template #body="slotProps">
                {{ formatDate(slotProps.data.nextRun) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="slotProps">
                <Button icon="pi pi-pencil" class="p-button-text p-button-sm" @click="editScheduledReport(slotProps.data)" />
                <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" @click="deleteScheduledReport(slotProps.data)" />
              </template>
            </Column>
          </DataTable>
          
          <div class="mt-3 flex justify-content-end">
            <Button label="Schedule New Report" icon="pi pi-plus" @click="showScheduleReportDialog" />
          </div>
        </template>
      </Card>
    </div>
    
    <Dialog v-model:visible="scheduleReportDialog.visible" :header="scheduleReportDialog.isEdit ? 'Edit Scheduled Report' : 'Schedule New Report'" :style="{ width: '500px' }">
      <div class="p-fluid">
        <div class="field">
          <label for="reportName">Report Name</label>
          <InputText id="reportName" v-model="scheduleReportDialog.data.name" />
        </div>
        <div class="field">
          <label for="reportType">Report Type</label>
          <Dropdown id="reportType" v-model="scheduleReportDialog.data.type" :options="reportTypes" optionLabel="label" optionValue="value" />
        </div>
        <div class="field">
          <label for="reportFrequency">Frequency</label>
          <Dropdown id="reportFrequency" v-model="scheduleReportDialog.data.frequency" :options="reportFrequencies" optionLabel="label" optionValue="value" />
        </div>
        <div class="field">
          <label for="reportRecipients">Recipients</label>
          <Chips id="reportRecipients" v-model="scheduleReportDialog.data.recipients" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="scheduleReportDialog.visible = false" />
        <Button label="Save" icon="pi pi-check" @click="saveScheduledReport" />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'primevue/usetoast';
import pdfService from '@/services/pdf.service';

export default {
  name: 'Reports',
  setup() {
    const store = useStore();
    const toast = useToast();
    
    // Loading states
    const loading = reactive({
      schedule: false,
      utilization: false,
      performance: false
    });
    
    // Report parameters
    const scheduleReportParams = reactive({
      date: new Date(),
      format: 'pdf',
      includeDetails: true
    });
    
    const utilizationReportParams = reactive({
      dateRange: 'week',
      resourceType: 'room',
      format: 'pdf'
    });
    
    const performanceReportParams = reactive({
      dateRange: 'month',
      surgeonId: 'all',
      format: 'pdf'
    });
    
    // Options for dropdowns
    const reportFormats = [
      { label: 'PDF', value: 'pdf' },
      { label: 'Excel', value: 'excel' },
      { label: 'CSV', value: 'csv' }
    ];
    
    const dateRanges = [
      { label: 'Today', value: 'today' },
      { label: 'This Week', value: 'week' },
      { label: 'This Month', value: 'month' },
      { label: 'Last 3 Months', value: 'quarter' },
      { label: 'Year to Date', value: 'ytd' }
    ];
    
    const resourceTypes = [
      { label: 'Operating Rooms', value: 'room' },
      { label: 'Surgeons', value: 'surgeon' },
      { label: 'Staff', value: 'staff' }
    ];
    
    const surgeons = [
      { label: 'All Surgeons', value: 'all' },
      { label: 'Dr. Smith', value: 1 },
      { label: 'Dr. Johnson', value: 2 },
      { label: 'Dr. Williams', value: 3 },
      { label: 'Dr. Brown', value: 4 }
    ];
    
    const reportTypes = [
      { label: 'Schedule Report', value: 'schedule' },
      { label: 'Utilization Report', value: 'utilization' },
      { label: 'Surgeon Performance Report', value: 'performance' }
    ];
    
    const reportFrequencies = [
      { label: 'Daily', value: 'daily' },
      { label: 'Weekly', value: 'weekly' },
      { label: 'Monthly', value: 'monthly' }
    ];
    
    // Scheduled reports
    const scheduledReports = ref([
      {
        id: 1,
        name: 'Daily Schedule',
        type: 'schedule',
        frequency: 'daily',
        recipients: ['admin@example.com', 'manager@example.com'],
        nextRun: new Date(new Date().setHours(6, 0, 0, 0) + 86400000) // Tomorrow at 6 AM
      },
      {
        id: 2,
        name: 'Weekly Utilization',
        type: 'utilization',
        frequency: 'weekly',
        recipients: ['admin@example.com'],
        nextRun: new Date(new Date().setDate(new Date().getDate() + (7 - new Date().getDay()) % 7 + 1)) // Next Monday
      },
      {
        id: 3,
        name: 'Monthly Surgeon Performance',
        type: 'performance',
        frequency: 'monthly',
        recipients: ['admin@example.com', 'chief@example.com'],
        nextRun: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1) // First day of next month
      }
    ]);
    
    // Schedule report dialog
    const scheduleReportDialog = reactive({
      visible: false,
      isEdit: false,
      data: {
        id: null,
        name: '',
        type: 'schedule',
        frequency: 'daily',
        recipients: []
      }
    });
    
    // Format date for display
    const formatDate = (date) => {
      return new Date(date).toLocaleString();
    };
    
    // Generate schedule report
    const generateScheduleReport = async () => {
      loading.schedule = true;
      
      try {
        // In a real application, this would fetch data from the API
        const scheduleData = await store.dispatch('schedule/fetchCurrentSchedule', scheduleReportParams.date.toISOString().split('T')[0]);
        
        // Generate PDF
        const pdfBlob = await pdfService.generateScheduleReport(scheduleData, {
          includeDetails: scheduleReportParams.includeDetails
        });
        
        // Download the PDF
        pdfService.downloadPdf(pdfBlob, `schedule-report-${scheduleReportParams.date.toISOString().split('T')[0]}.pdf`);
        
        toast.add({
          severity: 'success',
          summary: 'Report Generated',
          detail: 'Schedule report has been generated successfully',
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Report Generation Failed',
          detail: error.message || 'An error occurred while generating the report',
          life: 3000
        });
      } finally {
        loading.schedule = false;
      }
    };
    
    // Generate utilization report
    const generateUtilizationReport = async () => {
      loading.utilization = true;
      
      try {
        // Mock utilization data
        const utilizationData = {
          'OR-1': 85,
          'OR-2': 78,
          'OR-3': 92,
          'OR-4': 65
        };
        
        // Generate PDF
        const pdfBlob = await pdfService.generateUtilizationReport(utilizationData, {
          dateRange: utilizationReportParams.dateRange,
          resourceType: utilizationReportParams.resourceType
        });
        
        // Download the PDF
        pdfService.downloadPdf(pdfBlob, `utilization-report-${new Date().toISOString().split('T')[0]}.pdf`);
        
        toast.add({
          severity: 'success',
          summary: 'Report Generated',
          detail: 'Utilization report has been generated successfully',
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Report Generation Failed',
          detail: error.message || 'An error occurred while generating the report',
          life: 3000
        });
      } finally {
        loading.utilization = false;
      }
    };
    
    // Generate performance report
    const generatePerformanceReport = async () => {
      loading.performance = true;
      
      try {
        // Mock performance data
        const performanceData = {
          'Dr. Smith': {
            surgeries: 45,
            avgDuration: 120,
            onTimeStart: 92,
            complications: 3
          },
          'Dr. Johnson': {
            surgeries: 38,
            avgDuration: 135,
            onTimeStart: 88,
            complications: 5
          },
          'Dr. Williams': {
            surgeries: 52,
            avgDuration: 110,
            onTimeStart: 95,
            complications: 2
          },
          'Dr. Brown': {
            surgeries: 41,
            avgDuration: 125,
            onTimeStart: 90,
            complications: 4
          }
        };
        
        // Generate PDF
        const pdfBlob = await pdfService.generateSurgeonPerformanceReport(performanceData, {
          dateRange: performanceReportParams.dateRange,
          surgeonId: performanceReportParams.surgeonId
        });
        
        // Download the PDF
        pdfService.downloadPdf(pdfBlob, `surgeon-performance-report-${new Date().toISOString().split('T')[0]}.pdf`);
        
        toast.add({
          severity: 'success',
          summary: 'Report Generated',
          detail: 'Surgeon performance report has been generated successfully',
          life: 3000
        });
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Report Generation Failed',
          detail: error.message || 'An error occurred while generating the report',
          life: 3000
        });
      } finally {
        loading.performance = false;
      }
    };
    
    // Show schedule report dialog
    const showScheduleReportDialog = () => {
      scheduleReportDialog.isEdit = false;
      scheduleReportDialog.data = {
        id: null,
        name: '',
        type: 'schedule',
        frequency: 'daily',
        recipients: []
      };
      scheduleReportDialog.visible = true;
    };
    
    // Edit scheduled report
    const editScheduledReport = (report) => {
      scheduleReportDialog.isEdit = true;
      scheduleReportDialog.data = { ...report };
      scheduleReportDialog.visible = true;
    };
    
    // Delete scheduled report
    const deleteScheduledReport = (report) => {
      // In a real application, this would call an API to delete the report
      scheduledReports.value = scheduledReports.value.filter(r => r.id !== report.id);
      
      toast.add({
        severity: 'success',
        summary: 'Report Deleted',
        detail: `Scheduled report "${report.name}" has been deleted`,
        life: 3000
      });
    };
    
    // Save scheduled report
    const saveScheduledReport = () => {
      if (!scheduleReportDialog.data.name) {
        toast.add({
          severity: 'error',
          summary: 'Validation Error',
          detail: 'Report name is required',
          life: 3000
        });
        return;
      }
      
      if (scheduleReportDialog.data.recipients.length === 0) {
        toast.add({
          severity: 'error',
          summary: 'Validation Error',
          detail: 'At least one recipient is required',
          life: 3000
        });
        return;
      }
      
      // In a real application, this would call an API to save the report
      if (scheduleReportDialog.isEdit) {
        // Update existing report
        const index = scheduledReports.value.findIndex(r => r.id === scheduleReportDialog.data.id);
        if (index !== -1) {
          scheduledReports.value[index] = { ...scheduleReportDialog.data };
        }
        
        toast.add({
          severity: 'success',
          summary: 'Report Updated',
          detail: `Scheduled report "${scheduleReportDialog.data.name}" has been updated`,
          life: 3000
        });
      } else {
        // Add new report
        const newReport = {
          ...scheduleReportDialog.data,
          id: scheduledReports.value.length + 1,
          nextRun: new Date(new Date().setDate(new Date().getDate() + 1)) // Tomorrow
        };
        
        scheduledReports.value.push(newReport);
        
        toast.add({
          severity: 'success',
          summary: 'Report Scheduled',
          detail: `Report "${newReport.name}" has been scheduled`,
          life: 3000
        });
      }
      
      scheduleReportDialog.visible = false;
    };
    
    return {
      loading,
      scheduleReportParams,
      utilizationReportParams,
      performanceReportParams,
      reportFormats,
      dateRanges,
      resourceTypes,
      surgeons,
      reportTypes,
      reportFrequencies,
      scheduledReports,
      scheduleReportDialog,
      formatDate,
      generateScheduleReport,
      generateUtilizationReport,
      generatePerformanceReport,
      showScheduleReportDialog,
      editScheduledReport,
      deleteScheduledReport,
      saveScheduledReport
    };
  }
}
</script>
