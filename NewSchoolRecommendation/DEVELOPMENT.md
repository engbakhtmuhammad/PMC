# Development Workflow - School Feasibility Analysis System

## Quick Start for Developers

### 1. Environment Setup
```bash
# Navigate to project directory
cd /Users/macbookpro/Desktop/PMC/NewSchoolRecommendation

# Install dependencies
pip3 install -r requirements.txt

# Start development server
python3 app.py
```

### 2. VS Code Tasks
Use the configured VS Code tasks for common development activities:

- **Ctrl+Shift+P** → "Tasks: Run Task"
- Available tasks:
  - **Start Flask Server**: Runs the development server
  - **Install Dependencies**: Installs Python packages
  - **Run Tests**: Execute test suite (when implemented)

## Project Structure

```
NewSchoolRecommendation/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── TESTING_GUIDE.md      # Testing instructions
├── DEVELOPMENT.md        # This file
├── sample_schools_data.csv # Sample data for testing
├── .vscode/              # VS Code configuration
│   └── tasks.json        # Development tasks
├── static/               # Static assets (CSS, JS, images)
│   └── styles.css        # Custom CSS styles
├── templates/            # HTML templates
│   ├── index.html        # File upload page
│   ├── coordinate_input.html # Coordinate input form
│   └── results.html      # Analysis results display
├── uploads/              # Uploaded CSV files
└── reports/              # Generated reports and maps
```

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add comprehensive comments for complex logic
- Implement proper error handling
- Use type hints where appropriate

### HTML/CSS Guidelines
- Use semantic HTML5 elements
- Follow Bootstrap 5 conventions
- Maintain government-style professional appearance
- Ensure responsive design for mobile devices
- Use consistent color scheme and typography

### JavaScript Guidelines
- Use modern ES6+ syntax
- Implement proper error handling
- Add meaningful comments
- Ensure cross-browser compatibility

## Key Development Areas

### 1. Backend (Flask)
**File**: `app.py`

Key functions to understand:
- `upload_file()`: Handles CSV file uploads and validation
- `coordinate_input()`: Processes coordinate form submissions
- `analyze_coordinates()`: Core feasibility analysis logic
- `generate_map()`: Creates interactive Folium maps

### 2. Frontend Templates

#### index.html
- File upload interface
- File validation
- Progress indicators
- Error handling

#### coordinate_input.html
- Dynamic coordinate input forms
- Client-side validation
- Interactive UI elements
- Form submission handling

#### results.html
- Results display
- Interactive maps
- Download functionality
- Data tables

### 3. Styling (CSS)
**File**: `static/styles.css`

Key areas:
- Government color scheme
- Responsive design
- Professional typography
- Interactive elements
- Map styling

## Adding New Features

### 1. New Analysis Methods
To add new feasibility analysis algorithms:

```python
def new_analysis_method(existing_schools, proposed_coords):
    """
    Add your analysis logic here
    
    Args:
        existing_schools: DataFrame with school data
        proposed_coords: List of coordinate dictionaries
    
    Returns:
        List of analysis results
    """
    pass
```

### 2. New Templates
When adding new pages:

1. Create HTML template in `templates/`
2. Add route in `app.py`
3. Update navigation links
4. Add styling in `static/styles.css`

### 3. New Data Sources
To support additional data formats:

1. Add file validation in `upload_file()`
2. Create data processing functions
3. Update sample data files
4. Update documentation

## Testing During Development

### Quick Tests
```bash
# Test Flask app imports
python3 -c "import app; print('App imports successfully')"

# Test with sample data
curl -X POST http://127.0.0.1:5011/upload \
  -F "file=@sample_schools_data.csv"
```

### Manual Testing Checklist
- [ ] File upload works with sample data
- [ ] Coordinate input validates properly
- [ ] Maps display correctly
- [ ] Downloads function properly
- [ ] Error handling works
- [ ] Mobile responsiveness
- [ ] Cross-browser compatibility

## Debugging

### Common Issues
1. **Import Errors**: Check virtual environment and dependencies
2. **Template Not Found**: Verify template paths and names
3. **Static Files Not Loading**: Check Flask static configuration
4. **Map Not Displaying**: Verify internet connection and Folium integration

### Debug Mode
The application runs with debug mode enabled by default during development:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5011)
```

### Logging
Add logging for debugging:
```python
import logging
app.logger.info('Debug message here')
```

## Performance Optimization

### Frontend
- Minimize CSS and JavaScript
- Optimize images
- Use CDN for external libraries
- Implement lazy loading for maps

### Backend
- Cache frequently accessed data
- Optimize distance calculations
- Use efficient pandas operations
- Implement pagination for large datasets

## Security Considerations

### File Upload Security
- Validate file types and sizes
- Sanitize file names
- Check file content
- Limit upload directory permissions

### Input Validation
- Validate coordinate ranges
- Sanitize user inputs
- Implement CSRF protection
- Use secure file paths

## Deployment Preparation

### Production Settings
- Disable debug mode
- Use environment variables for sensitive data
- Configure proper logging
- Set up error monitoring

### Required Environment Variables
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export MAX_UPLOAD_SIZE=16777216  # 16MB
```

## Git Workflow (when using version control)

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `hotfix/*`: Critical fixes

### Commit Messages
Use clear, descriptive commit messages:
```
feat: Add coordinate validation
fix: Resolve map rendering issue
docs: Update README with new features
style: Improve CSS formatting
```

## Contributing

### Before Submitting Changes
1. Test all functionality thoroughly
2. Update documentation if needed
3. Follow code style guidelines
4. Add appropriate comments
5. Verify no breaking changes

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed

---

For questions or support, refer to the README.md or TESTING_GUIDE.md files.
