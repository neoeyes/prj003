# README.md

## 파일명 일괄 변경 프로그램

이 프로그램은 파일 탐색기에서 선택한 파일들의 이름을 일괄적으로 변경하는 데 도움을 줍니다. 직관적인 사용자 인터페이스를 통해 파일 목록을 관리하고, 사용자 정의 패턴을 적용하여 새로운 파일명을 손쉽게 생성할 수 있습니다. 특히, 숫자 시퀀스([00], [03,04,06] 등)와 파일 확장자([확장자])를 자동으로 적용하는 고급 기능을 제공합니다.

### 주요 기능

* **파일 선택 및 그리드 표시:**
    * **"파일 선택"** 버튼을 클릭하여 파일 탐색기에서 변경할 파일을 선택합니다.
    * 선택된 파일들은 프로그램 내 그리드에 **순서**와 **파일명**과 함께 표시됩니다.
    * 파일 경로 및 파일명은 내부적으로 배열에 저장됩니다.

* **파일 순서 변경:**
    * 그리드에 나열된 파일의 순서를 **마우스 드래그 앤 드롭**으로 자유롭게 변경할 수 있습니다.
    * 키보드 단축키 **`Ctrl + Up Arrow`** 및 **`Ctrl + Down Arrow`**를 사용하여 포커스된 파일의 순서를 위아래로 조절할 수도 있습니다.
    * **여러 파일 순서 변경:** 스페이스바로 여러 파일을 선택(하이라이트)한 후 `Ctrl + Up Arrow` 또는 `Ctrl + Down Arrow`를 누르면 선택된 파일 묶음이 함께 이동합니다.

* **새 파일명 규칙 설정:**
    * **"새로운 파일명 규칙 설정"** 필드에 원하는 파일명 패턴을 입력합니다.
    * **패턴 예시:**
        * `새로운파일.S01E[00].[확장자]`
        * `사진.[03].jpg`
        * `영상.part_[03,04,06].[확장자]`
    * **`[00]`**: 파일 순서에 따라 `01`, `02`, `03`...과 같이 두 자리 숫자가 적용됩니다. (0부터 시작하는 인덱스 + 00 패턴의 시작 숫자)
    * **`[03]`**: 파일 순서에 따라 `03`, `04`, `05`...와 같이 두 자리 숫자가 적용됩니다. (0부터 시작하는 인덱스 + 03 패턴의 시작 숫자)
    * **`[03,04,06]`**: 지정된 순서의 숫자가 먼저 적용되며, 지정된 숫자를 넘어선 파일은 마지막 지정 숫자 이후부터 순차적으로 증가합니다.
    * **`[확장자]`**: 원본 파일의 확장자(예: `mp4`, `jpg`)가 자동으로 삽입됩니다. 확장자는 소문자로 통일됩니다.

* **미리보기 및 일괄 변경:**
    * **"미리보기"** 버튼을 클릭하여 설정한 규칙이 실제 파일명에 어떻게 적용될지 미리 확인할 수 있습니다.
    * 미리보기 결과를 확인한 후, **"일괄 변경 실행"** 버튼을 클릭하여 실제 파일명 변경을 수행합니다. 이 작업은 되돌릴 수 없으므로 신중하게 진행해야 합니다.

* **그리드 상호작용 개선:**
    * **`Spacebar`로 선택/해제:** 그리드의 특정 행에 포커스(커서)가 있을 때 `Spacebar`를 누르면 해당 행이 선택되거나 선택 해제됩니다. 선택된 행은 **Light Yellow** 배경색으로 하이라이트됩니다. 이는 여러 파일을 한 번에 이동할 때 유용합니다.
    * **`Enter` 키로 선택 종료:** `Spacebar`로 선택된 모든 항목을 한 번에 해제하려면 `Enter` 키를 누릅니다.
    * **그리드 행 커서 색상:** 현재 그리드에서 포커스(커서)가 있는 행의 배경색은 **White Gray**로 변경되어 현재 작업 중인 파일을 쉽게 식별할 수 있습니다.
