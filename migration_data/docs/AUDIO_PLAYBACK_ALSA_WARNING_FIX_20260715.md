# PyAudio playback and ALSA warning fix

## Diagnosis

The `Unknown PCM front/rear/surround`, failed PulseAudio connection, and
invalid OSS/USB PCM messages came from PortAudio probing every ALSA
compatibility device. They were not playback stream failures.

The migrated SGTL5000 headphone switch was genuinely muted, so a successfully
opened stream could still produce no audible output.

## Applied playback mixer state

```text
H40-SGTL Headphone Mux = DAC
H40-SGTL Headphone = 81%, on
H40-SGTL PCM = 100%
```

The state was saved with `alsactl store 1` for reboot restoration.

## Jupyter warning handling

`migration_data/tests/quiet_alsa_ipython.py` is installed on the Jetson as:

```text
/home/soda/.ipython/profile_default/startup/10-quiet-alsa.py
```

New Jupyter kernels suppress only libasound's device-enumeration text.
PyAudio continues to raise Python exceptions for actual open, read, and write
failures. Existing notebook kernels must be restarted once to load the file.

Verification results:

- IPython enumerated 27 devices without the ALSA diagnostic flood.
- A one-second 440 Hz float32 playback stream completed with `PLAYBACK_OK`.
- Mixer readback showed headphone left/right at 81%, both switched on.

Reusable test:

```bash
python3 migration_data/tests/test_pyaudio_playback.py \
  --seconds 5 --frequency 440 --volume 0.5
```
