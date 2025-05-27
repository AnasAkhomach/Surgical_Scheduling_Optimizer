import { mount } from '@vue/test-utils';
import { createTestingPinia } from '@pinia/testing';
import { useResourceStore } from '@/stores/resourceStore';
import ResourceManagementScreen from '@/components/ResourceManagementScreen.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import flushPromises from 'flush-promises';

// Mock data for the store
const INITIAL_STATE = {
  operatingRooms: [
    { id: 'or1', name: 'OR 1', location: 'Main', status: 'Available', primaryService: 'General' },
    { id: 'or2', name: 'OR 2', location: 'Main', status: 'In Use', primaryService: 'Orthopedics' },
  ],
  staff: [
    { id: 'staff1', name: 'Dr. Smith', role: 'Surgeon', specializations: ['General'], status: 'Available' },
    { id: 'staff2', name: 'Nurse Jones', role: 'Nurse', specializations: ['Anesthesia'], status: 'In Surgery' },
  ],
  equipment: [
    { id: 'equip1', name: 'X-Ray Machine', type: 'Imaging', status: 'Available', location: 'OR 1' },
    { id: 'equip2', name: 'Anesthesia Cart', type: 'Anesthesia', status: 'In Use', location: 'OR 2' },
  ],
  isLoading: false,
  error: null,
};

// Helper function to wait for table content to appear
// This helper is simplified; the primary fix is the selector change.
async function waitForTableContent(wrapper, selector, expectedRowCount, timeout = 3000) {
  const startTime = Date.now();
  let rowCount = 0;
  while (rowCount < expectedRowCount && (Date.now() - startTime < timeout)) {
    const section = wrapper.find(selector);
    if (section.exists()) {
      const table = section.find('table');
      if (table.exists()) {
        rowCount = table.findAll('tbody tr').length;
      }
    }
    if (rowCount < expectedRowCount) {
      await new Promise(resolve => setTimeout(resolve, 50)); // Wait a bit before re-checking
    }
  }
   if (rowCount < expectedRowCount) {
        console.error(`waitForTableContent failed for selector ${selector}. Expected at least ${expectedRowCount} rows, found ${rowCount}. HTML: ${wrapper.html()}`);
    }
  return rowCount;
}

