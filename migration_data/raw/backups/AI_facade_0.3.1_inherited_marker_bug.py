"""Memory-aware, backward-compatible facade for POP TensorFlow AI classes.

Importing this module is intentionally cheap. TensorFlow and the legacy POP
implementation are loaded only when an AI class/function is first accessed.
The default device policy is CPU so many classroom Jupyter kernels can coexist
on an 8 GB Jetson. Call ``configure("gpu")`` before accessing a class when a
lesson actually needs GPU acceleration.
"""

from __future__ import annotations

import importlib
import os
import threading
import warnings


_IMPLEMENTATION_EXPORTS = (
    "Linear_Regression",
    "Logistic_Regression",
    "Perceptron",
    "ANN",
    "DNN",
    "CNN",
    "RNN",
    "DQN",
    "FaceNet",
    "onehot",
)

__all__ = (
    "configure",
    "device_policy",
    "is_loaded",
    *_IMPLEMENTATION_EXPORTS,
)

_lock = threading.RLock()
_implementation = None
_configured_device = None
_effective_device = None


def _normalize_device(device):
    value = str(device).strip().lower()
    aliases = {
        "cpu": "cpu",
        "gpu": "gpu",
        "cuda": "gpu",
        "auto": "auto",
    }
    if value not in aliases:
        raise ValueError("device must be one of: cpu, gpu, cuda, auto")
    return aliases[value]


def configure(device="cpu"):
    """Select the TensorFlow device before the first POP AI class is used.

    ``cpu`` is the memory-saving classroom default. ``gpu`` enables the Jetson
    GPU with incremental allocation. ``auto`` selects GPU when one is present.
    The policy cannot be changed after the implementation has been loaded.
    """

    global _configured_device
    normalized = _normalize_device(device)
    with _lock:
        if _implementation is not None and normalized != _configured_device:
            raise RuntimeError(
                "POP AI is already loaded; restart the Jupyter kernel before "
                "changing the device policy"
            )
        _configured_device = normalized
        os.environ["POP_AI_DEVICE"] = normalized
    return normalized


def device_policy():
    """Return the requested and effective POP AI device policy."""

    requested = _configured_device or _normalize_device(
        os.environ.get("POP_AI_DEVICE", "cpu")
    )
    return {
        "requested": requested,
        "effective": _effective_device,
        "loaded": _implementation is not None,
    }


def is_loaded():
    """Return whether TensorFlow-backed POP AI classes have been loaded."""

    return _implementation is not None


def _apply_tensorflow_device_policy():
    global _configured_device, _effective_device

    requested = _configured_device or _normalize_device(
        os.environ.get("POP_AI_DEVICE", "cpu")
    )
    _configured_device = requested

    # Import only at first class access, never at ``from pop import AI``.
    import tensorflow as tf

    gpus = tf.config.list_physical_devices("GPU")
    selected = "gpu" if requested == "auto" and gpus else requested
    if selected == "auto":
        selected = "cpu"

    try:
        if selected == "cpu":
            tf.config.set_visible_devices([], "GPU")
        else:
            if not gpus:
                raise RuntimeError("POP AI GPU mode requested, but no GPU was found")
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as exc:
        # Device visibility is immutable after TensorFlow runtime initialization.
        warnings.warn(
            "TensorFlow was initialized before POP AI device selection; "
            f"requested policy {selected!r} could not be applied: {exc}",
            RuntimeWarning,
            stacklevel=3,
        )
        selected = "existing"

    _effective_device = selected


def _install_instance_optimizers(module, tf):
    """Give each model its own TF 2.12 optimizer and variable-slot state."""

    model_classes = (
        "Linear_Regression",
        "Logistic_Regression",
        "Perceptron",
        "ANN",
        "DNN",
        "CNN",
        "RNN",
        "DQN",
    )
    for name in model_classes:
        cls = getattr(module, name)
        if getattr(cls, "_pop_instance_optimizer", False):
            continue
        original_init = cls.__init__

        def init_with_private_optimizer(self, *args, __init=original_init, **kwargs):
            self.optimizer = tf.keras.optimizers.Adam(
                learning_rate=self.learning_rate
            )
            return __init(self, *args, **kwargs)

        init_with_private_optimizer.__name__ = original_init.__name__
        init_with_private_optimizer.__doc__ = original_init.__doc__
        cls.__init__ = init_with_private_optimizer
        cls._pop_instance_optimizer = True


def _load_implementation():
    global _implementation
    with _lock:
        if _implementation is None:
            _apply_tensorflow_device_policy()
            module = importlib.import_module("._AI_tensorflow", __package__)

            import tensorflow as tf

            _install_instance_optimizers(module, tf)

            # Preserve the historical public module path for introspection and
            # pickling even though definitions live in the private module.
            for name in _IMPLEMENTATION_EXPORTS:
                obj = getattr(module, name)
                if getattr(obj, "__module__", None) == module.__name__:
                    try:
                        obj.__module__ = __name__
                    except (AttributeError, TypeError):
                        pass
                globals()[name] = obj

            _implementation = module
        return _implementation


def __getattr__(name):
    if name in _IMPLEMENTATION_EXPORTS:
        return getattr(_load_implementation(), name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))
