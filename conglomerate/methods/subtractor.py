from conglomerate.methods.method import Method
from conglomerate.tools.tool import CALCULATOR_TOOL


class Subtractor(Method):
    def _getMappings(self):
        return {'LOGICAL_ARG_1': 'a', 'LOGICAL_ARG_2': 'b', 'LOGICAL_ARG_3': 'operation'}

    def _getTool(self):
        return CALCULATOR_TOOL
