from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("village-report-generator")
except PackageNotFoundError:
    # package is not installed
    pass
