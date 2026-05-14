export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        leaf: '#10b981',
        'leaf-dark': '#059669',
        tomato: '#ef4444',
        grain: '#f59e0b',
        ink: '#0f172a',
        surface: '#ffffff',
        'surface-subtle': '#f8fafc',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      }
    }
  },
  plugins: []
};
