# bulk_rename_gui_advanced_number_pattern.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re # 정규표현식 모듈 import

class BulkRenameApp:
    def __init__(self, master):
        self.master = master
        master.title("파일명 일괄 변경 프로그램")
        master.geometry("800x600")

        self.file_paths = [] # 선택된 파일들의 전체 경로를 저장할 리스트
        self.file_data = []  # 그리드에 표시될 {원본 파일명, 경로, selected_for_move} 딕셔너리 리스트

        # --- UI 구성 ---

        # 1. 파일 선택 및 표시 영역
        self.frame_file_selection = tk.LabelFrame(master, text="1. 파일 선택 및 목록")
        self.frame_file_selection.pack(pady=10, padx=10, fill="both", expand=True)

        self.btn_select_files = tk.Button(self.frame_file_selection, text="파일 선택", command=self.select_files)
        self.btn_select_files.pack(pady=5)

        # 파일 목록을 표시할 Treeview (그리드 역할)
        self.tree = ttk.Treeview(self.frame_file_selection, columns=("order", "filename", "selected"), show="headings")
        self.tree.heading("order", text="순서", anchor=tk.CENTER)
        self.tree.heading("filename", text="파일명", anchor=tk.W)
        self.tree.heading("selected", text="선택", anchor=tk.CENTER) # 선택 여부 표시
        self.tree.column("order", width=50, stretch=tk.NO, anchor=tk.CENTER)
        self.tree.column("filename", width=400, stretch=tk.YES)
        self.tree.column("selected", width=50, stretch=tk.NO, anchor=tk.CENTER) # 체크박스 너비
        self.tree.pack(pady=5, fill="both", expand=True)

        # Treeview 스크롤바 추가
        self.scrollbar_y = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)

        # 그리드 순서 변경 이벤트 바인딩 (마우스 드래그)
        self.tree.bind("<Button-1>", self.on_tree_click)
        self.tree.bind("<B1-Motion>", self.on_tree_drag)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_release)

        # 그리드 순서 변경 이벤트 바인딩 (화살표 Up/Down)
        self.tree.bind("<Up>", self.move_item_up)
        self.tree.bind("<Down>", self.move_item_down)
        
        # Spacebar로 선택/선택 해제 토글
        self.tree.bind("<space>", self.toggle_selection)
        
        # Enter 키로 선택 종료
        self.tree.bind("<Return>", self.deselect_all)

        # 포커스 변경 시 색상 업데이트를 위한 이벤트 바인딩
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_selection_change)


        # 2. 파일명 규칙 설정 영역
        self.frame_rename_rule = tk.LabelFrame(master, text="2. 새로운 파일명 규칙 설정")
        self.frame_rename_rule.pack(pady=10, padx=10, fill="x")

        # 패턴 예시 텍스트 업데이트
        self.lbl_rule_example = tk.Label(self.frame_rename_rule, text="패턴 예시: [00], [03], [03,04,06], [확장자]")
        self.lbl_rule_example.pack(pady=5, anchor=tk.W)

        self.entry_rename_pattern = tk.Entry(self.frame_rename_rule)
        self.entry_rename_pattern.insert(0, "새로운파일.S01E[00].[확장자]") # 기본 패턴 제공
        self.entry_rename_pattern.pack(pady=5, fill="x")

        # 3. 미리보기 및 실행 버튼 영역
        self.frame_actions = tk.Frame(master)
        self.frame_actions.pack(pady=10, padx=10, fill="x")

        self.btn_preview = tk.Button(self.frame_actions, text="미리보기", command=self.preview_rename)
        self.btn_preview.pack(side="left", padx=5)

        self.btn_rename = tk.Button(self.frame_actions, text="일괄 변경 실행", command=self.execute_rename, state=tk.DISABLED)
        self.btn_rename.pack(side="right", padx=5)

        # 미리보기 결과를 표시할 텍스트 영역
        self.preview_text = tk.Text(master, height=10, state=tk.DISABLED)
        self.preview_text.pack(pady=10, padx=10, fill="both", expand=True)

        self.dragging_item = None # 드래그 중인 아이템 ID 저장
        self.drag_start_y = 0     # 드래그 시작 시 마우스 Y 좌표
        self.drag_offset_y = 0    # 드래그 중 아이템 위치 보정
        self.selected_for_move = [] # 스페이스바로 선택된 아이템의 인덱스 리스트 (단일 포커스와 구분)

        # Treeview 스타일 설정
        style = ttk.Style()
        # 기본 선택된 행 (포커스) 스타일: White Gray
        style.map('Treeview',
                  background=[('selected', 'light gray')], # Treeview 기본 'selected'는 포커스된 항목
                  foreground=[('selected', 'black')])
        
        # 'selected_for_move' 태그 스타일: Light Yellow
        self.tree.tag_configure('selected_for_move_tag', background='light yellow', foreground='black')


    def select_files(self):
        """
        파일 탐색기를 열어 파일을 선택하고, 선택된 파일들을 그리드에 표시합니다.
        """
        # 로그: 파일 선택 대화 상자 열기
        print("로그: 파일 선택 대화 상자 열기...")
        selected_files = filedialog.askopenfilenames(
            title="파일 선택",
            filetypes=(("모든 파일", "*.*"), ("비디오 파일", "*.mp4;*.mov;*.avi"), ("문서 파일", "*.txt;*.docx"))
        )

        if not selected_files:
            print("로그: 파일 선택 취소됨.")
            return

        self.file_paths = list(selected_files)
        self.file_data = [] # 기존 데이터 초기화
        self.selected_for_move = [] # 선택된 항목 초기화

        # 기존 Treeview 아이템 모두 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, path in enumerate(self.file_paths):
            filename = os.path.basename(path)
            # 순서와 파일명, 선택 여부 ('')를 그리드에 추가
            self.tree.insert("", "end", iid=str(i), values=(i + 1, filename, ''))
            # file_data에 'selected_for_move' 상태 추가
            self.file_data.append({"original_path": path, "filename": filename, "selected_for_move": False})

        print(f"로그: {len(self.file_paths)}개의 파일이 선택되었습니다.")
        self.btn_rename.config(state=tk.DISABLED) # 미리보기 후 활성화
        self.update_tree_view() # 초기 뷰 업데이트

    def update_tree_view(self):
        """현재 self.file_data를 기반으로 Treeview를 업데이트합니다."""
        focused_item_id = self.tree.focus() # 현재 포커스된 아이템 ID 저장
        
        # 기존 Treeview 아이템 모두 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, data in enumerate(self.file_data):
            # '✔' 또는 ''로 선택 여부 표시
            selection_marker = "✔" if data["selected_for_move"] else ""
            
            # 태그 초기화 및 재설정
            tags = ()
            if data["selected_for_move"]:
                tags = ('selected_for_move_tag',) # 스페이스바로 선택된 항목 태그

            self.tree.insert("", "end", iid=str(i), values=(i + 1, data["filename"], selection_marker), tags=tags)
        
        # 포커스된 아이템이 여전히 유효하다면 다시 포커스 설정
        if focused_item_id and focused_item_id in self.tree.get_children():
            self.tree.focus(focused_item_id)
            self.tree.selection_set(focused_item_id) # 선택도 유지 (Treeview의 기본 선택 스타일)
        elif self.file_data: # 파일이 있다면 첫 번째 항목에 포커스
            self.tree.focus(str(0))
            self.tree.selection_set(str(0))
        
        # 포커스 변경 시 색상을 업데이트하기 위해 트리거
        self.on_tree_selection_change(None)

    def on_tree_selection_change(self, event):
        """Treeview의 선택(포커스)이 변경될 때 호출되어 색상을 업데이트합니다."""
        # 모든 항목의 태그를 재설정하여 색상 업데이트를 강제
        # (Treeview의 기본 'selected' 스타일과 커스텀 태그가 충돌하지 않도록 관리)
        for i, data in enumerate(self.file_data):
            item_id = str(i)
            # Treeview의 'selected' 상태는 Treeview 자체적으로 관리
            # 여기서는 커스텀 태그인 'selected_for_move_tag'만 관리
            current_tags = list(self.tree.item(item_id, 'tags'))
            
            if data["selected_for_move"]:
                if 'selected_for_move_tag' not in current_tags:
                    current_tags.append('selected_for_move_tag')
            else:
                if 'selected_for_move_tag' in current_tags:
                    current_tags.remove('selected_for_move_tag')
            
            self.tree.item(item_id, tags=tuple(current_tags))

    def toggle_selection(self, event):
        """스페이스바를 눌러 파일 선택/해제 및 하이라이팅"""
        focused_item_id = self.tree.focus()
        if not focused_item_id:
            return

        current_idx = int(focused_item_id)
        if 0 <= current_idx < len(self.file_data):
            # 선택 상태 토글
            self.file_data[current_idx]["selected_for_move"] = not self.file_data[current_idx]["selected_for_move"]
            
            # selected_for_move 리스트 업데이트
            if self.file_data[current_idx]["selected_for_move"] and current_idx not in self.selected_for_move:
                self.selected_for_move.append(current_idx)
                self.selected_for_move.sort() # 순서 유지
            elif not self.file_data[current_idx]["selected_for_move"] and current_idx in self.selected_for_move:
                self.selected_for_move.remove(current_idx)

            print(f"로그: {self.file_data[current_idx]['filename']} 파일 선택 상태 토글: {'선택됨' if self.file_data[current_idx]['selected_for_move'] else '해제됨'}")
            
            # Treeview의 값 업데이트 및 태그 재설정
            selection_marker = "✔" if self.file_data[current_idx]["selected_for_move"] else ""
            self.tree.set(focused_item_id, "selected", selection_marker)
            
            tags = list(self.tree.item(focused_item_id, 'tags'))
            if self.file_data[current_idx]["selected_for_move"]:
                if 'selected_for_move_tag' not in tags:
                    tags.append('selected_for_move_tag')
            else:
                if 'selected_for_move_tag' in tags:
                    tags.remove('selected_for_move_tag')
            self.tree.item(focused_item_id, tags=tuple(tags))
            
            self.btn_rename.config(state=tk.DISABLED)

    def deselect_all(self, event):
        """Enter 키를 눌러 스페이스바로 선택된 모든 항목을 해제합니다."""
        if not self.selected_for_move:
            print("로그: 선택된 항목이 없습니다.")
            return

        for idx in self.selected_for_move:
            if 0 <= idx < len(self.file_data):
                self.file_data[idx]["selected_for_move"] = False
                item_id = str(idx)
                self.tree.set(item_id, "selected", "") # '✔' 제거
                
                tags = list(self.tree.item(item_id, 'tags'))
                if 'selected_for_move_tag' in tags:
                    tags.remove('selected_for_move_tag')
                self.tree.item(item_id, tags=tuple(tags))

        self.selected_for_move = [] # 선택된 리스트 초기화
        print("로그: 모든 파일 선택이 해제되었습니다.")
        self.btn_rename.config(state=tk.DISABLED)
        # Treeview의 포커스된 행 색상 유지를 위해 업데이트 트리거
        self.on_tree_selection_change(None)


    def on_tree_click(self, event):
        """마우스 클릭 시 드래그 시작 지점 설정"""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.dragging_item = row_id
            self.drag_start_y = event.y
            bbox = self.tree.bbox(row_id)
            if bbox:
                self.drag_offset_y = event.y - bbox[1]

    def on_tree_drag(self, event):
        """마우스 드래그 중 아이템 위치 이동 (시각적 효과 없음)"""
        pass # 실제 Treeview 아이템의 시각적 이동은 복잡하므로, 여기서는 데이터만 처리

    def on_tree_release(self, event):
        """마우스 버튼 떼었을 때 드래그 종료 및 아이템 순서 변경"""
        if self.dragging_item:
            drop_row_id = self.tree.identify_row(event.y)
            if drop_row_id and drop_row_id != self.dragging_item:
                current_idx = int(self.dragging_item)
                target_idx = int(drop_row_id)

                # 데이터 리스트에서 아이템 순서 변경
                item_to_move = self.file_data.pop(current_idx)
                self.file_data.insert(target_idx, item_to_move)

                # selected_for_move 리스트도 업데이트 (인덱스 변경 반영)
                # 이동된 항목과 그 주변 항목의 인덱스 조정
                new_selected_for_move = []
                for idx in self.selected_for_move:
                    if idx == current_idx: # 이동된 항목 자체
                        new_selected_for_move.append(target_idx)
                    elif current_idx < target_idx: # 아래로 이동했을 때 (현재 인덱스보다 크고, 타겟 인덱스보다 작거나 같은 경우)
                        if current_idx < idx <= target_idx:
                            new_selected_for_move.append(idx - 1)
                        else:
                            new_selected_for_move.append(idx)
                    else: # 위로 이동했을 때 (현재 인덱스보다 작고, 타겟 인덱스보다 크거나 같은 경우)
                        if target_idx <= idx < current_idx:
                            new_selected_for_move.append(idx + 1)
                        else:
                            new_selected_for_move.append(idx)
                self.selected_for_move = sorted(list(set(new_selected_for_move))) # 중복 제거 및 정렬

                print(f"로그: {self.file_data[target_idx]['filename']} 파일의 순서가 {current_idx+1} -> {target_idx+1}로 변경되었습니다.")
                self.update_tree_view() # Treeview 업데이트
                self.tree.focus(str(target_idx)) # 드롭된 위치로 포커스 이동
                self.tree.selection_set(str(target_idx))
            self.dragging_item = None
            self.btn_rename.config(state=tk.DISABLED) # 미리보기 후 활성화

    def move_item_up(self, event):
        """선택된/포커스된 아이템을 위로 이동"""
        focused_item_id = self.tree.focus()
        if not focused_item_id:
            return

        current_idx = int(focused_item_id)
        if current_idx > 0: # 맨 위가 아니라면
            # 이동할 아이템 목록 구성: 스페이스바로 선택된 항목 + 포커스된 항목 (중복 방지)
            items_to_move_indices = set(self.selected_for_move)
            items_to_move_indices.add(current_idx) # 현재 포커스된 항목도 이동 대상에 포함

            # 가장 위쪽의 선택된/포커스된 항목이 맨 위로 이동할 수 있는지 확인
            sorted_indices = sorted(list(items_to_move_indices))
            if sorted_indices[0] == 0:
                return # 이미 맨 위이므로 이동 불가

            # 실제 데이터 리스트에서 이동
            # 이동할 항목들을 새로운 위치에 삽입하기 위해 임시로 제거
            moved_items = [self.file_data[idx] for idx in sorted_indices]
            
            # 원본 위치에서 삭제 (뒤에서부터 삭제해야 인덱스 오류 방지)
            for idx in sorted_indices[::-1]:
                del self.file_data[idx]

            # 새로운 위치에 삽입
            insert_pos = sorted_indices[0] - 1 # 가장 상단 항목의 새 위치
            for item in moved_items:
                self.file_data.insert(insert_pos, item)
                insert_pos += 1
            
            # selected_for_move 리스트 업데이트 (새로운 인덱스로 조정)
            self.selected_for_move = sorted([idx - 1 for idx in self.selected_for_move])

            print(f"로그: 선택된/포커스된 파일들의 순서가 위로 이동되었습니다.")
            self.update_tree_view()
            # 이동된 항목 중 현재 포커스된 항목의 새 위치에 포커스 유지
            new_focus_idx = int(focused_item_id) - 1
            self.tree.focus(str(new_focus_idx))
            self.tree.selection_set(str(new_focus_idx)) # 선택도 유지
            self.btn_rename.config(state=tk.DISABLED) # 미리보기 후 활성화


    def move_item_down(self, event):
        """선택된/포커스된 아이템을 아래로 이동"""
        focused_item_id = self.tree.focus()
        if not focused_item_id:
            return

        current_idx = int(focused_item_id)
        if current_idx < len(self.file_data) - 1: # 맨 아래가 아니라면
            # 이동할 아이템 목록 구성: 스페이스바로 선택된 항목 + 포커스된 항목 (중복 방지)
            items_to_move_indices = set(self.selected_for_move)
            items_to_move_indices.add(current_idx) # 현재 포커스된 항목도 이동 대상에 포함

            # 가장 아래쪽의 선택된/포커스된 항목이 맨 아래로 이동할 수 있는지 확인
            sorted_indices = sorted(list(items_to_move_indices))
            if sorted_indices[-1] == len(self.file_data) - 1:
                return # 이미 맨 아래이므로 이동 불가

            # 실제 데이터 리스트에서 이동
            # 이동할 항목들을 새로운 위치에 삽입하기 위해 임시로 제거
            moved_items = [self.file_data[idx] for idx in sorted_indices]
            
            # 원본 위치에서 삭제 (뒤에서부터 삭제해야 인덱스 오류 방지)
            for idx in sorted_indices[::-1]:
                del self.file_data[idx]

            # 새로운 위치에 삽입
            # 가장 마지막 항목의 새로운 위치 계산
            insert_pos = sorted_indices[-1] + 1 - len(moved_items) + len(sorted_indices)
            if insert_pos > len(self.file_data):
                insert_pos = len(self.file_data) # 맨 끝으로 보장

            for item in moved_items:
                self.file_data.insert(insert_pos, item)
                insert_pos += 1
            
            # selected_for_move 리스트 업데이트 (새로운 인덱스로 조정)
            self.selected_for_move = sorted([idx + 1 for idx in self.selected_for_move])

            print(f"로그: 선택된/포커스된 파일들의 순서가 아래로 이동되었습니다.")
            self.update_tree_view()
            # 이동된 항목 중 현재 포커스된 항목의 새 위치에 포커스 유지
            new_focus_idx = int(focused_item_id) + 1
            self.tree.focus(str(new_focus_idx))
            self.tree.selection_set(str(new_focus_idx)) # 선택도 유지
            self.btn_rename.config(state=tk.DISABLED) # 미리보기 후 활성화


    def generate_new_filename(self, original_filename, index, pattern):
        """
        새로운 파일명 규칙에 따라 파일명을 생성합니다.
        [00], [03], [03,04,06] 등의 숫자 패턴과 [확장자]를 처리합니다.
        """
        base_name, ext = os.path.splitext(original_filename)
        ext = ext.lower() # 확장자는 소문자로 통일

        new_name = pattern

        # [확장자] 패턴 처리
        new_name = new_name.replace("[확장자]", ext.lstrip('.')) # .mp4 -> mp4 (점 제거)

        # 숫자 패턴 ([NN] 또는 [NN,NN,NN] 등) 처리
        # 정규표현식을 사용하여 [숫자 또는 콤마로 구분된 숫자들] 패턴을 찾습니다.
        # r'\[(\d{2}(?:,\d{2})*)\]'
        #   \[ : 리터럴 '['
        #   (\d{2}(?:,\d{2})*) : 그룹 1 (캡처되는 부분)
        #       \d{2} : 두 자리 숫자 (예: 03)
        #       (?:,\d{2})* : 콤마로 시작하고 두 자리 숫자가 오는 패턴이 0번 이상 반복 (?:는 비캡처 그룹)
        #   \] : 리터럴 ']'
        matches = list(re.finditer(r'\[(\d{2}(?:,\d{2})*)\]', new_name))
        
        # 매치된 패턴을 뒤에서부터 처리하여 인덱스 변경 오류 방지
        for match_obj in reversed(matches):
            pattern_str = match_obj.group(1) # '00' 또는 '03,04,06'
            
            # 콤마로 구분된 숫자인지 단일 숫자인지 확인
            if ',' in pattern_str:
                # 콤마로 구분된 경우 (예: [03,04,06])
                specific_numbers_str = pattern_str.split(',')
                specific_numbers = [int(n) for n in specific_numbers_str]
                
                # 파일 인덱스에 따라 숫자를 결정
                if index < len(specific_numbers):
                    # 지정된 숫자 범위 내 (03, 04, 06)
                    calculated_number = specific_numbers[index]
                else:
                    # 지정된 숫자를 넘어선 경우 (그 다음부터는 순차적으로 증가)
                    # 마지막 지정된 숫자 + (현재 인덱스 - 지정된 숫자 개수 + 1)
                    calculated_number = specific_numbers[-1] + (index - len(specific_numbers) + 1)
                
                formatted_number = f"{calculated_number:02d}"
            else:
                # 단일 숫자 패턴인 경우 (예: [00], [03])
                start_number_in_pattern = int(pattern_str)
                calculated_number = index + start_number_in_pattern
                formatted_number = f"{calculated_number:02d}"
            
            # 실제 문자열 대체
            # match_obj.start()와 match_obj.end()를 사용하여 정확한 위치를 대체
            new_name = new_name[:match_obj.start()] + formatted_number + new_name[match_obj.end():]
            print(f"로그: 패턴 '{match_obj.group(0)}'이(가) '{formatted_number}'로 대체됨.")

        return new_name

    def preview_rename(self):
        """
        미리보기 버튼 클릭 시, 새로운 파일명 규칙에 따라 변경될 파일명을 미리 보여줍니다.
        """
        if not self.file_data:
            messagebox.showwarning("경고", "먼저 파일을 선택해주세요.")
            return

        pattern = self.entry_rename_pattern.get()
        if not pattern:
            messagebox.showwarning("경고", "파일명 규칙을 입력해주세요.")
            return

        self.preview_text.config(state=tk.NORMAL) # 텍스트 편집 가능하게 설정
        self.preview_text.delete(1.0, tk.END) # 기존 미리보기 내용 삭제

        preview_lines = []
        for i, data in enumerate(self.file_data):
            original_filename = data["filename"]
            try:
                # generate_new_filename 함수에 0부터 시작하는 인덱스를 전달
                new_filename = self.generate_new_filename(original_filename, i, pattern) 
                preview_lines.append(f"적용 전: {original_filename} ➔ 적용 후: {new_filename}")
            except Exception as e:
                preview_lines.append(f"오류: {original_filename} 처리 중 오류 발생 - {e}")
                print(f"로그: 미리보기 오류 발생 - {e}")

        self.preview_text.insert(tk.END, "\n".join(preview_lines))
        self.preview_text.config(state=tk.DISABLED) # 텍스트 편집 불가능하게 설정
        self.btn_rename.config(state=tk.NORMAL) # 미리보기 후 일괄 변경 버튼 활성화
        print("로그: 파일명 변경 미리보기가 생성되었습니다.")

    def execute_rename(self):
        """
        일괄 변경 실행 버튼 클릭 시, 실제 파일명 변경을 수행합니다.
        """
        if not self.file_data:
            messagebox.showwarning("경고", "먼저 파일을 선택해주세요.")
            return

        pattern = self.entry_rename_pattern.get()
        if not pattern:
            messagebox.showwarning("경고", "파일명 규칙을 입력해주세요.")
            return

        confirm = messagebox.askyesno("확인", "정말로 파일명을 일괄 변경하시겠습니까?\n이 작업은 되돌릴 수 없습니다!")
        if not confirm:
            print("로그: 파일명 변경 취소됨.")
            return

        successful_renames = 0
        failed_renames = 0
        rename_results = []

        for i, data in enumerate(self.file_data):
            original_path = data["original_path"]
            original_filename = data["filename"]
            base_dir = os.path.dirname(original_path)

            try:
                # generate_new_filename 함수에 0부터 시작하는 인덱스를 전달
                new_filename = self.generate_new_filename(original_filename, i, pattern)
                new_path = os.path.join(base_dir, new_filename)

                # 실제 파일명 변경
                os.rename(original_path, new_path)
                data["original_path"] = new_path # 경로 업데이트
                data["filename"] = new_filename # 파일명 업데이트
                successful_renames += 1
                rename_results.append(f"✔ {original_filename} -> {new_filename}")
                print(f"로그: 파일명 변경 성공 - {original_filename} -> {new_filename}")
            except Exception as e:
                failed_renames += 1
                rename_results.append(f"✖ {original_filename} 변경 실패: {e}")
                print(f"로그: 파일명 변경 실패 - {original_filename} -> 오류: {e}")

        self.update_tree_view() # 변경된 파일명으로 그리드 업데이트
        messagebox.showinfo("변경 완료", f"총 {len(self.file_data)}개 파일 중 {successful_renames}개 성공, {failed_renames}개 실패.")
        self.btn_rename.config(state=tk.DISABLED) # 재실행 방지

        # 변경 결과 로그 출력
        print("\n--- 파일명 변경 결과 ---")
        for result in rename_results:
            print(result)
        print("---------------------\n")


# 애플리케이션 실행
if __name__ == "__main__":
    root = tk.Tk()
    app = BulkRenameApp(root)
    root.mainloop()