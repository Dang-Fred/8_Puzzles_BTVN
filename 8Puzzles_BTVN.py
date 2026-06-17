import tkinter as tk
from tkinter import scrolledtext
from collections import deque
import time
import random

START_STATE = (2, 8, 3, 1, 6, 4, 7, 0, 5)
GOAL_STATE = (2, 3, 4, 1, 8, 0, 7, 6, 5)


# LỚP NODE & HÀM SINH CON
class Node:
    def __init__(self, state, parent=None, action="", depth=0, node_id=1, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.id = node_id
        self.name = ""
        self.path_cost = path_cost


def get_neighbors(state):
    idx = state.index(0)
    row, col = idx // 3, idx % 3
    moves = []
    if row > 0: moves.append(("LÊN", idx - 3))
    if row < 2: moves.append(("XUỐNG", idx + 3))
    if col > 0: moves.append(("TRÁI", idx - 1))
    if col < 2: moves.append(("PHẢI", idx + 1))

    neighbors = []
    for action, new_idx in moves:
        s_list = list(state)
        s_list[idx], s_list[new_idx] = s_list[new_idx], s_list[idx]
        neighbors.append((action, tuple(s_list)))
    return neighbors


# GIAO DIỆN (UI) - LAYOUT 3 CỘT
class app_puzzle:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Phân Tích Tìm Kiếm (BFS, IDS, UCF, Greedy, Hill Climbing, Beam Search, CSP)")
        self.root.state('zoomed')

        self.root.columnconfigure(0, weight=4)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=3)
        self.root.rowconfigure(0, weight=1)

        self.current_advanced_mode = 20

        # GIAO DIỆN MODE 1

        self.frame_left = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        top_left = tk.Frame(self.frame_left, bg="white")
        top_left.pack(pady=5)
        tk.Label(top_left, text="CẤU HÌNH BÀI TOÁN (MODE 1)", font=("Arial", 12, "bold"), bg="white").pack(pady=2)

        boards_container = tk.Frame(top_left, bg="white")
        boards_container.pack()
        self.draw_board(boards_container, "BẮT ĐẦU", START_STATE, "lightgray").pack(side=tk.LEFT, padx=15)
        self.draw_board(boards_container, "ĐÍCH ĐẾN", GOAL_STATE, "yellow").pack(side=tk.LEFT, padx=15)

        tk.Frame(self.frame_left, height=2, bg="black").pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.frame_left, text="LỊCH SỬ DUYỆT TRẠNG THÁI", font=("Arial", 10, "bold"), bg="white",
                 fg="blue").pack(pady=2)

        history_container = tk.Frame(self.frame_left, bg="white")
        history_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        history_container.rowconfigure(0, weight=1)
        history_container.columnconfigure(0, weight=1)

        self.canvas_left = tk.Canvas(history_container, bg="white")
        self.scrollbar_left_y = tk.Scrollbar(history_container, orient="vertical", command=self.canvas_left.yview)
        self.scrollbar_left_x = tk.Scrollbar(history_container, orient="horizontal", command=self.canvas_left.xview)

        self.scrollable_history = tk.Frame(self.canvas_left, bg="white")

        self.scrollable_history.bind(
            "<Configure>",
            lambda e: self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all"))
        )
        self.canvas_left.create_window((0, 0), window=self.scrollable_history, anchor="nw")
        self.canvas_left.configure(yscrollcommand=self.scrollbar_left_y.set, xscrollcommand=self.scrollbar_left_x.set)

        self.canvas_left.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_left_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_left_x.grid(row=1, column=0, sticky="ew")

        def _on_mousewheel(event):
            self.canvas_left.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas_left.bind('<Enter>', lambda _: self.canvas_left.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas_left.bind('<Leave>', lambda _: self.canvas_left.unbind_all("<MouseWheel>"))

        self.frame_mid = tk.Frame(root, bg="#f0f0f0", bd=2, relief=tk.RIDGE)
        self.frame_mid.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        tk.Label(self.frame_mid, text="MENU THUẬT TOÁN", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=15)

        list_frame = tk.Frame(self.frame_mid)
        list_frame.pack(fill=tk.BOTH, padx=10, pady=5)

        self.algo_listbox = tk.Listbox(list_frame, font=("Arial", 10), height=21, selectbackground="#a9dfbf",
                                       selectforeground="black")
        scroll_list = tk.Scrollbar(list_frame, orient="vertical", command=self.algo_listbox.yview)
        self.algo_listbox.config(yscrollcommand=scroll_list.set)

        self.algo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_list.pack(side=tk.RIGHT, fill=tk.Y)

        # CẬP NHẬT MENU: Bổ sung thuật toán 17 và 18 (AC-3, Min-Conflicts)
        algorithms = [
            "1. BFS (Tối ưu)",
            "2. BFS (Nhớ trễ)",
            "3. BFS (Đích trễ)",
            "4. Tìm kiếm Sâu dần (IDS)",
            "5. UCF (Lai - Cost là số ô sai)",
            "6. Tham lam / Greedy (Manhattan)",
            "7. A* (g=Số ô sai, h=Manhattan)",
            "8. IDA* (g=Manhattan, h=Manhattan)",
            "9. Simple Hill Climbing (Leo đồi cơ bản)",
            "10. Steepest-Ascent Hill Climbing (Chọn Tốt Nhất)",
            "11. Stochastic Hill Climbing (Leo đồi Ngẫu nhiên)",
            "12. Random Restart Hill Climbing (Lặp lại)",
            "13. Local Beam Search (Mã giả chuẩn k=2)",
            "14. AND-OR Graph Search (Mô phỏng)",
            "15. Backtracking (Nguyên bản)",
            "16. Forward Checking (Backtracking + Nhìn trước)",
            "17. AC-3 (Arc Consistency - Tỉa nhánh kề)",
            "18. Min-Conflicts (Local Search cho CSP)",
            "---------------------------------------",
            "20. [MODE 2] Đa Start - Cố định Đích",
            "21. [MODE 2] Đa Đích - Cố định Start",
            "22. [MODE 2] Random cả Start và Đích"
        ]
        for algo in algorithms:
            self.algo_listbox.insert(tk.END, algo)
        self.algo_listbox.selection_set(0)

        tk.Button(self.frame_mid, text="▶ CHẠY THUẬT TOÁN", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                  height=2, command=self.on_run_click).pack(fill=tk.X, padx=10, pady=15)

        tk.Frame(self.frame_mid, height=2, bg="gray").pack(fill=tk.X, padx=10, pady=10)

        tk.Label(self.frame_mid, text="BẢNG ĐÁNH GIÁ", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
        self.lbl_stats = tk.Label(self.frame_mid, text="Chưa có dữ liệu.\nHãy chọn và chạy\nthuật toán ở trên.",
                                  font=("Consolas", 10), bg="#f0f0f0", justify=tk.LEFT)
        self.lbl_stats.pack(padx=10, pady=5, anchor="w")

        self.frame_right = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
        self.frame_right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        tk.Label(self.frame_right, text="NHẬT KÝ CHẠY (TRACE LOG)", font=("Arial", 12, "bold"), bg="white").pack(
            pady=10)
        self.txt_log = scrolledtext.ScrolledText(self.frame_right, font=("Consolas", 11), bg="#1e1e1e", fg="#4af626")
        self.txt_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tu_dien_ten = {}
        self.dem_node = 0
        self.step_counter = 0

        # Khởi tạo Giao diện Mode 2 (ẩn đi lúc đầu)
        self.build_mode2_ui()

    # XÂY DỰNG GIAO DIỆN MODE 2 ĐA NĂNG
    def build_mode2_ui(self):
        self.frame_m2_left = tk.Frame(self.root, bg="#f9ebea", bd=2, relief=tk.RIDGE)
        self.frame_m2_mid = tk.Frame(self.root, bg="#e8f8f5", bd=2, relief=tk.RIDGE)
        self.frame_m2_right = tk.Frame(self.root, bg="#fef9e7", bd=2, relief=tk.RIDGE)

        # -- CỘT 1 (Left) --
        top_left = tk.Frame(self.frame_m2_left, bg="#f9ebea")
        top_left.pack(pady=5, fill=tk.X)

        self.m2_title_label = tk.Label(top_left, text="CẤU HÌNH BÀI TOÁN (MODE 2)", font=("Arial", 12, "bold"),
                                       bg="#f9ebea")
        self.m2_title_label.pack(pady=2)

        self.btn_m2_generate = tk.Button(top_left, text=" Tạo Random (Dựa trên Mode)", bg="#3498db", fg="white",
                                         font=("Arial", 10, "bold"), command=self.generate_m2_random_starts)
        self.btn_m2_generate.pack(pady=5)

        # Vùng chứa các board
        self.m2_boards_container = tk.Frame(top_left, bg="#f9ebea")
        self.m2_boards_container.pack()

        self.m2_starts = []
        self.m2_goals = []

        tk.Frame(self.frame_m2_left, height=2, bg="black").pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.frame_m2_left, text="LỊCH SỬ DUYỆT TRẠNG THÁI TỔNG HỢP", font=("Arial", 10, "bold"), bg="#f9ebea",
                 fg="blue").pack(pady=2)

        history_container = tk.Frame(self.frame_m2_left, bg="white")
        history_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        history_container.rowconfigure(0, weight=1)
        history_container.columnconfigure(0, weight=1)

        self.m2_canvas_left = tk.Canvas(history_container, bg="white")
        scrollbar_y = tk.Scrollbar(history_container, orient="vertical", command=self.m2_canvas_left.yview)
        scrollbar_x = tk.Scrollbar(history_container, orient="horizontal", command=self.m2_canvas_left.xview)
        self.m2_scrollable_history = tk.Frame(self.m2_canvas_left, bg="white")

        self.m2_scrollable_history.bind("<Configure>", lambda e: self.m2_canvas_left.configure(
            scrollregion=self.m2_canvas_left.bbox("all")))
        self.m2_canvas_left.create_window((0, 0), window=self.m2_scrollable_history, anchor="nw")
        self.m2_canvas_left.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.m2_canvas_left.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # -- CỘT 2 (Mid) --
        tk.Button(self.frame_m2_mid, text=" QUAY LẠI GIAO DIỆN MODE 1", bg="#e74c3c", fg="white",
                  font=("Arial", 10, "bold"), command=self.switch_to_mode1).pack(fill=tk.X, padx=10, pady=10)

        tk.Frame(self.frame_m2_mid, height=2, bg="gray").pack(fill=tk.X, padx=10, pady=5)

        tk.Label(self.frame_m2_mid, text="CHỌN THUẬT TOÁN ĐỂ CHẠY HÀNG LOẠT", font=("Arial", 10, "bold"),
                 bg="#e8f8f5").pack(
            pady=5)

        list_frame = tk.Frame(self.frame_m2_mid)
        list_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        self.m2_algo_listbox = tk.Listbox(list_frame, font=("Arial", 10), height=15, selectbackground="#a9dfbf",
                                          selectforeground="black")
        scroll_list = tk.Scrollbar(list_frame, orient="vertical", command=self.m2_algo_listbox.yview)
        self.m2_algo_listbox.config(yscrollcommand=scroll_list.set)
        self.m2_algo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_list.pack(side=tk.RIGHT, fill=tk.Y)

        for i in range(18):  # Hiển thị 18 thuật toán đầu trong Mode 2
            self.m2_algo_listbox.insert(tk.END, self.algo_listbox.get(i))
        self.m2_algo_listbox.selection_set(0)

        tk.Button(self.frame_m2_mid, text="▶ CHẠY BỘ TEST CASE", bg="#4CAF50", fg="white",
                  font=("Arial", 10, "bold"), height=2, command=self.run_mode2_algo).pack(fill=tk.X, padx=10, pady=15)

        tk.Frame(self.frame_m2_mid, height=2, bg="gray").pack(fill=tk.X, padx=10, pady=10)
        tk.Label(self.frame_m2_mid, text="BẢNG ĐÁNH GIÁ CHUNG", font=("Arial", 11, "bold"), bg="#e8f8f5").pack(pady=5)
        self.m2_lbl_stats = tk.Label(self.frame_m2_mid, text="Chưa có dữ liệu.", font=("Consolas", 10), bg="#e8f8f5",
                                     justify=tk.LEFT)
        self.m2_lbl_stats.pack(padx=10, pady=5, anchor="w")

        # -- CỘT 3 (Right) --
        tk.Label(self.frame_m2_right, text="NHẬT KÝ CHẠY TỔNG HỢP", font=("Arial", 12, "bold"), bg="#fef9e7").pack(
            pady=10)
        self.m2_txt_log = scrolledtext.ScrolledText(self.frame_m2_right, font=("Consolas", 11), bg="#1e1e1e",
                                                    fg="#f1c40f")
        self.m2_txt_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Chuyển đổi linh hoạt UI
    def switch_to_mode2(self, mode_idx):
        self.current_advanced_mode = mode_idx

        # Cập nhật thông báo tùy thuộc vào lựa chọn (Điều chỉnh index mới)
        if mode_idx == 20:
            self.m2_title_label.config(text="CẤU HÌNH: ĐA START - CỐ ĐỊNH ĐÍCH (Chế độ 1)")
            self.btn_m2_generate.config(text=" Xáo trộn tạo 3 Start ngẫu nhiên")
        elif mode_idx == 21:
            self.m2_title_label.config(text="CẤU HÌNH: ĐA ĐÍCH - CỐ ĐỊNH START (Chế độ 2)")
            self.btn_m2_generate.config(text=" Xáo trộn tạo 3 Đích ngẫu nhiên")
        elif mode_idx == 22:
            self.m2_title_label.config(text="CẤU HÌNH: RANDOM CẢ START & ĐÍCH (Chế độ 3)")
            self.btn_m2_generate.config(text=" Sinh 3 cặp Start-Goal ngẫu nhiên")

        self.frame_left.grid_remove()
        self.frame_mid.grid_remove()
        self.frame_right.grid_remove()

        self.frame_m2_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.frame_m2_mid.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.frame_m2_right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Xóa các board trên màn hình chờ người dùng tự bấm tạo
        for widget in self.m2_boards_container.winfo_children():
            widget.destroy()
        self.m2_starts.clear()
        self.m2_goals.clear()

    def switch_to_mode1(self):
        self.frame_m2_left.grid_remove()
        self.frame_m2_mid.grid_remove()
        self.frame_m2_right.grid_remove()

        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.frame_mid.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.frame_right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

    # Hàm xáo trộn dùng chung
    def scramble_state(self, state, steps=30):
        st = list(state)
        for _ in range(steps):
            idx = st.index(0)
            row, col = idx // 3, idx % 3
            moves = []
            if row > 0: moves.append(idx - 3)
            if row < 2: moves.append(idx + 3)
            if col > 0: moves.append(idx - 1)
            if col < 2: moves.append(idx + 1)
            new_idx = random.choice(moves)
            st[idx], st[new_idx] = st[new_idx], st[idx]
        return tuple(st)

    def generate_m2_random_starts(self):
        for widget in self.m2_boards_container.winfo_children():
            widget.destroy()

        self.m2_starts.clear()
        self.m2_goals.clear()

        if self.current_advanced_mode == 20:
            self.m2_goals = [GOAL_STATE] * 3
            self.m2_starts = [self.scramble_state(GOAL_STATE, 30) for _ in range(3)]

            self.draw_board(self.m2_boards_container, "ĐÍCH CỐ ĐỊNH", GOAL_STATE, "yellow").pack(side=tk.LEFT, padx=15)
            for i, st in enumerate(self.m2_starts):
                self.draw_board(self.m2_boards_container, f"START {i + 1}", st, "lightblue").pack(side=tk.LEFT, padx=5)

        elif self.current_advanced_mode == 21:
            self.m2_starts = [START_STATE] * 3
            self.m2_goals = [self.scramble_state(START_STATE, 30) for _ in range(3)]

            self.draw_board(self.m2_boards_container, "START CỐ ĐỊNH", START_STATE, "lightblue").pack(side=tk.LEFT,
                                                                                                      padx=15)
            for i, gl in enumerate(self.m2_goals):
                self.draw_board(self.m2_boards_container, f"ĐÍCH {i + 1}", gl, "yellow").pack(side=tk.LEFT, padx=5)

        elif self.current_advanced_mode == 22:
            for i in range(3):
                random_gl = self.scramble_state(GOAL_STATE, 20)
                random_st = self.scramble_state(random_gl, 30)

                self.m2_goals.append(random_gl)
                self.m2_starts.append(random_st)

                pair_frame = tk.Frame(self.m2_boards_container, bg="#f9ebea")
                pair_frame.pack(side=tk.LEFT, padx=10)
                self.draw_board(pair_frame, f"START {i + 1}", random_st, "lightblue").pack(pady=2)
                self.draw_board(pair_frame, f"ĐÍCH {i + 1}", random_gl, "yellow").pack(pady=2)

    def on_run_click(self):
        selection = self.algo_listbox.curselection()
        if not selection: return
        version = selection[0] + 1

        # Cập nhật index điều hướng: Mode 2 nằm từ vị trí 20
        if version >= 20:
            self.switch_to_mode2(version)
        elif version == 19:
            return  # Bỏ qua vạch kẻ ngang
        else:
            self.run_algo(version)

    def run_mode2_algo(self):
        selection = self.m2_algo_listbox.curselection()
        if not selection: return
        m2_version = selection[0] + 1

        if not self.m2_starts or not self.m2_goals:
            self.m2_lbl_stats.config(text="LỖI:\nHãy bấm nút 'Tạo Random' trước!")
            return

        self.m2_txt_log.delete(1.0, tk.END)
        for widget in self.m2_scrollable_history.winfo_children():
            widget.destroy()

        # BẢO LƯU Biến UI và Cấu hình cũ
        old_txt_log = self.txt_log
        old_scrollable = self.scrollable_history
        old_canvas = self.canvas_left
        old_lbl_stats = self.lbl_stats

        self.txt_log = self.m2_txt_log
        self.scrollable_history = self.m2_scrollable_history
        self.canvas_left = self.m2_canvas_left
        self.lbl_stats = self.m2_lbl_stats

        global START_STATE, GOAL_STATE
        original_global_start = START_STATE
        original_global_goal = GOAL_STATE

        danh_sach_ham = {
            1: self.algo_v1, 2: self.algo_v2, 3: self.algo_v3, 4: self.algo_ids,
            5: self.algo_ucf, 6: self.algo_greedy, 7: self.algo_astar,
            8: self.algo_idastar, 9: self.algo_hill_climbing, 10: self.algo_steepest_hill_climbing,
            11: self.algo_stochastic_hill_climbing, 12: self.algo_random_restart_hill_climbing,
            13: self.algo_local_beam_search,
            14: self.algo_and_or,
            15: self.algo_backtracking,
            16: self.algo_forward_checking,
            17: self.algo_ac3,
            18: self.algo_min_conflicts
        }
        ham_can_chay = danh_sach_ham.get(m2_version)

        total_time = 0
        total_nodes = 0
        success_count = 0

        # Bật cờ hiệu cho biết đang chạy ở Mode 2 (để kích hoạt cầu dao 5000 bước)
        self.is_mode2_running = True

        try:
            for i, (st, gl) in enumerate(zip(self.m2_starts, self.m2_goals)):
                START_STATE = st
                GOAL_STATE = gl

                self.tu_dien_ten = {}
                self.dem_node = 0
                self.step_counter = 0

                self.log(f"\n==========================================================")
                self.log(f"  BẮT ĐẦU GIẢI CẶP BÀI TOÁN SỐ {i + 1}")
                self.log(f"    - Start : {st}")
                self.log(f"    - Đích  : {gl}")
                self.log(f"==========================================================\n")

                t0 = time.time()

                try:
                    res = ham_can_chay()
                    t1 = time.time()

                    total_time += (t1 - t0)
                    total_nodes += len(self.tu_dien_ten)

                    if res and len(res) == 3 and res[0] is not None:
                        self.log(f"\n >>> KẾT LUẬN: ĐÃ TÌM THẤY ĐÍCH! (Tại Node {res[0].name})\n")
                        success_count += 1
                    else:
                        self.log(f"\n >>> KẾT LUẬN: BẾ TẮC HOẶC ĐẠT LOCAL MAXIMUM.\n")

                except Exception as e:
                    if str(e) == "OVERLOAD":
                        t1 = time.time()
                        total_time += (t1 - t0)
                        total_nodes += len(self.tu_dien_ten)
                        self.log(f"\n [CẢNH BÁO] Đã duyệt chạm ngưỡng {self.step_counter} Node!")
                        self.log(f" >>> KẾT LUẬN: QUÁ TẢI TÀI NGUYÊN. Buộc dừng bài toán này để bảo vệ hệ thống!\n")
                    else:
                        raise e
        finally:
            self.is_mode2_running = False
            START_STATE = original_global_start
            GOAL_STATE = original_global_goal
            self.txt_log = old_txt_log
            self.scrollable_history = old_scrollable
            self.canvas_left = old_canvas
            self.lbl_stats = old_lbl_stats

        self.m2_lbl_stats.config(
            text=f"Đã duyệt xong 3 bài toán!\n- Tỷ lệ thành công: {success_count}/3\n- Tổng t.gian giải: {total_time:.3f}s\n- Tổng số Node sinh ra: {total_nodes}")

    # 18 THUẬT TOÁN ĐIỀU PHỐI
    def draw_board(self, parent, title, state, title_bg="lightgray"):
        frame = tk.Frame(parent, bd=2, relief=tk.GROOVE, bg="black")
        tk.Label(frame, text=title, font=("Arial", 8, "bold"), bg=title_bg).pack(fill=tk.X)
        grid_frame = tk.Frame(frame, bg="black")
        grid_frame.pack(padx=1, pady=1)

        for i in range(9):
            row, col = i // 3, i % 3
            val = state[i]
            txt = str(val) if val != 0 else ""
            bg_c = "white" if val != 0 else "black"
            fg_c = "black" if val != 0 else "white"
            tk.Label(grid_frame, text=txt, width=2, height=1, bg=bg_c, fg=fg_c, font=("Arial", 10, "bold")).grid(
                row=row, column=col, padx=1, pady=1)
        return frame

    def get_name(self, state):
        if state not in self.tu_dien_ten:
            self.tu_dien_ten[state] = chr(65 + self.dem_node) if self.dem_node < 26 else f"N{self.dem_node}"
            self.dem_node += 1
        return self.tu_dien_ten[state]

    def log(self, text):
        self.txt_log.insert(tk.END, text + "\n")
        self.txt_log.see(tk.END)

    def calc_misplaced_tiles(self, state):
        count = 0
        for i in range(9):
            if state[i] != 0 and state[i] != GOAL_STATE[i]:
                count += 1
        return count

    def calc_manhattan(self, state):
        dist = 0
        for i in range(9):
            val = state[i]
            if val != 0:
                target_idx = GOAL_STATE.index(val)
                curr_row, curr_col = i // 3, i % 3
                tgt_row, tgt_col = target_idx // 3, target_idx % 3
                dist += abs(curr_row - tgt_row) + abs(curr_col - tgt_col)
        return dist

    def add_history_block(self, curr_node, children_nodes, special_msg=""):
        self.step_counter += 1

        # CƠ CHẾ CHỐNG LAG GIAO DIỆN
        if self.step_counter > 150:
            if self.step_counter == 151:
                self.log("\n[HỆ THỐNG] Tạm dừng vẽ đồ họa từ bước 150 để chống lag.")
                self.log("[HỆ THỐNG] Đang chạy ngầm ở tốc độ tối đa, vui lòng đợi...\n")
                self.root.update()

            # CẦU DAO TỰ ĐỘNG: CHỈ ÁP DỤNG CHO MODE 2
            if getattr(self, 'is_mode2_running', False):
                if self.step_counter > 5000:  # Ngưỡng an toàn đủ lớn
                    raise Exception("OVERLOAD")  # Kéo cầu dao!

            # Thoát hàm sớm, không tạo Frame đồ họa để tiết kiệm RAM
            return

        block = tk.Frame(self.scrollable_history, bg="#f9f9f9", bd=1, relief=tk.SOLID)
        block.pack(fill=tk.X, padx=10, pady=5)

        algo_idx = 1
        if hasattr(self, 'm2_algo_listbox') and self.m2_algo_listbox.winfo_viewable():
            sel = self.m2_algo_listbox.curselection()
            if sel: algo_idx = sel[0] + 1
        else:
            sel = self.algo_listbox.curselection()
            if sel: algo_idx = sel[0] + 1

        header_text = f"Bước {self.step_counter}: Xét node {curr_node.name} (Độ sâu: {curr_node.depth}"
        if algo_idx == 5 and hasattr(curr_node, 'path_cost'):
            header_text += f", g={curr_node.path_cost}"
        elif algo_idx in [6, 9, 10, 11, 12, 13, 18] and hasattr(curr_node, 'h_cost'):
            header_text += f", h={curr_node.h_cost}"
        header_text += ")"

        tk.Label(block, text=header_text, font=("Arial", 10, "bold"), bg="#f9f9f9", fg="blue", anchor="w").pack(
            fill=tk.X, padx=5, pady=2)

        content_frame = tk.Frame(block, bg="#f9f9f9")
        content_frame.pack(fill=tk.X, padx=5, pady=5)

        parent_frame = tk.Frame(content_frame, bg="#f9f9f9")
        parent_frame.pack(side=tk.LEFT, padx=5)
        self.draw_board(parent_frame, f"Node {curr_node.name}", curr_node.state, "#85c1e9").pack()

        if special_msg:
            tk.Label(content_frame, text=f"  ➡\n{special_msg}", font=("Arial", 10, "bold"), bg="#f9f9f9",
                     fg="red").pack(side=tk.LEFT, padx=15)
            self.root.update()
            self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all"))
            self.canvas_left.yview_moveto(1)
            return

        tk.Label(content_frame, text=" ➡\nSinh ra", font=("Arial", 9, "bold"), bg="#f9f9f9", fg="gray").pack(
            side=tk.LEFT, padx=5)

        children_frame = tk.Frame(content_frame, bg="#f9f9f9")
        children_frame.pack(side=tk.LEFT, padx=5)

        for child, is_dup in children_nodes:
            color = "gray" if is_dup else "#a9dfbf"
            title = f"{child.name}(Trùng)" if is_dup else f"{child.action} -> {child.name}"
            self.draw_board(children_frame, title, child.state, color).pack(side=tk.LEFT, padx=2)

        self.root.update()
        self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all"))
        self.canvas_left.yview_moveto(1)

    def run_algo(self, version):
        self.txt_log.delete(1.0, tk.END)
        self.lbl_stats.config(text="Đang tính toán...")
        for widget in self.scrollable_history.winfo_children():
            widget.destroy()

        self.tu_dien_ten = {}
        self.dem_node = 0
        self.step_counter = 0

        danh_sach_ham = {
            1: self.algo_v1, 2: self.algo_v2, 3: self.algo_v3, 4: self.algo_ids,
            5: self.algo_ucf, 6: self.algo_greedy, 7: self.algo_astar,
            8: self.algo_idastar, 9: self.algo_hill_climbing, 10: self.algo_steepest_hill_climbing,
            11: self.algo_stochastic_hill_climbing, 12: self.algo_random_restart_hill_climbing,
            13: self.algo_local_beam_search,
            14: self.algo_and_or,
            15: self.algo_backtracking,
            16: self.algo_forward_checking,
            17: self.algo_ac3,
            18: self.algo_min_conflicts
        }

        ham_can_chay = danh_sach_ham.get(version)
        if not ham_can_chay:
            self.log("Lỗi: Thuật toán chưa được phát triển!")
            return

        algo_name = [
            "BFS Mã giả 1", "BFS Mã giả 2", "BFS Mã giả 3", "IDS (Tìm kiếm sâu dần)",
            "UCF (Số ô sai)", "Greedy (Tham lam - Manhattan)", "A* (g=Số ô sai, h=Manhattan)",
            "IDA* (g=Manhattan, h=Manhattan)", "Simple Hill Climbing (Leo đồi cơ bản)",
            "Steepest-Ascent Hill Climbing (Chọn Tốt Nhất)", "Stochastic Hill Climbing",
            "Random Restart Hill Climbing", "Local Beam Search (Mã giả chuẩn k=2)",
            "AND-OR Graph Search (Mô phỏng)",
            "Backtracking (Nguyên bản)",
            "Forward Checking (Nhìn trước 1 bước)",
            "AC-3 (Arc Consistency 3)",
            "Min-Conflicts (Local Search CSP)"
        ][version - 1]

        self.log(f"=== KHỞI ĐỘNG: {algo_name} ===\n")

        start_time = time.time()
        result = ham_can_chay()

        if result and len(result) == 3:
            goal_node, total_popped, max_frontier = result
        else:
            goal_node, total_popped, max_frontier = None, 0, 0

        time_taken = time.time() - start_time

        stats_text = (
            f"- Kết Quả: {'THÀNH CÔNG' if goal_node else 'THẤT BẠI'}\n\n"
            f"- Số liệu đánh giá:\n"
            f"- Tống số vòng lặp: {total_popped}\n"
            f"- Max hàng đợi: {max_frontier}\n"
            f"- Số Node đã sinh: {len(self.tu_dien_ten)}\n"
            f"- Thời gian: {time_taken:.3f} s\n"
        )
        if goal_node:
            stats_text += f"- Độ sâu đích: {goal_node.depth} bước\n"
            if version == 5:
                stats_text += f"- Chi phí (g): {goal_node.path_cost}"
            elif version in [6, 9, 10, 11, 12, 13, 18]:
                stats_text += f"- Heuristic đích (h): {goal_node.h_cost}"
            elif version in [7, 8] and hasattr(goal_node, 'f_cost'):
                stats_text += f"- Tổng chi phí f đích: {goal_node.f_cost}"

        self.lbl_stats.config(text=stats_text)

        if goal_node:
            self.log(f"\n Tìm thấy đích tại Node: {goal_node.name}!")
        else:
            self.log("\n Không tìm thấy đích hoặc quá giới hạn!")

    def algo_greedy(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.h_cost = self.calc_manhattan(root.state)
        frontier = [root]
        frontier_states = {START_STATE}
        reached = set()
        counter = 2
        popped = 0
        max_f = 1

        while frontier:
            frontier.sort(key=lambda n: n.h_cost)
            max_f = max(max_f, len(frontier))
            curr = frontier.pop(0)
            frontier_states.remove(curr.state)
            popped += 1
            self.log(f"Xét Node {curr.name} (h={curr.h_cost}):")
            if curr.state == GOAL_STATE:
                self.add_history_block(curr, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return curr, popped, max_f
            reached.add(curr.state)
            visual_children = []

            for action, child_state in get_neighbors(curr.state):
                is_duplicate = child_state in reached or child_state in frontier_states
                child = Node(child_state, curr, action, curr.depth + 1, counter)
                child.name = self.get_name(child.state)

                if not is_duplicate:
                    child.h_cost = self.calc_manhattan(child_state)
                    counter += 1
                    self.log(f"  [{curr.name}, {action}] -> Node {child.name} (h={child.h_cost})")
                    frontier.append(child)
                    frontier_states.add(child_state)
                    visual_children.append((child, False))
                else:
                    self.log(f"  [{curr.name}, {action}] -> Node {child.name} (Đã có trong Reached/Frontier - Bỏ qua)")
                    visual_children.append((child, True))
            self.add_history_block(curr, visual_children)
        return None, popped, max_f

    def algo_ucf(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.path_cost = 0
        if root.state == GOAL_STATE: return root, 0, 1
        frontier = [root]
        reached = {START_STATE: 0}
        counter = 2
        popped = 0
        max_f = 1

        while frontier:
            frontier.sort(key=lambda n: n.path_cost)
            max_f = max(max_f, len(frontier))
            curr = frontier.pop(0)
            popped += 1
            self.log(f"Xét Node {curr.name} (g={curr.path_cost}):")
            visual_children = []

            for action, child_state in get_neighbors(curr.state):
                h_cost = self.calc_misplaced_tiles(child_state)
                g_cost = curr.path_cost + h_cost
                is_duplicate = False
                if child_state in reached and reached[child_state] <= g_cost:
                    is_duplicate = True
                child = Node(child_state, curr, action, curr.depth + 1, counter)
                child.name = self.get_name(child.state)
                child.path_cost = g_cost
                visual_children.append((child, is_duplicate))

                if not is_duplicate:
                    reached[child_state] = g_cost
                    counter += 1
                    self.log(
                        f"  [{curr.name}, {action}] -> Node {child.name} (g={curr.path_cost} + {h_cost} = {g_cost})")
                    if child_state == GOAL_STATE:
                        self.add_history_block(curr, visual_children)
                        return child, popped, max_f
                    frontier.append(child)
                else:
                    self.log(f"  [{curr.name}, {action}] -> Trùng lặp/Cost cao (Bỏ qua)")
            self.add_history_block(curr, visual_children)
        return None, popped, max_f

    def algo_ids(self):
        total_popped = 0
        max_f = 1
        depth_limit = 0
        while True:
            self.log(f"\n" + "=" * 30)
            self.log(f" BẮT ĐẦU VÒNG LẶP IDS VỚI ĐỘ SÂU (LIMIT) = {depth_limit}")
            self.log("=" * 30)
            result, popped, current_max_f = self.dls(START_STATE, depth_limit)
            total_popped += popped
            max_f = max(max_f, current_max_f)
            if type(result) == Node:
                return result, total_popped, max_f
            elif result == "failure":
                return None, total_popped, max_f
            depth_limit += 1
            if depth_limit > 10:
                self.log(f"\n Đạt giới hạn an toàn UI (depth > 10). Dừng lại.")
                return None, total_popped, max_f

    def dls(self, start_state, limit):
        root = Node(start_state, node_id=1)
        root.name = self.get_name(root.state)
        frontier = [root]
        result = "failure"
        popped = 0
        max_f = 1
        while frontier:
            max_f = max(max_f, len(frontier))
            curr = frontier.pop()
            popped += 1
            self.log(f"Xét Node {curr.name} (Độ sâu: {curr.depth}):")
            if curr.state == GOAL_STATE: return curr, popped, max_f
            if curr.depth >= limit:
                result = "cutoff"
                self.log(f"  -> Cắt vì đã đạt độ sâu giới hạn {limit}")
                self.add_history_block(curr, [], "Cutoff\n(Giới hạn độ sâu)")
                continue
            if self.is_cycle(curr):
                self.log(f"  -> Bỏ qua vì Trùng lặp nhánh")
                self.add_history_block(curr, [], "Bỏ qua\n(Trùng lặp nhánh)")
                continue
            visual_children = []
            for action, child_state in get_neighbors(curr.state):
                child = Node(child_state, curr, action, curr.depth + 1)
                child.name = self.get_name(child.state)
                visual_children.append((child, False))
                self.log(f"  [{curr.name}, {action}, Sâu:{child.depth}] = Node {child.name}")
                frontier.append(child)
            self.add_history_block(curr, visual_children)
        return result, popped, max_f

    def is_cycle(self, node):
        curr = node.parent
        while curr:
            if curr.state == node.state: return True
            curr = curr.parent
        return False

    def algo_v1(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        if root.state == GOAL_STATE: return root, 0, 1
        frontier = deque([root])
        reached = {START_STATE}
        counter = 2
        popped = 0
        max_f = 1
        while frontier:
            max_f = max(max_f, len(frontier))
            curr = frontier.popleft()
            popped += 1
            self.log(f"Xét Node {curr.name}:")
            visual_children = []
            for action, child_state in get_neighbors(curr.state):
                is_duplicate = child_state in reached
                child = Node(child_state, curr, action, curr.depth + 1, counter)
                child.name = self.get_name(child.state)
                visual_children.append((child, is_duplicate))
                if not is_duplicate:
                    reached.add(child_state)
                    counter += 1
                    self.log(f"  [{curr.name}, {action}, {child.depth}] = Node {child.name}")
                    if child_state == GOAL_STATE:
                        self.add_history_block(curr, visual_children)
                        return child, popped, max_f
                    frontier.append(child)
                else:
                    self.log(f"  [{curr.name}, {action}] -> Trùng lặp (Bỏ qua)")
            self.add_history_block(curr, visual_children)
        return None, popped, max_f

    def algo_v2(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        if root.state == GOAL_STATE: return root, 0, 1
        frontier = deque([root])
        frontier_set = {START_STATE}
        explored = set()
        counter = 2
        popped = 0
        max_f = 1
        while frontier:
            max_f = max(max_f, len(frontier))
            curr = frontier.popleft()
            frontier_set.remove(curr.state)
            explored.add(curr.state)
            popped += 1
            self.log(f"Xét Node {curr.name}:")
            visual_children = []
            for action, child_state in get_neighbors(curr.state):
                is_duplicate = child_state in explored or child_state in frontier_set
                child = Node(child_state, curr, action, curr.depth + 1, counter)
                child.name = self.get_name(child.state)
                visual_children.append((child, is_duplicate))
                if not is_duplicate:
                    counter += 1
                    self.log(f"  [{curr.name}, {action}, {child.depth}] = Node {child.name}")
                    if child_state == GOAL_STATE:
                        self.add_history_block(curr, visual_children)
                        return child, popped, max_f
                    frontier.append(child)
                    frontier_set.add(child_state)
                else:
                    self.log(f"  [{curr.name}, {action}] -> Trùng lặp (Bỏ qua)")
            self.add_history_block(curr, visual_children)
        return None, popped, max_f

    def algo_v3(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        frontier = deque([root])
        frontier_set = {START_STATE}
        reached = set()
        counter = 2
        popped = 0
        max_f = 1
        while frontier:
            max_f = max(max_f, len(frontier))
            curr = frontier.popleft()
            frontier_set.remove(curr.state)
            reached.add(curr.state)
            popped += 1
            if curr.state == GOAL_STATE: return curr, popped, max_f
            self.log(f"Xét Node {curr.name}:")
            visual_children = []
            for action, child_state in get_neighbors(curr.state):
                is_duplicate = child_state in reached or child_state in frontier_set
                child = Node(child_state, curr, action, curr.depth + 1, counter)
                child.name = self.get_name(child.state)
                visual_children.append((child, is_duplicate))
                if not is_duplicate:
                    counter += 1
                    self.log(f"  [{curr.name}, {action}, {child.depth}] = Node {child.name}")
                    frontier.append(child)
                    frontier_set.add(child_state)
                else:
                    self.log(f"  [{curr.name}, {action}] -> Trùng lặp (Bỏ qua)")
            self.add_history_block(curr, visual_children)
        return None, popped, max_f

    def algo_astar(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.path_cost = 0
        root.h_cost = self.calc_manhattan(root.state)
        root.f_cost = root.path_cost + root.h_cost

        frontier = [root]
        frontier_dict = {START_STATE: root}
        reached_dict = {}
        counter = 2
        popped = 0
        max_f = 1

        while frontier:
            frontier.sort(key=lambda n: n.f_cost)
            max_f = max(max_f, len(frontier))
            curr = frontier.pop(0)
            frontier_dict.pop(curr.state, None)
            popped += 1
            self.log(f"Xét Node {curr.name} (g={curr.path_cost}, h={curr.h_cost}, f={curr.f_cost}):")

            if curr.state == GOAL_STATE:
                self.add_history_block(curr, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return curr, popped, max_f
            reached_dict[curr.state] = curr
            visual_children = []

            for action, child_state in get_neighbors(curr.state):
                h_cost = self.calc_manhattan(child_state)
                step_cost = self.calc_misplaced_tiles(child_state)
                g_new = curr.path_cost + step_cost

                if child_state in reached_dict:
                    old_child = reached_dict[child_state]
                    if g_new >= old_child.path_cost:
                        self.log(
                            f"  [{curr.name}, {action}] -> Node {old_child.name} đã thuộc Reached và tối ưu hơn (Bỏ qua)")
                        visual_children.append((old_child, True))
                        continue
                    else:
                        self.log(f"  [{curr.name}, {action}] -> Tối ưu lại g cho Node {old_child.name} trong Reached")
                        reached_dict.pop(child_state)
                        old_child.path_cost = g_new
                        old_child.f_cost = g_new + h_cost
                        old_child.parent = curr
                        old_child.action = action
                        old_child.depth = curr.depth + 1
                        frontier.append(old_child)
                        frontier_dict[child_state] = old_child
                        visual_children.append((old_child, False))
                        continue

                elif child_state in frontier_dict:
                    old_child = frontier_dict[child_state]
                    if g_new < old_child.path_cost:
                        self.log(
                            f"  [{curr.name}, {action}] -> Cập nhật g tốt hơn cho Node {old_child.name} trong Frontier")
                        old_child.path_cost = g_new
                        old_child.f_cost = g_new + h_cost
                        old_child.parent = curr
                        old_child.action = action
                        old_child.depth = curr.depth + 1
                    else:
                        self.log(
                            f"  [{curr.name}, {action}] -> Node {old_child.name} đã thuộc Frontier với g tối ưu hơn (Bỏ qua)")
                    visual_children.append((old_child, True))
                    continue
                else:
                    child = Node(child_state, curr, action, curr.depth + 1, counter)
                    child.name = self.get_name(child.state)
                    child.path_cost = g_new
                    child.h_cost = h_cost
                    child.f_cost = g_new + h_cost
                    counter += 1
                    self.log(
                        f"  [{curr.name}, {action}] -> Node {child.name} (g={g_new}, h={h_cost}, f={child.f_cost})")
                    frontier.append(child)
                    frontier_dict[child_state] = child
                    visual_children.append((child, False))

            self.add_history_block(curr, visual_children)
        return None, popped, max_f

    def algo_idastar(self):
        total_popped = 0
        max_f = 1
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.path_cost = 0
        root.h_cost = self.calc_manhattan(root.state)
        root.f_cost = root.path_cost + root.h_cost
        limit = root.f_cost

        while True:
            self.log(f"\n" + "=" * 30)
            self.log(f" BẮT ĐẦU VÒNG LẶP IDA* VỚI GIỚI HẠN (LIMIT) = {limit}")
            self.log("=" * 30)
            self.next_limit = float('inf')
            self.idastar_popped = 0
            self.idastar_max_stack = 0
            result = self.idastar_dfs(root, limit, {START_STATE})

            total_popped += self.idastar_popped
            max_f = max(max_f, self.idastar_max_stack)

            if isinstance(result, Node): return result, total_popped, max_f
            if self.next_limit == float('inf'): return None, total_popped, max_f
            limit = self.next_limit
            if total_popped > 1000:
                self.log(f"\n Đạt giới hạn an toàn vòng lặp của hệ thống. Dừng thuật toán.")
                return None, total_popped, max_f

    def idastar_dfs(self, curr, limit, path_states):
        self.idastar_popped += 1
        self.idastar_max_stack = max(self.idastar_max_stack, len(path_states))
        self.log(f"Xét Node {curr.name} (g={curr.path_cost}, h={curr.h_cost}, f={curr.f_cost}):")

        if curr.state == GOAL_STATE: return curr
        if curr.f_cost > limit:
            if curr.f_cost < self.next_limit: self.next_limit = curr.f_cost
            self.log(f"  -> CẮT  vì f={curr.f_cost} > Limit={limit}")
            self.add_history_block(curr, [], f"Cutoff\n(f={curr.f_cost} > {limit})")
            return "cutoff"

        visual_children = []
        children_nodes = []

        for action, child_state in get_neighbors(curr.state):
            h_cost = self.calc_manhattan(child_state)
            g_cost = curr.path_cost + h_cost
            f_cost = g_cost + h_cost
            child = Node(child_state, curr, action, curr.depth + 1)
            child.name = self.get_name(child.state)
            child.path_cost = g_cost
            child.h_cost = h_cost
            child.f_cost = f_cost
            is_cycle = child_state in path_states
            visual_children.append((child, is_cycle))

            if not is_cycle:
                self.log(f"  [{curr.name}, {action}] -> Node {child.name} (g={g_cost}, h={h_cost}, f={f_cost})")
                children_nodes.append(child)
            else:
                self.log(f"  [{curr.name}, {action}] -> Trùng lặp nhánh (Bỏ qua)")

        self.add_history_block(curr, visual_children)

        for child in children_nodes:
            path_states.add(child.state)
            res = self.idastar_dfs(child, limit, path_states)
            path_states.remove(child.state)
            if isinstance(res, Node): return res
        return "cutoff"

    def algo_hill_climbing(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.h_cost = self.calc_misplaced_tiles(root.state)

        current_node = root
        counter = 2
        popped = 0
        max_f = 1

        while True:
            popped += 1
            self.log(f"\nXét Current_State: Node {current_node.name} (h={current_node.h_cost}):")

            if current_node.state == GOAL_STATE:
                self.add_history_block(current_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return current_node, popped, max_f

            idx = current_node.state.index(0)
            row, col = idx // 3, idx % 3
            moves_lrud = []
            if col > 0: moves_lrud.append(("Trái", idx - 1))
            if col < 2: moves_lrud.append(("Phải", idx + 1))
            if row > 0: moves_lrud.append(("Lên", idx - 3))
            if row < 2: moves_lrud.append(("Xuống", idx + 3))

            found_better = False
            visual_children = []
            evaluating_node = current_node

            for action, new_idx in moves_lrud:
                s_list = list(evaluating_node.state)
                s_list[idx], s_list[new_idx] = s_list[new_idx], s_list[idx]
                child_state = tuple(s_list)

                h_cost = self.calc_misplaced_tiles(child_state)
                child = Node(child_state, evaluating_node, action, evaluating_node.depth + 1, counter)
                child.name = self.get_name(child.state)
                child.h_cost = h_cost
                counter += 1

                visual_children.append((child, False))
                self.log(f"  Sinh lân cận: [{evaluating_node.name}, {action}] -> Node {child.name} (h={h_cost})")

                if h_cost < evaluating_node.h_cost:
                    self.log(f"  => Tốt hơn! (h={h_cost} < {evaluating_node.h_cost}). Trở thành Current_State mới.")
                    current_node = child
                    found_better = True
                    break

            self.add_history_block(evaluating_node, visual_children)

            if not found_better:
                self.log(f"  => Không có lân cận nào tốt hơn (h đều >= {evaluating_node.h_cost}).")
                self.log(f"  => ĐẠT  Local Maximum. DỪNG THUẬT TOÁN.")
                self.add_history_block(current_node, [], "Local Maximum\n(Thất bại)")
                return None, popped, max_f

    def algo_steepest_hill_climbing(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.h_cost = self.calc_manhattan(root.state)

        current_node = root
        counter = 2
        popped = 0
        max_f = 1

        while True:
            popped += 1
            self.log(f"\nXét Current_State: Node {current_node.name} (h={current_node.h_cost}):")

            if current_node.state == GOAL_STATE:
                self.add_history_block(current_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return current_node, popped, max_f

            best_next_node = None
            min_h = float('inf')
            visual_children = []

            for action, child_state in get_neighbors(current_node.state):
                h_cost = self.calc_manhattan(child_state)
                child = Node(child_state, current_node, action, current_node.depth + 1, counter)
                child.name = self.get_name(child.state)
                child.h_cost = h_cost
                counter += 1

                visual_children.append((child, False))
                self.log(f"  Sinh lân cận: [{current_node.name}, {action}] -> Node {child.name} (h={h_cost})")

                if h_cost < min_h:
                    min_h = h_cost
                    best_next_node = child

            self.add_history_block(current_node, visual_children)

            if best_next_node and best_next_node.h_cost < current_node.h_cost:
                self.log(
                    f"  => Chọn tốt nhất: Node {best_next_node.name} (h={best_next_node.h_cost} < {current_node.h_cost}). Cập nhật Current_State.")
                current_node = best_next_node
            else:
                self.log(
                    f"  => Không có lân cận nào tốt hơn trạng thái hiện tại (min_h = {min_h} >= {current_node.h_cost}).")
                self.log(f"  => Đạt Local Maximum. DỪNG THUẬT TOÁN.")
                self.add_history_block(current_node, [], "Local Maximum\n(Thất bại)")
                return None, popped, max_f

    def algo_stochastic_hill_climbing(self):
        root = Node(START_STATE, node_id=1)
        root.name = self.get_name(root.state)
        root.h_cost = self.calc_manhattan(root.state)

        current_node = root
        counter = 2
        popped = 0
        max_f = 1

        while True:
            popped += 1
            self.log(f"\nXét Current_State: Node {current_node.name} (h={current_node.h_cost}):")

            if current_node.state == GOAL_STATE:
                self.add_history_block(current_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return current_node, popped, max_f

            better_neighbors = []
            visual_children = []

            for action, child_state in get_neighbors(current_node.state):
                h_cost = self.calc_manhattan(child_state)
                child = Node(child_state, current_node, action, current_node.depth + 1, counter)
                child.name = self.get_name(child.state)
                child.h_cost = h_cost
                counter += 1

                visual_children.append((child, False))
                self.log(f"  Sinh lân cận: [{current_node.name}, {action}] -> Node {child.name} (h={h_cost})")

                if h_cost < current_node.h_cost:
                    better_neighbors.append(child)

            self.add_history_block(current_node, visual_children)

            if not better_neighbors:
                self.log(f"  => Tập Better_Neighbors rỗng (Không có lân cận nào có h < {current_node.h_cost}).")
                self.log(f"  => Đạt Local Maximum. DỪNG THUẬT TOÁN.")
                self.add_history_block(current_node, [], "Local Maximum\n(Thất bại)")
                return None, popped, max_f
            else:
                next_node = random.choice(better_neighbors)
                better_names = [n.name for n in better_neighbors]
                self.log(f"  => Tập Better_Neighbors gồm: {better_names}")
                self.log(f"  => Chọn ngẫu nhiên: Node {next_node.name} (h={next_node.h_cost}). Cập nhật Current_State.")
                current_node = next_node

    def algo_random_restart_hill_climbing(self):
        MAX_RESTART = 10
        total_popped = 0
        max_f = 1
        counter = 2

        for i in range(1, MAX_RESTART + 1):
            self.log(f"\n" + "=" * 40)
            self.log(f" Bắt đầu lượt chạy thứ {i}/{MAX_RESTART}")
            self.log("=" * 40)

            root = Node(START_STATE, node_id=1)
            root.name = self.get_name(root.state)
            root.h_cost = self.calc_manhattan(root.state)

            current_node = root

            while True:
                total_popped += 1
                self.log(f"\nXét Current_State: Node {current_node.name} (h={current_node.h_cost}):")

                if current_node.state == GOAL_STATE:
                    self.add_history_block(current_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                    return current_node, total_popped, max_f

                better_neighbors = []
                visual_children = []

                for action, child_state in get_neighbors(current_node.state):
                    h_cost = self.calc_manhattan(child_state)
                    child = Node(child_state, current_node, action, current_node.depth + 1, counter)
                    child.name = self.get_name(child.state)
                    child.h_cost = h_cost
                    counter += 1

                    visual_children.append((child, False))
                    self.log(f"  Sinh lân cận: [{current_node.name}, {action}] -> Node {child.name} (h={h_cost})")

                    if h_cost < current_node.h_cost:
                        better_neighbors.append(child)

                self.add_history_block(current_node, visual_children)

                if not better_neighbors:
                    self.log(f"  => Tập Better_Neighbors RỖNG. Đạt cực đại cục bộ.")
                    self.log(f"  => Thoát vòng lặp. Chuẩn bị chạy lại...")
                    self.add_history_block(current_node, [], f"Local Maximum\n(Kẹt ở lượt {i})")
                    break
                else:
                    next_node = random.choice(better_neighbors)
                    better_names = [n.name for n in better_neighbors]
                    self.log(f"  => Tập Better_Neighbors gồm: {better_names}")
                    self.log(f"  => Chọn ngẫu nhiên: Node {next_node.name} (h={next_node.h_cost}).")
                    current_node = next_node

        self.log(f"\n[THẤT BẠI] Đã chạy hết sạch {MAX_RESTART} lượt mà vẫn không chạm được Goal.")
        return None, total_popped, max_f

    def algo_local_beam_search(self):
        k = 2
        counter = 2
        popped = 0
        max_f = k

        self.log(f"Khởi tạo Local Beam Search (k = {k}).")

        current_state_set = []

        start_neighbors = [child_state for action, child_state in get_neighbors(START_STATE)]
        random_initial_states = random.sample(start_neighbors, min(k, len(start_neighbors)))

        for st in random_initial_states:
            root = Node(st, node_id=counter)
            root.name = self.get_name(root.state)
            root.h_cost = self.calc_manhattan(root.state)
            current_state_set.append(root)
            counter += 1
            self.log(f" + Sinh ngẫu nhiên từ Start: Node {root.name} (h={root.h_cost})")

        while True:
            popped += 1
            self.log(f"\n" + "=" * 40)
            self.log(f"VÒNG LẶP {popped}: Đang xét chùm {len(current_state_set)} trạng thái")
            self.log("=" * 40)

            neighbor_states = []

            for curr in current_state_set:
                self.log(f"\n + Xét Node {curr.name} trong chùm (h={curr.h_cost}):")
                visual_children = []

                for action, child_state in get_neighbors(curr.state):
                    h_cost = self.calc_manhattan(child_state)
                    child = Node(child_state, curr, action, curr.depth + 1, counter)
                    child.name = self.get_name(child.state)
                    child.h_cost = h_cost
                    counter += 1

                    neighbor_states.append(child)
                    visual_children.append((child, False))
                    self.log(f"    [{action}] -> Sinh Node {child.name} (h={h_cost})")

                self.add_history_block(curr, visual_children)

            if not neighbor_states:
                self.log(f"\n => Kiểm tra bế tắt: Neighbor_States rỗng!")
                current_state_set.sort(key=lambda n: n.h_cost)
                best_node = current_state_set[0]
                self.log(f" => Trả về trạng thái tốt nhất trong Current_State_set: Node {best_node.name}")
                self.add_history_block(best_node, [], "Bế tắc\n(Dừng thuật toán)")
                return None, popped, max_f

            for neighbor in neighbor_states:
                if neighbor.state == GOAL_STATE:
                    self.log(f"\n => Kiểm tra đích: TÌM THẤY ĐÍCH tại Node {neighbor.name}!")
                    self.add_history_block(neighbor, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                    return neighbor, popped, max_f

            neighbor_states.sort(key=lambda n: n.h_cost)

            current_state_set = neighbor_states[:k]

            chosen_names = [f"{n.name}(h={n.h_cost})" for n in current_state_set]
            self.log(f"\n => Lụa chọn chùm ({k} tốt nhất từ Neighbor_States): {', '.join(chosen_names)}")

            if popped > 500:
                self.log("\n[CẢNH BÁO] Đạt giới hạn an toàn vòng lặp. Dừng hệ thống (Beam Search bị kẹt).")
                return None, popped, max_f

    def algo_backtracking(self):
        self.bt_goal = None
        self.bt_popped = 0

        def backtrack(curr_state, path, parent_node):
            if self.bt_goal or self.bt_popped > 3000: return
            self.bt_popped += 1

            curr_node = Node(curr_state, parent_node, depth=len(path) - 1)
            curr_node.name = self.get_name(curr_state)

            if curr_state == GOAL_STATE:
                self.bt_goal = curr_node
                self.add_history_block(curr_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return

            if len(path) > 15:
                self.log(f"  -> Vi phạm ràng buộc: Đạt giới hạn độ sâu 15. Buộc quay lui!")
                self.add_history_block(curr_node, [], "Quay lui\n(Quá sâu)")
                return

            neighbors = get_neighbors(curr_state)
            visual_children = []
            valid_children = []

            for a, s in neighbors:
                child = Node(s, curr_node, a, curr_node.depth + 1)
                child.name = self.get_name(s)
                if s in path:
                    visual_children.append((child, True))
                else:
                    visual_children.append((child, False))
                    valid_children.append((a, s))

            self.add_history_block(curr_node, visual_children)

            for a, s in valid_children:
                path.append(s)
                self.log(f"\n[DO] Gán hành động {a} -> Chuyển sang Node {self.get_name(s)}")
                backtrack(s, path, curr_node)
                if self.bt_goal: return
                popped_state = path.pop()
                self.log(
                    f"[UNDO] Nhánh {a} thất bại. Xóa Node {self.get_name(popped_state)}, rút lui về {curr_node.name}")

        self.log("Khởi tạo Assignment rỗng. Ràng buộc: Độ sâu <= 15.")
        backtrack(START_STATE, [START_STATE], None)
        return self.bt_goal, self.bt_popped, 1

    def algo_forward_checking(self):
        self.fc_goal = None
        self.fc_popped = 0

        def backtrack_fc(curr_state, path, parent_node):
            if self.fc_goal or self.fc_popped > 3000: return
            self.fc_popped += 1

            curr_node = Node(curr_state, parent_node, depth=len(path) - 1)
            curr_node.name = self.get_name(curr_state)

            if curr_state == GOAL_STATE:
                self.fc_goal = curr_node
                self.add_history_block(curr_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return

            if len(path) > 15:
                self.add_history_block(curr_node, [], "Quay lui\n(Quá sâu)")
                return

            neighbors = get_neighbors(curr_state)
            visual_children = []
            valid_children = []

            for a, s in neighbors:
                child = Node(s, curr_node, a, curr_node.depth + 1)
                child.name = self.get_name(s)
                if s in path:
                    visual_children.append((child, True))
                else:
                    future = get_neighbors(s)
                    all_dead = True
                    for fa, fs in future:
                        if fs not in path and fs != curr_state:
                            all_dead = False
                            break

                    if all_dead and s != GOAL_STATE:
                        visual_children.append((child, True))
                        self.log(f"  [FORWARD CHECKING] Nhìn trước nhánh {a} thấy 100% ngõ cụt. Tỉa cành (Prune)!")
                    else:
                        visual_children.append((child, False))
                        valid_children.append((a, s))

            self.add_history_block(curr_node, visual_children)

            for a, s in valid_children:
                path.append(s)
                self.log(f"\n[DO] Gán hành động {a} -> Node {self.get_name(s)}")
                backtrack_fc(s, path, curr_node)
                if self.fc_goal: return
                popped_state = path.pop()
                self.log(f"[UNDO] Rút lui khỏi {self.get_name(popped_state)}")

        backtrack_fc(START_STATE, [START_STATE], None)
        return self.fc_goal, self.fc_popped, 1

    def algo_and_or(self):
        self.ao_goal = None
        self.ao_popped = 0

        def or_search(state, path, parent_node):
            if self.ao_goal or self.ao_popped > 3000: return "failure"
            self.ao_popped += 1

            curr_node = Node(state, parent_node, depth=len(path))
            curr_node.name = self.get_name(state)

            if state == GOAL_STATE:
                self.ao_goal = curr_node
                self.add_history_block(curr_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return "success"

            if len(path) > 15:
                self.add_history_block(curr_node, [], "Thất bại\n(Quá sâu)")
                return "failure"

            neighbors = get_neighbors(state)
            visual_children = []
            for a, s in neighbors:
                child = Node(s, curr_node, a, curr_node.depth + 1)
                child.name = self.get_name(s)
                visual_children.append((child, s in path))

            self.add_history_block(curr_node, visual_children)

            for a, s in neighbors:
                if s in path: continue
                self.log(f"\n[OR_SEARCH] AI chọn hành động: {a}")

                res = and_search([s], path + [state], curr_node)
                if res == "success": return "success"

            return "failure"

        def and_search(states, path, parent_node):
            for s in states:
                self.log(f"[AND_SEARCH] Môi trường phản hồi trạng thái: Node {self.get_name(s)}. Lập kế hoạch...")
                res = or_search(s, path, parent_node)
                if res == "failure": return "failure"
            return "success"

        or_search(START_STATE, [], None)
        return self.ao_goal, self.ao_popped, 1

    # =========================================================================
    # THUẬT TOÁN 17: AC-3 (Arc Consistency 3)
    # Tương tự Forward Checking nhưng tập trung vào việc loại bỏ các Cung (Arc) vô ích
    # =========================================================================
    def algo_ac3(self):
        self.ac3_goal = None
        self.ac3_popped = 0

        def backtrack_ac3(curr_state, path, parent_node):
            if self.ac3_goal or self.ac3_popped > 3000: return
            self.ac3_popped += 1

            curr_node = Node(curr_state, parent_node, depth=len(path) - 1)
            curr_node.name = self.get_name(curr_state)

            if curr_state == GOAL_STATE:
                self.ac3_goal = curr_node
                self.add_history_block(curr_node, [], "ĐÍCH ĐẾN!\n(Dừng thuật toán)")
                return

            if len(path) > 15:
                self.add_history_block(curr_node, [], "Quay lui\n(Quá sâu)")
                return

            neighbors = get_neighbors(curr_state)
            visual_children = []
            valid_children = []

            for a, s in neighbors:
                child = Node(s, curr_node, a, curr_node.depth + 1)
                child.name = self.get_name(s)
                if s in path:
                    visual_children.append((child, True))
                else:
                    # Kỹ thuật AC-3: Kiểm tra tính nhất quán của Cung (curr_state, s)
                    # Nếu từ 's' không thể sinh ra bất kỳ trạng thái nào hợp lệ, Cung này không nhất quán.
                    is_consistent = False
                    if s == GOAL_STATE:
                        is_consistent = True
                    else:
                        future_neighbors = get_neighbors(s)
                        for fa, fs in future_neighbors:
                            if fs not in path and fs != curr_state:
                                is_consistent = True
                                break

                    if not is_consistent:
                        visual_children.append((child, True))
                        self.log(
                            f"  [AC-3] Phát hiện Cung ({curr_node.name} -> {child.name}) không nhất quán. Xóa nhánh {a}!")
                    else:
                        visual_children.append((child, False))
                        valid_children.append((a, s))

            self.add_history_block(curr_node, visual_children)

            for a, s in valid_children:
                path.append(s)
                self.log(f"\n[DO] Đi theo Cung nhất quán {a} -> Node {self.get_name(s)}")
                backtrack_ac3(s, path, curr_node)
                if self.ac3_goal: return
                popped_state = path.pop()
                self.log(f"[UNDO] Rút lui khỏi {self.get_name(popped_state)}")

        self.log("Khởi tạo AC-3: Quét và loại bỏ các cung (Arc) dẫn đến ngõ cụt.")
        backtrack_ac3(START_STATE, [START_STATE], None)
        return self.ac3_goal, self.ac3_popped, 1

    # =========================================================================
    # THUẬT TOÁN 18: MIN-CONFLICTS (Local Search)
    # Liên tục chọn nhánh làm giảm "Xung đột" (Số ô sai vị trí) nhanh nhất
    # =========================================================================
    def algo_min_conflicts(self):
        max_steps = 150  # Tránh lặp vô hạn
        current_state = START_STATE

        current_node = Node(current_state, node_id=1)
        current_node.name = self.get_name(current_state)

        counter = 2
        popped = 0

        self.log(f"Khởi tạo Min-Conflicts (Tối đa = {max_steps} bước)")

        for i in range(1, max_steps + 1):
            popped += 1
            conflicts = self.calc_misplaced_tiles(current_state)
            current_node.h_cost = conflicts
            self.log(f"\nBước {i}: Xét Node {current_node.name} (Xung đột hiện tại: {conflicts})")

            if current_state == GOAL_STATE:
                self.add_history_block(current_node, [], "ĐÍCH ĐẾN!\n(Không còn xung đột)")
                return current_node, popped, 1

            neighbors = get_neighbors(current_state)
            visual_children = []
            best_neighbors = []
            min_conflict_val = float('inf')

            # Đánh giá xung đột của tất cả nhánh con
            for a, s in neighbors:
                child = Node(s, current_node, a, current_node.depth + 1, counter)
                child.name = self.get_name(s)
                child_conflicts = self.calc_misplaced_tiles(s)
                child.h_cost = child_conflicts
                counter += 1

                visual_children.append((child, False))
                self.log(f"  Thử {a} -> Node {child.name} có {child_conflicts} xung đột.")

                # Lọc ra các nhánh làm giảm xung đột tốt nhất
                if child_conflicts < min_conflict_val:
                    min_conflict_val = child_conflicts
                    best_neighbors = [(a, child)]
                elif child_conflicts == min_conflict_val:
                    best_neighbors.append((a, child))

            self.add_history_block(current_node, visual_children)

            # Chọn NGẪU NHIÊN một biến (hành động) trong tập làm giảm xung đột tốt nhất
            chosen_action, chosen_node = random.choice(best_neighbors)
            self.log(
                f" => GÁN LẠI (Cập nhật): Chọn hành động {chosen_action} (Tối thiểu hóa xung đột về {min_conflict_val})")

            current_state = chosen_node.state
            current_node = chosen_node

        self.log(
            f"\n[THẤT BẠI] Đã chạm ngưỡng {max_steps} bước nhưng vẫn chưa giải quyết hết xung đột (Bị kẹt ở Cực tiểu cục bộ).")
        return None, popped, 1


if __name__ == "__main__":
    root = tk.Tk()
    app = app_puzzle(root)
    root.mainloop()