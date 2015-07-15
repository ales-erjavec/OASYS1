import pkgutil
import inspect
import types
import logging

import pkg_resources

from orangecanvas.registry import WidgetDescription
from orangecanvas.registry import discovery

from oasys.menus.menu import OMenu

log = logging.getLogger(__name__)


class MenuRegistry(object):

    def __init__(self, menus=None):
        self.registry = menus if menus is not None else []

    def menus(self):
        return self.registry

    def addMenu(self, menu):
        self.registry.append(menu)


def widget_desc_from_module(module):

    """
    Get the widget description from a module.

    The module is inspected for a Orange.widgets.widget.OWWidget instance
    and the class attributes (upper case versions of
    `WidgetDescription.__init__` parameters).

    Parameters
    ----------
    module : `module` or str
        A module to inspect for widget description. Can be passed
        as a string (qualified import name).

    """
    from Orange.widgets.widget import WidgetMetaClass

    if isinstance(module, str):
        module = __import__(module, fromlist=[""])

    module_name = module.__name__.rsplit(".", 1)[-1]
    if module.__package__:
        package_name = module.__package__.rsplit(".", 1)[-1]
    else:
        package_name = None

    default_cat_name = package_name if package_name else ""

    for widget_cls_name, widget_class in module.__dict__.items():
        if (isinstance(widget_class, WidgetMetaClass) and
                widget_class.name):
            break
    else:
        raise discovery.WidgetSpecificationError

    qualified_name = "%s.%s" % (module.__name__, widget_cls_name)

    # Convert all signal types into qualified names.
    # This is to prevent any possible import problems when cached
    # descriptions are unpickled (the relevant code using this lists
    # should be able to handle missing types better).
    for s in widget_class.inputs + widget_class.outputs:
        if isinstance(s.type, type):
            s.type = "%s.%s" % (s.type.__module__, s.type.__name__)

    return WidgetDescription(
        name=widget_class.name,
        id=widget_class.id or module_name,
        category=widget_class.category or default_cat_name,
        version=widget_class.version,
        description=widget_class.description,
        long_description=widget_class.long_description,
        qualified_name=qualified_name,
        package=module.__package__,
        inputs=widget_class.inputs,
        outputs=widget_class.outputs,
        author=widget_class.author,
        author_email=widget_class.author_email,
        maintainer=widget_class.maintainer,
        maintainer_email=widget_class.maintainer_email,
        help=widget_class.help,
        help_ref=widget_class.help_ref,
        url=widget_class.url,
        keywords=widget_class.keywords,
        priority=widget_class.priority,
        icon=widget_class.icon,
        background=widget_class.background,
        replaces=widget_class.replaces)


class WidgetDiscovery(discovery.WidgetDiscovery):
    """
    OASYS widget discovery.
    """

    def widget_description(self, module, widget_name=None, category_name=None,
                           distribution=None):
        """
        Return widget description from a module.
        """
        module = discovery.asmodule(module)
        desc = widget_desc_from_module(module)

        if widget_name is not None:
            desc.name = widget_name

        if category_name is not None:
            desc.category = category_name

        if distribution is not None:
            desc.project_name = distribution.project_name

        return desc


def omenus_from_package(package):
    try:
        package = discovery.asmodule(package)
    except ImportError:
        return
    for path in package.__path__:
        for _, mod_name, ispkg in pkgutil.iter_modules([path]):
            if ispkg:
                continue

            name = package.__name__ + "." + mod_name
            try:
                menu_module = discovery.asmodule(name)
            except ImportError:
                log.error("Error importing '%s'", name, exc_info=True)
                return

            for name, menu_class in inspect.getmembers(menu_module):
                if inspect.isclass(menu_class) and \
                        issubclass(menu_class, OMenu) and not name == "OMenu":
                    try:
                        yield menu_class()
                    except Exception:
                        log.error("Error creating menu instance from '%s'",
                                  menu_class, exc_info=True)
