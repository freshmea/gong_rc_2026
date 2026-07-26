# Jupyter 예제 배포 및 a04 오디오 수정 결과

날짜: 2026-07-17  
대상: `gong-rc-32gb` (`192.168.0.67`, user `soda`)

## 노트북 예제 배포

64GB 수업 구성에 사용한 보존 원본을 다음 위치로 실제 복사했다.

- 원본: `/home/soda/gong_rc_2026/autocar/jupyter_source/`
- Jupyter 폴더: `/home/soda/Project/python/notebook/gong_rc_2026/`

원본 구성은 파일 44개이며, 이 중 노트북은 `a01`부터 `a30` 및
`video_test.ipynb`까지 31개다. 오디오 WAV/MP3, 이미지, 조향 보정 JSON도
함께 복사했다.

`validate_notebook_bundle.py` 결과:

```text
NOTEBOOK_BUNDLE_VALIDATION=PASS
source_files_verified=44
notebooks=31
manifest_sha256=f9ef29e8221e9c5bc37d859ca1e790a985b661d691e943866260fa8db599840e
```

Jupyter가 만든 `.ipynb_checkpoints/`와 수업 실행 중 생성한 모델 파일은
사용자 작업물일 수 있으므로 삭제하지 않는다. 검증기는 44개 원본의 존재와
SHA-256 일치 여부는 엄격히 검사하되 이러한 생성물은 별도로 보고한다.

최종 검증 중 Jupyter에서 저장된 `a12_led.ipynb`와 `a26_v1_ann.ipynb`가
원본과 달라진 것이 발견됐다. 두 수정본은 다음 위치에 보존한 뒤 64GB 원본
체크섬으로 복원했다.

```text
/home/soda/Project/python/notebook/.migration_backups/
  gong_rc_2026_20260717_005630/
```

`deploy_notebook_bundle.sh`는 이후에도 `rsync --checksum --backup`을 사용해
원본과 다른 대상 파일을 먼저 시간별 백업 폴더에 보관한다.

Jupyter ContentsManager가 폴더를 정상 인식했고, 하드웨어를 움직이지 않는
`a14_linear_regresstion.ipynb`는 20개 셀, 오류 0으로 실행됐다.

## Jupyter sklearn TLS 수정

기존 노트북은 커널 이름이 `python3`, 새 커널은 `gong-rc`이므로 두 커널
스펙을 모두 설정했다. scikit-learn wheel에 포함된 아래 라이브러리를 커널
시작 전에 로드해야 `cannot allocate memory in static TLS block` 오류가
발생하지 않는다.

```text
/home/soda/venvs/gong-rc/lib/python3.8/site-packages/
  scikit_learn.libs/libgomp-d22c30c5.so.1.0.0
```

`configure_jupyter_kernel_env.py`가 두 커널의 `kernel.json`에 이 경로와
TensorFlow memory growth, CUDA, Matplotlib, OpenCV 환경을 기록한다. 원본
노트북의 메타데이터는 수정하지 않았다.

## a04 무음 원인과 수정

`a04_sound_blocking.ipynb`의 PyAudio 코드는 정상이고 APE의 재생 경로도
`ADMAIF1 -> I2S5 -> SGTL5000 DAC`로 맞았다. 실제 원인은 다음 두 ALSA
출력 스위치가 모두 `[off]`였던 것이다.

- `H40-SGTL Headphone Playback Switch`
- `H40-SGTL Lineout Playback Switch`

적용한 최종 값:

- `I2S5 Mux = ADMAIF1`
- `H40-SGTL Digital Input Mux = I2S`
- `H40-SGTL Headphone Mux = DAC`
- PCM = 100%
- Headphone = 81%, unmuted
- Lineout = 58% (-6.5 dB), unmuted

`configure_sgtl5000_playback.sh`가 값을 설정하고 `alsactl store 1`로
저장한다. 두 스위치를 임의로 mute한 후 `alsactl restore 1`을 실행했을 때
둘 다 `[on]`으로 복원됐고, a04 전체 실행도 다시 통과했다.

## 다른 기체 적용 명령

```bash
sudo /home/soda/gong_rc_2026/migration_data/scripts/deploy_notebook_bundle.sh
/home/soda/venvs/gong-rc/bin/python \
  /home/soda/gong_rc_2026/migration_data/scripts/configure_jupyter_kernel_env.py
sudo /home/soda/gong_rc_2026/migration_data/tests/configure_sgtl5000_playback.sh
sudo systemctl restart jupyter-gong-rc.service

/home/soda/venvs/gong-rc/bin/python \
  /home/soda/gong_rc_2026/migration_data/tests/validate_notebook_bundle.py
/home/soda/venvs/gong-rc/bin/python \
  /home/soda/gong_rc_2026/migration_data/tests/validate_jupyter_notebook_access.py
```

Jupyter 파일 브라우저가 이미 열려 있었다면 새로고침하면
`gong_rc_2026` 폴더가 나타난다.
