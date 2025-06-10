"""Application constants and configuration."""

# Google Material Design Color Palette
MATERIAL_COLORS = {
    'Red': {
        '50': '#ffebee', '100': '#ffcdd2', '200': '#ef9a9a', '300': '#e57373',
        '400': '#ef5350', '500': '#f44336', '600': '#e53935', '700': '#d32f2f',
        '800': '#c62828', '900': '#b71c1c'
    },
    'Pink': {
        '50': '#fce4ec', '100': '#f8bbd9', '200': '#f48fb1', '300': '#f06292',
        '400': '#ec407a', '500': '#e91e63', '600': '#d81b60', '700': '#c2185b',
        '800': '#ad1457', '900': '#880e4f'
    },
    'Purple': {
        '50': '#f3e5f5', '100': '#e1bee7', '200': '#ce93d8', '300': '#ba68c8',
        '400': '#ab47bc', '500': '#9c27b0', '600': '#8e24aa', '700': '#7b1fa2',
        '800': '#6a1b9a', '900': '#4a148c'
    },
    'Deep Purple': {
        '50': '#ede7f6', '100': '#d1c4e9', '200': '#b39ddb', '300': '#9575cd',
        '400': '#7e57c2', '500': '#673ab7', '600': '#5e35b1', '700': '#512da8',
        '800': '#4527a0', '900': '#311b92'
    },
    'Indigo': {
        '50': '#e8eaf6', '100': '#c5cae9', '200': '#9fa8da', '300': '#7986cb',
        '400': '#5c6bc0', '500': '#3f51b5', '600': '#3949ab', '700': '#303f9f',
        '800': '#283593', '900': '#1a237e'
    },
    'Blue': {
        '50': '#e3f2fd', '100': '#bbdefb', '200': '#90caf9', '300': '#64b5f6',
        '400': '#42a5f5', '500': '#2196f3', '600': '#1e88e5', '700': '#1976d2',
        '800': '#1565c0', '900': '#0d47a1'
    },
    'Light Blue': {
        '50': '#e1f5fe', '100': '#b3e5fc', '200': '#81d4fa', '300': '#4fc3f7',
        '400': '#29b6f6', '500': '#03a9f4', '600': '#039be5', '700': '#0288d1',
        '800': '#0277bd', '900': '#01579b'
    },
    'Cyan': {
        '50': '#e0f2f1', '100': '#b2dfdb', '200': '#80cbc4', '300': '#4db6ac',
        '400': '#26a69a', '500': '#009688', '600': '#00897b', '700': '#00796b',
        '800': '#00695c', '900': '#004d40'
    },
    'Teal': {
        '50': '#e0f2f1', '100': '#b2dfdb', '200': '#80cbc4', '300': '#4db6ac',
        '400': '#26a69a', '500': '#009688', '600': '#00897b', '700': '#00796b',
        '800': '#00695c', '900': '#004d40'
    },
    'Green': {
        '50': '#e8f5e8', '100': '#c8e6c9', '200': '#a5d6a7', '300': '#81c784',
        '400': '#66bb6a', '500': '#4caf50', '600': '#43a047', '700': '#388e3c',
        '800': '#2e7d32', '900': '#1b5e20'
    },
    'Light Green': {
        '50': '#f1f8e9', '100': '#dcedc8', '200': '#c5e1a5', '300': '#aed581',
        '400': '#9ccc65', '500': '#8bc34a', '600': '#7cb342', '700': '#689f38',
        '800': '#558b2f', '900': '#33691e'
    },
    'Lime': {
        '50': '#f9fbe7', '100': '#f0f4c3', '200': '#e6ee9c', '300': '#dce775',
        '400': '#d4e157', '500': '#cddc39', '600': '#c0ca33', '700': '#afb42b',
        '800': '#9e9d24', '900': '#827717'
    },
    'Yellow': {
        '50': '#fffde7', '100': '#fff9c4', '200': '#fff59d', '300': '#fff176',
        '400': '#ffee58', '500': '#ffeb3b', '600': '#fdd835', '700': '#fbc02d',
        '800': '#f9a825', '900': '#f57f17'
    },
    'Amber': {
        '50': '#fff8e1', '100': '#ffecb3', '200': '#ffe082', '300': '#ffd54f',
        '400': '#ffca28', '500': '#ffc107', '600': '#ffb300', '700': '#ffa000',
        '800': '#ff8f00', '900': '#ff6f00'
    },
    'Orange': {
        '50': '#fff3e0', '100': '#ffe0b2', '200': '#ffcc80', '300': '#ffb74d',
        '400': '#ffa726', '500': '#ff9800', '600': '#fb8c00', '700': '#f57c00',
        '800': '#ef6c00', '900': '#e65100'
    },
    'Deep Orange': {
        '50': '#fbe9e7', '100': '#ffccbc', '200': '#ffab91', '300': '#ff8a65',
        '400': '#ff7043', '500': '#ff5722', '600': '#f4511e', '700': '#e64a19',
        '800': '#d84315', '900': '#bf360c'
    },
    'Brown': {
        '50': '#efebe9', '100': '#d7ccc8', '200': '#bcaaa4', '300': '#a1887f',
        '400': '#8d6e63', '500': '#795548', '600': '#6d4c41', '700': '#5d4037',
        '800': '#4e342e', '900': '#3e2723'
    },
    'Grey': {
        '50': '#fafafa', '100': '#f5f5f5', '200': '#eeeeee', '300': '#e0e0e0',
        '400': '#bdbdbd', '500': '#9e9e9e', '600': '#757575', '700': '#616161',
        '800': '#424242', '900': '#212121'
    },
    'Blue Grey': {
        '50': '#eceff1', '100': '#cfd8dc', '200': '#b0bec5', '300': '#90a4ae',
        '400': '#78909c', '500': '#607d8b', '600': '#546e7a', '700': '#455a64',
        '800': '#37474f', '900': '#263238'
    }
}

