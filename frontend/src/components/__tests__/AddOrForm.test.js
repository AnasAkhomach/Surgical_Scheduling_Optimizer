import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import AddOrForm from '../AddOrForm.vue';

describe('AddOrForm', () => {
  // Test case for rendering in add mode
  it('renders correctly in add mode', () => {
    const wrapper = mount(AddOrForm, {
      props: { orToEdit: null },
    });

    expect(wrapper.text()).toContain('Add New Operating Room');
    expect(wrapper.find('input#or-name').exists()).toBe(true);
    expect(wrapper.find('input#or-location').exists()).toBe(true);
    expect(wrapper.find('select#or-status').exists()).toBe(true);
    expect(wrapper.find('input#or-service').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Save OR');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
    expect(wrapper.find('.error-message').exists()).toBe(false); // No errors initially
  });

  // Test case for rendering in edit mode with initial data
  it('renders correctly in edit mode with initial data', () => {
    const initialData = {
      id: 1,
      name: 'OR 1',
      location: 'Floor 2',
      status: 'Active',
      primaryService: 'General Surgery',
    };
    const wrapper = mount(AddOrForm, {
      props: { orToEdit: initialData },
    });

    expect(wrapper.text()).toContain('Edit Operating Room');
    expect(wrapper.find('input#or-name').element.value).toBe(initialData.name);
    expect(wrapper.find('input#or-location').element.value).toBe(initialData.location);
    expect(wrapper.find('select#or-status').element.value).toBe(initialData.status);
    expect(wrapper.find('input#or-service').element.value).toBe(initialData.primaryService);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Update OR');
  });

  // Test case for form input and data binding
  it('updates form data on input', async () => {
    const wrapper = mount(AddOrForm);
    const nameInput = wrapper.find('input#or-name');
    const locationInput = wrapper.find('input#or-location');
    const statusSelect = wrapper.find('select#or-status');
    const serviceInput = wrapper.find('input#or-service');

    await nameInput.setValue('OR 5');
    await locationInput.setValue('Floor 3');
    await statusSelect.setValue('Under Maintenance');
    await serviceInput.setValue('Orthopedics');

    // Check the element values still
    expect(nameInput.element.value).toBe('OR 5');
    expect(locationInput.element.value).toBe('Floor 3');
    expect(statusSelect.element.value).toBe('Under Maintenance');
    expect(serviceInput.element.value).toBe('Orthopedics');
  });

  // Test case for submitting the form in add mode
  it('emits save event with form data and generated id when submitting in add mode', async () => {
    const wrapper = mount(AddOrForm);
    const nameInput = wrapper.find('input#or-name');
    const locationInput = wrapper.find('input#or-location');
    const statusSelect = wrapper.find('select#or-status');
    const serviceInput = wrapper.find('input#or-service');
    const form = wrapper.find('form');

    await nameInput.setValue('OR 6');
    await locationInput.setValue('Basement');
    await statusSelect.setValue('Active');
    await serviceInput.setValue('Cardiology');

    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    const emittedData = wrapper.emitted('save')[0][0];
    expect(emittedData).toMatchObject({
      name: 'OR 6',
      location: 'Basement',
      status: 'Active',
      primaryService: 'Cardiology',
    });
    expect(emittedData.id).toBeTypeOf('string'); // Check if an ID string is generated
  });

  // Test case for submitting the form in edit mode
  it('emits save event with updated form data and isUpdate flag when submitting in edit mode', async () => {
    const initialData = {
      id: 2,
      name: 'OR 2',
      location: 'Floor 1',
      status: 'Active',
      primaryService: 'Neurosurgery',
    };
    const wrapper = mount(AddOrForm, { props: { orToEdit: initialData } });

    const nameInput = wrapper.find('input#or-name');
    const statusSelect = wrapper.find('select#or-status');
    const form = wrapper.find('form');

    await nameInput.setValue('OR 2 Updated');
    await statusSelect.setValue('Inactive');

    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: 2,
      name: 'OR 2 Updated',
      location: 'Floor 1',
      status: 'Inactive',
      primaryService: 'Neurosurgery',
      isUpdate: true,
    });
  });

  // Test case for emitting cancel event
  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(AddOrForm);
    await wrapper.find('button.button-secondary').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  // Test case for validation - missing required fields
  it('shows validation errors for missing required fields on submit', async () => {
    const wrapper = mount(AddOrForm);
    const form = wrapper.find('form');

    await form.trigger('submit.prevent');

    expect(wrapper.find('span.error-message').exists()).toBe(true); // At least one error message should be shown
    expect(wrapper.text()).toContain('Name/ID is required.');
    expect(wrapper.text()).toContain('Status is required.');
    expect(wrapper.emitted('save')).toBeUndefined(); // Save should not be emitted
  });

  // Test case for clearing validation errors on input
  it('clears validation errors on input', async () => {
    const wrapper = mount(AddOrForm);
    const nameInput = wrapper.find('input#or-name');
    const form = wrapper.find('form');

    // Submit once to show errors
    await form.trigger('submit.prevent');
    expect(wrapper.find('span.error-message').exists()).toBe(true);

    // Enter value and check if error clears
    await nameInput.setValue('Some OR Name');
    expect(wrapper.text()).not.toContain('Name/ID is required.');

     // Also check for status error clearing
     const statusSelect = wrapper.find('select#or-status');
     await statusSelect.setValue('Active');
     expect(wrapper.text()).not.toContain('Status is required.');
  });

  // Test case for resetting form after successful submission (simulated)
  it('emits save event and does not reset form itself on successful submission', async () => {
     const wrapper = mount(AddOrForm);
     const nameInput = wrapper.find('input#or-name');
     const statusSelect = wrapper.find('select#or-status');
     // const form = wrapper.find('form'); // Not needed if directly calling handleSubmit

     await nameInput.setValue('To Be Reset OR');
     await statusSelect.setValue('Active');

     // Simulate successful save by calling handleSubmit directly after filling
     await wrapper.vm.handleSubmit();

     // Check that the save event was emitted
     expect(wrapper.emitted('save')).toBeTruthy();
     const emittedData = wrapper.emitted('save')[0][0];
    expect(emittedData).toMatchObject({
      name: 'To Be Reset OR',
      status: 'Active',
    });

     // Check that form fields are NOT reset by the component itself
     expect(nameInput.element.value).toBe('To Be Reset OR');
     expect(statusSelect.element.value).toBe('Active');
     expect(wrapper.find('.error-message').exists()).toBe(false); // Errors should be cleared if submission was valid
  });

   // Test case for resetting form and clearing errors on cancel
    it('resets form and clears errors on cancel', async () => {
       const wrapper = mount(AddOrForm);
       const nameInput = wrapper.find('input#or-name');
       const form = wrapper.find('form');

       // Put some data in the form and trigger validation to show errors
       await nameInput.setValue('Some OR Data');
       await form.trigger('submit.prevent'); // This will show errors
       expect(wrapper.find('.error-message').exists()).toBe(true);

       // Click cancel
       await wrapper.find('button.button-secondary').trigger('click');

       // Check if form fields are reset and errors cleared
       expect(nameInput.element.value).toBe('');
       expect(wrapper.find('.error-message').exists()).toBe(false);
       expect(wrapper.emitted('cancel')).toBeTruthy(); // Ensure cancel event was emitted
    });

    // Snapshot test in add mode
    it('matches snapshot in add mode', () => {
        const wrapper = mount(AddOrForm, { props: { orToEdit: null } });
        expect(wrapper.html()).toMatchSnapshot();
    });

    // Snapshot test in edit mode
     it('matches snapshot in edit mode', () => {
         const initialData = {
           id: 3,
           name: 'OR 3',
           location: 'Floor 4',
           status: 'Inactive',
           primaryService: 'Pediatrics',
         };
         const wrapper = mount(AddOrForm, { props: { orToEdit: initialData } });
         expect(wrapper.html()).toMatchSnapshot();
     });
});