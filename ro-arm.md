# RoArm M2·M3·SO-ARM101 로봇팔 비교 보고서

## 1. 보고서 개요

### 1.1 작성 목적

본 보고서는 교육용·연구용 소형 서보 로봇팔인 다음 세 제품을 비교하여, ROS2 기반 로봇 제어 교육과 AI·스마트팩토리 실습 장비 선정에 필요한 기초자료를 제공하는 것을 목적으로 한다.

* Waveshare **RoArm-M2**
* Waveshare **RoArm-M3**
* 오픈소스 로봇팔 **SO-ARM101**

세 제품은 모두 시리얼 버스 서보를 기반으로 구성할 수 있지만, 개발 목적과 소프트웨어 생태계에 차이가 있다.

* RoArm-M2: ROS2와 MoveIt2를 배우기 쉬운 입문·교육형 로봇팔
* RoArm-M3: 자유도와 손목 움직임을 확장한 ROS2·LeRobot 융합형 로봇팔
* SO-ARM101: 모방학습과 로봇 AI 데이터 수집에 특화된 오픈소스 로봇팔

---

# 2. 핵심 비교

| 구분          | RoArm-M2            | RoArm-M3             | SO-ARM101                            |
| ----------- | ------------------- | -------------------- | ------------------------------------ |
| 주요 제조·관리 주체 | Waveshare           | Waveshare            | TheRobotStudio·Hugging Face 오픈소스 생태계 |
| 주요 목적       | ROS2 입문, 제어, 교육     | 다자유도 제어, ROS2, AI 확장 | 모방학습, 데이터 수집, LeRobot                |
| 자유도         | 4DOF 계열             | 5+1DOF               | 6축 계열                                |
| 제어기         | ESP32 기반            | ESP32 기반             | USB 서보 드라이버 보드                       |
| 구동 방식       | 시리얼 버스 서보           | 시리얼 버스 서보            | Feetech 계열 시리얼 버스 서보                 |
| 기본 제어       | USB, UART, Wi-Fi, 웹 | USB, UART, Wi-Fi, 웹  | Python·USB 시리얼                       |
| ROS2        | 공식 지원               | 공식 지원                | 공식 중심 생태계는 아님                        |
| MoveIt2     | 공식 예제 제공            | 공식 예제 제공             | 별도 ROS2 통합 필요                        |
| LeRobot     | 일부 확장 가능            | 공식 호환 제품·AI 키트 존재    | 핵심 지원 플랫폼                            |
| 지도 방식       | 좌표·관절·ROS2 제어       | 좌표·관절·ROS2·AI        | 리더-팔로워 텔레오퍼레이션                       |
| 조립 난이도      | 낮음                  | 낮음                   | 중간 이상                                |
| AI 학습 적합성   | 보통                  | 높음                   | 매우 높음                                |
| ROS2 교육 적합성 | 매우 높음               | 매우 높음                | 별도 개발 필요                             |
| 스마트팩토리 실습   | 적합                  | 매우 적합                | AI 공정연구에 적합                          |
| 제품 가격대      | 약 189.99~299.99달러   | 약 239.99~339.99달러    | 옵션에 따라 편차 큼                          |

가격은 옵션, 서보 사양, 그리퍼, 카메라, 컴퓨팅 보드 포함 여부에 따라 크게 달라질 수 있다. Waveshare 공식 제품 목록에서는 RoArm-M2가 189.99달러부터, RoArm-M3가 239.99달러부터 표시되며, SO-ARM100/101 제품군은 부품 키트부터 완성형·AI 키트까지 넓은 가격 범위를 가진다. ([Waveshare][1])

---

# 3. RoArm-M2 제품 분석

## 3.1 제품 개요

RoArm-M2는 Waveshare가 개발한 ESP32 기반 데스크톱 로봇팔이다. 360도 회전이 가능한 베이스와 세 개의 주요 관절을 결합한 4DOF 구조이며, 소형 모바일 플랫폼이나 고정형 작업대에 설치할 수 있도록 설계되었다.

공식 설명에 따르면 RoArm-M2-S는 경량 구조를 사용하고, 최대 작업 반경 기준 약 0.5kg 수준의 유효 하중을 목표로 한다. 어깨 관절에는 듀얼 구동 구조가 적용되어 토크를 높였으며, 관절 직접구동 방식을 사용한다. ([Waveshare][2])

