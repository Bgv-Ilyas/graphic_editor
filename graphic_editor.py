import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox


class GraphicEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Графический редактор курсовой работы")
        self.geometry("1000x700")

        self.current_color = "#000000"
        self.brush_size = 3
        # pencil | eraser | line | rect | oval
        self.current_tool = "pencil"

        # Для рисования
        self.last_x = None
        self.last_y = None
        self.shape_start_x = None
        self.shape_start_y = None
        self.preview_item = None

        # Стек действий для Undo (Ctrl+Z)
        self.undo_stack: list[list[int]] = []
        self.current_action_items: list[int] = []

        self._build_ui()

    def _build_ui(self):
        # Меню
        self._build_menu()

        # Верхняя панель инструментов
        toolbar = tk.Frame(self, bd=2, relief=tk.RIDGE)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Панель выбора инструмента
        tools_frame = tk.Frame(toolbar)
        tools_frame.pack(side=tk.LEFT, padx=4, pady=4)

        tk.Label(tools_frame, text="Инструменты:").pack(side=tk.TOP, anchor=tk.W)

        btn_row = tk.Frame(tools_frame)
        btn_row.pack(side=tk.TOP)

        tk.Button(btn_row, text="Карандаш", command=self.set_pencil).pack(
            side=tk.LEFT, padx=1
        )
        tk.Button(btn_row, text="Ластик", command=self.set_eraser).pack(
            side=tk.LEFT, padx=1
        )
        tk.Button(btn_row, text="Линия", command=self.set_line).pack(
            side=tk.LEFT, padx=1
        )
        tk.Button(btn_row, text="Прямоугольник", command=self.set_rect).pack(
            side=tk.LEFT, padx=1
        )
        tk.Button(btn_row, text="Овал", command=self.set_oval).pack(
            side=tk.LEFT, padx=1
        )

        # Компактная панель выбора цвета: одна кнопка "Цвет"
        color_frame = tk.Frame(toolbar)
        color_frame.pack(side=tk.LEFT, padx=8, pady=4)

        tk.Button(color_frame, text="Цвет", command=self.choose_color).pack(
            side=tk.TOP, padx=2
        )

        # Размер кисти
        size_frame = tk.Frame(toolbar)
        size_frame.pack(side=tk.LEFT, padx=8, pady=4)

        tk.Label(size_frame, text="Размер кисти:").pack(side=tk.TOP, anchor=tk.W)

        self.size_scale = tk.Scale(
            size_frame, from_=1, to=30, orient=tk.HORIZONTAL, command=self.on_size_change
        )
        self.size_scale.set(self.brush_size)
        self.size_scale.pack(side=tk.TOP)

        # Действия
        actions_frame = tk.Frame(toolbar)
        actions_frame.pack(side=tk.LEFT, padx=8, pady=4)

        tk.Button(actions_frame, text="Очистить", command=self.clear_canvas).pack(
            side=tk.LEFT, padx=4
        )
        tk.Button(actions_frame, text="Отменить", command=self.undo_last_action).pack(
            side=tk.LEFT, padx=4
        )
        tk.Button(actions_frame, text="Сохранить .ps", command=self.save_canvas_ps).pack(
            side=tk.LEFT, padx=4
        )

        # Холст для рисования
        self.canvas = tk.Canvas(
            self,
            bg="#ffffff",
            cursor="cross",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Привязка событий мыши
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Горячая клавиша Undo
        self.bind_all("<Control-z>", lambda event: self.undo_last_action())

        # Строка состояния
        self.status_var = tk.StringVar()
        self.status_var.set("Готово. Инструмент: карандаш")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=8,
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый холст", command=self.clear_canvas)
        file_menu.add_separator()
        file_menu.add_command(
            label="Сохранить как .ps", command=self.save_canvas_ps
        )
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(
            label="Сменить цвет фона холста", command=self.change_background_color
        )
        menubar.add_cascade(label="Вид", menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    # --- Инструменты ---
    def set_pencil(self):
        self.current_tool = "pencil"
        self.status_var.set("Инструмент: карандаш")

    def set_eraser(self):
        self.current_tool = "eraser"
        self.status_var.set("Инструмент: ластик")

    def set_line(self):
        self.current_tool = "line"
        self.status_var.set("Инструмент: линия")

    def set_rect(self):
        self.current_tool = "rect"
        self.status_var.set("Инструмент: прямоугольник")

    def set_oval(self):
        self.current_tool = "oval"
        self.status_var.set("Инструмент: овал")

    def choose_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)[1]
        if color:
            self.current_color = color
            if self.current_tool == "eraser":
                self.current_tool = "pencil"
                self.status_var.set("Инструмент: карандаш")
            else:
                self.status_var.set(f"Текущий цвет: {color}")

    def on_size_change(self, value):
        self.brush_size = int(value)

    def clear_canvas(self):
        # Сохраняем текущее состояние для Undo
        all_items = list(self.canvas.find_all())
        if all_items:
            self.undo_stack.append(all_items)
        self.canvas.delete("all")
        self.status_var.set("Холст очищен")

    def undo_last_action(self):
        if not self.undo_stack:
            self.status_var.set("Нет действий для отмены")
            return
        last_items = self.undo_stack.pop()
        for item in last_items:
            try:
                self.canvas.delete(item)
            except Exception:
                pass
        self.status_var.set("Отмена последнего действия")

    def change_background_color(self):
        color = colorchooser.askcolor(initialcolor="#ffffff")[1]
        if color:
            self.canvas.configure(bg=color)
            self.status_var.set(f"Цвет фона: {color}")

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Графический редактор для курсовой работы\n"
            "Тема: \"Разработка графического редактора\".\n"
            "Поддерживает рисование, фигуры, выбор цвета и сохранение рисунка.",
        )

    # --- Рисование ---
    def on_mouse_down(self, event):
        self.last_x = event.x
        self.last_y = event.y
        self.shape_start_x = event.x
        self.shape_start_y = event.y
        self.current_action_items = []

        if self.current_tool in {"line", "rect", "oval"} and self.preview_item is not None:
            self.canvas.delete(self.preview_item)
            self.preview_item = None

    def on_mouse_move(self, event):
        if self.last_x is None or self.last_y is None:
            return

        if self.current_tool in {"pencil", "eraser"}:
            color = "white" if self.current_tool == "eraser" else self.current_color
            item_id = self.canvas.create_line(
                self.last_x,
                self.last_y,
                event.x,
                event.y,
                fill=color,
                width=self.brush_size,
                capstyle=tk.ROUND,
                smooth=True,
            )
            self.current_action_items.append(item_id)
            self.last_x = event.x
            self.last_y = event.y
        elif self.current_tool in {"line", "rect", "oval"}:
            if self.preview_item is not None:
                self.canvas.delete(self.preview_item)

            color = self.current_color
            if self.current_tool == "line":
                self.preview_item = self.canvas.create_line(
                    self.shape_start_x,
                    self.shape_start_y,
                    event.x,
                    event.y,
                    fill=color,
                    width=self.brush_size,
                )
            elif self.current_tool == "rect":
                self.preview_item = self.canvas.create_rectangle(
                    self.shape_start_x,
                    self.shape_start_y,
                    event.x,
                    event.y,
                    outline=color,
                    width=self.brush_size,
                )
            elif self.current_tool == "oval":
                self.preview_item = self.canvas.create_oval(
                    self.shape_start_x,
                    self.shape_start_y,
                    event.x,
                    event.y,
                    outline=color,
                    width=self.brush_size,
                )

    def on_mouse_up(self, event):
        if self.current_tool in {"line", "rect", "oval"}:
            if self.preview_item is not None:
                self.canvas.delete(self.preview_item)
                self.preview_item = None

            color = self.current_color
            if self.current_tool == "line":
                item_id = self.canvas.create_line(
                    self.shape_start_x,
                    self.shape_start_y,
                    event.x,
                    event.y,
                    fill=color,
                    width=self.brush_size,
                )
            elif self.current_tool == "rect":
                item_id = self.canvas.create_rectangle(
                    self.shape_start_x,
                    self.shape_start_y,
                    event.x,
                    event.y,
                    outline=color,
                    width=self.brush_size,
                )
            elif self.current_tool == "oval":
                item_id = self.canvas.create_oval(
                    self.shape_start_x,
                    self.shape_start_y,
                    event.x,
                    event.y,
                    outline=color,
                    width=self.brush_size,
                )
            else:
                item_id = None

            if item_id is not None:
                self.current_action_items.append(item_id)

        if self.current_action_items:
            self.undo_stack.append(self.current_action_items)

        self.last_x = None
        self.last_y = None
        self.shape_start_x = None
        self.shape_start_y = None

    # --- Сохранение ---
    def save_canvas_ps(self):
        """
        Сохраняет рисунок в формате PostScript (.ps).
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ps",
            filetypes=[("PostScript", "*.ps"), ("Все файлы", "*.*")],
            title="Сохранить рисунок как",
        )
        if not file_path:
            return

        try:
            self.canvas.postscript(file=file_path, colormode="color")
            messagebox.showinfo(
                "Сохранение", f"Рисунок сохранён в PostScript-файл:\n{file_path}"
            )
            self.status_var.set(f"Сохранено как .ps: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить рисунок:\n{e}")


def main():
    app = GraphicEditor()
    app.mainloop()


if __name__ == "__main__":
    main()


