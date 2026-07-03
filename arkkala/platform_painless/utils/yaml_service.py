import yaml


class Yaml:
    @classmethod
    def load_diagram(cls, diagram_path):
        """
        load db diagram
        """
        with open(diagram_path, 'r') as f:
            diagram = yaml.load_all(f.read(), Loader=yaml.FullLoader)
        return list(diagram)