## 3.2 주요 하드웨어 특성

* ESP32 기반 메인 제어기
* 4DOF 구조
* 시리얼 버스 서보 사용
* 360도 회전 베이스
* 그리퍼 또는 말단장치 장착
* USB·UART·Wi-Fi 통신
* 웹 기반 제어 인터페이스
* 어깨 관절 듀얼 서보 구조
* 모바일 로봇 또는 고정형 프레임 장착 가능

일반 PWM 서보와 달리 시리얼 버스 서보는 하나의 통신선에 여러 서보를 연결하고, 각 서보에 ID를 부여하여 제어할 수 있다. 제품과 서보 모델에 따라 현재 각도, 부하, 온도 등의 피드백도 활용할 수 있다.

## 3.3 ROS2 지원

RoArm-M2의 가장 큰 장점은 제조사가 ROS2 Humble과 MoveIt2 사용을 위한 문서와 워크스페이스를 제공한다는 점이다.

공식 ROS2 패키지는 다음 기능을 포함한다.

* 로봇 모델 URDF
* 실제 로봇팔 제어 드라이버
* RViz2 시각화
* MoveIt2 설정
* 역기구학
* 키보드·게임패드 제어
* 웹 기반 제어
* 명령 기반 로봇팔 제어
* Pick-and-Place 확장

Waveshare의 `roarm_ws` 저장소에는 로봇 모델, 실제 장비 드라이버, MoveIt2 설정과 IKFast 기반 역기구학 플러그인이 포함되어 있다. ([GitHub][3])

RoArm-M2 공식 튜토리얼에서는 ROS2 Humble, MoveIt2, RViz2, 게임패드 제어, Foxglove 및 웹 애플리케이션 연동 예제를 제공한다. ([Waveshare][4])

## 3.4 ROS2 제어 구조

```text
ROS2 PC
 ├─ RViz2
 ├─ MoveIt2
 ├─ robot_state_publisher
 ├─ joint_state_publisher
 └─ roarm_driver
          │
       USB Serial
          │
        ESP32
          │
   시리얼 버스 서보
```

ROS2 드라이버 노드는 `/dev/ttyUSB0` 등의 시리얼 포트를 통해 ESP32와 통신한다. RViz2 또는 MoveIt2에서 생성한 관절 명령은 드라이버에서 RoArm 제어 명령으로 변환되어 실제 로봇팔에 전달된다.

## 3.5 교육 활용 분야

RoArm-M2는 다음 교육에 적합하다.

* ROS2 Node·Topic·Service 이해
* URDF와 TF 학습
* JointState와 관절 제어
* RViz2 로봇 시각화
* MoveIt2 모션 플래닝
* 순기구학·역기구학
* 카메라 기반 물체 분류
* 컨베이어와 로봇팔 연동
* Modbus·OPC UA 기반 스마트팩토리 실습

## 3.6 장점과 한계

### 장점

* ROS2 공식 예제가 비교적 잘 갖추어져 있음
* 자유도가 적어 입문자가 구조를 이해하기 쉬움
* ESP32 기반으로 독립적인 기본 제어 가능
* 웹, Wi-Fi, USB 등 다양한 제어 방법 제공
* MoveIt2 실습에 바로 활용 가능
* M3보다 가격이 낮고 구조가 단순함

### 한계

* 손목의 자세 제어 자유도가 부족함
* 복잡한 물체 집기에는 제한이 있음
* 6축 산업용 로봇의 자세 제어를 완전히 재현하기 어려움
* 모방학습과 AI 데이터 수집은 별도 환경 구축이 필요함

## 3.7 참고 링크

