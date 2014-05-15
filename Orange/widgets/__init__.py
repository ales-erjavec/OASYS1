"""

"""
import pkg_resources


# Entry point for main Orange categories/widgets discovery
def widget_discovery(discovery):
    #from . import data
    dist = pkg_resources.get_distribution("Orange")
    pkgs = [#"Orange.widgets.data",
            #"Orange.widgets.visualize",
            #"Orange.widgets.classify",
            #"Orange.widgets.evaluate",
            "Orange.widgets.shadow_experimental_elements",
            "Orange.widgets.shadow_optical_elements",
            "Orange.widgets.shadow_preprocessor",
            "Orange.widgets.shadow_user_defined",
            "Orange.widgets.shadow_loop_management",
            "Orange.widgets.shadow_sources",
            "Orange.widgets.shadow_plots"]
    for pkg in pkgs:
        discovery.process_category_package(pkg, distribution=dist)
