from typing import Any

from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models import Configuration

from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.checker import ConsistencyChecker
from flamapy.metamodels.pysat_metamodel.operations.diagnosis.diagnosis_model import DiagnosisModel

from flamapy.metamodels.pysat_metamodel.operations.diagnosis.fastdiag import FastDiag


class Glucose3FastDiag(Operation):

    def __init__(self) -> None:
        self.result = False
        self.configuration = None
        self.solverName = 'glucose3'
        self.diagnosis_messages: list[str] = []

        self.checker = None

    def get_diagnosis_messages(self) -> list[Any]:
        return self.get_result()

    # if specify configuration -> C=configuration
    # otherwise -> C=PySATModel
    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration
        print(self.configuration)

    def is_valid(self) -> bool:
        pass

    def get_result(self) -> list[str]:
        return self.diagnosis_messages

    def execute(self, model: PySATModel) -> 'Glucose3FastDiag':
        # transform model to diagnosis model
        diag_model = DiagnosisModel(model)
        diag_model.prepare_diagnosis_task(configuration=self.configuration)

        print(f'C: {diag_model.get_C()}')
        print(f'B: {diag_model.get_B()}')

        checker = ConsistencyChecker(self.solverName)
        fastdiag = FastDiag(checker)

        diag = fastdiag.findDiagnosis(diag_model.get_C(), diag_model.get_B())

        if diag:
            self.diagnosis_messages.append(f'Diagnosis: {diag}')

        return self
