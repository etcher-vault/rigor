import related
import jmespath
import ast

from mako.template import Template


class Namespace(related.ImmutableDict):

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, name):
        return self.get(name) if name in self else jmespath.search(name, self)

    def evaluate(self, namespace, existing=None):
        values = existing or {}

        for key, value in self.items():
            values[key] = self.render(value, namespace)

        return Namespace(values)

    @classmethod
    def wrap(cls, value):
        if isinstance(value, dict) and not isinstance(value, cls):
            return cls(value)

        if isinstance(value, list):
            new_list = []
            for item in value:
                new_list.append(cls.wrap(item))
            value = new_list

        return value

    @classmethod
    def render(cls, value, namespace):
        if isinstance(value, str):
            template = Template(value)

            try:
                rendered = template.render(**namespace)
            except:
                raise

            try:
                value = ast.literal_eval(rendered)
            except:
                value = rendered

        value = cls.wrap(value)

        return value