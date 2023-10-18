from typing import Any, cast

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration

from .diagnosis.checker import ConsistencyChecker
from .diagnosis.hsdag.hsdag import HSDAG
from .diagnosis.hsdag.labeler.quickxplain_labeler import QuickXPlainParameters, QuickXPlainLabeler
from ..models.pysat_diagnosis_model import DiagnosisModel


class Glucose3Conflict(Operation):
    """
    An operation that computes conflicts and diagnoses
    using the combination of HSDAG and QuickXPlain algorithms.
    Four optional inputs:
    - configuration - a configuration to be diagnosed
    - test_case - a test case to be used for diagnosis
    - max_conflicts - specify the maximum number of conflicts to be computed
    - max_depth - specify the maximum depth of the HSDAG to be computed
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        self.result = False
        self.configuration = None
        self.test_case = None
        self.solver_name = 'glucose3'
        self.diagnosis_messages: list[str] = []

        self.checker = None
        self.max_conflicts = -1  # -1 means no limit
        self.max_depth = 0  # 0 means no limit

    def set_max_conflicts(self, max_conflicts: int) -> None:
        self.max_conflicts = max_conflicts

    def set_max_depth(self, max_depth: int) -> None:
        self.max_depth = max_depth

    def get_diagnosis_messages(self) -> list[Any]:
        return self.get_result()

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def set_test_case(self, test_case: Configuration) -> None:
        self.test_case = test_case

    def get_result(self) -> list[str]:
        return self.diagnosis_messages

    def execute(self, model: VariabilityModel) -> 'Glucose3Conflict':
        model = cast(DiagnosisModel, model)

        # transform model to diagnosis model
        model.prepare_diagnosis_task(configuration=self.configuration, test_case=self.test_case)

        # print(f'C: {diag_model.get_C()}')
        # print(f'B: {diag_model.get_B()}')

        set_c = model.get_c()
        # if self.configuration is None:
        # reverse the list to get the correct order of constraints in the diagnosis messages
        #     C.reverse()

        checker = ConsistencyChecker(self.solver_name, model.get_kb())
        parameters = QuickXPlainParameters(set_c, [], model.get_b())
        quickxplain = QuickXPlainLabeler(checker, parameters)
        hsdag = HSDAG(quickxplain)
        hsdag.max_number_conflicts = self.max_conflicts
        hsdag.max_depth = self.max_depth

        hsdag.construct()

        diagnoses = hsdag.get_diagnoses()
        conflicts = hsdag.get_conflicts()

        if len(diagnoses) == 0:
            diag_mess = 'No diagnosis found'
        elif len(diagnoses) == 1:
            diag_mess = 'Diagnosis: '
            diag_mess += model.get_pretty_diagnoses(diagnoses)
        else:
            diag_mess = 'Diagnoses: '
            diag_mess += model.get_pretty_diagnoses(diagnoses)

        if len(conflicts) == 0:
            cs_mess = 'No conflicts found'
        elif len(conflicts) == 1:
            cs_mess = 'Conflict: '
            cs_mess += model.get_pretty_diagnoses(conflicts)
        else:
            cs_mess = 'Conflicts: '
            cs_mess += model.get_pretty_diagnoses(conflicts)

        self.diagnosis_messages.append(cs_mess)
        self.diagnosis_messages.append(diag_mess)
        checker.delete()
        return self
