# FQ
## 구성

![00](https://i.imgur.com/Ub8kEU0.png)

- `Sender`/`Queue`/`Receiver`로 구성

## 실행

`Sender`와`Queue`는 실행 순서에 상관 없지만 `Receiver`는 `Queue`가 실행된 상태에서 실행해야한다.

### config 작성

프로젝트의 root path에 `.fq` 파일 작성

```
FQ_HOST=localhost
FQ_SUB_PORT=50000
FQ_REP_PORT=50001
```

- `FQ_HOST` : `Queue`가 구동 중인 노드의 호스트
- `FQ_SUB_PORT` : 프레임을 수신하는 `Queue`의 포트. Sender에서 사용
- `FQ_REP_PORT` : 요청을 처리하는 `Queue`의 포트. Receiver에서 사용

### Sender

`fq send` 명령어로 실행

```bash
$ fq send --src="/path/to/video.mp4"

# 다수의 비디오를 전송할 경우
$ fq send --src="/path/to/video1.mp4,/path/to/video1.mp4,/path/to/video1.mp4"
```

- `src` : 1개 이상의 비디오 경로. 2개 이상일 경우 쉼표로 구분해서 입력

### FQueue

`fq queue` 명령어로 실행

```bash
$ fq queue
```

```bash
Queue...

/path/to/video1.mp4(569frames): 00:00:00.000(0) ~ 00:00:18.952(568)
/path/to/video2.mp4(569frames): 00:00:00.000(0) ~ 00:00:18.919(567)
```

실행하면 각 비디오의 프레임이 전달되는 현황을 확인할 수 있다.

### Receiver

`FQueue`에 저장된 프레임을 가져온다.

```python
import FQ.FrameReceiver


video_src = "/path/to/video.mp4" # 가져올 비디오
start = "00:04:40" # 프레임 시작 시간
end = "00:04:45" # 프레임 종료 시간
fps = 1 # 프레임 fps
for (frame, frame_num, time) in FrameReceiver(video_src=video_src, start_time=start, end_time=end, fps=fps):
	# do something..
```