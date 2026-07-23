from jinja2 import Environment, BaseLoader, TemplateSyntaxError
from typing import Dict, Any

class StringTemplateLoader(BaseLoader):
    def __init__(self, template_string: str):
        self.template_string = template_string
    
    def get_source(self, environment, template):
        return self.template_string, template, lambda: True

class Jinja2TemplateEngine:
    def __init__(self):
        self.env_kwargs = {
            'autoescape': True
        }

    def render(self, template_string: str, variables: Dict[str, Any]) -> str:
        """
        Renders a given template string with the provided variables.
        """
        try:
            env = Environment(loader=StringTemplateLoader(template_string), **self.env_kwargs)
            template = env.get_template("default")
            return template.render(**variables)
        except TemplateSyntaxError as e:
            raise ValueError(f"Template syntax error: {e.message} at line {e.lineno}")
        except Exception as e:
            raise ValueError(f"Template rendering failed: {str(e)}")

template_engine = Jinja2TemplateEngine()
