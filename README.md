# Typing counter

<p align="center">
  <img src="./data/typecount.png" alt="Typing Count Screenshot">
</p>

매일 얼마나 많은 키를 입력하는지 기록하고 통계를 보여주는 타이핑 카운터입니다.

## 사용 방법

1.  **설치:** 먼저 터미널을 열고 다음 명령어를 입력하여 `typecount`를 설치합니다.

    <pre><code class="bash">
    uv venv
    uv pip install typecount
    </code></pre>

    이 명령어는 `typecount`를 여러분의 시스템에 다운로드하고 설치해 줍니다. 설치가 완료되면 다음 단계로 넘어갈 수 있습니다.

2.  **실행:** 설치가 완료되면 터미널에 다음 명령어를 입력하여 `typecount`를 실행합니다.

    <pre><code class="bash">
    uv run typecount
    </code></pre>

    이 명령어를 실행하면 타이핑 카운터가 백그라운드에서 작동하기 시작하며, 여러분이 입력하는 키의 횟수를 자동으로 기록합니다. 별도의 창이 뜨지 않을 수도 있습니다.

3.  **기록 확인:** 타이핑 횟수는 기본적으로 **날짜별**로 기록됩니다. 현재까지의 기록을 확인하고 싶다면, **`typecount`를 실행한 상태에서** 특정 단축키를 누르거나 (만약 있다면), 별도의 명령어를 터미널에 입력해야 할 수 있습니다. (아직 이 부분에 대한 구체적인 정보가 없으므로, 필요하다면 이 기능을 어떻게 활성화하는지 알려주세요.)

4.  **통계 확인 (구현 예정 또는 추가 설명 필요):** 단순히 횟수를 기록하는 것 외에, 일별, 주간, 월간 통계 또는 추이를 그래프로 확인하는 기능이 있다면 해당 방법을 설명해 주세요. 예를 들어, 특정 명령어를 입력하거나, 웹 인터페이스를 통해 확인할 수 있다면 자세한 안내가 필요합니다.

5.  **프로그램 종료:** `typecount`의 기록을 중단하고 싶다면, 실행 중인 프로세스를 종료해야 합니다.

**팁:**

* `typecount`를 실행해두면 컴퓨터를 사용하는 동안 자동으로 타이핑 횟수가 기록됩니다.
* 기록된 데이터는 특정 파일에 저장될 것이며, 필요하다면 해당 파일을 백업해두는 것이 좋습니다. (데이터 저장 위치에 대한 정보가 있다면 추가해 주세요.)
