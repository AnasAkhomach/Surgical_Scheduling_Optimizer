import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import AddStaffForm from '../AddStaffForm.vue';

describe('AddStaffForm', () => {
  // Test case for rendering in add mode
  it('renders correctly in add mode', () => {
    const wrapper = mount(AddStaffForm, {
      props: { staffToEdit: null },
    });

    expect(wrapper.text()).toContain('Add New Staff Member');
    expect(wrapper.find('input#staff-name').exists()).toBe(true);
    expect(wrapper.find('select#staff-role').exists()).toBe(true);
    expect(wrapper.find('input#staff-specializations').exists()).toBe(true);
    expect(wrapper.find('select#staff-status').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Save Staff');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
    expect(wrapper.find('.error-message').exists()).toBe(false); // No errors initially
  });

  // Test case for rendering in edit mode with initial data
  it('renders correctly in edit mode with initial data', () => {
    const initialData = {
      id: 1,
      name: 'Dr. Smith',
      role: 'Surgeon',
      specializations: ['Orthopedics', 'Sports Medicine'],
      status: 'Active',
    };
    const wrapper = mount(AddStaffForm, {
      props: { staffToEdit: initialData },
    });

    expect(wrapper.text()).toContain('Edit Staff Member');
    expect(wrapper.find('input#staff-name').element.value).toBe(initialData.name);
    expect(wrapper.find('select#staff-role').element.value).toBe(initialData.role);
    expect(wrapper.find('input#staff-specializations').element.value).toBe('Orthopedics, Sports Medicine');
    expect(wrapper.find('select#staff-status').element.value).toBe(initialData.status);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Update Staff');
  });

  // Test case for form input and data binding
  it('updates form data on input', async () => {
    const wrapper = mount(AddStaffForm);
    const nameInput = wrapper.find('input#staff-name');
    const roleSelect = wrapper.find('select#staff-role');
    const specializationsInput = wrapper.find('input#staff-specializations');
    const statusSelect = wrapper.find('select#staff-status');

    await nameInput.setValue('Dr. Johnson');
    await roleSelect.setValue('Anesthetist');
    await specializationsInput.setValue('Pediatric, General');
    await statusSelect.setValue('Active');

    // Check the element values
    expect(nameInput.element.value).toBe('Dr. Johnson');
    expect(roleSelect.element.value).toBe('Anesthetist');
    expect(specializationsInput.element.value).toBe('Pediatric, General');
    expect(statusSelect.element.value).toBe('Active');
  });

  // Test case for submitting the form in add mode
  it('emits save event with form data when submitting in add mode', async () => {
    const wrapper = mount(AddStaffForm);
    const nameInput = wrapper.find('input#staff-name');
    const roleSelect = wrapper.find('select#staff-role');
    const specializationsInput = wrapper.find('input#staff-specializations');
    const statusSelect = wrapper.find('select#staff-status');
    const form = wrapper.find('form');

    await nameInput.setValue('Dr. Williams');
    await roleSelect.setValue('Surgeon');
    await specializationsInput.setValue('Cardiology, Vascular');
    await statusSelect.setValue('Active');

    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: null,
      name: 'Dr. Williams',
      role: 'Surgeon',
      specializations: ['Cardiology', 'Vascular'],
      status: 'Active',
    });
  });

  // Test case for submitting the form in edit mode
  it('emits save event with updated form data and isUpdate flag when submitting in edit mode', async () => {
    const initialData = {
      id: 2,
      name: 'Dr. Brown',
      role: 'Nurse',
      specializations: ['ICU'],
      status: 'On Leave',
    };
    const wrapper = mount(AddStaffForm, { props: { staffToEdit: initialData } });

    const nameInput = wrapper.find('input#staff-name');
    const statusSelect = wrapper.find('select#staff-status');
    const form = wrapper.find('form');

    await nameInput.setValue('Dr. Brown Updated');
    await statusSelect.setValue('Active');

    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: 2,
      name: 'Dr. Brown Updated',
      role: 'Nurse',
      specializations: ['ICU'],
      status: 'Active',
      isUpdate: true,
    });
  });

  // Test case for emitting cancel event
  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(AddStaffForm);
    await wrapper.find('button.button-secondary').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  // Test case for validation - missing required fields
  it('shows validation errors for missing required fields on submit', async () => {
    const wrapper = mount(AddStaffForm);
    const form = wrapper.find('form');

    await form.trigger('submit.prevent');

    expect(wrapper.find('span.error-message').exists()).toBe(true); // At least one error message should be shown
    expect(wrapper.text()).toContain('Name is required.');
    expect(wrapper.text()).toContain('Role is required.');
    expect(wrapper.text()).toContain('Status is required.');
    expect(wrapper.emitted('save')).toBeUndefined(); // Save should not be emitted
  });

  // Test case for clearing validation errors on input
  it('clears validation errors on input', async () => {
    const wrapper = mount(AddStaffForm);
    const nameInput = wrapper.find('input#staff-name');
    const form = wrapper.find('form');

    // Submit once to show errors
    await form.trigger('submit.prevent');
    expect(wrapper.find('span.error-message').exists()).toBe(true);

    // Enter value and check if error clears
    await nameInput.setValue('Dr. Test');
    expect(wrapper.text()).not.toContain('Name is required.');

    // Also check for role error clearing
    const roleSelect = wrapper.find('select#staff-role');
    await roleSelect.setValue('Surgeon');
    expect(wrapper.text()).not.toContain('Role is required.');
  });

  // Test case for resetting form after successful submission
  it('resets form after successful submission', async () => {
    const wrapper = mount(AddStaffForm);
    const nameInput = wrapper.find('input#staff-name');
    const roleSelect = wrapper.find('select#staff-role');
    const statusSelect = wrapper.find('select#staff-status');

    await nameInput.setValue('To Be Reset');
    await roleSelect.setValue('Surgeon');
    await statusSelect.setValue('Active');

    // Simulate successful save by calling handleSubmit directly
    await wrapper.vm.handleSubmit();

    // Check if form fields are reset to initial state
    expect(nameInput.element.value).toBe('');
    expect(roleSelect.element.value).toBe('');
    expect(statusSelect.element.value).toBe('');
    expect(wrapper.find('.error-message').exists()).toBe(false); // Errors should also be cleared
  });

  // Test case for resetting form and clearing errors on cancel
  it('resets form and clears errors on cancel', async () => {
    const wrapper = mount(AddStaffForm);
    const nameInput = wrapper.find('input#staff-name');
    const form = wrapper.find('form');

    // Put some data in the form and trigger validation to show errors
    await nameInput.setValue('Some Staff Data');
    await form.trigger('submit.prevent'); // This will show errors
    expect(wrapper.find('.error-message').exists()).toBe(true);

    // Click cancel
    await wrapper.find('button.button-secondary').trigger('click');

    // Check if form fields are reset and errors cleared
    expect(nameInput.element.value).toBe('');
    expect(wrapper.find('.error-message').exists()).toBe(false);
    expect(wrapper.emitted('cancel')).toBeTruthy(); // Ensure cancel event was emitted
  });

  // Test case for specializations string to array conversion
  it('converts specializations string to array correctly', async () => {
    const wrapper = mount(AddStaffForm);
    const specializationsInput = wrapper.find('input#staff-specializations');

    await specializationsInput.setValue('Cardiology, Neurology, Pediatrics');

    // Trigger form submission to check the emitted data
    const nameInput = wrapper.find('input#staff-name');
    const roleSelect = wrapper.find('select#staff-role');
    const statusSelect = wrapper.find('select#staff-status');

    await nameInput.setValue('Dr. Specialist');
    await roleSelect.setValue('Surgeon');
    await statusSelect.setValue('Active');

    await wrapper.find('form').trigger('submit.prevent');

    const emittedData = wrapper.emitted('save')[0][0];
    expect(emittedData.specializations).toEqual(['Cardiology', 'Neurology', 'Pediatrics']);
  });

  // Snapshot test in add mode
  it('matches snapshot in add mode', () => {
    const wrapper = mount(AddStaffForm);
    expect(wrapper.html()).toMatchSnapshot();
  });

  // Snapshot test in edit mode
  it('matches snapshot in edit mode', () => {
    const initialData = {
      id: 3,
      name: 'Dr. Snapshot',
      role: 'Surgeon',
      specializations: ['General'],
      status: 'Active',
    };
    const wrapper = mount(AddStaffForm, { props: { staffToEdit: initialData } });
    expect(wrapper.html()).toMatchSnapshot();
  });
});