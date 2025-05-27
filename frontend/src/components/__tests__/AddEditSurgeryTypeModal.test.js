import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import AddEditSurgeryTypeModal from '../AddEditSurgeryTypeModal.vue';

describe('AddEditSurgeryTypeModal', () => {
  // Test case for adding a new surgery type
  it('renders correctly in add mode', () => {
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true, // Assume show prop is added and controls visibility
        isEditing: false,
      },
    });

    expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain('Add New Surgery Type');
    expect(wrapper.find('input#type-name').exists()).toBe(true);
    expect(wrapper.find('input#type-code').exists()).toBe(true);
    expect(wrapper.find('textarea#type-description').exists()).toBe(true);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Add Type');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
  });

  // Test case for editing an existing surgery type
  it('renders correctly in edit mode with initial data', () => {
    const initialData = {
      id: 123,
      name: 'Existing Type',
      code: 'EXT',
      description: 'Existing Description',
    };
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true, // Assume show prop is added and controls visibility
        isEditing: true,
        initialData: initialData,
      },
    });

    expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain('Edit Surgery Type');
    expect(wrapper.find('input#type-name').element.value).toBe(initialData.name);
    expect(wrapper.find('input#type-code').element.value).toBe(initialData.code);
    expect(wrapper.find('textarea#type-description').element.value).toBe(initialData.description);
    expect(wrapper.find('button[type="submit"]').text()).toBe('Save Changes');
    expect(wrapper.find('button[type="button"]').text()).toBe('Cancel');
  });

  // Test case for submitting the form in add mode
  it('emits save event with form data when submitting in add mode', async () => {
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true,
        isEditing: false,
      },
    });

    const nameInput = wrapper.find('input#type-name');
    const codeInput = wrapper.find('input#type-code');
    const descriptionInput = wrapper.find('textarea#type-description');
    const form = wrapper.find('form');

    await nameInput.setValue('New Type');
    await codeInput.setValue('NT');
    await descriptionInput.setValue('New Description');
    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: null, // ID should be null in add mode
      name: 'New Type',
      code: 'NT',
      description: 'New Description',
    });
  });

  // Test case for submitting the form in edit mode
  it('emits save event with updated form data when submitting in edit mode', async () => {
    const initialData = {
      id: 123,
      name: 'Existing Type',
      code: 'EXT',
      description: 'Existing Description',
    };
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true,
        isEditing: true,
        initialData: initialData,
      },
    });

    const nameInput = wrapper.find('input#type-name');
    // code and description are not changed in this test
    const form = wrapper.find('form');

    await nameInput.setValue('Updated Type');
    await form.trigger('submit.prevent');

    expect(wrapper.emitted('save')).toBeTruthy();
    expect(wrapper.emitted('save')[0][0]).toEqual({
      id: 123,
      name: 'Updated Type',
      code: 'EXT',
      description: 'Existing Description',
    });
  });

  // Test case for emitting cancel event from button
  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true,
      },
    });
    await wrapper.find('button.button-secondary').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

   // Test case for emitting cancel event from overlay click
   it('emits cancel event when clicking on modal overlay', async () => {
       const wrapper = mount(AddEditSurgeryTypeModal, {
           props: {
               show: true,
           },
       });
       await wrapper.find('.modal-overlay').trigger('click.self');
       expect(wrapper.emitted('cancel')).toBeTruthy();
   });

  // Test case for not rendering when show is false
  it('does not render when show prop is false', () => {
    const wrapper = mount(AddEditSurgeryTypeModal, { props: { show: false } });
    expect(wrapper.find('.modal-overlay').exists()).toBe(false);
  });

  // Snapshot tests
  it('matches snapshot in add mode', () => {
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true,
        isEditing: false,
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });

  it('matches snapshot in edit mode', () => {
    const initialData = {
      id: 456,
      name: 'Another Existing Type',
      code: 'AET',
      description: 'Another Description',
    };
    const wrapper = mount(AddEditSurgeryTypeModal, {
      props: {
        show: true,
        isEditing: true,
        initialData: initialData,
      },
    });
    expect(wrapper.html()).toMatchSnapshot();
  });
});