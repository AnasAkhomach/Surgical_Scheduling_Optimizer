import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { ref } from 'vue';
import BulkSDSTEditor from '../BulkSDSTEditor.vue';

// Mock the schedule store
const mockSurgeryTypes = {
  'CABG': { name: 'Coronary Artery Bypass Graft', duration: 240 },
  'KNEE': { name: 'Knee Replacement', duration: 120 },
  'APPEN': { name: 'Appendectomy', duration: 60 }
};

const mockSdsRules = {
  'CABG': { 'KNEE': 45, 'APPEN': 30 },
  'KNEE': { 'CABG': 60, 'APPEN': 15 },
  'APPEN': { 'CABG': 50, 'KNEE': 20 }
};

vi.mock('@/stores/scheduleStore', () => ({
  useScheduleStore: () => ({
    surgeryTypes: mockSurgeryTypes,
    sdsRules: mockSdsRules,
    updateSDSTValue: vi.fn()
  })
}));

describe('BulkSDSTEditor', () => {
  let wrapper;
  let pinia;

  beforeEach(async () => {
    // Create a fresh Pinia instance for each test
    pinia = createPinia();
    setActivePinia(pinia);

    wrapper = mount(BulkSDSTEditor, {
      props: {
        show: true
      },
      global: {
        plugins: [pinia]
      }
    });
  });

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount();
    }
  });

  it('renders correctly when show prop is true', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.modal-overlay').exists()).toBe(true);
    expect(wrapper.find('.bulk-edit-modal').exists()).toBe(true);
  });

  it('does not render when show prop is false', () => {
    wrapper = mount(BulkSDSTEditor, {
      props: {
        show: false
      },
      global: {
        plugins: [pinia]
      }
    });

    expect(wrapper.find('.modal-overlay').exists()).toBe(false);
  });

  it('renders the modal title', () => {
    expect(wrapper.find('#bulk-edit-title').text()).toBe('Bulk Edit SDST Values');
  });

  it('renders tab buttons', () => {
    const tabButtons = wrapper.findAll('.tab-button');
    expect(tabButtons.length).toBe(2);
    expect(tabButtons[0].text()).toBe('Pattern-based Editing');
    expect(tabButtons[1].text()).toBe('CSV Import/Export');
  });

  it('switches tabs when tab buttons are clicked', async () => {
    // Initially on pattern tab
    expect(wrapper.find('.tab-button.active').text()).toBe('Pattern-based Editing');

    // Click CSV tab
    const csvTab = wrapper.findAll('.tab-button')[1];
    await csvTab.trigger('click');

    expect(wrapper.find('.tab-button.active').text()).toBe('CSV Import/Export');
  });

  it('renders pattern-based editing form by default', () => {
    expect(wrapper.find('[id="pattern-type"]').exists()).toBe(true);
    expect(wrapper.find('[id="fixed-value"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('Apply to:');
  });

  it('renders CSV import/export tab content', async () => {
    // Switch to CSV tab
    const csvTab = wrapper.findAll('.tab-button')[1];
    await csvTab.trigger('click');

    expect(wrapper.text()).toContain('Import or export SDST values as CSV');
    expect(wrapper.text()).toContain('Export as CSV');
    expect(wrapper.text()).toContain('Import from CSV');
    expect(wrapper.text()).toContain('CSV Format');
  });

  it('shows different input fields based on pattern type', async () => {
    const patternSelect = wrapper.find('#pattern-type');

    // Test fixed value (default)
    expect(wrapper.find('#fixed-value').exists()).toBe(true);
    expect(wrapper.find('#percentage-value').exists()).toBe(false);
    expect(wrapper.find('#increment-value').exists()).toBe(false);

    // Test percentage
    await patternSelect.setValue('percentage');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('#fixed-value').exists()).toBe(false);
    expect(wrapper.find('#percentage-value').exists()).toBe(true);
    expect(wrapper.find('#increment-value').exists()).toBe(false);

    // Test increment
    await patternSelect.setValue('increment');
    await wrapper.vm.$nextTick();

    expect(wrapper.find('#fixed-value').exists()).toBe(false);
    expect(wrapper.find('#percentage-value').exists()).toBe(false);
    expect(wrapper.find('#increment-value').exists()).toBe(true);
  });

  it('handles apply to all checkbox correctly', async () => {
    const applyToAllCheckbox = wrapper.find('input[type="checkbox"]');

    // Initially checked (apply to all)
    expect(applyToAllCheckbox.element.checked).toBe(true);

    // Individual category checkboxes should not be visible
    expect(wrapper.text()).not.toContain('Low values (≤ 15 min)');

    // Uncheck apply to all
    await applyToAllCheckbox.setChecked(false);
    await wrapper.vm.$nextTick();

    // Individual category checkboxes should now be visible
    expect(wrapper.text()).toContain('Low values (≤ 15 min)');
    expect(wrapper.text()).toContain('Medium values (16-30 min)');
    expect(wrapper.text()).toContain('High values (> 30 min)');
  });

  it('shows preview section when pattern tab is active and has selection', () => {
    // Should show preview by default (apply to all is checked)
    expect(wrapper.find('.preview-section').exists()).toBe(true);
    expect(wrapper.text()).toContain('Preview of Changes');
    expect(wrapper.text()).toContain('values will be affected');
  });

  it('emits close event when cancel button is clicked', async () => {
    const cancelButton = wrapper.findAll('button').find(btn => btn.text() === 'Cancel');
    await cancelButton.trigger('click');

    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('has apply button disabled when no selection is made', async () => {
    // Uncheck apply to all
    const applyToAllCheckbox = wrapper.find('input[type="checkbox"]');
    await applyToAllCheckbox.setChecked(false);
    await wrapper.vm.$nextTick();

    const applyButton = wrapper.findAll('button').find(btn => btn.text() === 'Apply Changes');
    expect(applyButton.attributes('disabled')).toBeDefined();
  });

  it('updates input values correctly', async () => {
    // Test fixed value input
    const fixedValueInput = wrapper.find('#fixed-value');
    await fixedValueInput.setValue('45');
    expect(fixedValueInput.element.value).toBe('45');

    // Switch to percentage and test
    const patternSelect = wrapper.find('#pattern-type');
    await patternSelect.setValue('percentage');
    await wrapper.vm.$nextTick();

    const percentageInput = wrapper.find('#percentage-value');
    await percentageInput.setValue('25');
    expect(percentageInput.element.value).toBe('25');

    // Switch to increment and test
    await patternSelect.setValue('increment');
    await wrapper.vm.$nextTick();

    const incrementInput = wrapper.find('#increment-value');
    await incrementInput.setValue('10');
    expect(incrementInput.element.value).toBe('10');
  });

  it('shows correct preview text for different pattern types', async () => {
    const patternSelect = wrapper.find('#pattern-type');
    const fixedValueInput = wrapper.find('#fixed-value');

    // Test fixed value preview
    await fixedValueInput.setValue('45');
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Set selected SDST values to 45 minutes');

    // Test percentage increase preview
    await patternSelect.setValue('percentage');
    await wrapper.vm.$nextTick();
    const percentageInput = wrapper.find('#percentage-value');
    await percentageInput.setValue('20');
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Increase selected SDST values by 20%');

    // Test percentage decrease preview
    const percentageDirectionSelect = wrapper.findAll('select').find(select =>
      select.element.innerHTML.includes('Increase by')
    );
    await percentageDirectionSelect.setValue('decrease');
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Decrease selected SDST values by 20%');

    // Test increment preview
    await patternSelect.setValue('increment');
    await wrapper.vm.$nextTick();
    const incrementInput = wrapper.find('#increment-value');
    await incrementInput.setValue('15');
    await wrapper.vm.$nextTick();
    expect(wrapper.text()).toContain('Increase selected SDST values by 15 minutes');
  });

  it('handles individual category checkboxes correctly', async () => {
    // Uncheck apply to all first
    const applyToAllCheckbox = wrapper.find('input[type="checkbox"]');
    await applyToAllCheckbox.setChecked(false);
    await wrapper.vm.$nextTick();

    // Find and check individual category checkboxes
    const checkboxes = wrapper.findAll('input[type="checkbox"]');
    const lowCheckbox = checkboxes.find(cb =>
      cb.element.parentElement.textContent.includes('Low values')
    );
    const mediumCheckbox = checkboxes.find(cb =>
      cb.element.parentElement.textContent.includes('Medium values')
    );

    expect(lowCheckbox.exists()).toBe(true);
    expect(mediumCheckbox.exists()).toBe(true);

    // Check low values checkbox
    await lowCheckbox.setChecked(true);
    await wrapper.vm.$nextTick();

    // Apply button should now be enabled
    const applyButton = wrapper.findAll('button').find(btn => btn.text() === 'Apply Changes');
    expect(applyButton.attributes('disabled')).toBeUndefined();
  });

  it('emits update and close events when apply changes is clicked', async () => {
    const applyButton = wrapper.findAll('button').find(btn => btn.text() === 'Apply Changes');
    await applyButton.trigger('click');

    expect(wrapper.emitted('update')).toBeTruthy();
    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('triggers file input when import button is clicked', async () => {
    // Switch to CSV tab
    const csvTab = wrapper.findAll('.tab-button')[1];
    await csvTab.trigger('click');

    // Mock the file input click method
    const fileInput = wrapper.find('input[type="file"]');
    const clickSpy = vi.spyOn(fileInput.element, 'click');

    const importButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Import from CSV')
    );
    await importButton.trigger('click');

    expect(clickSpy).toHaveBeenCalled();
  });

  it('handles CSV export functionality', async () => {
    // Switch to CSV tab
    const csvTab = wrapper.findAll('.tab-button')[1];
    await csvTab.trigger('click');

    // Mock URL.createObjectURL and document methods
    global.URL.createObjectURL = vi.fn(() => 'mock-url');
    const createElementSpy = vi.spyOn(document, 'createElement');
    const appendChildSpy = vi.spyOn(document.body, 'appendChild');
    const removeChildSpy = vi.spyOn(document.body, 'removeChild');

    const exportButton = wrapper.findAll('button').find(btn =>
      btn.text().includes('Export as CSV')
    );
    await exportButton.trigger('click');

    expect(createElementSpy).toHaveBeenCalledWith('a');
    expect(appendChildSpy).toHaveBeenCalled();
    expect(removeChildSpy).toHaveBeenCalled();
  });

  it('validates CSV format information is displayed', async () => {
    // Switch to CSV tab
    const csvTab = wrapper.findAll('.tab-button')[1];
    await csvTab.trigger('click');

    expect(wrapper.text()).toContain('CSV Format');
    expect(wrapper.text()).toContain('FromType,ToType,Minutes');
    expect(wrapper.text()).toContain('CABG,KNEE,30');
    expect(wrapper.text()).toContain('The first row is a header row');
  });
});