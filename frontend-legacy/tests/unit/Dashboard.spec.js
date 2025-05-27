import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'
import Dashboard from '@/views/Dashboard.vue'

// Mock PrimeVue components
jest.mock('primevue/card', () => ({
  name: 'Card',
  render: h => h('div', { class: 'p-card' }, [
    h('div', { class: 'p-card-title' }, h('slot', { name: 'title' })),
    h('div', { class: 'p-card-content' }, h('slot', { name: 'content' }))
  ])
}))

jest.mock('primevue/chart', () => ({
  name: 'Chart',
  render: h => h('canvas', { class: 'p-chart' })
}))

jest.mock('primevue/datatable', () => ({
  name: 'DataTable',
  render: h => h('table', { class: 'p-datatable' }, h('slot'))
}))

jest.mock('primevue/column', () => ({
  name: 'Column',
  render: h => h('col')
}))

describe('Dashboard.vue', () => {
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
    wrapper = mount(Dashboard, {
      global: {
        plugins: [store],
        stubs: ['Card', 'Chart', 'DataTable', 'Column']
      }
    })
  })

  it('renders the dashboard', () => {
    // Check that the component renders
    expect(wrapper.exists()).toBe(true)

    // Check that the title is present
    expect(wrapper.find('h1').text()).toBe('Dashboard')
  })

  it('displays the statistics cards', () => {
    // Check that the statistics cards are present
    const cards = wrapper.findAll('.p-card')
    expect(cards.length).toBeGreaterThan(0)

    // Check that the today's surgeries card is present
    const todaySurgeriesCard = wrapper.findAll('.p-card').find(card => 
      card.find('.p-card-title').text().includes('Today\'s Surgeries')
    )
    expect(todaySurgeriesCard).toBeTruthy()

    // Check that the operating rooms card is present
    const operatingRoomsCard = wrapper.findAll('.p-card').find(card => 
      card.find('.p-card-title').text().includes('Operating Rooms')
    )
    expect(operatingRoomsCard).toBeTruthy()

    // Check that the surgeons card is present
    const surgeonsCard = wrapper.findAll('.p-card').find(card => 
      card.find('.p-card-title').text().includes('Surgeons')
    )
    expect(surgeonsCard).toBeTruthy()

    // Check that the upcoming appointments card is present
    const upcomingAppointmentsCard = wrapper.findAll('.p-card').find(card => 
      card.find('.p-card-title').text().includes('Upcoming Appointments')
    )
    expect(upcomingAppointmentsCard).toBeTruthy()
  })

  it('displays the charts', () => {
    // Check that the charts are present
    const charts = wrapper.findAll('.p-chart')
    expect(charts.length).toBe(2)
  })

  it('displays the today\'s schedule table', () => {
    // Check that the table is present
    const table = wrapper.find('.p-datatable')
    expect(table.exists()).toBe(true)
  })

  it('initializes with mock data', () => {
    // Check that the component data is initialized
    expect(wrapper.vm.todaySurgeries).toBe(8)
    expect(wrapper.vm.operatingRoomsCount).toBe(5)
    expect(wrapper.vm.surgeonsCount).toBe(12)
    expect(wrapper.vm.upcomingAppointments).toBe(23)
    expect(wrapper.vm.todaySchedule.length).toBe(5)
  })

  it('formats status with the correct class', () => {
    // Check the getStatusClass method
    expect(wrapper.vm.getStatusClass('Completed')).toBe('p-tag p-tag-success')
    expect(wrapper.vm.getStatusClass('In Progress')).toBe('p-tag p-tag-warning')
    expect(wrapper.vm.getStatusClass('Scheduled')).toBe('p-tag p-tag-info')
    expect(wrapper.vm.getStatusClass('Cancelled')).toBe('p-tag p-tag-danger')
    expect(wrapper.vm.getStatusClass('Unknown')).toBe('p-tag')
  })

  it('sets loading to false after component is mounted', async () => {
    // Wait for the component to be mounted
    await wrapper.vm.$nextTick()

    // Check that loading is set to false
    expect(wrapper.vm.loading).toBe(false)
  })
})
