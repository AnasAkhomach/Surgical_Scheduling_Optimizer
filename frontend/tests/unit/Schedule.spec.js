import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import Schedule from '@/views/Schedule.vue'

// Mock PrimeVue components
jest.mock('primevue/card', () => ({
  name: 'Card',
  render: h => h('div', { class: 'p-card' }, [
    h('div', { class: 'p-card-title' }, h('slot', { name: 'title' })),
    h('div', { class: 'p-card-content' }, h('slot', { name: 'content' }))
  ])
}))

jest.mock('primevue/button', () => ({
  name: 'Button',
  render: h => h('button', { class: 'p-button' })
}))

jest.mock('primevue/calendar', () => ({
  name: 'Calendar',
  render: h => h('input', { class: 'p-calendar' })
}))

jest.mock('primevue/inputtext', () => ({
  name: 'InputText',
  render: h => h('input', { class: 'p-inputtext' })
}))

jest.mock('primevue/datatable', () => ({
  name: 'DataTable',
  render: h => h('table', { class: 'p-datatable' }, h('slot'))
}))

jest.mock('primevue/column', () => ({
  name: 'Column',
  render: h => h('col')
}))

jest.mock('primevue/progressspinner', () => ({
  name: 'ProgressSpinner',
  render: h => h('div', { class: 'p-progress-spinner' })
}))

// Mock useToast
jest.mock('primevue/usetoast', () => ({
  useToast: () => ({
    add: jest.fn()
  })
}))

describe('Schedule.vue', () => {
  let store
  let wrapper

  beforeEach(() => {
    // Create a fresh store before each test
    store = createStore({
      state: {
        loading: false
      },
      getters: {
        isLoading: state => state.loading
      },
      modules: {
        auth: {
          namespaced: true,
          state: {
            user: { id: 1, username: 'testuser', role: 'admin' }
          },
          getters: {
            currentUser: state => state.user
          }
        }
      }
    })

    // Mount the component
    wrapper = mount(Schedule, {
      global: {
        plugins: [store],
        stubs: ['Card', 'Button', 'Calendar', 'InputText', 'DataTable', 'Column', 'ProgressSpinner']
      }
    })
  })

  it('renders the schedule view', () => {
    // Check that the component renders
    expect(wrapper.exists()).toBe(true)

    // Check that the title is present
    expect(wrapper.find('h1').text()).toBe('Surgery Schedule')
  })

  it('displays the optimization parameters form', () => {
    // Check that the optimization parameters form is present
    const parametersCard = wrapper.findAll('.p-card').find(card => 
      card.find('.p-card-title').text().includes('Optimization Parameters')
    )
    expect(parametersCard).toBeTruthy()

    // Check that the form fields are present
    expect(wrapper.find('#date').exists()).toBe(true)
    expect(wrapper.find('#maxIterations').exists()).toBe(true)
    expect(wrapper.find('#tabuTenure').exists()).toBe(true)
    expect(wrapper.find('#timeLimit').exists()).toBe(true)
  })

  it('displays the schedule table', () => {
    // Check that the schedule table is present
    const table = wrapper.find('.p-datatable')
    expect(table.exists()).toBe(true)
  })

  it('initializes with default optimization parameters', () => {
    // Check that the optimization parameters are initialized
    expect(wrapper.vm.optimizationParams.max_iterations).toBe(100)
    expect(wrapper.vm.optimizationParams.tabu_tenure).toBe(10)
    expect(wrapper.vm.optimizationParams.max_no_improvement).toBe(20)
    expect(wrapper.vm.optimizationParams.time_limit_seconds).toBe(300)
    expect(wrapper.vm.optimizationParams.weights).toBeTruthy()
  })

  it('displays current schedule when no optimized schedule exists', () => {
    // Check that the current schedule is displayed
    expect(wrapper.vm.scheduleData).toEqual(wrapper.vm.currentSchedule)
  })

  it('has optimize and apply schedule buttons', () => {
    // Check that the buttons are present
    const optimizeButton = wrapper.findAll('button').find(button => 
      button.text().includes('Optimize Schedule')
    )
    expect(optimizeButton).toBeTruthy()

    const applyButton = wrapper.findAll('button').find(button => 
      button.text().includes('Apply Schedule')
    )
    expect(applyButton).toBeTruthy()
  })

  it('disables apply button when no optimized schedule exists', () => {
    // Check that the apply button is disabled
    const applyButton = wrapper.findAll('button').find(button => 
      button.text().includes('Apply Schedule')
    )
    expect(applyButton.attributes('disabled')).toBeTruthy()
  })

  it('shows loading spinner when loading', async () => {
    // Set loading to true
    await wrapper.setData({ loading: true })

    // Check that the loading spinner is displayed
    expect(wrapper.find('.p-progress-spinner').exists()).toBe(true)
  })

  it('calls optimizeSchedule method when optimize button is clicked', async () => {
    // Mock the optimizeSchedule method
    const optimizeScheduleSpy = jest.spyOn(wrapper.vm, 'optimizeSchedule')
    
    // Find and click the optimize button
    const optimizeButton = wrapper.findAll('button').find(button => 
      button.text().includes('Optimize Schedule')
    )
    await optimizeButton.trigger('click')

    // Check that the optimizeSchedule method was called
    expect(optimizeScheduleSpy).toHaveBeenCalled()
  })

  it('calls applySchedule method when apply button is clicked', async () => {
    // Mock the applySchedule method
    const applyScheduleSpy = jest.spyOn(wrapper.vm, 'applySchedule')
    
    // Set an optimized schedule
    await wrapper.setData({ 
      optimizedSchedule: [
        { time: '08:00 - 09:30', surgery_id: 101, surgery_type: 'Appendectomy', duration: '1h 30m', surgeon: 'Dr. Smith', room: 'OR-2' }
      ]
    })
    
    // Find and click the apply button
    const applyButton = wrapper.findAll('button').find(button => 
      button.text().includes('Apply Schedule')
    )
    await applyButton.trigger('click')

    // Check that the applySchedule method was called
    expect(applyScheduleSpy).toHaveBeenCalled()
  })

  it('displays optimization results when available', async () => {
    // Set optimization results
    await wrapper.setData({ 
      optimizationResult: {
        score: 87.5,
        iteration_count: 78,
        execution_time_seconds: 2.34,
        assignments: [
          { time: '08:00 - 09:30', surgery_id: 101, surgery_type: 'Appendectomy', duration: '1h 30m', surgeon: 'Dr. Smith', room: 'OR-2' }
        ]
      }
    })

    // Check that the optimization results are displayed
    const resultsSection = wrapper.find('h3.text-xl.font-bold.mb-2')
    expect(resultsSection.exists()).toBe(true)
    expect(resultsSection.text()).toBe('Optimization Results')
  })
})
