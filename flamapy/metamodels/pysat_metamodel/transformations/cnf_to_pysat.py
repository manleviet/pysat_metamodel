from flamapy.core.transformations import TextToModel

import flamapy.metamodels.pysat_metamodel.operations.diagnosis.utils
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.models.txtcnf_model import (
    TextCNFModel, 
    TextCNFNotation, 
    CNFLogicConnective
)


class CNFReader(TextToModel):
    """
    Read a CNF formula as a string representing a feature model.

    The expected format is the generated by FeatureIDE when exporting the model as CNF (.txt).
    That generates a file with the CNF formula in four different notations:
        Logical Symbols:
            (A) ∧ (¬B ∨ C) ∧ ...
        Textual Symbols:
            (A) and (not B or C) and ...
        Java Symbols:
            (A) && (!B || C) && ...
        Short Symbols:
            (A) & (-B | C) & ...
    This class is able to read any of these notations, but only one notation,
    so the .txt file should be modified to include only
    one of those notations by removing the others.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'txt'

    def __init__(self, path: str):
        self._path = path
        self.counter = 1
        self.destination_model = PySATModel()

    def transform(self) -> PySATModel:
        cnf_model = TextCNFModel()
        cnf_model.from_textual_cnf_file(self._path)
        cnf_notation = cnf_model.get_textual_cnf_notation()
        cnf_formula = cnf_model.get_textual_cnf_formula(cnf_notation)

        self._extract_clauses(cnf_formula, cnf_notation)
        return self.destination_model

    def _add_feature(self, feature_name: str) -> None:
        if feature_name not in self.destination_model.variables:
            self.destination_model.variables[feature_name] = self.counter
            self.destination_model.features[self.counter] = feature_name
            self.counter += 1

    def _extract_clauses(self, cnf_formula: str, cnf_notation: TextCNFNotation) -> None:
        and_symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.AND] + ' '
        clauses = list(map(lambda c: c[1:len(c) - 1], cnf_formula.split(and_symbol_pattern)))
        # Remove initial and final parenthesis

        # Remove final parenthesis of last clause (because of the possible end of line: '\n')
        if ')' in clauses[len(clauses) - 1]:
            clauses[len(clauses) - 1] = clauses[len(clauses) - 1][:-1]

        for _c in clauses:
            tokens = flamapy.metamodels.pysat_metamodel.operations.diagnosis.utils.split(' ')
            tokens = list(filter(lambda t: t != cnf_notation.value[CNFLogicConnective.OR], tokens))
            logic_not = False
            cnf_clause = []
            for feature in tokens:
                if feature == cnf_notation.value[CNFLogicConnective.NOT]:
                    logic_not = True
                elif feature.startswith(cnf_notation.value[CNFLogicConnective.NOT]):
                    feature = feature.replace(cnf_notation.value[CNFLogicConnective.NOT], '', 1)
                    self._add_feature(feature)
                    cnf_clause.append(-1 * self.destination_model.variables[feature])
                else:
                    self._add_feature(feature)
                    if logic_not:
                        cnf_clause.append(-1 * self.destination_model.variables[feature])
                    else:
                        cnf_clause.append(self.destination_model.variables[feature])
                    logic_not = False
            self.destination_model.add_clause(cnf_clause)

    # def get_cnf_formula(self, cnf_output_syntax: TextCNFNotation = TextCNFNotation.JAVA) -> str:
    #     cnf_formula = self._read_cnf_formula()
    #     cnf_notation = identify_notation(cnf_formula)

    #     if cnf_output_syntax == cnf_notation:
    #         return cnf_formula
    #     # Translate AND operators
    #     symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.AND] + ' '
    #     new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.AND] + ' '
    #     cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

    #     # Translate OR operators
    #     symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.OR] + ' '
    #     new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.OR] + ' '
    #     cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

    #     # Translate NOT operators (this is more complex because
    #     # the symbol may be part of a feature's name)
    #     if cnf_notation == TextCNFNotation.TEXTUAL:
    #         symbol_pattern = cnf_notation.value[CNFLogicConnective.NOT] + ' '
    #         new_symbol = cnf_output_syntax.value[CNFLogicConnective.NOT]
    #         cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
    #     elif cnf_output_syntax == TextCNFNotation.TEXTUAL:
    #         symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.NOT]
    #         new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.NOT] + ' '
    #         cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

    #         symbol_pattern = '(' + cnf_notation.value[CNFLogicConnective.NOT]
    #         new_symbol = '(' + cnf_output_syntax.value[CNFLogicConnective.NOT] + ' '
    #         cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
    #     else:
    #         symbol_pattern = ' ' + cnf_notation.value[CNFLogicConnective.NOT]
    #         new_symbol = ' ' + cnf_output_syntax.value[CNFLogicConnective.NOT]
    #         cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)

    #         symbol_pattern = '(' + cnf_notation.value[CNFLogicConnective.NOT]
    #         new_symbol = '(' + cnf_output_syntax.value[CNFLogicConnective.NOT]
    #         cnf_formula = cnf_formula.replace(symbol_pattern, new_symbol)
    #     return cnf_formula
