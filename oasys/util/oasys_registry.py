class AlreadyInitializedError(ValueError):
    def __init__(self, message=None): super(AlreadyInitializedError, self).__init__(message)

class GenericRegistry(object):
    _NO_APPLICATION = "<NO APPLICATION>"

    def __init__(self, registry_name):
        self.__registry_name = registry_name
        self.__registry = {self._NO_APPLICATION: None}

    def register_instance(self, instance, application_name=None, replace=False):
        if instance is None: raise ValueError(self.__registry_name + " Instance is None")

        application_name = self.__get_application_name(application_name)

        if application_name in self.__registry.keys():
            if self.__registry[application_name] is None or replace==True: self.__registry[application_name] = instance
            else: raise AlreadyInitializedError(self.__registry_name + " Instance already initialized")
        else: self.__registry[application_name] = instance

    def reset(self, application_name=None):
        application_name = self.__get_application_name(application_name)

        if application_name in self.__registry.keys(): self.__registry[self.__get_application_name(application_name)] = None
        else: raise ValueError(self.__registry_name + " Instance not existing")

    def get_instance(self, application_name=None):
        application_name = self.__get_application_name(application_name)

        if application_name in self.__registry.keys(): return self.__registry[self.__get_application_name(application_name)]
        else: raise ValueError(self.__registry_name + " Instance not existing")

    def __get_application_name(self, application_name):
        return self._NO_APPLICATION if application_name is None else application_name
