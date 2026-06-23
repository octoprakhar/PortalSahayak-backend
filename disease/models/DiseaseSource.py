from enum import Enum

class DiseaseSource(Enum):
    """
    This will tell from where this disease is selected. I mean 
    is it selected by filling the value, or by clicking checkbox, 
    or just user selected it, or computer has wrongly selected it
    """
    VALUE = "value"
    CHECKBOX = "checkbox"
    USER = "user"
    PORTAL_AUTO = "portal_auto"
    UNKNOWN = "unknown"