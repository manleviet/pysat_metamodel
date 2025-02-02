from typing import Any, cast

from pysat.solvers import Solver

from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.core.operations import Filter
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.core.models import VariabilityModel


class PySATFilter(Filter):

    def __init__(self) -> None:
        self.filter_products: list[list[Any]] = []
        self.configuration = Configuration({})
        self.solver = Solver(name='glucose3')

    def get_filter_products(self) -> list[list[Any]]:
        return self.filter_products

    def get_result(self) -> list[list[Any]]:
        return self.get_filter_products()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: VariabilityModel) -> 'PySATFilter':  # noqa: MC0001
        model = cast(PySATModel, model)

        for clause in model.get_all_clauses():  # AC es conjunto de conjuntos
            self.solver.add_clause(clause)  # añadimos la constraint

        if not self.configuration.is_full:
            assumptions = []
            for feature, selected in self.configuration.elements.items():
                if selected:
                    assumptions.append(model.variables[feature])
                else:
                    assumptions.append(-model.variables[feature])
        else:
            missing_features = [feature for feature in self.configuration.elements.keys() 
                                if feature not in model.variables.keys()]
            if missing_features:
                raise ValueError("The configuration contains features that are \
                                 not present in the feature model.",
                                 list(missing_features))
            assumptions = []
            for feature in model.features.values():
                if self.configuration.elements.get(feature, False):
                    assumptions.append(model.variables[feature])
                else:
                    assumptions.append(-model.variables[feature])

        for solution in self.solver.enum_models(assumptions=assumptions):
            product = []
            for variable in solution:
                if variable is not None and variable > 0:
                    product.append(model.features.get(variable))
            self.filter_products.append(product)
        self.solver.delete()
        return self