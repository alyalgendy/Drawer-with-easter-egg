import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

class PainterApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Painter App")
		
		self.color = "black"
		self.brush_size = 5
		self.image_modified = False
		
		self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
		self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
		
		self.canvas.bind("<B1-Motion>", self.paint)
		self.canvas.bind("<ButtonRelease-1>", self.reset)
		
		self.toolbar = tk.Frame(self.root)
		self.toolbar.pack(side=tk.LEFT, fill=tk.Y)
		
		self.color_button = tk.Button(self.toolbar, text="Color", command=self.choose_color)
		self.color_button.pack(pady=5)
		
		self.eraser_button = tk.Button(self.toolbar, text="Eraser", command=self.use_eraser)
		self.eraser_button.pack(pady=5)
		
		self.pen_button = tk.Button(self.toolbar, text="Pen", command=self.use_pen)
		self.pen_button.pack(pady=5)
		
		self.bucket_button = tk.Button(self.toolbar, text="Bucket", command=self.use_bucket)
		self.bucket_button.pack(pady=5)
		
		self.text_button = tk.Button(self.toolbar, text="Text", command=self.use_text)
		self.text_button.pack(pady=5)
		
		self.clear_button = tk.Button(self.toolbar, text="Clear All", command=self.clear_all)
		self.clear_button.pack(pady=5)
		
		self.size_scale = tk.Scale(self.toolbar, from_=1, to=10, orient=tk.HORIZONTAL, label="Brush Size")
		self.size_scale.set(self.brush_size)
		self.size_scale.pack(pady=5)
		
		self.text_entry = tk.Entry(self.toolbar)
		self.text_entry.pack(pady=5)
		
		self.create_color_buttons()
		
		self.image = Image.new("RGB", (800, 600), "white")
		self.draw = ImageDraw.Draw(self.image)
		
		self.create_menu()
		
		self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
		
		self.undo_stack = []
		self.redo_stack = []
		
		self.root.bind("<Control-z>", self.undo)
		self.root.bind("<Control-y>", self.redo)
		
		self.last_x, self.last_y = None, None
		
	def create_menu(self):
		menubar = tk.Menu(self.root)
		file_menu = tk.Menu(menubar, tearoff=0)
		file_menu.add_command(label="Save", command=self.save_image)
		file_menu.add_command(label="Save As", command=self.save_as_image)
		file_menu.add_command(label="Open", command=self.open_image)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self.on_closing)
		menubar.add_cascade(label="File", menu=file_menu)
		self.root.config(menu=menubar)
		
	def create_color_buttons(self):
		colors = ["black", "red", "green", "blue", "yellow", "purple", "orange", "brown", "pink", "gray"]
		for color in colors:
			button = tk.Button(self.toolbar, bg=color, width=2, command=lambda c=color: self.set_color(c))
			button.pack(pady=2)
		
	def set_color(self, color):
		self.color = color
		
	def choose_color(self):
		self.color = colorchooser.askcolor(color=self.color)[1]
		
	def use_eraser(self):
		self.canvas.bind("<B1-Motion>", self.erase)
		
	def use_pen(self):
		self.canvas.bind("<B1-Motion>", self.paint)
		
	def use_bucket(self):
		self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(), fill=self.color, outline=self.color)
		self.draw.rectangle([0, 0, self.canvas.winfo_width(), self.canvas.winfo_height()], fill=self.color)
		self.image_modified = True
		self.save_state()
		
	def use_text(self):
		self.canvas.bind("<Button-1>", self.draw_text)
		
	def draw_text(self, event):
		text = self.text_entry.get()
		if text == "DsMans0021":
			messagebox.showinfo("Easter Egg", "You found the easter egg. You are great")
		else:
			self.canvas.create_text(event.x, event.y, text=text, fill=self.color, font=("Arial", self.brush_size * 2))
			self.draw.text((event.x, event.y), text, fill=self.color, font=None)
			self.image_modified = True
			self.save_state()
		
	def paint(self, event):
		self.brush_size = self.size_scale.get()
		if self.last_x and self.last_y:
			self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, fill=self.color, width=self.brush_size)
			self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.color, width=self.brush_size)
		self.last_x, self.last_y = event.x, event.y
		self.image_modified = True
		self.save_state()
		
	def reset(self, event):
		self.last_x, self.last_y = None, None
		
	def erase(self, event):
		self.brush_size = self.size_scale.get()
		x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
		x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
		items = self.canvas.find_overlapping(x1, y1, x2, y2)
		for item in items:
			self.canvas.delete(item)
		self.image_modified = True
		self.save_state()
		
	def clear_all(self):
		self.canvas.delete("all")
		self.image = Image.new("RGB", (self.canvas.winfo_width(), self.canvas.winfo_height()), "white")
		self.draw = ImageDraw.Draw(self.image)
		self.image_modified = True
		self.save_state()
		
	def save_image(self):
		self.image.save("output.png")
		self.image_modified = False
		
	def save_as_image(self):
		file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
		if file_path:
			self.image.save(file_path)
			self.image_modified = False
		
	def open_image(self):
		file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
		if file_path:
			self.image = Image.open(file_path)
			self.draw = ImageDraw.Draw(self.image)
			self.canvas_image = ImageTk.PhotoImage(self.image)
			self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
			self.canvas.image = self.canvas_image
			self.image_modified = False
			self.save_state()
			
	def on_closing(self):
		if self.image_modified:
			if messagebox.askokcancel("Quit", "Do you want to save your changes before quitting?"):
				self.save_as_image()
		self.root.destroy()
		
	def save_state(self):
		self.undo_stack.append(self.image.copy())
		self.redo_stack.clear()
		
	def undo(self, event=None):
		if self.undo_stack:
			self.redo_stack.append(self.image.copy())
			self.image = self.undo_stack.pop()
			self.draw = ImageDraw.Draw(self.image)
			self.canvas_image = ImageTk.PhotoImage(self.image)
			self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
			self.canvas.image = self.canvas_image
			self.image_modified = True
		
	def redo(self, event=None):
		if self.redo_stack:
			self.undo_stack.append(self.image.copy())
			self.image = self.redo_stack.pop()
			self.draw = ImageDraw.Draw(self.image)
			self.canvas_image = ImageTk.PhotoImage(self.image)
			self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
			self.canvas.image = self.canvas_image
			self.image_modified = True

if __name__ == "__main__":
	root = tk.Tk()
	app = PainterApp(root)
	root.mainloop()
