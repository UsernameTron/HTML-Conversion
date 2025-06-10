# HTML Text Formatter Pro

A professional-grade web application that transforms text content into stunning, Google-inspired HTML documents. Built with Streamlit for optimal user experience and modern design aesthetics.

## ✨ Enhanced Features

- **Google Material Design**: Complete Material Design color palette with 14 color families
- **Premium Typography**: Google Fonts integration with 10 premium font combinations
- **Advanced Styling**: Shadows, gradients, modern typography scales, and responsive design
- **Professional Themes**: 12 pre-designed color schemes inspired by Google's design language
- **Smart Color Controls**: Material Design color picker with custom fallbacks
- **Modern HTML Generation**: Professional CSS with animations, responsive design, and print styles
- **File Support**: Text files, images, PDF, Word documents with enhanced placeholders
- **Live Preview**: Real-time preview with Google-inspired styling
- **Theme Export**: Save and share custom theme configurations
- **Responsive Design**: Optimized for all devices and screen sizes

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up the Python path:
```bash
source setup_env.sh
```

3. Run the application:
```bash
streamlit run app.py
```

### Running Tests

To run the test suite:

```bash
source setup_env.sh  # Set up proper Python path
python -m pytest tests/
```

To run the comprehensive tester:

```bash
source setup_env.sh  # Set up proper Python path
python comprehensive_tester.py
```

3. Open your browser to `http://localhost:8501`

### Deploy to Streamlit Cloud (Recommended)

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set the main file path to `app.py`
6. Click "Deploy"

Your app will be live at: `https://[your-app-name].streamlit.app`

### Alternative: Deploy to Heroku

1. Create a `Procfile`:
```
web: sh setup.sh && streamlit run app.py --server.port $PORT --server.headless true
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

3. Deploy to Heroku using Git

## Supported File Types

- **Text Files**: .txt, .md, .csv, .json, .html, .css, .js
- **Images**: .png, .jpg, .jpeg, .gif, .bmp (embedded as base64)
- **Documents**: .pdf, .docx, .doc (placeholder generation)

## Usage

1. **Input Text**: Type or paste your content in the text area
2. **Upload Files**: Use the file uploader for various formats
3. **Customize Styling**: Use the sidebar controls to adjust appearance
4. **Preview**: See live preview of your formatted content
5. **Download**: Export the complete HTML document

## 🎨 Advanced Styling Options

### Material Design Colors
- **14 Color Families**: Red, Pink, Purple, Deep Purple, Indigo, Blue, Light Blue, Cyan, Teal, Green, Light Green, Lime, Yellow, Amber, Orange, Deep Orange, Brown, Grey, Blue Grey
- **9 Shades Each**: From 50 (lightest) to 900 (darkest) for precise color control
- **Custom Picker**: Fallback color picker for unlimited color choices

### Premium Typography
- **Google Fonts**: Roboto, Open Sans, Lato, Montserrat, Poppins, Inter
- **System Fonts**: Apple System, Modern Sans, Classic Serif, Code Mono
- **Typography Scale**: Modern heading hierarchy with proper spacing
- **Font Weight Control**: 300 (Light) to 700 (Bold)
- **Letter Spacing**: Fine-tune character spacing

### Professional Themes
- **Google Official**: Blue, Red, Green, Yellow themes
- **Material Design**: Purple, Indigo, Teal, Orange schemes
- **Modern Palettes**: Elegant Dark, Sunset, Ocean, Forest

### Advanced Layout
- **Responsive Design**: Mobile-first approach with breakpoints
- **Shadow System**: Professional depth with multiple shadow levels
- **Gradient Backgrounds**: Subtle gradients for modern appeal
- **Border Radius**: Customizable corner rounding
- **Max Width Control**: Optimal reading width settings

### Enhanced HTML Output
- **Modern CSS**: CSS Grid, Flexbox, Custom Properties
- **Animations**: Subtle entrance animations and hover effects
- **Print Styles**: Optimized for professional printing
- **Accessibility**: WCAG-compliant contrast and typography
- **Cross-browser**: Works on all modern browsers

## Technical Details

- Built with Streamlit for optimal user experience
- Responsive design for all devices
- No JavaScript knowledge required
- Pure Python implementation
- Secure file handling

## Contributing

Feel free to submit issues and enhancement requests!