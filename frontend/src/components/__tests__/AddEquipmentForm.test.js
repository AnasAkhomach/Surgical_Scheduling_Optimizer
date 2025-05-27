import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import AddEquipmentForm from '../AddEquipmentForm.vue';

describe('AddEquipmentForm', () => {
  // Test case for rendering in add mode
  it('renders correctly in add mode', () => {
    const wrapper = mount(AddEquipmentForm, {
      props: { equipmentToEdit: null },
    });

    expect(wrapper.text()).toContain('Add New Equipment');
    expect(wrapper.find('input#equipment-name').exists()).toBe(true);
    expect(wrapper.find('input#equipment-type').exists()).toBe(true);
    expect(wrapper.find('select#equipment-status').exists()).toBe(true);
    expect(wrapper.find('input#equipment-location').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Save Equipment');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
    expect(wrapper.find('.error-message').exists()).toBe(false); // No errors initially
  });

  // Test case for rendering in edit mode with initial data
  it('renders correctly in edit mode with initial data', () => {
    const initialData = {
      id: 1,
      name: 'OR Table 1',
      type: 'Operating Table',
      status: 'Available',
      location: 'OR 1',
    };
    const wrapper = mount(AddEquipmentForm, {
      props: { equipmentToEdit: initialData },
    });

    expect(wrapper.text()).toContain('Edit Equipment');
    expect(wrapper.find('input#equipment-name').element.value).toBe(initialData.name);
    expect(wrapper.find('input#equipment-type').element.value).toBe(initialData.type);
    expect(wrapper.find('select#equipment-status').element.value).toBe(initialData.status);
    expect(wrapper.find('input#equipment-location').element.value).toBe(initialData.location);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Update Equipment');
  });

  // Test case for form input and data binding
  it('updates form data on input', async () => {
    const wrapper = mount(AddEquipmentForm);
    const nameInput = wrapper.find('input#equipment-name');
    const typeInput = wrapper.find('input#equipment-type');
    const statusSelect = wrapper.find('select#equipment-status');
    const locationInput = wrapper.find('input#equipment-location');

    await nameInput.setValue('New Ventilator');
    await typeInput.setValue('Ventilator');
    await statusSelect.setValue('In Use');
    await locationInput.setValue('OR 3');

    // Check if component's internal data reflects the input
    // This requires accessing the component instance, which is not standard Vue Test Utils practice
    // We will rely on the submit test to verify data correctness.

    // However, we can check the element values still
    expect(nameInput.element.value).toBe('New Ventilator');
    expect(typeInput.element.value).toBe('Ventilator');
    expect(statusSelect.element.value).toBe('In Use');
    expect(locationInput.element.value).toBe('OR 3');
  });

  // Test case for submitting the form in add mode
  it('emits save event with form data when submitting in add mode', async () => {
    const wrapper = mount(AddEquipmentForm);
    const nameInput = wrapper.find('input#equipment-name');
    const typeInput = wrapper.find('input#equipment-type');
    const statusSelect = wrapper.find('select#equipment-status');
    const locationInput = wrapper.find('input#equipment-location');
    const form = wrapper.find('form');

    await nameInput.setValue('New Infusion Pump');
    await typeInput.setValue('Infusion Pump');
    await statusSelect.setValue('Available');
    await locationInput.setValue('Storage');

    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: null,
      name: 'New Infusion Pump',
      type: 'Infusion Pump',
      status: 'Available',
      location: 'Storage',
    });
  });

  // Test case for submitting the form in edit mode
  it('emits save event with updated form data and isUpdate flag when submitting in edit mode', async () => {
    const initialData = {
      id: 2,
      name: 'Laser Machine',
      type: 'Laser',
      status: 'Maintenance',
      location: 'Laser Room',
    };
    const wrapper = mount(AddEquipmentForm, { props: { equipmentToEdit: initialData } });

    const nameInput = wrapper.find('input#equipment-name');
    const statusSelect = wrapper.find('select#equipment-status');
    const form = wrapper.find('form');

    await nameInput.setValue('Updated Laser Machine');
    await statusSelect.setValue('Available');

    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: 2,
      name: 'Updated Laser Machine',
      type: 'Laser', // Type should remain unchanged as per edit mode behavior logic (though not disabled in template)
      status: 'Available',
      location: 'Laser Room', // Location should remain unchanged
      isUpdate: true, // Flag should be true in edit mode
    });
  });

  // Test case for emitting cancel event
  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(AddEquipmentForm);
    await wrapper.find('button.button-secondary').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  // Test case for validation - missing required fields
  it('shows validation errors for missing required fields on submit', async () => {
    const wrapper = mount(AddEquipmentForm);
    const form = wrapper.find('form');

    await form.trigger('submit.prevent');

    expect(wrapper.find('span.error-message').exists()).toBe(true); // At least one error message should be shown
    expect(wrapper.text()).toContain('Name/ID is required.');
    expect(wrapper.text()).toContain('Type is required.');
    expect(wrapper.text()).toContain('Status is required.');
    expect(wrapper.emitted('save')).toBeUndefined(); // Save should not be emitted
  });

  // Test case for clearing validation errors on input
  it('clears validation errors on input', async () => {
    const wrapper = mount(AddEquipmentForm);
    const nameInput = wrapper.find('input#equipment-name');
    const form = wrapper.find('form');

    // Submit once to show errors
    await form.trigger('submit.prevent');
    expect(wrapper.find('span.error-message').exists()).toBe(true);

    // Enter value and check if error clears
    await nameInput.setValue('Some Name');
    expect(wrapper.text()).not.toContain('Name/ID is required.');
  });

  // Test case for resetting form after successful submission (simulated)
  it('resets form after successful submission', async () => {
     const wrapper = mount(AddEquipmentForm);
     const nameInput = wrapper.find('input#equipment-name');
     const typeInput = wrapper.find('input#equipment-type');
     const statusSelect = wrapper.find('select#equipment-status');
     const form = wrapper.find('form');

     await nameInput.setValue('To Be Reset');
     await typeInput.setValue('To Be Reset Type');
     await statusSelect.setValue('Available');

     // Simulate successful save by calling handleSubmit directly after filling
     // In a real scenario, this would happen after the parent handles the emit
     // We'll test the state change directly here for simplicity.
     await wrapper.vm.handleSubmit();

     // Check if form fields are reset to initial state
     expect(nameInput.element.value).toBe('');
     expect(typeInput.element.value).toBe('');
     expect(statusSelect.element.value).toBe('');
     expect(wrapper.find('.error-message').exists()).toBe(false); // Errors should also be cleared
  });

   // Test case for resetting form on cancel
    it('resets form and clears errors on cancel', async () => {
       const wrapper = mount(AddEquipmentForm);
       const nameInput = wrapper.find('input#equipment-name');
       const typeInput = wrapper.find('input#equipment-type');
       const cancelButton = wrapper.find('button.button-secondary');
       const form = wrapper.find('form');

       // Put some data in the form and trigger validation to show errors
       await nameInput.setValue('Some Data');
       await form.trigger('submit.prevent'); // This will show errors
       expect(wrapper.find('.error-message').exists()).toBe(true);

       // Click cancel
       await cancelButton.trigger('click');

       // Check if form fields are reset and errors cleared
       expect(nameInput.element.value).toBe('');
       expect(typeInput.element.value).toBe('');
       expect(wrapper.find('.error-message').exists()).toBe(false);
       expect(wrapper.emitted('cancel')).toBeTruthy(); // Ensure cancel event was emitted
    });

    // Snapshot test in add mode
    it('matches snapshot in add mode', () => {
        const wrapper = mount(AddEquipmentForm, { props: { equipmentToEdit: null } });
        expect(wrapper.html()).toMatchSnapshot();
    });

    // Snapshot test in edit mode
     it('matches snapshot in edit mode', () => {
         const initialData = {
           id: 3,
           name: 'X-Ray Machine',
           type: 'Imaging',
           status: 'Available',
           location: 'Mobile',
         };
         const wrapper = mount(AddEquipmentForm, { props: { equipmentToEdit: initialData } });
         expect(wrapper.html()).toMatchSnapshot();
     });
});