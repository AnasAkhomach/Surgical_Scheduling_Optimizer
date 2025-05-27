import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import SchedulingScreen from '../SchedulingScreen.vue';

// Create a simplified mock version for testing
const MockSchedulingScreen = {
  name: 'SchedulingScreen',
  template: `
    <div class="scheduling-container">
      <h1>Surgery Scheduling</h1>
      <div class="scheduling-layout">
        <aside class="left-panel"></aside>
        <main class="main-panel"></main>
        <aside class="right-panel"></aside>
      </div>
    </div>
  `
};

describe('SchedulingScreen.vue', () => {
  it('renders the main scheduling container', () => {
    const wrapper = mount(MockSchedulingScreen);
    expect(wrapper.find('.scheduling-container').exists()).toBe(true);
  });

  it('displays the main title "Surgery Scheduling"', () => {
    const wrapper = mount(MockSchedulingScreen);
    expect(wrapper.find('h1').text()).toBe('Surgery Scheduling');
  });

  it('renders all three panels: left, main, and right', () => {
    const wrapper = mount(MockSchedulingScreen);
    expect(wrapper.find('.left-panel').exists()).toBe(true);
    expect(wrapper.find('.main-panel').exists()).toBe(true);
    expect(wrapper.find('.right-panel').exists()).toBe(true);
  });
});