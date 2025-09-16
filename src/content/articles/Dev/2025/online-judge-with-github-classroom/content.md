---
title: GitHub Classroom으로 온라인 저지 시스템 만들기
date: 2025-08-21
tags: algorithm, education
---

[GitHub Classroom](https://classroom.github.com/)이라는 서비스가 있습니다. [GitHub](https://github.com/)에서 제공하는 교육용 서비스인데, repository 단위로 과제를 출제하고, 학생들로 하여금 [git](https://git-scm.com/)을 기반으로 과제를 제출 할 수 있도록 해주는 서비스입니다. 이때 과제 채점을 [GitHub Action](https://github.com/features/actions)을 통해 진행할 수 있도록 시스템을 제공합니다.

이 서비스를 활용해서, 일반적인 온라인 저지 시스템을 한번 구축해봤습니다. 실제로 수업에서 사용할지는 아직 미지수입니다. 예전에 [Stepik](http://stepik.org/)을 사용해서 과제를 낸 적이 있었는데, 출제하기도 편하고 학생용 UI도 잘 되어있어서 잘 썼던 기억이 있습니다만, GitHub Classroom을 쓰게 되면 자연스럽게 repository 단위로 코드 관리를 하는것, 그리고 git 사용법을 익히게 되니까 교육적인 측면에서 한번 검토해봤습니다.

GitHub Classroom의 기본적인 구성 및 출제 흐름은 다음과 같습니다:

1. (반드시) Organization 단위에서, 여러개의 Classroom을 만들 수 있습니다.
2. 이 Classroom 단위에서, 또 여러개의 Assignment를 만들 수 있습니다.
3. 각 Assignment는 (거의 반드시) template repository로부터 복사된 starter code를 제공해야합니다. template과 starter code는 다르게 관리 할 일이 별로 없어서, 솔직히 항상 template을 따로 둬야하고 복사된 버전도 따로 둬야하는게 좀 번거롭기만 합니다.
4. 학생들은 starter code의 fork로써 Organization 소속의 repository를 각자 갖게 되고, 문제를 풀어서 코드를 제출하면 설정에 맞게 채점이 이뤄집니다. 이때 fork는 뒤에 학생 아이디가 postfix로 붙습니다.

요컨대, 다음과 같은 화면 구성으로 이뤄집니다:

![Classroom]({attach}classroom.jpg){width=720}

---

문제는, repository의 수입니다. 원본 template, 복사된 starter code, 그리고 학생별로 한개씩. 이렇게 $(n + 2)$개의 repository가 과제별로 생깁니다. 과제를 매주 주면 (14주 정도 되니까), 그리고 수업이 보통 한 학기에 2개씩이니까 (교수 기준) 학기당 repository가 $2 \times 14 \times (n + 2)$개씩 생깁니다. 학생이 30명만 되어도 900개쯤 됩니다. 이 시점에서 Classroom 전용 Organization 분리는 필수가 됩니다. Repository 수가 너무 많다보니 관리가 어렵고 (학생용 repository는 관리 대상이 아니지만) 헷갈리고 그렇습니다. 그래서 처음에는 과제 관리용 Organization과 학생 repository용 Organization을 분리하는 방식을 생각했었습니다. 그러나 이렇게 하면 private 채점 코드를 돌릴때 문제가 됩니다.

채점 얘기를 하자면, 기본적으로 제공하는 채점기가 몇개 있습니다. Standard I/O를 비교하는 가장 흔한 방식부터 [pytest](https://pytest.org/)를 돌려서 결과로 판단하는 방식까지 다양하게 있습니다. 그러나 이 채점은 어디까지나 GitHub Action이라서, **학생용 repository 내부에 스크립트가 들어가야합니다**. 즉, 채점 코드나 테스트 케이스를 숨길수가 없다는 뜻이죠. 다행히 fork된 repository에서 특정 파일들을 바꾸지 못하게끔 하는 옵션은 있습니다.

저는 채점 코드를 숨기고 싶었기 때문에, private으로 채점 코드 repository를 과제 관리용 Organization에 만들고, 이를 학생용 Action에서 (비밀리에) checkout해서 채점을 돌리는 방식을 하려고 했습니다. 그런데 이때 Organization이 다르다보니, private repository의 접근 권한을 주기 위해서는 Personal Access Token (PAT)을 모든 학생용 repository에 발급해줘야해습니다. PAT는 starter code repository에 넣어놔도 fork할때 복사되지 않고, Organization 단위의 secret은 유료 플랜에서만 제공하는 기능이기 때문에, 결국 Organization을 분리하는건 포기했습니다.

그런데 같은 Organization 내에서라도, private repository에 접근하려면 여전히 PAT는 필요합니다. 대신, Organization에서 배포한 Action이라면 private이라도 사용이 가능합니다! **단, 설정을 별도로 해줘야하고, private repo에서만 사용이 가능합니다**. 여하튼, 저는 이 점을 이용해서 본격적으로 채점기를 만들기 시작했습니다.

---

Repository들의 구성은 아래와 같습니다. 예시 코드를 공유드립니다. 원래는 모두 private이어야 합니다.

* [general-grader](https://github.com/DKU-IRDM-Classroom/general-cstdio-grader): 범용 채점기 (private)
* [Assignment-Template](https://github.com/DKU-IRDM-Classroom/Test-Classroom-Test-Assignment-C): 과제 템플릿 (private)
* `Assignment-Grader`: 과제 전용 채점기 (private)
* [Assignment](https://github.com/DKU-IRDM-Classroom/Test-Classroom-Test-Assignment-C-Starter): 과제 템플릿에서 복사된 starter code (private)
* `Assignment-student`: starter code에서 fork된 학생 과제용 repository (private이지만 각 학생은 자기 repository에 접근이 가능)

---

##### 과제 예시

과제는 예시로 두 숫자를 입력받아서 합을 출력하는 프로그램을 C로 구현하는게 목표라고 합시다.

**입력 예시:**

    :::text
    1 1

**출력 예시:**

    :::text
    2

---

##### Assigment-student

학생이 문제를 풀어서 commit을 하면, 가장 먼저 `Assignment-student`에 있던 Action을 발동시킵니다:

    :::yaml
    jobs:
      grade:
        runs-on: ubuntu-latest
        if: github.actor != 'github-classroom[bot]'
        steps:
          - name: 코드 체크아웃
            uses: actions/checkout@v4
          - name: 과제 전용 채점기 실행
            uses: Organization/Assignment-Grader@v1

위 Action에서는 `Assignment-Grader` Action을 불러오는게 전부입니다. 앞서 말했듯, private Action이지만 같은 Organization 내에 있기 때문에 코드를 볼 수는 없어도 사용은 가능합니다.

---

##### Assigment-Grader

`Assignment-Grader`에서는 두가지 파일, `generate.py`와 `solve.py`를 반드시 구현하도록 합니다. 이 방식은 Stepik에서 차용했습니다.

`generate.py`:

    :::python
    import random

    def generate(case_number):
        lines_in = []
        if case_number == 1:
            n = 1
            m = 1
            lines_in.append([n, m])
        else:
            n = random.randint(1, 1000)
            m = random.randint(1, 1000)
            lines_in.append([n, m])
        return lines_in

`solve.py`:

    :::python
    def solve(lines_in):
        n, m = lines_in[0]
        return [[n + m]]

이 파일들은 `general-grader`에서 사용될 예정입니다. 이렇게 해두면 코드의 integrity는 좀 떨어지지만, 과제마다 `Assignment-Grader`를 매번 구현해야하는데, 그 수고를 좀 줄일 수 있습니다. 어차피 다 비슷비슷하니까 공통된 부분을 `general-grader`한테 넘기는 것입니다.

`Assignment-Grader`의 Action은 아래와 같이 `general-grader` Action을 불러오는게 전부입니다. 이때 과제마다 지정된 제한 사항들을 옵션으로 줍니다:

    :::yaml
    - name: 범용 채점기 실행
      uses: Organization/general-grader@v1
      with:
        module-path: ${{ github.action_path }}
        total-cases: 5
        time-limit: 2
        memory-limit: 256m
        output-limit: 1048576

넘길때는 `Assignment-Grader`의 Python 파일들을 직접 사용 할 수 있도록, `action_path`를 `module-path`라는 파라미터로 같이 넘깁니다. 이제 대망의 `general-grader`입니다.

---

##### general-grader

`general-grader` 내부에는 우선 두 파일의 토큰을 비교해서 exit code로 내뱉는 [compare.py](https://github.com/DKU-IRDM-Classroom/general-cstdio-grader/blob/main/compare.py)라는 스크립트가 있습니다. exit code는 0이 정답, 1이 오답, 그리고 2가 형식 오류라고 해둡시다. 3은 혹시 모를 내부 오류입니다.

그리고 `Assignment-Grader`에서 만들어둔 `generate.py`와 `solve.py`를 사용해서 실제로 테스트 케이스를 생성하는 [generate_cases.py](https://github.com/DKU-IRDM-Classroom/general-cstdio-grader/blob/main/generate_cases.py)가 있습니다. 이 모듈을 활용하기 위해, Action에서 파라미터로 넘겨받은 `module-path`를 경로에 추가해줘야합니다:

    :::yaml
    - name: 케이스 생성
      shell: bash
      env:
        PYTHONPATH: "${{ inputs.module-path }}:${PYTHONPATH}"
      run: |
        python3 "${{ github.action_path }}/generate_cases.py

그럼 이제 테스트 케이스 생성기, 그리고 실제 결과를 보고 채점을 해주는 채점기가 준비되었습니다. 이것들을 실행시켜줄 Action을 구현해봅시다.

시행착오 끝에, 임시용 777 폴더를 만드는게 편했습니다:

    :::yaml
    - name: 채점기 준비
      shell: bash
      run: |
        mkdir -p "$HOME/workdir"
        chmod 777 "$HOME/workdir"

그다음은 우선 빌드를 합니다. 빌드가 안되면 바로 0점 처리를 해야하니까요. 우선 `main.c`가 무조건 있어야한다고 합시다:

    :::yaml
    - name: 빌드 준비
      shell: bash
      run: |
        if [ ! -f ./main.c ]; then
          echo "형식 오류 (PE): main.c 파일 없음"
          echo "::notice::점수 0/${{ inputs.total-cases }}"
          echo "::notice title=Autograding report::{\"totalPoints\":0,\"maxPoints\":${{ inputs.total-cases }}}"
          exit 2
        fi

여기서 아주 중요한게 나옵니다!!! 이것을 알아내기가 정말 어려웠는데... GitHub Classroom은 사실 지금 관리가 잘 되고 있는 서비스는 아닌것 같습니다. 제대로된 스펙이 모두 나와있는 문서가 없거든요...

위 step에서 아래 부분이 중요합니다:

    :::bash
    echo "::notice title=Autograding report::{\"totalPoints\":0,\"maxPoints\":5}"

이 부분이 있어야만 GitHub Classroom에서 점수를 인식합니다! 이 부분이라 하면, 저 json 부분과 notice의 title까지가 중요합니다. title이 반드시 "Autograding report"로 되어있어야합니다... 이게... 그 어디에도 적혀있지 않아서 [사람들끼리 추론을 하다가 말았습니다](https://github.com/orgs/community/discussions/77361). 이게 없으면 점수가 나오질 않습니다:

![Points]({attach}points.jpg){width=480}

보통은 GitHub Classroom측에서 제공하는 [공식 채점기](https://github.com/classroom-resources)를 쓰거나 [공식 채점 결과 리포터](https://github.com/classroom-resources/autograding-grading-reporter)를 쓰면 알아서 되긴 하는데, 이러면 커스텀의 영역이 굉장히 제한됩니다. 그래서 어떻게든 스펙을 알아내고 싶었고... 이 부분에서 아주 많은 시간을 소비하게 되었습니다...

암튼... 그런 일이 있었으며... 이어서 빌드를 해봅시다. 빌드 또한 Docker로 감싸주는게 좋긴 한데, 그러면 매번 gcc 이미지를 다운 받게되고, 등등의 과정을 거치다보면 채점이 너무 오래 걸려서 결국 GitHub Action 자체 내장되어있는 gcc를 쓰기로 결정했습니다. 빌드 과정에서 뭔가 큰일이 나진 않겠죠 설마:

    :::yaml
    - name: 빌드
      shell: bash
      run: |
        cp ./main.c "$HOME/workdir/"
        if gcc -O2 -std=c17 -o "$HOME/workdir/main" main.c >/dev/null 2>/tmp/gcc.err; then
          exit 0
        else
          echo "컴파일 오류 (CE)"
          echo "::notice::점수 0/${{ inputs.total-cases }}"
          echo "::notice title=Autograding report::{\"totalPoints\":0,\"maxPoints\":${{ inputs.total-cases }}}"
          exit 2
        fi

빌드까지 끝나면, 이제 드디어 테스트 케이스들을 생성해줍니다. 이건 위에 미리 써둔 step에 해당합니다. 케이스 생성기는 우리의 작업 폴더인 `$HOME/workdir` 안에 `1.in`, `1.ans`, `2.in`, `2.ans`와 같은 텍스트 파일들을 만들어 준다고 칩시다. 이 파일들을 이용해서 드디어 대망의 학생 코드를 실행하게 됩니다.

    :::yaml
    - name: 채점
      shell: bash
      run: |
        set -euo pipefail
        docker pull -q ubuntu:latest >/dev/null
        docker run --rm ubuntu:latest bash -lc 'echo "grader ready"'

        (아래에서 이어서...)

학생 코드는 위험하니까 Docker로 감쌀텐데, GitHub Action에는 몇가지 캐싱 되어있는 이미지가 있습니다. `ubuntu:latest`도 그 중 하나라서, 이것을 pull하는건 무척 빠르게 잘 됩니다. pull 하자마자 한번 실행을 해주는데, 이게 없으면 왠지 가끔씩 학생 코드가 시간 초과에 걸리게 됩니다. 그래서 약간 캐시 warm-up 한다는 느낌으로 추가해봤고, 안정적으로 잘 됩니다.

학생 코드 실행에는 많은 일들이 일어나야합니다. 요약하자면:

1. 네트워크라던가 등등의 사용 제한을 가능한 전부 걸어야합니다.
2. 메모리 초과를 잡을 수 있어야합니다.
3. 시간 초과를 잡을 수 있어야합니다.

그래서 아주아주 길고 긴 `docker run`이 탄생합니다 (위 step 내 run에서 이어집니다):

    :::bash
    PASS=0
    for n in $(seq 1 ${{ inputs.total-cases }}); do
      NAME="grader-${n}-$$"
      set +e
      docker run \
        --name "$NAME" \
        --network none \
        --cpus "1.0" \
        --memory "${{ inputs.memory-limit }}" \
        --memory-swap "${{ inputs.memory-limit }}" \
        --pids-limit "128" \
        --cap-drop ALL \
        --security-opt no-new-privileges \
        --tmpfs /tmp:rw,nosuid,nodev,noexec,size=64m \
        -u "$(id -u):$(id -g)" \
        -v "$HOME/workdir":/workdir \
        -w /workdir \
        -e n="$n" \
        ubuntu:latest \
        bash -lc 'timeout -k 1s ${{ inputs.time-limit }}s /workdir/main < "/workdir/${n}.in" > "/workdir/${n}.out"' 2>/dev/null
      RC=$?
      set -e

학생 코드와 정답들이 들어있는 `$HOME/workdir`은 volume으로 bind해줬습니다. 그리고 실제 실행 할 때는 `timeout`을 걸어서 시간 제한을 뒀구요. Docker는 container 자체에 메모리 제한을 걸 수 있어서 그 기능도 사용했습니다. 다만 이게 이제 kill 되면 시간 초과인지 메모리 초과인지 애매할때가 있습니다. 그것을 container를 실제로 살펴보는 것으로 구분짓기 위해 이름(`--name`)도 지정을 해줍니다. `OOMKilled`라는 State로 확인이 가능합니다:

    :::bash
    OOM=false
    EXIT=0
    if docker inspect "$NAME" >/dev/null 2>&1; then
      OOM=$(docker inspect -f '{{.State.OOMKilled}}' "$NAME")
      EXIT=$(docker inspect -f '{{.State.ExitCode}}' "$NAME")
    fi
    docker rm -f "$NAME" >/dev/null 2>&1 || true

여기까지 했으면, 나머지는 단순하게 경우에 따라서 에러 종류만 if문으로 잘 나눠주면 됩니다. 사실 위에 있는 `docker run` 단 한(?) 줄이 거의 모든 일을 다 해주는것이었죠. 시간 초과는 exit code가 124입니다 (137일때가 있는데, 없어야합니다(?)):

    :::bash
    if [ "$OOM" = "true" ]; then
      echo "[Case ${n}] 메모리 초과 (MLE)"
      continue
    elif [ "$EXIT" -eq 124 ]; then
      echo "[Case ${n}] 시간 초과 (TLE)"
      continue
    elif [ ${RC} -ne 0 ] || [ ${EXIT} -ne 0 ]; then
      echo "[Case ${n}] 실행 오류 (RE)"
      continue
    fi
    BYTES=$(stat -c%s "$HOME/workdir/${n}.out")
    if [ "$BYTES" -gt ${{ inputs.output-limit }} ]; then
      echo "[Case ${n}] 출력 초과 (OLE)"
      continue
    fi

continue가 있는건 아직 `${n}`에 대한 for문 안에서 일어나는 일이기 때문입니다. 아무튼, 여기까지가 학생 코드 실행이었고, 이제 결과물을 놓고 정답과 비교하는 일만 남았습니다:

    :::bash
    set +e
    python3 \
      "${{ github.action_path }}/compare.py" \
      "$HOME/workdir/${n}.ans" \
      "$HOME/workdir/${n}.out"
    CMP=$?
    set -e
    if [ $CMP -eq 0 ]; then
      echo "[Case ${n}] 정답 (AC)"
      PASS=$((PASS+1))
    elif [ $CMP -eq 1 ]; then
      echo "[Case ${n}] 오답 (WA)"
    elif [ $CMP -eq 2 ]; then
      echo "[Case ${n}] 형식 오류 (PE)"
    else
      echo "[Case ${n}] 내부 오류 (IE)"
    fi

그럼 이제 채점이 모두 종료되고, 마지막으로 점수를 정확히 전달해줘야합니다. 위에서 언급했듯, 무엇보다도 notice의 title이 중요합니다!

    :::bash
    echo "::notice::점수 ${PASS}/${{ inputs.total-cases }}"
    echo "::notice title=Autograding report::{\"totalPoints\":${PASS},\"maxPoints\":${{ inputs.total-cases }}}"

이렇게 하면 채점기 구현이 완료가 됩니다. AC, WA, PE, IE, OLE, RE, TLE, MLE까지. 거의 대부분의 온라인 저지 시스템에서 사용하는 채점 결과들을 모두 구현한 셈입니다. 실제 Action에서는 아래와 같이 출력이 됩니다:

![Result]({attach}result.jpg){width=480}

전체 코드 예시는 [DKU-IRDM-Classroom/general-cstdio-grader](https://github.com/DKU-IRDM-Classroom/general-cstdio-grader)에서 살펴볼 수 있습니다.

---

##### 결론

요컨대, 그다지 추천드리지 않습니다. 아래와 같이 요약이 됩니다:

1. 전용 Organization을 따로 만들어야합니다 아무래도.
2. Repository 수가 기하급수적으로 늘어납니다.
3. Action을 계속 돌리는건 100% 무료는 아닙니다.
4. 과제 출제 과정이 불편합니다.

여기서 사실 4번이 제일 큰 문제입니다. Stepik 같은 사이트에서는 아주 편리한 웹 UI를 제공하고 있어서, 전체적으로 온라인 강의 플랫폼 내에 온라인 저지가 있다는 느낌을 줍니다. 그런데 GitHub Classroom에서는 다 repository 단위로만 이뤄지다보니, 통일감 있는건 좋긴 한데, 과제를 자주 (매주?) 출제하거나 연습용 실습들을 잔뜩 만들고 싶을때는 좀 부적합한것 같습니다. 반대로, 큰 규모의 프로젝트를 잘게 쪼개서 과제로 출제할때는 또 적합하게 잘 사용될수도 있을것 같습니다.

저는 이렇게 잘 만들어두긴 했는데, 아마 C언어 수업에서는 사용을 안할것 같습니다. 다른 과목(네트워크 등)에서는 pytest 같은것을 기반으로 사용할것 같은데, 그럴거였다면 이런 온라인 저지 시스템을 만들 필요가 없었는데... 검토 해봤다는 부분에서 일단 만족합니다. 다시 말하지만, 저 point를 인식하는 부분을 알아내는데 가장 많은 시간을 사용했습니다.

아래는 이 시스템을 구현하고 있는 저의 모습(?)입니다:

![Result]({attach}hm.jpg){width=240}