# Modern Color Schemes inspired by Google
COLOR_SCHEMES = {
    'Google Blue': {'primary': '#4285f4', 'secondary': '#1a73e8', 'accent': '#34a853'},
    'Google Red': {'primary': '#ea4335', 'secondary': '#d33b2c', 'accent': '#fbbc05'},
    'Google Green': {'primary': '#34a853', 'secondary': '#137333', 'accent': '#4285f4'},
    'Google Yellow': {'primary': '#fbbc05', 'secondary': '#f9ab00', 'accent': '#ea4335'},
    'Material Purple': {'primary': '#9c27b0', 'secondary': '#7b1fa2', 'accent': '#e91e63'},
    'Material Indigo': {'primary': '#3f51b5', 'secondary': '#303f9f', 'accent': '#2196f3'},
    'Material Teal': {'primary': '#009688', 'secondary': '#00796b', 'accent': '#4caf50'},
    'Material Orange': {'primary': '#ff9800', 'secondary': '#f57c00', 'accent': '#ff5722'},
    'Elegant Dark': {'primary': '#2c3e50', 'secondary': '#34495e', 'accent': '#3498db'},
    'Sunset': {'primary': '#ff6b6b', 'secondary': '#feca57', 'accent': '#48dbfb'},
    'Ocean': {'primary': '#0abde3', 'secondary': '#006ba6', 'accent': '#74b9ff'},
    'Forest': {'primary': '#00b894', 'secondary': '#00a085', 'accent': '#55a3ff'}
}

# Premium font combinations
FONT_COMBINATIONS = {
    'Google Fonts - Roboto': 'Roboto, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Open Sans': 'Open Sans, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Lato': 'Lato, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Montserrat': 'Montserrat, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Poppins': 'Poppins, -apple-system, BlinkMacSystemFont, sans-serif',
    'Google Fonts - Inter': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
    'Apple System': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'Modern Sans': '"Helvetica Neue", Helvetica, Arial, sans-serif',
    'Classic Serif': 'Georgia, "Times New Roman", Times, serif',
    'Code Mono': '"SF Mono", "Monaco", "Consolas", "Courier New", monospace'
}

# Supported file types
SUPPORTED_FILE_TYPES = {
    'text': ['txt', 'md', 'csv', 'json', 'html', 'css', 'js'],
    'images': ['png', 'jpg', 'jpeg', 'gif', 'bmp'],
    'documents': ['pdf', 'docx', 'doc']
}

# Security limits
SECURITY_LIMITS = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'max_text_length': 1 * 1024 * 1024,  # 1MB
    'max_filename_length': 255
}