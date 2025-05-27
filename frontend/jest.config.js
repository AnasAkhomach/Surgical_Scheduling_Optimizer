module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\.(vue|js|jsx|ts|tsx|mjs|cjs)$': 'vite-jest',
  },
  moduleFileExtensions: ['vue', 'js', 'json', 'jsx', 'ts', 'tsx', 'node', 'mjs', 'cjs'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(@vitejs/plugin-vue))', // Allow vite-jest to process vite specific modules if needed
  ],
  collectCoverage: true,
  collectCoverageFrom: [
    'src/components/**/*.vue',
    'src/views/**/*.vue', // If you have a views folder
    // Add other paths if needed
  ],
  coverageReporters: ['html', 'text-summary'],
  // vite-jest specific options (if any, consult vite-jest documentation)
  // globals: {
  //   'vite-jest': {
  //     // vite config options
  //   }
  // }
};