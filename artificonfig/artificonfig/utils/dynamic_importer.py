class DynamicImporter:
    """
    Dynamic import class
    This class load automatically a python class inside a python module and
    return the class type

    Parameters
    ----------
    module_name : `string`
        The name of the python module (the python file) to be imported.
    class_name : `string`
        The name of the python class to be imported.
    """

    def __init__(self, module_name: str, class_name: str):
        """Constructor"""
        module = __import__(module_name)
        components = module_name.split(".")
        for comp in components[1:]:
            module = getattr(module, comp)
        self._class_imported = getattr(module, class_name)

    def get_instance(self, **args) -> object:
        """
        Get an instance of the class loaded

        Parameters
        -------
        args: argument for class initialization

        Returns
        -------
        The instance of the class loaded

        """
        return self._class_imported(**args)

    def get_class(self):
        """
        Get the class loaded

        Returns
        -------
        The class loaded

        """
        return self._class_imported
