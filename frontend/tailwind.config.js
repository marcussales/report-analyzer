/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'class',
	theme: {
		extend: {
			colors: {
				// Dark theme colors
				dark: {
					50: '#2a2a2a',
					100: '#252525',
					200: '#1f1f1f',
					300: '#1b1b1b',
					400: '#171717',
					500: '#141414',
					600: '#111111',
					700: '#0d0d0d',
					800: '#0a0a0a',
					900: '#050505'
				},
				// Warm gray text colors
				warm: {
					50: '#f5f4f2',
					100: '#e8e6e3',
					200: '#dcdad5',
					300: '#c5c1b9',
					400: '#a9a49a',
					500: '#8d877c',
					600: '#716b61',
					700: '#555049',
					800: '#3a3632',
					900: '#1f1c1a'
				},
				// Accent purple-blue
				accent: {
					50: '#eef0ff',
					100: '#dde1ff',
					200: '#c3c9ff',
					300: '#9ea7ff',
					400: '#7880ff',
					500: '#575ECF',
					600: '#4a4fb8',
					700: '#3d419a',
					800: '#33367d',
					900: '#2b2e66'
				},
				// Status colors (adjusted for dark theme)
				success: {
					50: '#0d2818',
					100: '#134e26',
					200: '#1a7338',
					300: '#22994a',
					400: '#2abf5c',
					500: '#34d66e',
					600: '#5ade8a',
					700: '#80e6a6',
					800: '#a6eec2',
					900: '#ccf6de'
				},
				error: {
					50: '#2d1215',
					100: '#5a1f24',
					200: '#872d34',
					300: '#b43a44',
					400: '#d94a56',
					500: '#e66a74',
					600: '#ed8a92',
					700: '#f3aab0',
					800: '#f9cace',
					900: '#fceaec'
				},
				warning: {
					50: '#2d2412',
					100: '#5a471f',
					200: '#876a2d',
					300: '#b48e3a',
					400: '#d9ac4a',
					500: '#e6c06a',
					600: '#edd08a',
					700: '#f3e0aa',
					800: '#f9efca',
					900: '#fcf8ea'
				}
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif']
			},
			borderRadius: {
				'sm': '4px',
				'md': '6px',
				'lg': '8px',
				'xl': '12px',
				'2xl': '16px'
			},
			boxShadow: {
				'dark-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
				'dark-md': '0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)',
				'dark-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4)',
				'dark-xl': '0 16px 16px -8px rgba(0, 0, 0, 0.5)',
				'glow': '0 0 20px rgba(87, 94, 207, 0.3)',
				'glow-sm': '0 0 10px rgba(87, 94, 207, 0.2)'
			},
			animation: {
				'fade-in': 'fadeIn 0.2s ease-out',
				'slide-up': 'slideUp 0.3s ease-out',
				'pulse-slow': 'pulse 3s infinite'
			},
			keyframes: {
				fadeIn: {
					'0%': { opacity: '0' },
					'100%': { opacity: '1' }
				},
				slideUp: {
					'0%': { opacity: '0', transform: 'translateY(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' }
				}
			}
		}
	},
	plugins: [require('@tailwindcss/forms')]
};