* [RoArm-M2 공식 제품 페이지](https://www.waveshare.com/roarm-m2-s.htm)
* [RoArm-M2 공식 Wiki](https://www.waveshare.com/wiki/RoArm-M2-S)
* [RoArm-M2 ROS2 Humble·MoveIt2 튜토리얼](https://www.waveshare.com/wiki/RoArm-M2-S_ROS2_Humble_%2B_Moveit2_Tutorial)
* [Waveshare RoArm ROS2 GitHub 저장소](https://github.com/waveshareteam/roarm_ws)
* [RoArm-M2 펌웨어·개발 저장소](https://github.com/waveshareteam/roarm_m2)

---

# 4. RoArm-M3 제품 분석

## 4.1 제품 개요

RoArm-M3는 RoArm-M2보다 관절 수와 손목 자유도를 확장한 상위 모델이다. 공식 제품 설명에서는 5+1DOF 구조로 표시되며, 360도 베이스와 다섯 개의 관절, 그리퍼를 조합한다.

M3는 손목에 2DOF 구조를 적용하여 로봇팔 끝단의 위치뿐 아니라 그리퍼의 방향과 자세까지 더 세밀하게 조절할 수 있다. 제조사는 약 1m 직경의 작업 영역과 0.5m 거리에서 약 0.2kg 수준의 유효 하중을 제시한다. ([Waveshare][5])

M2보다 자유도가 증가했지만, 팔을 길게 뻗었을 때의 공식 유효 하중은 M2보다 낮게 제시된다. 따라서 M3는 무거운 물체를 드는 용도보다는 다양한 자세와 정교한 작업 방향을 구현하는 데 초점이 있다.

## 4.2 주요 하드웨어 특성

* ESP32 기반 제어기
* 5+1DOF 구조
* 2DOF 손목 관절
* 시리얼 버스 서보
* 360도 회전 베이스
* USB·UART·Wi-Fi 통신
* 웹 기반 제어
* 확장형 그리퍼
* 카메라와 AI 컴퓨팅 보드 확장
* LeRobot 호환 제품 및 AI 키트 제공

## 4.3 M2와 M3의 구조적 차이

```text
RoArm-M2
베이스 회전
  └─ 어깨
      └─ 팔꿈치
          └─ 손목·그리퍼

RoArm-M3
베이스 회전
  └─ 어깨
      └─ 팔꿈치
          └─ 손목 Pitch
              └─ 손목 Roll
                  └─ 그리퍼
```

M3의 추가 손목 관절은 다음 작업에서 유리하다.

* 물체 방향에 맞춘 그리퍼 회전
* 비스듬하게 놓인 물체 집기
* 부품 삽입
* 컵이나 공구의 방향 변경
* 카메라를 이용한 정밀 Pick-and-Place
* 산업용 6축 로봇과 유사한 자세 제어 교육

## 4.4 ROS2 지원

RoArm-M3도 ROS2 Humble과 MoveIt2를 공식적으로 지원한다.

공식 문서에는 다음 내용이 포함되어 있다.

* Windows PC에서 가상머신으로 ROS2 설치
* Ubuntu 22.04 및 ROS2 Humble 환경
* 실제 로봇팔 드라이버 실행
* RViz2 모델 시각화
* 관절 슬라이더 제어
* MoveIt2 드래그 기반 제어
* ROS2 Service 기반 명령 제어
* MoveIt Task Constructor
* Cartesian 경로 생성
* Pick-and-Place 데모

RoArm-M3 공식 튜토리얼은 ROS2 Humble 환경을 기준으로 설명되며, MoveIt2에서 목표 위치를 드래그하면 경로를 계산해 실제 로봇팔을 제어하는 예제를 제공한다. ([Waveshare][6])

공식 GitHub 저장소에는 M3용 URDF와 MoveIt2 설정 디렉터리가 포함되어 있다. ([GitHub][7])

## 4.5 MoveIt Task Constructor 활용

RoArm-M3는 MoveIt Task Constructor를 이용한 다음 작업 예제를 제공한다.

```text
접근 위치 이동
   ↓
그리퍼 열기
   ↓
물체에 접근
   ↓
그리퍼 닫기
   ↓
물체 들어 올리기
   ↓
목표 위치로 이동
   ↓
물체 내려놓기
```

공식 문서에는 Cartesian 이동과 Pick-and-Place를 포함한 MTC 예제가 제공된다. ([Waveshare][8])

## 4.6 LeRobot과 AI 확장

RoArm-M3는 ROS2 로봇팔이면서 동시에 LeRobot 기반 AI 로봇팔로 확장할 수 있다는 것이 특징이다.

Waveshare는 다음과 같은 M3 계열 AI 키트를 제공한다.

* M3 단일 로봇팔
* 리더·팔로워 듀얼 로봇팔
* 카메라 포함 키트
* Jetson Orin Nano 포함 키트
* LeRobot 학습 데이터·예제 포함 구성

RoArm-M3 AI 키트는 LeRobot 프로젝트를 지원하며, 모방학습과 강화학습을 위한 데이터셋과 예제를 활용할 수 있도록 구성되어 있다. ([Waveshare][9])

## 4.7 교육 활용 분야

* ROS2 중·고급 로봇팔 제어
* MoveIt2 모션 플래닝
* 6축에 가까운 자세 제어
* 손목 Pitch·Roll 제어
* Pick-and-Place
* MoveIt Task Constructor
* AI 비전 기반 물체 집기
* LeRobot 모방학습
* 리더-팔로워 텔레오퍼레이션
* 스마트팩토리 로봇 셀 구현

## 4.8 장점과 한계

### 장점

* M2보다 높은 자유도
* 그리퍼 방향과 자세를 세밀하게 제어 가능
* ROS2와 MoveIt2 공식 지원
* LeRobot과 AI 키트로 확장 가능
* 실제 산업용 다관절 로봇에 가까운 교육 가능
* 모션 플래닝과 Pick-and-Place 프로젝트에 유리

### 한계

* M2보다 가격이 높음
* 관절 수가 늘어나 초기 보정과 제어가 복잡함
* 팔을 길게 뻗을 때 허용 하중이 비교적 낮음
* AI 키트, 카메라, Jetson을 추가하면 전체 비용이 크게 증가함
* 학생 1인당 저가 지급 장비로는 예산 부담이 큼

## 4.9 참고 링크

* [RoArm-M3 공식 제품 페이지](https://www.waveshare.com/roarm-m3.htm)
* [RoArm-M3 공식 Wiki](https://www.waveshare.com/wiki/RoArm-M3)
* [RoArm-M3 ROS2 설치 안내](https://www.waveshare.com/wiki/RoArm-M3_How_to_Install_ROS2)
* [RoArm-M3 ROS2 워크스페이스 설명](https://www.waveshare.com/wiki/RoArm-M3_ROS2_Workspace_Description)
* [RoArm-M3 MoveIt2 제어 튜토리얼](https://www.waveshare.com/wiki/RoArm-M3_Moveit2_Drag-and-drop_Interaction_in_Moveit2)
* [RoArm-M3 MoveIt Task Constructor 예제](https://www.waveshare.com/wiki/RoArm-M3_Moveit_MTC_Demonstration)
* [RoArm ROS2 GitHub 저장소](https://github.com/waveshareteam/roarm_ws)
* [Waveshare RoArm Python SDK](https://github.com/waveshareteam/waveshare_roarm_sdk)

---

# 5. SO-ARM101 제품 분석

## 5.1 제품 개요

SO-ARM101은 완성품 하나를 지칭하기보다, 오픈소스로 공개된 설계와 소프트웨어를 기반으로 여러 제조사와 사용자가 제작하는 저비용 6축 로봇팔 플랫폼에 가깝다.

SO-101은 SO-100의 후속 버전으로, TheRobotStudio와 Hugging Face의 협력을 통해 발전했다. 공식 프로젝트 설명에 따르면 배선 구조가 개선되었고, 조립이 쉬워졌으며, 리더 암용 모터 구성이 변경되었다. ([GitHub][10])

SO-ARM101의 가장 중요한 목적은 정밀 산업제어나 ROS2 자체가 아니라 다음과 같은 AI 로봇 연구이다.

* 사람이 로봇팔을 움직여 시범 데이터 수집
* 리더 암의 움직임을 팔로워 암이 따라 하기
* 카메라 영상과 관절 상태 저장
* 행동복제 학습
* 학습된 정책으로 로봇팔 자동 제어
* VLA 및 로봇 파운데이션 모델 연구

## 5.2 제품 구성

SO-ARM101은 일반적으로 다음과 같이 구성한다.

### 팔로워 암

학습 결과에 따라 실제 작업을 수행하는 로봇팔이다.

```text
팔로워 암
 ├─ 6축 버스 서보
 ├─ 그리퍼
 ├─ 3D 프린팅 프레임
 ├─ USB 서보 드라이버
 └─ 12V 전원
```

### 리더 암

사람이 직접 움직여 팔로워 암에 동작을 전달하는 장치다.

```text
리더 암
 ├─ 관절 위치 검출용 버스 서보
 ├─ 그리퍼 입력
 ├─ USB 서보 드라이버
 └─ 텔레오퍼레이션 프로그램
```

### 카메라

* 작업 공간 카메라
* 손목 카메라
* 복수 시점 카메라

### 컴퓨팅 장치

* 일반 Ubuntu PC
* NVIDIA GPU PC
* Jetson Orin Nano
* 기타 Linux 컴퓨터

## 5.3 서보 사양

Waveshare의 SO-ARM100/101 설명에서는 SO-ARM101 팔로워 암에 12V 계열 고토크 버스 서보가 사용되며, SO-ARM100보다 높은 토크를 목표로 한다고 설명한다. 공식 Wiki에는 SO-ARM100의 7.4V·19.5kg·cm급 서보와 SO-ARM101의 12V·30kg·cm급 구성을 비교하고 있다. ([Waveshare][11])

다만 판매처와 키트 옵션에 따라 실제 서보 모델과 수량이 달라질 수 있으므로 구매 전 부품표를 확인해야 한다.

## 5.4 LeRobot 지원

SO-ARM101은 Hugging Face LeRobot의 대표적인 저비용 로봇팔 플랫폼이다.

LeRobot은 다음 기능을 제공한다.

* 로봇 하드웨어 제어
* 리더-팔로워 텔레오퍼레이션
* 카메라 영상 수집
* 관절 상태 기록
* 데이터셋 생성
* Hugging Face Hub 업로드
* 행동복제 모델 학습
* 사전학습 모델 활용
* 정책 추론 및 실제 로봇 실행

Hugging Face 공식 문서에서는 SO-101을 대표 로봇팔로 소개하며, 부품 구매, 3D 프린팅, 모터 설정, 조립, 캘리브레이션 절차를 제공한다. ([Hugging Face][12])

LeRobot은 PyTorch 기반의 실제 로봇 학습 프레임워크이며, 데이터셋, 사전학습 모델, 모방학습 및 강화학습 도구를 제공한다. ([Hugging Face][13])

## 5.5 제어 구조

```text
사람
 │
리더 암
 │ 관절 위치
 ▼
LeRobot 텔레오퍼레이션
 │
 ├─ 관절 명령
 │       ▼
 │   팔로워 암
 │
 ├─ 카메라 영상
 └─ 관절 상태
         │
         ▼
   LeRobot Dataset
         │
         ▼
     AI 정책 학습
         │
         ▼
  팔로워 암 자동제어
```

## 5.6 ROS2 지원 수준

SO-ARM101의 공식 중심 소프트웨어는 LeRobot이며, RoArm-M2나 M3처럼 제조사가 완성된 ROS2 Humble·MoveIt2 패키지를 중심으로 제공하는 제품은 아니다.

오픈소스 저장소에는 URDF 및 MuJoCo 모델이 존재하지만, ROS2 실물 제어를 위해서는 일반적으로 다음 작업이 추가로 필요하다.

* ROS2 패키지 생성
* URDF를 ROS2 패키지 구조로 정리
* 서보 드라이버 노드 개발
* JointState 발행
* JointTrajectory 수신
* ros2_control 하드웨어 인터페이스 구현
* MoveIt2 설정
* 관절 제한과 충돌 모델 보정

SO-101 공식 프로젝트 저장소에는 URDF와 MuJoCo 시뮬레이션 모델이 포함되어 있어 ROS2 확장의 기반으로 사용할 수 있다. 다만 일부 충돌 모델은 시뮬레이션 문제로 수정 또는 제거되었다고 설명되어 있어, MoveIt2 적용 시 검토가 필요하다. ([GitHub][14])

## 5.7 ROS2와 LeRobot을 함께 사용하는 구조

```text
                     ┌─ ROS2 MoveIt2
                     ├─ RViz2
SO-ARM101 Driver ────┼─ ros2_control
                     └─ LeRobot Bridge
                             │
                             ├─ 데이터 수집
                             ├─ 정책 학습
                             └─ AI 추론
```

ROS2와 LeRobot을 함께 사용하려면 관절 상태와 명령을 변환하는 브리지 노드를 작성할 수 있다.

```text
LeRobot 관절 명령
      ↓
ROS2 JointTrajectory
      ↓
ros2_control
      ↓
SO-ARM101 서보

SO-ARM101 관절 상태
      ↓
ROS2 JointState
      ↓
RViz2·MoveIt2·TF
```

## 5.8 교육 활용 분야

* 로봇 AI 입문
* 모방학습
* 행동복제
* 리더-팔로워 제어
* 데이터셋 수집
* 카메라 기반 로봇 행동 학습
* PyTorch 로봇 모델 학습
* VLA 모델 실험
* ROS2 하드웨어 인터페이스 개발
* URDF·MuJoCo 시뮬레이션

## 5.9 장점과 한계

### 장점

* 하드웨어와 프레임 설계가 오픈소스
* 3D 프린팅을 통한 부품 제작 가능
* 리더-팔로워 구조로 데이터 수집이 쉬움
* Hugging Face LeRobot 공식 지원
* AI 로봇팔 교육에 매우 적합
* 소프트웨어와 데이터셋 생태계가 빠르게 발전 중
* 사용자 목적에 따라 카메라와 프레임 변경 가능

### 한계

* 완제품보다 조립과 서보 설정 과정이 복잡함
* 키트별 부품 구성과 품질이 다를 수 있음
* ROS2와 MoveIt2가 기본 중심 생태계는 아님
* 리더·팔로워 두 대를 구성하면 비용이 증가함
* 서보 ID, 중심점, 방향 및 통신속도 설정이 필요함
* 학생 수가 많으면 조립·정비·캘리브레이션 관리가 어려움

## 5.10 참고 링크

* [Hugging Face SO-101 공식 문서](https://huggingface.co/docs/lerobot/so101)
* [Hugging Face SO-101 조립 문서](https://huggingface.co/docs/lerobot/main/en/assemble_so101)
* [SO-ARM100·SO-101 공식 오픈소스 저장소](https://github.com/TheRobotStudio/SO-ARM100)
* [Hugging Face LeRobot GitHub](https://github.com/huggingface/lerobot)
* [Hugging Face LeRobot 문서](https://huggingface.co/docs/lerobot/index)
* [Waveshare SO-ARM100·101 제품 페이지](https://www.waveshare.com/so-arm100-3dp-parts-kit.htm)
* [Waveshare SO-ARM100·101 Wiki](https://www.waveshare.com/wiki/SO-ARM100/101)
* [SO-ARM101 보정·원격제어 문서](https://www.waveshare.com/wiki/SO-ARM100/101_Robotic_Arm_Calibration_and_Remote_Control)

---

# 6. 세 제품의 소프트웨어 생태계 비교

## 6.1 RoArm 계열

```text
ESP32 펌웨어
    │
USB / Wi-Fi / UART
    │
RoArm Driver
    │
ROS2 Humble
 ├─ URDF
 ├─ TF
 ├─ RViz2
 ├─ MoveIt2
 └─ MoveIt Task Constructor
```

RoArm은 제품을 구입한 후 비교적 빠르게 ROS2 실습을 시작하는 데 적합하다.

## 6.2 SO-ARM101 계열

```text
버스 서보
    │
USB Driver Board
    │
LeRobot Python API
 ├─ 텔레오퍼레이션
 ├─ 카메라 데이터
 ├─ Dataset
 ├─ AI 모델 학습
 └─ 정책 추론
```

SO-ARM101은 로봇팔의 기구학이나 ROS2 제어보다는, 사람의 시범 데이터를 학습해 행동을 재현하는 로봇 AI 실습에 더 적합하다.

---

# 7. 스마트팩토리 교육 적용 비교

| 교육 주제     | RoArm-M2 | RoArm-M3 |    SO-ARM101 |
| --------- | -------: | -------: | -----------: |
| ROS2 기본   |    매우 적합 |    매우 적합 |     별도 개발 필요 |
| URDF·TF   |       적합 |    매우 적합 |           가능 |
| RViz2     |    공식 지원 |    공식 지원 |        별도 설정 |
| MoveIt2   |    공식 지원 |    공식 지원 |        별도 설정 |
| 기구학 교육    |       적합 |    매우 적합 |           적합 |
| 정밀 자세 제어  |      제한적 |    매우 적합 |           적합 |
| 컨베이어 연동   |       적합 |    매우 적합 |           가능 |
| Modbus 연동 |       적합 |       적합 |           가능 |
| OPC UA 연동 |       적합 |       적합 |           가능 |
| 카메라 검사    |       적합 |    매우 적합 |        매우 적합 |
| 모방학습      |    별도 구축 | 공식 확장 가능 |        매우 적합 |
| 학생 1인 지급  | 상대적으로 적합 |    비용 부담 | 키트 구성에 따라 가능 |
| 유지보수 편의   |       높음 |       중간 |           낮음 |
| 개발 자유도    |       중간 |       높음 |        매우 높음 |

---

# 8. 교육 목적별 권장 제품

## 8.1 ROS2 입문 및 학생 개인 실습

### 권장: RoArm-M2

선정 이유:

* 자유도가 단순해 처음 배우기 쉬움
* 제조사 ROS2 패키지가 준비되어 있음
* RViz2와 MoveIt2를 바로 사용할 수 있음
* M3보다 구매 비용과 관리 부담이 낮음
* ROS2·Modbus·SCADA 통합 실습에 충분함

적합한 과정:

> ROS2 기반 스마트팩토리 로봇팔 제어 입문

---

## 8.2 ROS2 고급 및 스마트팩토리 통합 프로젝트

### 권장: RoArm-M3

선정 이유:

* 손목 2DOF로 다양한 자세 구현 가능
* MoveIt2와 Pick-and-Place 교육에 유리
* 컨베이어, 비전 검사 및 공정 자동화 구현 가능
* ROS2에서 LeRobot으로 확장 가능
* 산업용 6축 로봇과 유사한 개념을 설명하기 좋음

적합한 과정:

> ROS2·AI 비전 기반 스마트팩토리 로봇팔 통합제어

---

## 8.3 AI 로봇·모방학습·VLA 교육

### 권장: SO-ARM101

선정 이유:

* LeRobot 공식 지원
* 리더-팔로워 데이터 수집 가능
* 행동복제 모델 학습 가능
* 카메라와 관절 데이터를 함께 기록 가능
* 하드웨어와 소프트웨어가 오픈소스
* 생성형 AI 이후의 Embodied AI 교육으로 확장 가능

적합한 과정:

> LeRobot 기반 로봇 모방학습과 AI 행동제어

---

# 9. 실제 교육 장비 구성 권고안

## 9.1 기본형 구성

학생 2인 1조 기준:

* RoArm-M2 1대
* Ubuntu 22.04 PC 1대
* USB 카메라 1대
* ArUco 마커
* 소형 부품 블록
* Modbus TCP I/O 또는 시뮬레이터
* ROS2 Humble
* MoveIt2
* 웹 SCADA

구현 프로젝트:

```text
Modbus 제품 감지
      ↓
ROS2 센서 노드
      ↓
USB 카메라 검사
      ↓
정상·불량 판정
      ↓
MoveIt2 경로계획
      ↓
RoArm-M2 분류 작업
      ↓
OPC UA·웹 SCADA 결과 표시
```

## 9.2 고급형 구성

4인 1조 기준:

* RoArm-M3 1대
* 카메라 2대
* 소형 컨베이어
* 광센서 또는 근접센서
* Modbus TCP I/O
* 산업용 PC 또는 Jetson
* ROS2 Humble
* MoveIt2
* LeRobot
* PostgreSQL
* OPC UA 서버

## 9.3 AI 연구형 구성

* SO-ARM101 리더 암 1대
* SO-ARM101 팔로워 암 1대
* 작업 공간 카메라 1~2대
* 손목 카메라 1대
* NVIDIA GPU PC 또는 Jetson
* Hugging Face LeRobot
* 데이터셋 저장 공간
* ROS2 브리지 패키지

---

# 10. 최종 결론

세 제품은 모두 교육용 로봇팔로 활용할 수 있지만 제품의 중심 목적이 다르다.

**RoArm-M2는 ROS2를 처음 배우는 학생에게 가장 적합하다.** 구조가 단순하고 제조사가 ROS2 Humble, RViz2, MoveIt2 튜토리얼을 제공하기 때문에 교육과정 도입이 쉽다.

**RoArm-M3는 스마트팩토리 로봇 셀과 고급 로봇팔 제어에 가장 적합하다.** 손목 자유도가 추가되어 물체의 위치뿐 아니라 방향까지 제어할 수 있고, ROS2와 MoveIt2뿐 아니라 LeRobot 기반 AI 실습으로 확장할 수 있다.

**SO-ARM101은 AI 로봇팔과 모방학습 교육에 가장 적합하다.** 다만 ROS2를 중심으로 수업하려면 별도의 드라이버와 ros2_control, MoveIt2 설정이 필요하다. 완제품형 ROS2 수업보다는 학생들이 직접 하드웨어 인터페이스를 개발하거나, LeRobot 데이터 수집과 행동학습을 수행하는 과정에 적합하다.

따라서 현재 계획 중인 **스마트팩토리 구현 소프트웨어 개발 과정에 ROS2를 추가하는 목적이라면 RoArm-M2 또는 RoArm-M3가 적절하다.**

* 예산과 수업 안정성 우선: **RoArm-M2**
* 고급 프로젝트와 자세 제어 우선: **RoArm-M3**
* 모방학습·Embodied AI 우선: **SO-ARM101**
* 가장 균형 잡힌 교육 운영안: **학생용 RoArm-M2 + 공용 RoArm-M3 또는 SO-ARM101**

[1]: https://www.waveshare.com/product/robotics/robot-arm-control/robot-arm.htm?utm_source=chatgpt.com "Robot Arm, Mechanical Grasper - Waveshare"
[2]: https://www.waveshare.com/roarm-m2-s.htm?utm_source=chatgpt.com "High-torque Serial Bus Servo, RoArm-M2 Desktop Robotic Arm Kit, Based On ESP32, 4-DOF"
[3]: https://github.com/waveshareteam/roarm_ws?utm_source=chatgpt.com "GitHub - waveshareteam/roarm_ws: Based On ESP32, High-torque Serial Bus Servo, RoArm ..."
[4]: https://www.waveshare.com/wiki/RoArm-M2-S_ROS2_Humble_%2B_Moveit2_Tutorial?utm_source=chatgpt.com "RoArm-M2-S ROS2 Humble + Moveit2 Tutorial - Waveshare Wiki"
[5]: https://www.waveshare.com/roarm-m3.htm?utm_source=chatgpt.com "5 + 1 DOF High-Torque Serial Bus Servo Robotic Arm Kit, Based On ESP32, 2-DOF Wrist ..."
[6]: https://www.waveshare.com/wiki/RoArm-M3_How_to_Install_ROS2?utm_source=chatgpt.com "RoArm-M3 How to Install ROS2 - Waveshare Wiki"
[7]: https://github.com/waveshareteam/roarm_ws/tree/ros2-humble/src/roarm_main/roarm_moveit/config/roarm_m3?utm_source=chatgpt.com "roarm_ws/src/roarm_main/roarm_moveit/config/roarm_m3 at ros2-humble · waveshareteam ..."
[8]: https://www.waveshare.com/wiki/RoArm-M3_Moveit_MTC_Demonstration?utm_source=chatgpt.com "RoArm-M3 Moveit MTC Demonstration - Waveshare Wiki"
[9]: https://www.waveshare.com/wiki/RoArm-M3-AI-Kit?utm_source=chatgpt.com "RoArm-M3-AI-Kit - Waveshare Wiki"
[10]: https://github.com/TheRobotStudio/SO-ARM100?utm_source=chatgpt.com "GitHub - TheRobotStudio/SO-ARM100: Standard Open Arm 100"
[11]: https://www.waveshare.com/wiki/SO-ARM100/101?utm_source=chatgpt.com "SO-ARM100/101 - Waveshare Wiki"
[12]: https://huggingface.co/docs/lerobot/so101?utm_source=chatgpt.com "LeRobot - SO-101 · Hugging Face"
[13]: https://huggingface.co/docs/lerobot/index?utm_source=chatgpt.com "LeRobot - Hugging Face"
[14]: https://github.com/TheRobotStudio/SO-ARM100/blob/main/Simulation/SO101/README.md?utm_source=chatgpt.com "SO-ARM100/Simulation/SO101/README.md at main - GitHub"
