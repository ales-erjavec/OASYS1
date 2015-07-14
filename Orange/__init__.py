try:
    from .import version
    # Always use short_version here (see PEP 386)
    __version__ = version.short_version
    __git_revision__ = version.git_revision
except ImportError:
    __version__ = "unknown"
    __git_revision__ = "unknown"