describe('ResourceManagementScreen.vue', () => {
  let wrapper;
  let pinia;
  let resourceStore;

  beforeEach(() => {
    pinia = createTestingPinia({
      initialState: {
        resource: INITIAL_STATE,
      },
      // stubActions: false, // Keep actions real to test store interaction
    });
    resourceStore = useResourceStore(pinia);

    wrapper = mount(ResourceManagementScreen, {
      global: {
        plugins: [pinia],
        stubs: {
          AddOrForm: true,
          AddStaffForm: true,
          AddEquipmentForm: true,
          ConfirmationModal: false, // Stub ConfirmationModal to control its behavior
          ResourceAvailabilityCalendar: true,
        }
      }
    });
  });

  afterEach(() => {
    wrapper.unmount();
  });

  it('renders the component and displays OR tab by default', async () => {
    // Wait for initial data load and rendering
    await flushPromises();
    await wrapper.vm.$nextTick();

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('h1').text()).toBe('Resource Management');
    expect(wrapper.find('.tabs button.active').text()).toBe('Operating Rooms');

    // Check if the OR section is displayed and others are not
    const orSection = wrapper.find('.resource-section'); // OR section is the first and only active one
    expect(orSection.exists()).toBe(true);
    expect(orSection.find('h2').text()).toBe('Operating Rooms List');

    // Check if other sections are NOT displayed (due to v-if)
    expect(wrapper.find('.resource-section:has(h2:contains("Staff List"))').exists()).toBe(false);
    expect(wrapper.find('.resource-section:has(h2:contains("Equipment List"))').exists()).toBe(false);

    // Wait for the OR table content
    const rowCount = await waitForTableContent(wrapper, '.resource-section', INITIAL_STATE.operatingRooms.length);
    expect(rowCount).toBe(INITIAL_STATE.operatingRooms.length);
  });

  it('switches to Staff tab when clicked', async () => {
    await wrapper.findAll('.tabs button')[1].trigger('click');
    await wrapper.vm.$nextTick();
    await flushPromises();

    expect(wrapper.find('.tabs button.active').text()).toBe('Staff');
    // Correct selector for the active Staff section
    const staffSection = wrapper.find('.resource-section');
    expect(staffSection.exists()).toBe(true);
    expect(staffSection.find('h2').text()).toBe('Staff List');

    // Check if other sections are NOT displayed
    expect(wrapper.find('.resource-section:has(h2:contains("Operating Rooms List"))').exists()).toBe(false);
    expect(wrapper.find('.resource-section:has(h2:contains("Equipment List"))').exists()).toBe(false);

    // Wait for the Staff table content
    const rowCount = await waitForTableContent(wrapper, '.resource-section', INITIAL_STATE.staff.length);
    expect(rowCount).toBe(INITIAL_STATE.staff.length);
  });

  it('switches to Equipment tab when clicked', async () => {
    await wrapper.findAll('.tabs button')[2].trigger('click');
    await wrapper.vm.$nextTick();
    await flushPromises();

    expect(wrapper.find('.tabs button.active').text()).toBe('Equipment');
    // Correct selector for the active Equipment section
    const equipmentSection = wrapper.find('.resource-section');
    expect(equipmentSection.exists()).toBe(true);
    expect(equipmentSection.find('h2').text()).toBe('Equipment List');

    // Check if other sections are NOT displayed
    expect(wrapper.find('.resource-section:has(h2:contains("Operating Rooms List"))').exists()).toBe(false);
    expect(wrapper.find('.resource-section:has(h2:contains("Staff List"))').exists()).toBe(false);

    // Wait for the Equipment table content
    const rowCount = await waitForTableContent(wrapper, '.resource-section', INITIAL_STATE.equipment.length);
    expect(rowCount).toBe(INITIAL_STATE.equipment.length);
  });

  // Test OR tab display
  describe('Operating Rooms tab', () => {
    // No separate beforeEach needed, uses the main one

    it('displays the OR table with correct columns', async () => {
      // Assumes OR tab is active by default and data is loaded (from main beforeEach)
      const orSection = wrapper.find('.resource-section'); // OR section is the active one
      expect(orSection.exists()).toBe(true);

      const table = orSection.find('table');
      expect(table.exists()).toBe(true);

      const headers = table.findAll('th').map(th => th.text());
      expect(headers).toEqual(['Name/ID', 'Location', 'Status', 'Primary Service', 'Actions']);
    });

    it('displays the initial OR data correctly', async () => {
      // Assumes OR tab is active by default and data is loaded (from main beforeEach)
      const orSection = wrapper.find('.resource-section'); // OR section is the active one
      expect(orSection.exists()).toBe(true);

      // Wait for the table content to be fully rendered
      await waitForTableContent(wrapper, '.resource-section', INITIAL_STATE.operatingRooms.length);

      const rows = orSection.findAll('tbody tr');
      expect(rows.length).toBe(INITIAL_STATE.operatingRooms.length);

      // Check content of the first row
      const firstRowCells = rows[0].findAll('td').map(td => td.text());
      expect(firstRowCells[0]).toBe(INITIAL_STATE.operatingRooms[0].name);
      expect(firstRowCells[1]).toBe(INITIAL_STATE.operatingRooms[0].location);
      expect(firstRowCells[2]).toBe(INITIAL_STATE.operatingRooms[0].status);
      expect(firstRowCells[3]).toBe(INITIAL_STATE.operatingRooms[0].primaryService);
    });

    it('shows the Add New OR form when button is clicked', async () => {
      const orSection = wrapper.find('.resource-section'); // OR section is the active one
      expect(orSection.exists()).toBe(true);

      const addButton = orSection.find('button.button-primary');
      expect(addButton.exists()).toBe(true);

      await addButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.findComponent({ name: 'AddOrForm' }).exists()).toBe(true);
      // Check if the table is hidden when the form is shown (requires component logic fix)
      expect(orSection.find('table').exists()).toBe(false);
    });
  });

  // Test Staff tab display
  describe('Staff tab', () => {
    beforeEach(async () => {
      // Switch to Staff tab before each test in this block
      await wrapper.findAll('.tabs button')[1].trigger('click');
      await wrapper.vm.$nextTick();
      await flushPromises();

      // Wait for the Staff table content
      await waitForTableContent(wrapper, '.resource-section', INITIAL_STATE.staff.length);
    });

    it('displays the Staff table with correct columns', async () => {
      const staffSection = wrapper.find('.resource-section'); // Staff section is the active one
      expect(staffSection.exists()).toBe(true);

      const table = staffSection.find('table');
      expect(table.exists()).toBe(true);

      const headers = table.findAll('th').map(th => th.text());
      expect(headers).toEqual(['Name', 'Role', 'Specialization(s)', 'Status', 'Actions']);
    });

    it('displays the initial staff data correctly', async () => {
      const staffSection = wrapper.find('.resource-section'); // Staff section is the active one
      expect(staffSection.exists()).toBe(true);

      const rows = staffSection.findAll('tbody tr');
      expect(rows.length).toBe(INITIAL_STATE.staff.length);

      // Check content of the first row
      const firstRowCells = rows[0].findAll('td').map(td => td.text());
      expect(firstRowCells[0]).toBe(INITIAL_STATE.staff[0].name);
      expect(firstRowCells[1]).toBe(INITIAL_STATE.staff[0].role);
      expect(firstRowCells[2]).toBe(INITIAL_STATE.staff[0].specializations.join(', '));
      expect(firstRowCells[3]).toBe(INITIAL_STATE.staff[0].status);
    });

    it('shows the Add New Staff form when button is clicked', async () => {
      const staffSection = wrapper.find('.resource-section'); // Staff section is the active one
      expect(staffSection.exists()).toBe(true);

      const addButton = staffSection.find('button.button-primary');
      expect(addButton.exists()).toBe(true);

      await addButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.findComponent({ name: 'AddStaffForm' }).exists()).toBe(true);
      // Check if the table is hidden when the form is shown (requires component logic fix)
      expect(staffSection.find('table').exists()).toBe(false);
    });
  });

  // Test Equipment tab display
  describe('Equipment tab', () => {
    beforeEach(async () => {
      // Switch to Equipment tab before each test in this block
      await wrapper.findAll('.tabs button')[2].trigger('click');
      await wrapper.vm.$nextTick();
      await flushPromises();

      // Wait for the Equipment table content
      await waitForTableContent(wrapper, '.resource-section', INITIAL_STATE.equipment.length);
    });

    it('displays the Equipment table with correct columns', async () => {
      const equipmentSection = wrapper.find('.resource-section'); // Equipment section is the active one
      expect(equipmentSection.exists()).toBe(true);

      const table = equipmentSection.find('table');
      expect(table.exists()).toBe(true);

      const headers = table.findAll('th').map(th => th.text());
      expect(headers).toEqual(['Name/ID', 'Type', 'Status', 'Location', 'Actions']);
    });

    it('displays the initial equipment data correctly', async () => {
      const equipmentSection = wrapper.find('.resource-section'); // Equipment section is the active one
      expect(equipmentSection.exists()).toBe(true);

      const rows = equipmentSection.findAll('tbody tr');
      expect(rows.length).toBe(INITIAL_STATE.equipment.length);

      // Check content of the first row
      const firstRowCells = rows[0].findAll('td').map(td => td.text());
      expect(firstRowCells[0]).toBe(INITIAL_STATE.equipment[0].name);
      expect(firstRowCells[1]).toBe(INITIAL_STATE.equipment[0].type);
      expect(firstRowCells[2]).toBe(INITIAL_STATE.equipment[0].status);
      expect(firstRowCells[3]).toBe(INITIAL_STATE.equipment[0].location);
    });

    it('shows the Add New Equipment form when button is clicked', async () => {
      const equipmentSection = wrapper.find('.resource-section'); // Equipment section is the active one
      expect(equipmentSection.exists()).toBe(true);

      const addButton = equipmentSection.find('button.button-primary');
      expect(addButton.exists()).toBe(true);

      await addButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.findComponent({ name: 'AddEquipmentForm' }).exists()).toBe(true);
      // Check if the table is hidden when the form is shown (requires component logic fix)
      expect(equipmentSection.find('table').exists()).toBe(false);
    });
  });

  // Test form submission for adding a new OR
  describe('Form submissions', () => {
    // Note: These tests use a separate wrapper instance to isolate form behavior
    it('adds a new OR when form is submitted', async () => {
      const localPinia = createTestingPinia({
        initialState: {
          resource: INITIAL_STATE,
        },
        stubActions: false, // Keep actions real to test store interaction
      });
      const orStore = useResourceStore(localPinia);

      const fullWrapper = mount(ResourceManagementScreen, {
        global: {
          plugins: [localPinia],
          stubs: {
            AddOrForm: false, // Don't stub the form to test its emission
            AddStaffForm: true,
            AddEquipmentForm: true,
            ConfirmationModal: true,
            ResourceAvailabilityCalendar: true,
          }
        }
      });

      // Wait for initial data load
      await flushPromises();
      await fullWrapper.vm.$nextTick();

      const orSection = fullWrapper.find('.resource-section'); // OR section is the active one
      expect(orSection.exists()).toBe(true);

      // Click Add New OR button to show the form
      await orSection.find('button.button-primary').trigger('click');
      await fullWrapper.vm.$nextTick();

      const addOrForm = fullWrapper.findComponent({ name: 'AddOrForm' });
      expect(addOrForm.exists()).toBe(true);

      // Simulate emitting the save event from the form
      const newOrData = { name: 'OR 3', location: 'South', status: 'Available', primaryService: 'Cardiology' };
      await addOrForm.vm.$emit('save', newOrData);

      // Wait for the store action and DOM updates
      await flushPromises();
      await fullWrapper.vm.$nextTick();

      // Assert that the form is hidden and the new OR is added to the store and table
      expect(fullWrapper.findComponent({ name: 'AddOrForm' }).exists()).toBe(false);
      expect(orStore.operatingRooms.length).toBe(INITIAL_STATE.operatingRooms.length + 1);

      // Wait for the table to update with the new row
      const updatedRowCount = await waitForTableContent(fullWrapper, '.resource-section', INITIAL_STATE.operatingRooms.length + 1);
      expect(updatedRowCount).toBe(INITIAL_STATE.operatingRooms.length + 1);

      // Optionally check if the new row content is correct
      const rows = fullWrapper.find('.resource-section').findAll('tbody tr');
      const newRowCells = rows[rows.length - 1].findAll('td').map(td => td.text());
      expect(newRowCells[0]).toBe(newOrData.name);
      expect(newRowCells[1]).toBe(newOrData.location);
    });

    // Add similar tests for Staff and Equipment form submissions if needed
  });

  // Test deletion confirmation
  describe('Deletion confirmation', () => {
    // Note: These tests use separate wrapper instances to isolate deletion behavior

    // Test OR deletion confirmation
    it('should show confirmation modal on deleting an OR', async () => {
      const localPinia = createTestingPinia({
        initialState: {
          resource: INITIAL_STATE,
        },
        stubActions: false, // Keep actions real to test store interaction
      });
      const orStore = useResourceStore(localPinia);

      const orWrapper = mount(ResourceManagementScreen, {
        global: {
          plugins: [localPinia],
          stubs: {
            AddOrForm: true,
            AddStaffForm: true,
            AddEquipmentForm: true,
            ConfirmationModal: false, // Don't stub modal to test its appearance
            ResourceAvailabilityCalendar: true,
          }
        }
      });

      // Wait for initial data load and rendering
      await flushPromises();
      await orWrapper.vm.$nextTick();

      const orSection = orWrapper.find('.resource-section'); // OR section is the active one
      expect(orSection.exists()).toBe(true);

      // Wait for the OR table content in this specific test context
      const initialRowCount = await waitForTableContent(
        orWrapper,
        '.resource-section',
        orStore.operatingRooms.length,
        5000 // Increased timeout
      );
      expect(initialRowCount).toBeGreaterThan(0); // Ensure there are rows to delete

      const firstRow = orSection.find('tbody tr');
      expect(firstRow.exists()).toBe(true);
      // Find the delete button in the first row
      const deleteButton = firstRow.findAll('button').filter(btn => btn.text() === 'Delete')[0];
      expect(deleteButton.exists()).toBe(true);

      // Click the delete button to open the confirmation modal
      await deleteButton.trigger('click');
      await orWrapper.vm.$nextTick(); // Wait for modal to appear

      // Assert that the confirmation modal is shown
      const confirmationModal = orWrapper.findComponent(ConfirmationModal);
      expect(confirmationModal.exists()).toBe(true);
      expect(confirmationModal.vm.title).toBe('Delete Operating Room?');

      // Simulate confirming the deletion
      await confirmationModal.vm.$emit('confirm');
      await flushPromises(); // Wait for the delete action and state update

      // Assert that the modal is hidden and the item is removed from the table
      expect(orWrapper.findComponent(ConfirmationModal).exists()).toBe(false);
      expect(orSection.find('table').exists()).toBe(true); // Table should still exist

      // Wait for the table to update after deletion
      const updatedRowCount = await waitForTableContent(orWrapper, '.resource-section', initialRowCount - 1);
      expect(updatedRowCount).toBe(initialRowCount - 1);
    });

    // Test Staff deletion confirmation
    describe('Staff deletion confirmation', () => {
      let wrapper;
      let resourceStore;

      beforeEach(async () => {
        const localPinia = createTestingPinia({
          initialState: {
            resource: INITIAL_STATE,
          },
          stubActions: false,
        });
        resourceStore = useResourceStore(localPinia);

        wrapper = mount(ResourceManagementScreen, {
          global: {
            plugins: [localPinia],
            stubs: {
              AddOrForm: true,
              AddStaffForm: true,
              AddEquipmentForm: true,
              ConfirmationModal: false,
              ResourceAvailabilityCalendar: true,
            }
          }
        });

        // Switch to Staff tab
        await wrapper.findAll('.tabs button')[1].trigger('click');
        await wrapper.vm.$nextTick(); // Wait for DOM to update after tab switch
        await flushPromises(); // Ensure all promises are resolved after tab switch

        // Wait for the Staff table rows to appear after tab switch
        const initialRowCount = await waitForTableContent(
          wrapper,
          '.resource-section', // Correct selector for the active section
          resourceStore.staff.length,
          5000 // Increased timeout to 5 seconds
        );
        expect(initialRowCount).toBeGreaterThan(0); // Assert that rows eventually exist
        wrapper.vm.initialRowCount = initialRowCount; // Store initial row count on the wrapper instance
      });

      it('should show confirmation modal on deleting a Staff', async () => {
        // Assuming initial data has at least one Staff member, checked in beforeEach
        const initialRowCount = wrapper.vm.initialRowCount; // Use stored initial row count

        const staffSection = wrapper.find('.resource-section'); // Staff section is the active one
        const firstRow = staffSection.find('tbody tr');
        expect(firstRow.exists()).toBe(true);
        // Find the delete button in the first row
        const deleteButton = firstRow.findAll('button').filter(btn => btn.text() === 'Delete')[0];
        expect(deleteButton.exists()).toBe(true);

        // Click the delete button to open the confirmation modal
        await deleteButton.trigger('click');
        await wrapper.vm.$nextTick(); // Wait for modal to appear

        // Assert that the confirmation modal is shown
        const confirmationModal = wrapper.findComponent(ConfirmationModal);
        expect(confirmationModal.exists()).toBe(true);
        expect(confirmationModal.vm.title).toBe('Delete Staff Member?');

        // Simulate confirming the deletion
        await confirmationModal.vm.$emit('confirm');
        await flushPromises(); // Wait for the delete action and state update

        // Assert that the modal is hidden and the item is removed from the table
        expect(wrapper.findComponent(ConfirmationModal).exists()).toBe(false);
        expect(staffSection.find('table').exists()).toBe(true); // Table should still exist within the section

        // Wait for the table to update after deletion
        const updatedRowCount = await waitForTableContent(wrapper, '.resource-section', initialRowCount - 1);
        expect(updatedRowCount).toBe(initialRowCount - 1);
      });
    });

    // Test Equipment deletion confirmation
    describe('Equipment deletion confirmation', () => {
      let wrapper;
      let resourceStore;

      beforeEach(async () => {
        const localPinia = createTestingPinia({
          initialState: {
            resource: INITIAL_STATE,
          },
          stubActions: false,
        });
        resourceStore = useResourceStore(localPinia);

        wrapper = mount(ResourceManagementScreen, {
          global: {
            plugins: [localPinia],
            stubs: {
              AddOrForm: true,
              AddStaffForm: true,
              AddEquipmentForm: true,
              ConfirmationModal: false,
              ResourceAvailabilityCalendar: true,
            }
          }
        });

        // Switch to Equipment tab
        await wrapper.findAll('.tabs button')[2].trigger('click');
        await wrapper.vm.$nextTick(); // Wait for DOM to update after tab switch
        await flushPromises(); // Ensure all promises are resolved after tab switch

        // Wait for the Equipment table rows to appear after tab switch
        const initialRowCount = await waitForTableContent(
          wrapper,
          '.resource-section', // Correct selector for the active section
          resourceStore.equipment.length,
          5000 // Increased timeout to 5 seconds
        );
        expect(initialRowCount).toBeGreaterThan(0); // Assert that rows eventually exist
        wrapper.vm.initialRowCount = initialRowCount; // Store initial row count on the wrapper instance
      });

      it('should show confirmation modal on deleting an Equipment', async () => {
        // Assuming initial data has at least one Equipment item, checked in beforeEach
        const initialRowCount = wrapper.vm.initialRowCount; // Use stored initial row count

        const equipmentSection = wrapper.find('.resource-section'); // Equipment section is the active one
        const firstRow = equipmentSection.find('tbody tr');
        expect(firstRow.exists()).toBe(true);
        // Find the delete button in the first row
        const deleteButton = firstRow.findAll('button').filter(btn => btn.text() === 'Delete')[0];
        expect(deleteButton.exists()).toBe(true);

        // Click the delete button to open the confirmation modal
        await deleteButton.trigger('click');
        await wrapper.vm.$nextTick(); // Wait for modal to appear

        // Assert that the confirmation modal is shown
        const confirmationModal = wrapper.findComponent(ConfirmationModal);
        expect(confirmationModal.exists()).toBe(true);
        expect(confirmationModal.vm.title).toBe('Delete Equipment?');

        // Simulate confirming the deletion
        await confirmationModal.vm.$emit('confirm');
        await flushPromises(); // Wait for the delete action and state update

        // Assert that the modal is hidden and the item is removed from the table
        expect(wrapper.findComponent(ConfirmationModal).exists()).toBe(false);
        expect(equipmentSection.find('table').exists()).toBe(true); // Table should still exist within the section

        // Wait for the table to update after deletion
        const updatedRowCount = await waitForTableContent(wrapper, '.resource-section', initialRowCount - 1);
        expect(updatedRowCount).toBe(initialRowCount - 1);
      });
    });
  });

  // Test form submission for adding a new OR
});