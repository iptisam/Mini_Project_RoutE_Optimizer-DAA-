"""Route Optimizer - simple Tkinter GUI for Dijkstra's shortest-path algorithm."""
import io
import tkinter as tk
from tkinter import ttk, messagebox
from contextlib import redirect_stdout

from dijkstra import dijkstra, GRAPH, INF

# Fixed positions for drawing the five-location case-study network
POSITIONS = {
    "A": (70, 150),
    "B": (200, 60),
    "C": (200, 240),
    "D": (360, 60),
    "E": (360, 240),
}
RADIUS = 22


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Route Optimizer - Dijkstra's Algorithm")
        self.resizable(False, False)
        self.nodes = list(GRAPH.keys())
        self.build_ui()
        self.draw_graph()

    def build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.grid(row=0, column=0, sticky="ew")

        ttk.Label(top, text="Source:").grid(row=0, column=0, padx=4)
        self.src = ttk.Combobox(top, values=self.nodes, width=4, state="readonly")
        self.src.set("A")
        self.src.grid(row=0, column=1, padx=4)

        ttk.Label(top, text="Destination:").grid(row=0, column=2, padx=4)
        self.dst = ttk.Combobox(top, values=self.nodes, width=4, state="readonly")
        self.dst.set("E")
        self.dst.grid(row=0, column=3, padx=4)

        self.show_trace = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Show step trace", variable=self.show_trace).grid(row=0, column=4, padx=8)

        ttk.Button(top, text="Find Shortest Path", command=self.run).grid(row=0, column=5, padx=4)

        self.canvas = tk.Canvas(self, width=430, height=300, bg="white", highlightthickness=1,
                                highlightbackground="#999")
        self.canvas.grid(row=1, column=0, padx=10)

        self.result = ttk.Label(self, text="Choose source and destination, then click the button.",
                                font=("Segoe UI", 11, "bold"))
        self.result.grid(row=2, column=0, pady=6)

        frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        frame.grid(row=3, column=0)
        self.output = tk.Text(frame, width=62, height=14, font=("Consolas", 9))
        scroll = ttk.Scrollbar(frame, command=self.output.yview)
        self.output.config(yscrollcommand=scroll.set)
        self.output.grid(row=0, column=0)
        scroll.grid(row=0, column=1, sticky="ns")

    def draw_graph(self, path=None):
        c = self.canvas
        c.delete("all")
        path_edges = set()
        if path:
            for a, b in zip(path, path[1:]):
                path_edges.add((a, b))
                path_edges.add((b, a))

        drawn = set()
        for u, neighbours in GRAPH.items():
            for v, w in neighbours:
                if (v, u) in drawn:
                    continue
                drawn.add((u, v))
                x1, y1 = POSITIONS[u]
                x2, y2 = POSITIONS[v]
                on_path = (u, v) in path_edges
                c.create_line(x1, y1, x2, y2, width=4 if on_path else 2,
                              fill="#e63946" if on_path else "#888")
                c.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 8, text=str(w),
                              font=("Segoe UI", 10, "bold"), fill="#1d3557")

        for n, (x, y) in POSITIONS.items():
            on_path = bool(path) and n in path
            c.create_oval(x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS,
                          fill="#e63946" if on_path else "#a8dadc", outline="#1d3557", width=2)
            c.create_text(x, y, text=n, font=("Segoe UI", 12, "bold"),
                          fill="white" if on_path else "#1d3557")

    def run(self):
        source, dest = self.src.get(), self.dst.get()
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                path, cost = dijkstra(GRAPH, source, dest, trace=self.show_trace.get())
        except (KeyError, ValueError) as e:
            messagebox.showerror("Error", str(e))
            return

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, buf.getvalue())

        if path is None:
            self.result.config(text=f"No route from {source} to {dest}.")
            self.draw_graph()
        else:
            self.result.config(text=f"Path: {' -> '.join(path)}    Total cost: {cost}")
            self.draw_graph(path)
            self.output.insert(tk.END, f"\nShortest path: {' -> '.join(path)}\nTotal cost: {cost}\n")


if __name__ == "__main__":
    App().mainloop()
