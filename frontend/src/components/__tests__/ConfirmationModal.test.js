import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ConfirmationModal from '../ConfirmationModal.vue';

describe('ConfirmationModal', () => {
  const defaultProps = {
    show: true,
    title: 'Test Title',
    message: 'Test Message',
  };

  it('renders correctly when show prop is true', () => {
    const wrapper = mount(ConfirmationModal, { props: defaultProps });
    expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    expect(wrapper.text()).toContain(defaultProps.title);
    expect(wrapper.text()).toContain(defaultProps.message);
    // Check default button text if props are not provided
    const confirmButton = wrapper.find('button.button-danger');
    const cancelButton = wrapper.find('button.button-secondary');
    expect(confirmButton.exists()).toBe(true);
    expect(cancelButton.exists()).toBe(true);
    expect(confirmButton.text()).toBe('Confirm'); // Default text from template
    expect(cancelButton.text()).toBe('Cancel'); // Default text from template
  });

  it('emits confirm event when confirm button is clicked', async () => {
    const wrapper = mount(ConfirmationModal, { props: defaultProps });
    await wrapper.find('button.button-danger').trigger('click');
    expect(wrapper.emitted('confirm')).toBeTruthy();
  });

  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(ConfirmationModal, { props: defaultProps });
    await wrapper.find('button.button-secondary').trigger('click');
    expect(wrapper.emitted('cancel')).toBeTruthy();
  });

  it('does not render when show prop is false', () => {
    const wrapper = mount(ConfirmationModal, { props: { ...defaultProps, show: false } });
    expect(wrapper.find('.modal-overlay').exists()).toBe(false);
  });

  // Snapshot test remains the same, but will capture the corrected HTML
  it('matches snapshot when shown', () => {
    const wrapper = mount(ConfirmationModal, { props: defaultProps });
    expect(wrapper.html()).toMatchSnapshot();
  });
});