"""Silence noisy ALSA device-enumeration diagnostics in classroom notebooks.

ALSA/PortAudio errors are still reported by PyAudio as Python exceptions.
Keep the callback and library in module globals so the C callback stays alive.
"""

import ctypes


_ALSA_ERROR_HANDLER = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
)


def _discard_alsa_diagnostic(*_args):
    pass


try:
    _ALSA_LIBRARY = ctypes.cdll.LoadLibrary("libasound.so.2")
    _ALSA_CALLBACK = _ALSA_ERROR_HANDLER(_discard_alsa_diagnostic)
    _ALSA_LIBRARY.snd_lib_error_set_handler(_ALSA_CALLBACK)
except OSError:
    _ALSA_LIBRARY = None
    _ALSA_CALLBACK = None
