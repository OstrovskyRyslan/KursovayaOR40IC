import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar
import datetime
import json
import winsound  # Для звуковых уведомлений

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Календар з нагадуваннями")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        self.events = {}  # Словник для збереження подій
        self.load_events()  # Загружаємо події з файлу при запуску програми
        self.is_dark_mode = False  # Стандартный режим - светлый

        # Стиль оформления
        self.root.configure(bg="#d4e8d4")  # Светло-зеленый фон

        # Заголовок
        header = tk.Label(root, text="📅 Мій Календар", font=("Helvetica", 20, "bold"), bg="#4CAF50", fg="white")
        header.pack(fill="x", pady=10)  # Добавили отступ вниз

        # Рамка для календаря без белой линии
        self.cal_frame = tk.Frame(root, bg="#d4e8d4")  # Убираем лишнюю рамку
        self.cal_frame.pack(pady=10)  # Добавили отступ вниз
        self.cal = Calendar(
            self.cal_frame, 
            selectmode="day", 
            date_pattern="yyyy-mm-dd",
            locale="uk",  # Локализация на украинский
            background="lightblue", 
            foreground="black", 
            bordercolor="lightblue"  # Используем тот же цвет для границы
        )
        self.cal.pack()

        # Подсветка текущей даты
        self.today_date = datetime.date.today()
        self.cal.calevent_create(self.today_date, "Сьогодні", "today")

        # Поле для введения событий
        self.event_frame = tk.Frame(root, bg="#d4e8d4")
        self.event_frame.pack(pady=10)

        self.event_label = tk.Label(self.event_frame, text="Опис події:", font=("Helvetica", 12), bg="#d4e8d4")
        self.event_label.grid(row=0, column=0, padx=5, pady=5)

        self.event_entry = ttk.Entry(self.event_frame, width=30, font=("Helvetica", 12))
        self.event_entry.grid(row=0, column=1, padx=5)
        self.event_entry.insert(0, "Введіть опис події")

        # Тип події (важность)
        self.event_type_label = tk.Label(self.event_frame, text="Тип події:", font=("Helvetica", 12), bg="#d4e8d4")
        self.event_type_label.grid(row=1, column=0, padx=5, pady=5)

        self.event_type = ttk.Combobox(self.event_frame, values=["Звичайна", "Важлива", "Термінова"], font=("Helvetica", 12))
        self.event_type.grid(row=1, column=1, padx=5)
        self.event_type.set("Звичайна")

        # Кнопки с отступами
        self.button_frame = tk.Frame(root, bg="#d4e8d4")
        self.button_frame.pack(pady=10)

        self.add_button = ttk.Button(self.button_frame, text="➕ Додати подію", command=self.add_event)
        self.add_button.grid(row=0, column=0, padx=10, pady=5)

        self.show_button = ttk.Button(self.button_frame, text="📜 Показати події", command=self.show_events)
        self.show_button.grid(row=0, column=1, padx=10, pady=5)

        self.remove_button = ttk.Button(self.button_frame, text="❌ Видалити подію", command=self.remove_event)
        self.remove_button.grid(row=0, column=2, padx=10, pady=5)

        self.edit_button = ttk.Button(self.button_frame, text="✏️ Редагувати подію", command=self.edit_event)
        self.edit_button.grid(row=1, column=0, padx=10, pady=5)

        # Новая кнопка для пометки події как выполненной
        self.complete_button = ttk.Button(self.button_frame, text="✔️ Завершити подію", command=self.complete_event)
        self.complete_button.grid(row=1, column=1, padx=10, pady=5)

        self.save_edit_button = None  # Место для кнопки "Зберегти зміни"

        # Переносим кнопку поиска в нижнюю часть
        self.search_frame = tk.Frame(root, bg="#d4e8d4")
        self.search_frame.pack(pady=10)

        self.search_entry = ttk.Entry(self.search_frame, width=20, font=("Helvetica", 12))
        self.search_entry.grid(row=0, column=0, padx=10)
        self.search_button = ttk.Button(self.search_frame, text="🔍 Пошук", command=self.search_event)
        self.search_button.grid(row=0, column=1, padx=10)

        # Список подій
        self.list_frame = tk.Frame(root, bg="#e6ffe6", bd=2, relief="groove")  # Светло-зеленый фон
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.list_label = tk.Label(self.list_frame, text="Список подій:", bg="#e6ffe6", font=("Helvetica", 14))
        self.list_label.pack(anchor="nw", padx=5, pady=5)

        self.event_list = tk.Listbox(
            self.list_frame, 
            font=("Helvetica", 12), 
            bg="#f9fff9",  # Светлый фон для списка
            selectbackground="#b3ffb3",  # Цвет при выделении элемента
            selectforeground="black", 
            height=10
        )
        self.event_list.pack(fill="both", expand=True, padx=5, pady=5)

        # Включение звукового уведомления
        self.root.after(1000, self.daily_check)

    def add_event(self):
        date = self.cal.get_date()
        event = self.event_entry.get()
        event_type = self.event_type.get()

        if date and event and event.strip() != "":
            if date in self.events:
                self.events[date].append((event, event_type, False))  # False означает, что подія еще не выполнена
            else:
                self.events[date] = [(event, event_type, False)]
            messagebox.showinfo("Успіх", f"Подія '{event}' додана на {date}!")
            self.event_entry.delete(0, tk.END)
            self.update_event_list()
            self.colorize_calendar()
            self.save_events()
        else:
            messagebox.showerror("Помилка", "Будь ласка, виберіть дату та введіть подію.")

    def complete_event(self):
        selected_event = self.event_list.curselection()
        if selected_event:
            event_info = self.event_list.get(selected_event)
            date = event_info.split(":")[0].strip()
            event_name = event_info.split(":")[1].split("(")[0].strip()

            # Отметить подію как выполненную
            if date in self.events:
                for idx, (e, et, completed) in enumerate(self.events[date]):
                    if e == event_name and not completed:
                        self.events[date][idx] = (e, et, True)  # Помечаем как завершенную
                        self.update_event_list()
                        self.colorize_calendar()
                        messagebox.showinfo("Успіх", f"Подія '{event_name}' на {date} була виконана!")
                        self.save_events()
                        break
                else:
                    messagebox.showinfo("Інформація", "Ця подія вже виконана.")
        else:
            messagebox.showerror("Помилка", "Будь ласка, виберіть подію для завершення.")

    def show_events(self):
        date = self.cal.get_date()
        if date in self.events:
            events = "\n".join([f"{event[0]} ({event[1]}) {'✔️' if event[2] else '❌'}" for event in self.events[date]])
            messagebox.showinfo("Події", f"Події на {date}:\n{events}")
        else:
            messagebox.showinfo("Події", f"На {date} немає подій.")

    def remove_event(self):
        selected_event = self.event_list.curselection()
        if selected_event:
            event_info = self.event_list.get(selected_event)
            date = event_info.split(":")[0].strip()
            event_name = event_info.split(":")[1].split("(")[0].strip()

            if date in self.events:
                self.events[date] = [e for e in self.events[date] if e[0] != event_name]
                self.update_event_list()
                self.colorize_calendar()
                self.save_events()
                messagebox.showinfo("Успіх", f"Подія '{event_name}' була видалена.")
        else:
            messagebox.showerror("Помилка", "Будь ласка, виберіть подію для видалення.")

    def edit_event(self):
        selected_event = self.event_list.curselection()
        if selected_event:
            event_info = self.event_list.get(selected_event)
            date = event_info.split(":")[0].strip()
            event_name = event_info.split(":")[1].split("(")[0].strip()
            event_type = event_info.split("(")[1][:-1]

            self.event_entry.delete(0, tk.END)
            self.event_entry.insert(0, event_name)
            self.event_type.set(event_type)

            if self.save_edit_button is None:  # Проверяем, чтобы кнопка не была создана повторно
                self.save_edit_button = ttk.Button(self.button_frame, text="Зберегти зміни", command=lambda: self.save_edited_event(date, event_name))
                self.save_edit_button.grid(row=1, column=2, padx=10, pady=5)
        else:
            messagebox.showerror("Помилка", "Будь ласка, виберіть подію для редагування.")

    def save_edited_event(self, date, old_event_name):
        new_event = self.event_entry.get().strip()
        new_event_type = self.event_type.get()

        if new_event != "":
            for idx, (event, event_type, completed) in enumerate(self.events[date]):
                if event == old_event_name:
                    self.events[date][idx] = (new_event, new_event_type, completed)
                    self.update_event_list()
                    self.colorize_calendar()
                    self.save_events()
                    messagebox.showinfo("Успіх", f"Подія '{old_event_name}' була змінена на '{new_event}'.")
                    break

    def search_event(self):
        query = self.search_entry.get().strip().lower()
        results = []
        for date, events in self.events.items():
            for event, event_type, completed in events:
                if query in event.lower():
                    results.append(f"{date}: {event} ({event_type}) {'✔️' if completed else '❌'}")

        if results:
            messagebox.showinfo("Результати пошуку", "\n".join(results))
        else:
            messagebox.showinfo("Результати пошуку", "Нічого не знайдено.")

    def daily_check(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today in self.events:
            events = "\n".join([f"{event[0]} ({event[1]}) {'✔️' if event[2] else '❌'}" for event in self.events[today]])
            messagebox.showinfo("Нагадування", f"Сьогоднішні події:\n{events}")
            winsound.Beep(1000, 1000)  # Звуковое уведомление
        self.root.after(86400000, self.daily_check)

    def update_event_list(self):
        self.event_list.delete(0, tk.END)
        for date, events in sorted(self.events.items()):
            for event, event_type, completed in events:
                color = "lightgreen" if event_type == "Звичайна" else "yellow" if event_type == "Важлива" else "red"
                self.event_list.insert(tk.END, f"{date}: {event} ({event_type}) {'✔️' if completed else '❌'}")
                self.event_list.itemconfig(tk.END, {'bg': color})

    def colorize_calendar(self):
        for date, events in self.events.items():
            for event, event_type, completed in events:
                color = "green" if event_type == "Звичайна" else "yellow" if event_type == "Важлива" else "red"
                self.cal.calevent_create(date, event, event_type)
                self.cal.tag_configure(event_type, background=color)

    def save_events(self):
        with open("events.json", "w", encoding="utf-8") as file:
            json.dump(self.events, file, ensure_ascii=False, indent=4)

    def load_events(self):
        try:
            with open("events.json", "r", encoding="utf-8") as file:
                self.events = json.load(file)
        except FileNotFoundError:
            self.events = {}

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()