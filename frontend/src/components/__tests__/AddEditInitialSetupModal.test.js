import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import AddEditInitialSetupModal from '../AddEditInitialSetupModal.vue';

describe('AddEditInitialSetupModal', () => {
  const mockSurgeryTypes = [
    { id: 1, name: 'Surgery Type A' },
    { id: 2, name: 'Surgery Type B' },
  ];

  // Test case for adding a new initial setup time
  it('renders correctly in add mode', () => {
    const wrapper = mount(AddEditInitialSetupModal, {
      props: {
        show: true,
        isEditing: false,
        surgeryTypes: mockSurgeryTypes,
      },
    });

    expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain('Add New Initial Setup Time');
    expect(wrapper.find('select#setup-type').exists()).toBe(true);
    expect(wrapper.find('select#setup-type').attributes('disabled')).toBeUndefined();
    expect(wrapper.find('input#setup-time').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Add Setup Time');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
  });

  // Test case for editing an existing initial setup time
  it('renders correctly in edit mode', () => {
    const initialData = { typeId: 1, time: 30 };
    const wrapper = mount(AddEditInitialSetupModal, {
      props: {
        show: true,
        isEditing: true,
        initialData: initialData,
        surgeryTypes: mockSurgeryTypes,
      },
    });

    expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain('Edit Initial Setup Time');
    expect(wrapper.find('select#setup-type').exists()).toBe(true);
    expect(wrapper.find('select#setup-type').attributes('disabled')).toBe(''); // Check for disabled attribute presence
    expect(wrapper.find('select#setup-type').element.value).toBe(initialData.typeId.toString()); // Select value is string
    expect(wrapper.find('input#setup-time').exists()).toBe(true);
    expect(wrapper.find('input#setup-time').element.value).toBe(initialData.time.toString()); // Input value is string
    expect(wrapper.find('button[type="submit"]').text()).toBe('Save Changes');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
  });

  // Test case for submitting the form in add mode
  it('emits save event with form data when submitting in add mode', async () => {
    const wrapper = mount(AddEditInitialSetupModal, {
      props: {
        show: true,
        isEditing: false,
        surgeryTypes: mockSurgeryTypes,
      },
    });

    const typeSelect = wrapper.find('select#setup-type');
    const timeInput = wrapper.find('input#setup-time');
    const form = wrapper.find('form');

    await typeSelect.setValue(mockSurgeryTypes[0].id);
    await timeInput.setValue(45);
    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      typeId: mockSurgeryTypes[0].id,
      time: 45,
    });
  });

  // Test case for submitting the form in edit mode
  it('emits save event with updated form data when submitting in edit mode', async () => {
    const initialData = { typeId: 1, time: 30, id: 123 }; // Include an ID for editing scenario
    const wrapper = mount(AddEditInitialSetupModal, {
      props: {
        show: true,
        isEditing: true,
        initialData: initialData,
        surgeryTypes: mockSurgeryTypes,
      },
    });

    const timeInput = wrapper.find('input#setup-time');
    const form = wrapper.find('form');

    await timeInput.setValue(60);
    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      typeId: initialData.typeId,
      time: 60,
      id: initialData.id, // Ensure ID is included in edited data
    });
  });

  // Test case for emitting cancel event
  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(AddEditInitialSetupModal, {
      props: {
         show: true,
         surgeryTypes: mockSurgeryTypes,
      },
    });
    await wrapper.find('button.button-secondary').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  // Test case for clicking outside the modal
   it('emits cancel event when clicking on modal overlay', async () => {
       const wrapper = mount(AddEditInitialSetupModal, {
           props: {
               show: true,
               surgeryTypes: mockSurgeryTypes,
           },
       });
       await wrapper.find('.modal-overlay').trigger('click.self');
       expect(wrapper.emitted('cancel')).toBeTruthy();
   });

  // Test case for not rendering when show is false
  it('does not render when show prop is false', () => {
    const wrapper = mount(AddEditInitialSetupModal, { props: { show: false, surgeryTypes: mockSurgeryTypes } });
    expect(wrapper.find('.modal-overlay').exists()).toBe(false);
  });

  // Snapshot test
  it('matches snapshot in add mode', () => {
    const wrapper = mount(AddEditInitialSetupModal, {
      props: {
        show: true,
        isEditing: false,
        surgeryTypes: mockSurgeryTypes,
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });

   it('matches snapshot in edit mode', () => {
     const initialData = { typeId: 1, time: 30 };
       const wrapper = mount(AddEditInitialSetupModal, {
         props: {
           show: true,
           isEditing: true,
           initialData: initialData,
           surgeryTypes: mockSurgeryTypes,
         },
       });
       expect(wrapper.html()).toMatchSnapshot();
   });

    // Basic validation tests (can be expanded)
    it('shows alert if surgery type is not selected in add mode', async () => {
        const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {}); // Mock alert
        const wrapper = mount(AddEditInitialSetupModal, {
            props: {
                show: true,
                isEditing: false,
                surgeryTypes: mockSurgeryTypes,
            },
        });

        const timeInput = wrapper.find('input#setup-time');
        const form = wrapper.find('form');

        await timeInput.setValue(45);
        await form.trigger('submit.prevent');

        expect(alertSpy).toHaveBeenCalledWith('Please select a Surgery Type.');
        expect(wrapper.emitted('save')).toBeUndefined(); // Ensure save was NOT emitted

        alertSpy.mockRestore(); // Restore original alert
    });

     it('shows alert if time is negative', async () => {
         const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {}); // Mock alert
         const wrapper = mount(AddEditInitialSetupModal, {
             props: {
                 show: true,
                 isEditing: false,
                 surgeryTypes: mockSurgeryTypes,
             },
         });

         const typeSelect = wrapper.find('select#setup-type');
         const timeInput = wrapper.find('input#setup-time');
         const form = wrapper.find('form');

         await typeSelect.setValue(mockSurgeryTypes[0].id);
         await timeInput.setValue(-10);
         await form.trigger('submit.prevent');

         expect(alertSpy).toHaveBeenCalledWith('Setup time cannot be negative.');
         expect(wrapper.emitted('save')).toBeUndefined(); // Ensure save was NOT emitted

         alertSpy.mockRestore(); // Restore original alert
     });
});