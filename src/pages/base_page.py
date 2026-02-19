from src.model.healing import VisualHealer

class BasePage:
    def __init__(self, page):
        self.page = page
        self.healer = VisualHealer()

    def smart_click(self, selector, template_name):
        try:
            # Try standard automation first
            self.page.click(selector, timeout=2000)
        except Exception:
            print(f"Selector {selector} failed. Triggering AI Vision Recovery...")
            # Take a screenshot of the current failed state
            self.page.screenshot(path="temp_scene.png")

            # Use AI to find the button based on a saved image (template)
            coords = self.healer.find_element_visually("temp_scene.png", f"assets/templates/{template_name}.png")

            if coords:
                self.page.mouse.click(coords[0], coords[1])
                print("AI successfully healed the locator!")
            else:
                raise Exception("AI Vision could not find the element. Manual intervention required.")