# POP AI, TensorFlow memory, and scikit-learn TLS fix

## Symptoms

- `NvMapMemAllocInternalTagged ... error 12` repeated while importing or using
  the POP AI module.
- Keras warned that optimizer argument `lr` was deprecated.
- Importing `sklearn.linear_model.LinearRegression` after TensorFlow failed
  with `cannot allocate memory in static TLS block`.
- TensorFlow process shutdown printed `No protocol specified`.

## Root causes

1. One Jupyter kernel retained about 5.0-5.25 GiB RSS on a 6.7 GiB Xavier NX.
   TensorFlow could not allocate additional NvMap GPU buffers.
2. POP `AI.py` created five Keras Adam optimizers with the deprecated `lr`
   keyword and did not request incremental TensorFlow GPU allocation before
   importing TensorFlow.
3. The aarch64 scikit-learn 1.3.2 wheel linked 68 extension modules to its own
   renamed `libgomp-d22c30c5.so.1.0.0`. Loading this second OpenMP runtime
   after TensorFlow exhausted the Jetson glibc static TLS block.
4. GDM ran Xorg on `:0`, but local user `soda` was not authorized. NVIDIA
   libraries touched that display during cleanup and Xorg rejected them.

## Applied changes

- Terminated only the runaway 5 GiB Jupyter kernel. Available RAM increased
  from about 1.5 GiB to 5.1 GiB.
- Released and installed `gong-rc-pop 0.2.4+20260715`.
- Replaced five `Adam(lr=...)` calls with `Adam(learning_rate=...)`.
- Added these settings before TensorFlow import in POP AI:

  ```python
  os.environ.setdefault('TF_FORCE_GPU_ALLOW_GROWTH', 'true')
  os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
  os.environ.setdefault('MPLBACKEND', 'Agg')
  ```

- Relinked 68 scikit-learn extensions from the bundled OpenMP runtime to the
  preloaded system `libgomp.so.1` using `fix_sklearn_static_tls.py`.
- Added and enabled `gong-rc-xhost-soda.service`. It grants Xorg access only
  to local user `soda`; it does not use the unsafe unrestricted `xhost +`.

scikit-learn backup:

```text
/home/soda/venvs/gong-rc/.migration_backups/sklearn_static_tls_20260715_150809.tar.gz
/home/soda/venvs/gong-rc/.migration_backups/sklearn_static_tls_20260715_150809.json
```

POP package:

```text
migration_data/packages/gong-rc-pop_0.2.4+20260715_arm64.deb
SHA-256 45bfa30c469610dae0b74adea5a0997941bfa306a4a1cc17ce8f4f4793a31151
```

## Final validation

One fresh process imported POP AI, ran a TensorFlow GPU matrix multiplication,
trained a POP Keras linear model, imported scikit-learn, and fitted/predicted a
`LinearRegression` model.

```text
POP_AI_PATH=/usr/lib/python3/dist-packages/pop/AI.py
TENSORFLOW=2.12.0
TF_GPU_MATMUL=[[7.0, 10.0], [15.0, 22.0]]
SKLEARN_COEF=[1.9999999999999996]
SKLEARN_PREDICT=[5.999999999999998]
POP_AI_SKLEARN_INTEROP=PASS
```

The final run contained none of the original NvMap, Keras `lr`, static TLS, or
X11 protocol diagnostics. `jupyter-gong-rc.service` and
`gong-rc-xhost-soda.service` are active, `dpkg --audit` is clean, and available
RAM returned to about 5.1 GiB after the test exited.

Reusable verification:

```bash
python3 migration_data/tests/test_pop_ai_sklearn_interop.py
```

If scikit-learn is upgraded or reinstalled from a wheel, rerun:

```bash
/home/soda/venvs/gong-rc/bin/python3 \
  migration_data/scripts/fix_sklearn_static_tls.py
```
