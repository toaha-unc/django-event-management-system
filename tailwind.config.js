module.exports = {
  content: [
    './templates/**/*.html',
    './events/templates/**/*.html',
    './static/js/**/*.js',
  ],
  safelist: [
    'focus:ring-2',
    'focus:ring-blue-300',
    'border',
    'border-gray-300',
    'rounded-sm',
    'w-full',
    'px-3',
    'py-2',
    'focus:outline-none',
    'focus:border-blue-500',
    'transform',
    'hover:scale-110',
    'transition-all',
    'duration-200',
    'hover:text-blue-700',
    'animate-slide-down',
    'backdrop-blur-md',
    'bg-white/95',
    'bg-white/98',
  ],
  theme: {
    extend: {
      animation: {
        'slide-down': 'slideDown 0.3s ease-out',
        'gradient-shift': 'gradientShift 3s ease infinite',
      },
      keyframes: {
        slideDown: {
          '0%': {
            opacity: '0',
            transform: 'translateY(-10px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        gradientShift: {
          '0%, 100%': {
            'background-position': '0% 50%',
          },
          '50%': {
            'background-position': '100% 50%',
          },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
