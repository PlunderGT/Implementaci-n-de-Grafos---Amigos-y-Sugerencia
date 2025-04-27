import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from collections import deque
import math

class Graph:
    def __init__(self):
        self.graph = {}

    def add_user(self, user):
        if user not in self.graph:
            self.graph[user] = []

    def connect_users(self, user1, user2):
        if user1 in self.graph and user2 in self.graph:
            if user2 not in self.graph[user1]:
                self.graph[user1].append(user2)
            if user1 not in self.graph[user2]:
                self.graph[user2].append(user1)

    def get_friends(self, user):
        return self.graph.get(user, [])

    def bfs_suggestions(self, user):
        if user not in self.graph:
            return []

        visited = {user}
        queue = deque([(user, 0)])  
        suggestions = set()

        while queue:
            current_user, level = queue.popleft()
            if level < 2:  
                for friend in self.graph[current_user]:
                    if friend not in visited:
                        visited.add(friend)
                        queue.append((friend, level + 1))
                        if level == 1:  
                            suggestions.add(friend)

        for friend in self.graph[user]:
            suggestions.discard(friend)

        suggestions.discard(user) 
        return list(suggestions)


class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title, prompt1, prompt2):
        self.prompt1 = prompt1
        self.prompt2 = prompt2
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt1).grid(row=0)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=0, column=1)

        tk.Label(master, text=self.prompt2).grid(row=1)
        self.e2 = tk.Entry(master)
        self.e2.grid(row=1, column=1)

        return self.e1  

    def apply(self):
        user1 = self.e1.get().strip()
        user2 = self.e2.get().strip()
        self.result = (user1, user2)


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafo de Amigos")
        self.graph = Graph()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, width=800, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.selected_user = None
        self.background_image = None  

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X)

        self.add_user_button = tk.Button(button_frame, text="Agregar Usuario", command=self.add_user)
        self.add_user_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.connect_users_button = tk.Button(button_frame, text="Conectar Usuarios", command=self.connect_users)
        self.connect_users_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.show_friends_button = tk.Button(button_frame, text="Ver Amigos", command=self.show_friends)
        self.show_friends_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.show_suggestions_button = tk.Button(button_frame, text="Sugerencias de Amistad",
                                                 command=self.show_suggestions)
        self.show_suggestions_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.set_background_button = tk.Button(button_frame, text="Establecer Fondo", command=self.set_background)
        self.set_background_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.result_panel = tk.Text(root, height=10, width=50)
        self.result_panel.pack(fill=tk.X, padx=5, pady=5)

        self.user_positions = {}  
    def add_user(self):
        user = simpledialog.askstring("Agregar Usuario", "Nombre del usuario:")
        if user:
            user = user.strip()  
            if user:
                self.graph.add_user(user)
                self.draw_graph()
            else:
                messagebox.showwarning("Advertencia", "El nombre del usuario no puede estar vacío.")

    def connect_users(self):
        dialog = CustomDialog(self.root, "Conectar Usuarios",
                              "Nombre del primer usuario:",
                              "Nombre del segundo usuario:")

        if dialog.result:
            user1, user2 = dialog.result
            if user1 and user2:
                if user1 in self.graph.graph and user2 in self.graph.graph:
                    self.graph.connect_users(user1, user2)
                    self.draw_graph()
                else:
                    messagebox.showwarning("Advertencia", "Ambos usuarios deben existir en el grafo.")
            else:
                messagebox.showwarning("Advertencia", "Ambos campos deben ser completados.")

    def show_friends(self):
        if self.selected_user:
            friends = self.graph.get_friends(self.selected_user)
            self.result_panel.delete(1.0, tk.END)
            self.result_panel.insert(tk.END, f"Amigos de {self.selected_user}: {friends}\n")
        else:
            messagebox.showwarning("Advertencia", "Selecciona un usuario primero.")

    def show_suggestions(self):
        if self.selected_user:
            suggestions = self.graph.bfs_suggestions(self.selected_user)
            self.result_panel.delete(1.0, tk.END)
            self.result_panel.insert(tk.END, f"Sugerencias para {self.selected_user}: {suggestions}\n")
        else:
            messagebox.showwarning("Advertencia", "Selecciona un usuario primero.")

    def set_background(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen de fondo",
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )

        if file_path:
            try:
                
                original_image = Image.open(file_path)
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()

               
                if canvas_width <= 1:
                    canvas_width = 800
                if canvas_height <= 1:
                    canvas_height = 600

                resized_image = original_image.resize((canvas_width, canvas_height), Image.LANCZOS)
                self.background_image = ImageTk.PhotoImage(resized_image)

                self.draw_graph()

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")

    def on_canvas_click(self, event):
        
        x, y = event.x, event.y
        for user, (ux, uy) in self.user_positions.items():
           
            if (x - ux) ** 2 + (y - uy) ** 2 <= 20 ** 2:
                self.selected_user = user
                self.highlight_user(user)
                return

    def draw_graph(self):
      
        self.canvas.delete("all")


        if self.background_image:
            self.canvas.create_image(0, 0, image=self.background_image, anchor=tk.NW)

        self.user_positions = {}

        
        num_users = len(self.graph.graph)
        if num_users == 0:
            return

        radius = 200  
        angle_step = 360 / num_users

  
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600

        center_x = canvas_width / 2
        center_y = canvas_height / 2

        for i, user in enumerate(self.graph.graph.keys()):
            angle = i * angle_step
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            self.user_positions[user] = (x, y)

        for user, friends in self.graph.graph.items():
            for friend in friends:
                if user < friend:  
                    ux, uy = self.user_positions[user]
                    fx, fy = self.user_positions[friend]
                    self.canvas.create_line(ux, uy, fx, fy, fill='black', width=2)

        for user, (x, y) in self.user_positions.items():
            if self.selected_user == user:
   
                self.canvas.create_oval(x - 22, y - 22, x + 22, y + 22, fill='yellow', outline='black', width=2)
                self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill='white', outline='black', width=1)
            else:

                self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill='white', outline='black', width=1)

            self.canvas.create_text(x, y, text=user, font=('Arial', 10, 'bold'))

    def highlight_user(self, user):
        self.draw_graph()  #
if __name__ == "__main__":
    try:
     
        from PIL import Image, ImageTk
    except ImportError:
        messagebox.showwarning("Advertencia",
                               "La biblioteca PIL/Pillow no está instalada. La funcionalidad de imagen de fondo no estará disponible.\n"
                               "Instala PIL con: pip install pillow")

    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
