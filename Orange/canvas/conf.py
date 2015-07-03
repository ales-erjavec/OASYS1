import itertools
import logging

import pkg_resources

from OrangeCanvas import config

from . import discovery, widgetsscheme


WIDGETS_ENTRY = "orange.widgets"
MENU_ENTRY = "orange.menu"

#: Parameters for searching add-on packages in PyPi using xmlrpc api.
ADDON_PYPI_SEARCH_SPEC = {"keywords": "oasys"}
#: Entry points by which add-ons register with pkg_resources.
ADDONS_ENTRY = "orangecontrib"


class oasysconf(config.default):
    OrganizationDomain = ""
    ApplicationName = "OASYS"
    ApplicationVersion = "1.0"

    @staticmethod
    def widgets_entry_points():
        ep_menu_iter = pkg_resources.iter_entry_points(MENU_ENTRY)
        ep_iter = pkg_resources.iter_entry_points(WIDGETS_ENTRY)
        return itertools.chain(ep_menu_iter, ep_iter)

    @staticmethod
    def addon_entry_points():
        return pkg_resources.iter_entry_points(ADDONS_ENTRY)

    @staticmethod
    def addon_pypi_search_spec():
        return dict(ADDON_PYPI_SEARCH_SPEC)

    @staticmethod
    def tutorials_entry_points():
        default_ep = pkg_resources.EntryPoint(
            "Orange", "Orange.canvas.application.tutorials",
            dist=pkg_resources.get_distribution("Orange"))

        return itertools.chain(
            (default_ep,), pkg_resources.iter_entry_points(""))

    widget_discovery = discovery.WidgetDiscovery
    workflow_constructor = widgetsscheme.WidgetsScheme


def omenus():
    """
    Return an iterator of Orange.menu.OMenu instances registered
    by 'orange.menu' pkg_resources entry point.
    """
    log = logging.getLogger(__name__)
    for ep in pkg_resources.iter_entry_points(MENU_ENTRY):
        try:
            menu = ep.load()
        except pkg_resources.ResolutionError:
            log.info("Error loading a 'orange.menu' entry point.", exc_info=True)
        except Exception:
            log.exception("Error loading a 'orange.menu' entry point.")
        else:
            if "MENU" in menu.__dict__:
                yield from discovery.omenus_from_package(menu)


def menu_registry():
    """
    Return the the OASYS extension menu registry.
    """
    return discovery.MenuRegistry(list(omenus()))
