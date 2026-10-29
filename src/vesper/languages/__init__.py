from .base import BaseLanguage
from .cpp import CppLanguage
from .python import PythonLanguage
from .java import JavaLanguage

LANGUAGE_REGISTRY = {
    "cpp": CppLanguage,
    "c++": CppLanguage,
    "py": PythonLanguage,
    "python": PythonLanguage,
    "python3": PythonLanguage,
    "java": JavaLanguage
}


def get_language_instance(language: str, time_limit: float, memory_limit: int, container=None) -> BaseLanguage:
    """
    Factory creating language-specific runner instances.
    """
    normalized = language.strip().lower()
    if normalized not in LANGUAGE_REGISTRY:
        supported = ", ".join(sorted(set(LANGUAGE_REGISTRY.keys())))
        raise ValueError(f"Unsupported language: '{language}'. Supported: {supported}")

    cls = LANGUAGE_REGISTRY[normalized]
    return cls(time_limit=time_limit, memory_limit=memory_limit, container=container)
