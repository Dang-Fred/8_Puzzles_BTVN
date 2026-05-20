import tkinter as tk
from tkinter import scrolledtext
from collections import deque
import time

# CẤU HÌNH BÀI TOÁN

START_STATE = (2, 8, 3, 1, 6, 4, 7, 0, 5)
GOAL_STATE = (2, 3, 4, 1, 8, 0, 7, 6, 5)

# LỚP NODE & HÀM SINH CON

class Node:
    def __init__(self, state, parent=None, action="", depth=0, node_id=1):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.id = node_id
        self.name = ""


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

# GIAO DIỆN

class BFSAppDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Phân Tích ")
        self.root.state('zoomed')

        self.root.columnconfigure(0, weight=4)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=3)
        self.root.rowconfigure(0, weight=1)

        # CỘT 1:(LỊCH SỬ TRỰC QUAN HÓA)
        self.frame_left = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
        self.frame_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        top_left = tk.Frame(self.frame_left, bg="white")
        top_left.pack(pady=5)
        tk.Label(top_left, text="CẤU HÌNH BÀI TOÁN", font=("Arial", 12, "bold"), bg="white").pack(pady=2)

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

        # CỘT 2:Đ
        self.frame_mid = tk.Frame(root, bg="#f0f0f0", bd=2, relief=tk.RIDGE)
        self.frame_mid.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        tk.Label(self.frame_mid, text="MENU THUẬT TOÁN", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=15)

        list_frame = tk.Frame(self.frame_mid)
        list_frame.pack(fill=tk.BOTH, padx=10, pady=5)

        self.algo_listbox = tk.Listbox(list_frame, font=("Arial", 10), height=8, selectbackground="#a9dfbf",
                                       selectforeground="black")
        scroll_list = tk.Scrollbar(list_frame, orient="vertical", command=self.algo_listbox.yview)
        self.algo_listbox.config(yscrollcommand=scroll_list.set)

        self.algo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_list.pack(side=tk.RIGHT, fill=tk.Y)

        # Thêm Thuật toán số 4 vào Listbox
        algorithms = [
            "1. BFS (Tối ưu)",
            "2. BFS (Nhớ trễ)",
            "3. BFS (Đích trễ)",
            "4. Tìm kiếm Sâu dần (IDS)"
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

        # CỘT 3: NHẬT KÝ TRACE LOG
        self.frame_right = tk.Frame(root, bg="white", bd=2, relief=tk.RIDGE)
        self.frame_right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        tk.Label(self.frame_right, text="NHẬT KÝ CHẠY (TRACE LOG)", font=("Arial", 12, "bold"), bg="white").pack(
            pady=10)
        self.txt_log = scrolledtext.ScrolledText(self.frame_right, font=("Consolas", 11), bg="#1e1e1e", fg="#4af626")
        self.txt_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tu_dien_ten = {}
        self.dem_node = 0
        self.step_counter = 0

    # CÁC HÀM VẼ GIAO DIỆN
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

    def add_history_block(self, curr_node, children_nodes, special_msg=""):
        self.step_counter += 1

        block = tk.Frame(self.scrollable_history, bg="#f9f9f9", bd=1, relief=tk.SOLID)
        block.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(block, text=f"BƯỚC {self.step_counter}: XÉT NODE {curr_node.name} (Độ sâu: {curr_node.depth})",
                 font=("Arial", 10, "bold"),
                 bg="#f9f9f9", fg="blue", anchor="w").pack(fill=tk.X, padx=5, pady=2)

        content_frame = tk.Frame(block, bg="#f9f9f9")
        content_frame.pack(fill=tk.X, padx=5, pady=5)

        parent_frame = tk.Frame(content_frame, bg="#f9f9f9")
        parent_frame.pack(side=tk.LEFT, padx=5)
        self.draw_board(parent_frame, f"Node {curr_node.name}", curr_node.state, "#85c1e9").pack()

        # Xử lý Cutoff hoặc Cycle cho IDS
        if special_msg:
            tk.Label(content_frame, text=f"  ➡\n{special_msg}", font=("Arial", 10, "bold"), bg="#f9f9f9",
                     fg="red").pack(side=tk.LEFT, padx=15)
            self.root.update_idletasks()
            self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all"))
            self.canvas_left.yview_moveto(1)
            time.sleep(0.05)
            return

        tk.Label(content_frame, text=" ➡\nSinh ra", font=("Arial", 9, "bold"), bg="#f9f9f9", fg="gray").pack(
            side=tk.LEFT, padx=5)

        children_frame = tk.Frame(content_frame, bg="#f9f9f9")
        children_frame.pack(side=tk.LEFT, padx=5)

        for child, is_dup in children_nodes:
            color = "gray" if is_dup else "#a9dfbf"
            title = f"{child.name}(Trùng)" if is_dup else f"{child.action} -> {child.name}"
            self.draw_board(children_frame, title, child.state, color).pack(side=tk.LEFT, padx=2)

        self.root.update_idletasks()
        self.canvas_left.configure(scrollregion=self.canvas_left.bbox("all"))
        self.canvas_left.yview_moveto(1)
        time.sleep(0.05)

    # QUẢN LÝ THUẬT TOÁN TỪ LISTBOX BẰNG DICTIONARY DISPATCH
    def on_run_click(self):
        selection = self.algo_listbox.curselection()
        if not selection:
            return

        version = selection[0] + 1
        self.run_algo(version)

    def run_algo(self, version):
        self.txt_log.delete(1.0, tk.END)
        self.lbl_stats.config(text="Đang tính toán...")
        for widget in self.scrollable_history.winfo_children():
            widget.destroy()

        self.tu_dien_ten = {}
        self.dem_node = 0
        self.step_counter = 0

        # TỪ ĐIỂN ĐIỀU PHỐI
        danh_sach_ham = {
            1: self.algo_v1,
            2: self.algo_v2,
            3: self.algo_v3,
            4: self.algo_ids
        }

        ham_can_chay = danh_sach_ham.get(version)
        if not ham_can_chay:
            self.log("Lỗi: Thuật toán chưa được phát triển!")
            return

        algo_name = ["BFS Mã giả 1", "BFS Mã giả 2", "BFS Mã giả 3", "IDS (Tìm kiếm sâu dần)"][version - 1]
        self.log(f"=== KHỞI ĐỘNG: {algo_name} ===\n")

        start_time = time.time()

        # Chạy thuật toán qua hàm điều phối
        result = ham_can_chay()

        # Vì IDS có thể trả về None do bị chặn an toàn
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
            stats_text += f"- Độ sâu đích: {goal_node.depth} bước"

        self.lbl_stats.config(text=stats_text)

        if goal_node:
            self.log(f"\n TÌM THẤY ĐÍCH TẠI NODE {goal_node.name}!")
        else:
            self.log("\n Không tìm thấy đích hoặc quá giới hạn!")

    # CÁC THUẬT TOÁN TÌM KIẾM
    # 4. IDS - TÌM KIẾM SÂU DẦN
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

            # Chốt chặn an toàn cho giao diện UI
            if depth_limit > 10:
                self.log(f"\n Đạt giới hạn an toàn UI (depth > 10). Dừng lại.")
                return None, total_popped, max_f

    def dls(self, start_state, limit):
        root = Node(start_state, node_id=1)
        root.name = self.get_name(root.state)

        # Dùng List như một LIFO Queue (Stack) cho Depth-First
        frontier = [root]
        result = "failure"
        popped = 0
        max_f = 1

        while frontier:
            max_f = max(max_f, len(frontier))
            curr = frontier.pop()  # POP từ đuôi Stack
            popped += 1

            self.log(f"Xét Node {curr.name} (Độ sâu: {curr.depth}):")

            if curr.state == GOAL_STATE:
                return curr, popped, max_f

            if curr.depth >= limit:
                result = "cutoff"
                self.log(f"  -> CẮT (Cutoff) vì đã đạt độ sâu giới hạn {limit}")
                self.add_history_block(curr, [], "Cutoff\n(Giới hạn độ sâu)")
                continue

            if self.is_cycle(curr):
                self.log(f"  -> BỎ QUA vì tạo thành Chu trình (Trùng lặp nhánh)")
                self.add_history_block(curr, [], "Bỏ qua\n(Trùng chu trình)")
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
            if curr.state == node.state:
                return True
            curr = curr.parent
        return False
    # 1. BFS MÃ GIẢ 1
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
    # 2. BFS MÃ GIẢ 2
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
    # 3. BFS MÃ GIẢ 3
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


if __name__ == "__main__":
    root = tk.Tk()
    app = BFSAppDashboard(root)
    root.mainloop()