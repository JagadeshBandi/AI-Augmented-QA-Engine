# API Documentation

## Core AI Components

### VisualHealer Class

**Purpose**: Computer vision-based element recovery using OpenCV template matching.

#### Methods

##### `__init__(threshold=0.8)`
Initialize the visual healer with confidence threshold.

**Parameters:**
- `threshold` (float): Confidence threshold for template matching (0.0-1.0)

**Returns:** VisualHealer instance

##### `find_element_visually(scene_path, template_path)`
Locate UI elements using template matching.

**Parameters:**
- `scene_path` (str): Path to current page screenshot
- `template_path` (str): Path to element template image

**Returns:**
- `tuple[int, int] | None`: Center coordinates (x, y) or None if not found

**Example:**
```python
healer = VisualHealer(threshold=0.8)
coords = healer.find_element_visually("screenshot.png", "button_template.png")
if coords:
    page.mouse.click(coords[0], coords[1])
```

### BasePage Class

**Purpose**: AI-augmented page object with self-healing capabilities.

#### Methods

##### `__init__(page)`
Initialize AI-enhanced page object.

**Parameters:**
- `page` (playwright.Page): Playwright page instance

##### `smart_click(selector, template_name)`
Attempt click with AI fallback.

**Parameters:**
- `selector` (str): CSS/XPath selector to try first
- `template_name` (str): Template filename for visual recovery

**Behavior:**
1. Try standard Playwright click (2s timeout)
2. On failure, trigger AI visual recovery
3. If found, click using coordinates
4. Raise exception if recovery fails

**Example:**
```python
base = BasePage(page)
base.smart_click("#login-button", "login_button")
```

---

## Configuration

### Settings YAML Structure

```yaml
[project]
name = "ARES: AI-Augmented QA Engine"
version = "1.0.0"

[ai_config]
opencv_threshold = 0.8
template_match_method = "TM_CCOEFF_NORMED"
visual_recovery_timeout = 30

[automation]
browser_timeout = 10000
retry_attempts = 3
headless_mode = false
```

### Environment Variables

- `ARES_AI_THRESHOLD`: Override OpenCV confidence threshold
- `ARES_HEADLESS`: Force headless browser mode
- `ARES_LOG_LEVEL`: Logging verbosity (DEBUG/INFO/WARN/ERROR)

---

## Integration Examples

### Pytest Integration

```python
import pytest
from src.pages.base_page import BasePage

@pytest.fixture
def ai_page(page):
    return BasePage(page)

def test_login_with_ai_healing(ai_page):
    # AI will recover if selector fails
    ai_page.smart_click("#dynamic-login-id", "login_button")
```

### Continuous Integration

```yaml
# .github/workflows/ai-tests.yml
name: AI-Augmented Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      - name: Run AI Tests
        run: pytest tests/ --cov=src --cov-report=xml
```

---

## Error Handling

### AI Healing Exceptions

```python
class AIHealingError(Exception):
    """Base exception for AI healing failures"""
    pass

class TemplateNotFoundError(AIHealingError):
    """Raised when template image is missing"""
    pass

class VisualRecoveryFailedError(AIHealingError):
    """Raised when visual recovery cannot locate element"""
    pass
```

### Best Practices

1. **Always provide fallback templates** for critical elements
2. **Monitor healing success rates** and adjust thresholds
3. **Log healing events** for continuous improvement
4. **Validate template quality** before deployment

---

## Performance Optimization

### Template Guidelines

- **Size**: Keep templates between 50x50 to 200x200 pixels
- **Format**: Use PNG for best quality/size ratio
- **Content**: Focus on unique visual features
- **Background**: Include minimal surrounding context

### Healing Optimization

```python
# Optimize for speed
healer = VisualHealer(threshold=0.85)  # Higher threshold = faster
healer.find_element_visually(scene, template, region_of_interest)

# Batch processing for multiple elements
elements = healer.find_multiple_elements(scene, templates)
```

---

## Troubleshooting

### Common Issues

**Problem**: AI cannot find elements
**Solution**: 
- Check template image quality
- Verify threshold settings (try 0.7-0.9)
- Ensure screenshot captures current state

**Problem**: False positives
**Solution**:
- Increase threshold value
- Use more specific templates
- Add secondary validation

**Problem**: Slow performance
**Solution**:
- Reduce template sizes
- Limit search regions
- Use appropriate thresholds

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed AI logging
healer = VisualHealer(threshold=0.8, debug=True)
```
