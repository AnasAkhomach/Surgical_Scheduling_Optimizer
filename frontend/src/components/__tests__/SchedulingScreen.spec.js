import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia'; // Import createPinia
import SchedulingScreen from '../SchedulingScreen.vue';

describe('SchedulingScreen.vue', () => {
  let pinia; // Declare pinia variable

  beforeEach(() => {
    pinia = createPinia(); // Create a new Pinia instance
  });

  it('renders the main scheduling container', () => {
    const wrapper = mount(SchedulingScreen, {
      global: {
        plugins: [pinia] // Add pinia to plugins
      }
    });
    expect(wrapper.find('.scheduling-container').exists()).toBe(true);
  });

  it('displays the main title "Surgery Scheduling"', () => {
    const wrapper = mount(SchedulingScreen, {
      global: {
        plugins: [pinia] // Add pinia to plugins
      }
    });
    expect(wrapper.find('h1').text()).toBe('Surgery Scheduling');
  });

  // Add more tests here
});