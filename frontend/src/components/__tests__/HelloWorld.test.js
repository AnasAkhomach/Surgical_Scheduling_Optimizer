import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../HelloWorld.vue';

describe('HelloWorld', () => {
  let wrapper;

  beforeEach(() => {
    wrapper = mount(HelloWorld, { props: { msg: 'Hello Vitest' } });
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders properly with message prop', () => {
    expect(wrapper.text()).toContain('Hello Vitest');
    expect(wrapper.find('h1').text()).toBe('Hello Vitest');
  });

  it('renders with different message prop', () => {
    const customWrapper = mount(HelloWorld, { props: { msg: 'Custom Message' } });
    expect(customWrapper.find('h1').text()).toBe('Custom Message');
    customWrapper.unmount();
  });

  it('renders without message prop', () => {
    const noPropsWrapper = mount(HelloWorld);
    expect(noPropsWrapper.find('h1').text()).toBe(''); // Should be empty when no prop provided
    noPropsWrapper.unmount();
  });

  it('displays initial count as 0', () => {
    const button = wrapper.find('button');
    expect(button.text()).toBe('count is 0');
  });

  it('increments count when button is clicked', async () => {
    const button = wrapper.find('button');

    // Initial state
    expect(button.text()).toBe('count is 0');

    // Click once
    await button.trigger('click');
    expect(button.text()).toBe('count is 1');

    // Click again
    await button.trigger('click');
    expect(button.text()).toBe('count is 2');

    // Click multiple times
    await button.trigger('click');
    await button.trigger('click');
    await button.trigger('click');
    expect(button.text()).toBe('count is 5');
  });

  it('renders static content correctly', () => {
    expect(wrapper.text()).toContain('Edit');
    expect(wrapper.text()).toContain('components/HelloWorld.vue');
    expect(wrapper.text()).toContain('to test HMR');
    expect(wrapper.text()).toContain('Check out');
    expect(wrapper.text()).toContain('create-vue');
    expect(wrapper.text()).toContain('Learn more about IDE Support');
    expect(wrapper.text()).toContain('Click on the Vite and Vue logos to learn more');
  });

  it('renders external links with correct attributes', () => {
    const links = wrapper.findAll('a');
    expect(links.length).toBe(2);

    // First link - create-vue
    expect(links[0].attributes('href')).toBe('https://vuejs.org/guide/quick-start.html#local');
    expect(links[0].attributes('target')).toBe('_blank');
    expect(links[0].text()).toBe('create-vue');

    // Second link - Vue Docs
    expect(links[1].attributes('href')).toBe('https://vuejs.org/guide/scaling-up/tooling.html#ide-support');
    expect(links[1].attributes('target')).toBe('_blank');
    expect(links[1].text()).toBe('Vue Docs Scaling up Guide');
  });

  it('has correct CSS classes', () => {
    expect(wrapper.find('.card').exists()).toBe(true);
    expect(wrapper.find('.read-the-docs').exists()).toBe(true);
  });

  it('button has correct type attribute', () => {
    const button = wrapper.find('button');
    expect(button.attributes('type')).toBe('button');
  });

  it('maintains independent count state across multiple instances', async () => {
    const wrapper1 = mount(HelloWorld, { props: { msg: 'Instance 1' } });
    const wrapper2 = mount(HelloWorld, { props: { msg: 'Instance 2' } });

    const button1 = wrapper1.find('button');
    const button2 = wrapper2.find('button');

    // Click first instance button
    await button1.trigger('click');
    await button1.trigger('click');

    // Click second instance button once
    await button2.trigger('click');

    // Each instance should maintain its own count
    expect(button1.text()).toBe('count is 2');
    expect(button2.text()).toBe('count is 1');

    wrapper1.unmount();
    wrapper2.unmount();
  });

  it('renders code element correctly', () => {
    const codeElement = wrapper.find('code');
    expect(codeElement.exists()).toBe(true);
    expect(codeElement.text()).toBe('components/HelloWorld.vue');
  });
})