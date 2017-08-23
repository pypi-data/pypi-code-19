"""
Validation as a defined model
This will have a list of validations that a service needs to check
before being added to the composition.

These validations will support multiple items, currently implemented is "file"

"""
from abc import ABC, abstractmethod
from os import getenv
from pathlib import Path


class BaseValidation(ABC):
    def __init__(self, **kwargs):
        pass

    @classmethod
    def all_validations(self):
        """
        Collection of all the validation classes that are included
        in the system

        This collection gets iterated and the validation is chosen by name

        """
        return BaseValidation.__subclasses__()

    @abstractmethod
    def validate(self):
        """
        Validate the specific inheriting validation

        """
        pass

    @classmethod
    def from_dict(cls, dct):
        """
        This will return an inheriting validation
        For example, when passing `file` in the `name`, it will
        load the FileExistValidation and will validate using the internal
        logic of that validation

        """
        name = dct.get("name")
        return cls.get(name)(**dct)

    @classmethod
    def iter_matching_validations(self, name):
        for validation in BaseValidation.all_validations():
            if validation.name() == name:
                yield validation

    @abstractmethod
    def name(cls):
        pass

    @classmethod
    def get(self, name):
        """
        Gets the validation for the name

        :name: name of a validation
        :returns: single validation that match the name or EmptyValidation

        """
        try:
            return next(BaseValidation.iter_matching_validations(name))
        except StopIteration:
            return EmptyValidation

        return EmptyValidation


class EnvVarExistValidation(BaseValidation):
    """
    Check if an env var exists

    """
    @classmethod
    def name(cls):
        return "env"

    def __init__(self, **kwargs):
        self.envvar = kwargs.get("var")

    def validate(self):
        value = getenv(self.envvar)
        return bool(value)


class FileExistValidation(BaseValidation):
    """
    Check if a File exists in a specific path

    """
    @classmethod
    def name(cls):
        return "file"

    def __init__(self, **kwargs):
        self.filepath = kwargs.get("filepath")

    def validate(self):
        valid_file = Path(self.filepath)
        return valid_file.is_file()


class EmptyValidation(BaseValidation):
    @classmethod
    def name(cls):
        return "empty"

    def validate(self):
        return False


class Validations(ABC):
    """
    Validations is the collection of all validations
    This serves the purpose of containing the parsed validation JSON
    returning a collection of ServiceValidation


    """
    def __init__(self, validations=[]):
        self.validations = validations

    def validate(self, service):
        """
        validate a specific service
        This will check if the list of validations has the service in it
        In most cases, this will have at least one which is the empty
        validation. it will loop through all the validations that are
        configured for the service and call the validate() method


        If a service does not pass validations, this will return false and
        the service will be added an error

        :service: Service instance
        :returns: True/False
        """
        passing = True

        for service_validation in self.iter_matching_validations(service):
            for validation in service_validation.validations:
                if not validation.validate():
                    passing = False
                    service.add_error("Failed to pass validation: {}".format(type(validation).name()))

        return passing

    def iter_matching_validations(self, service):
        service_validations = list(filter(lambda x: x.service == service.name, self.validations))
        for service_validation in service_validations:
            yield service_validation

    @classmethod
    def iter_service_validations(cls, dct):
        for key in dct.keys():
            service_validation = ServiceValidations(
                service=key,
                validations=list(
                    BaseValidation.from_dict(value)
                    for value in dct[key]
                )
            )
            yield service_validation

    @classmethod
    def from_dict(cls, dct):
        validations = list(cls.iter_service_validations(dct))

        return cls(
            validations=validations,
        )


class ServiceValidations(ABC):
    def __init__(self, service=None, validations=[]):
        self.service = service
        self.validations = validations
