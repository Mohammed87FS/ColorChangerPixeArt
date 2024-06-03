import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
from PIL import Image, ImageTk
import numpy as np
from colormath.color_objects import sRGBColor, HSVColor
from colormath.color_conversions import convert_color

class ColorChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Changer")

        self.image = None
        self.image_tk = None
        self.original_image = None
        self.selected_color = None
        self.new_color = None
        self.zoom_factor = 1.0

        self.history = []
        self.history_index = -1

        self.setup_gui()

        self.color_picker_enabled = False

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Load and Save Frame
        load_save_frame = ttk.Frame(main_frame, padding="5")
        load_save_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.load_button = ttk.Button(load_save_frame, text="Load Image", command=self.load_image)
        self.load_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.save_button = ttk.Button(load_save_frame, text="Save Image", command=self.save_image)
        self.save_button.grid(row=0, column=1, padx=5, pady=5)

        self.reset_button = ttk.Button(load_save_frame, text="Reset Image", command=self.reset_image)
        self.reset_button.grid(row=0, column=2, padx=5, pady=5)

        # Color Picker Frame
        color_picker_frame = ttk.LabelFrame(main_frame, text="Color Picker", padding="5")
        color_picker_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.pick_color_button = ttk.Button(color_picker_frame, text="Pick Color from Image", command=self.enable_color_picker)
        self.pick_color_button.grid(row=0, column=0, padx=5, pady=5)

        self.new_color_button = ttk.Button(color_picker_frame, text="Pick New Color", command=self.pick_new_color)
        self.new_color_button.grid(row=0, column=1, padx=5, pady=5)

        self.suggest_colors_button = ttk.Button(color_picker_frame, text="Suggest Colors", command=self.suggest_colors)
        self.suggest_colors_button.grid(row=0, column=2, padx=5, pady=5)

        # Process Frame
        process_frame = ttk.Frame(main_frame, padding="5")
        process_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        self.process_button = ttk.Button(process_frame, text="Process Image", command=self.process_image)
        self.process_button.grid(row=0, column=0, padx=5, pady=5)

        self.undo_button = ttk.Button(process_frame, text="Undo", command=self.undo)
        self.undo_button.grid(row=0, column=1, padx=5, pady=5)

        self.redo_button = ttk.Button(process_frame, text="Redo", command=self.redo)
        self.redo_button.grid(row=0, column=2, padx=5, pady=5)

        # Canvas for Image Display
        self.canvas = tk.Canvas(main_frame, background="white")
        self.canvas.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas.bind("<Button-1>", self.pick_color_from_image)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<B1-Motion>", self.pan)

        # Status Bar
        self.status_bar = ttk.Frame(main_frame, padding="5")
        self.status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(self.status_bar, text="Status: Ready", anchor=tk.W)
        self.status_label.grid(row=0, column=0, padx=5)

        self.selected_color_canvas = tk.Canvas(self.status_bar, width=20, height=20, bg='white', highlightthickness=1, highlightbackground="black")
        self.selected_color_canvas.grid(row=0, column=1, padx=5)

        self.new_color_canvas = tk.Canvas(self.status_bar, width=20, height=20, bg='white', highlightthickness=1, highlightbackground="black")
        self.new_color_canvas.grid(row=0, column=2, padx=5)

        # Configure resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
        if file_path:
            self.original_image = Image.open(file_path).convert("RGB")
            self.image = self.original_image.copy()
            self.history = [self.image.copy()]
            self.history_index = 0
            self.display_image()

    def display_image(self):
        self.image_tk = ImageTk.PhotoImage(self.image.resize((int(self.image.width * self.zoom_factor), int(self.image.height * self.zoom_factor))))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.status_label.config(text=f"Status: Zoom factor {self.zoom_factor:.1f}")

    def enable_color_picker(self):
        self.color_picker_enabled = True
        self.status_label.config(text="Status: Click on the image to pick a color.")

    def pick_color_from_image(self, event):
        if self.color_picker_enabled and self.image:
            x = int(event.x / self.zoom_factor)
            y = int(event.y / self.zoom_factor)
            self.selected_color = self.image.getpixel((x, y))
            self.color_picker_enabled = False
            self.status_label.config(text=f"Status: Selected color {self.selected_color}")
            self.update_color_preview(self.selected_color_canvas, self.selected_color)

    def pick_new_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            self.new_color = tuple(int(c) for c in color)
            self.status_label.config(text=f"Status: New color {self.new_color}")
            self.update_color_preview(self.new_color_canvas, self.new_color)

    def suggest_colors(self):
        if self.selected_color:
            suggested_colors = self.get_suggested_colors(self.selected_color)
            self.show_suggested_colors(suggested_colors)
        else:
            messagebox.showerror("Error", "Please select a color from the image first.")

    def get_suggested_colors(self, color):
        rgb_color = sRGBColor(color[0], color[1], color[2])
        hsv_color = convert_color(rgb_color, HSVColor)
        
        complementary_color = HSVColor((hsv_color.hsv_h + 180) % 360, hsv_color.hsv_s, hsv_color.hsv_v)
        triadic_color_1 = HSVColor((hsv_color.hsv_h + 120) % 360, hsv_color.hsv_s, hsv_color.hsv_v)
        triadic_color_2 = HSVColor((hsv_color.hsv_h + 240) % 360, hsv_color.hsv_s, hsv_color.hsv_v)
        
        complementary_color_rgb = convert_color(complementary_color, sRGBColor)
        triadic_color_1_rgb = convert_color(triadic_color_1, sRGBColor)
        triadic_color_2_rgb = convert_color(triadic_color_2, sRGBColor)
        
        return [
            (int(complementary_color_rgb.rgb_r), int(complementary_color_rgb.rgb_g), int(complementary_color_rgb.rgb_b)),
            (int(triadic_color_1_rgb.rgb_r), int(triadic_color_1_rgb.rgb_g), int(triadic_color_1_rgb.rgb_b)),
            (int(triadic_color_2_rgb.rgb_r), int(triadic_color_2_rgb.rgb_g), int(triadic_color_2_rgb.rgb_b)),
        ]

    def show_suggested_colors(self, colors):
        suggestion_window = tk.Toplevel(self.root)
        suggestion_window.title("Suggested Colors")
        suggestion_frame = ttk.Frame(suggestion_window, padding="10")
        suggestion_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        for i, color in enumerate(colors):
            color_canvas = tk.Canvas(suggestion_frame, width=50, height=50, bg='#%02x%02x%02x' % color, highlightthickness=1, highlightbackground="black")
            color_canvas.grid(row=0, column=i, padx=5)
            color_canvas.bind("<Button-1>", lambda e, col=color: self.set_new_color(col))
        
    def set_new_color(self, color):
        self.new_color = color
        self.status_label.config(text=f"Status: New color {self.new_color}")
        self.update_color_preview(self.new_color_canvas, self.new_color)

    def process_image(self):
        if self.image and self.selected_color and self.new_color:
            img_np = np.array(self.image)
            selected_color_np = np.array(self.selected_color)
            new_color_np = np.array(self.new_color)

            mask = np.all(img_np[:, :, :3] == selected_color_np, axis=-1)
            img_np[mask] = new_color_np

            self.image = Image.fromarray(img_np)
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.image.copy())
            self.history_index += 1
            self.display_image()
        else:
            messagebox.showerror("Error", "Please load an image and select both colors.")

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            if file_path:
                self.image.save(file_path)
                messagebox.showinfo("Info", "Image saved successfully.")
        else:
            messagebox.showerror("Error", "No image to save. Please process an image first.")

    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.history = [self.image.copy()]
            self.history_index = 0
            self.display_image()

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.display_image()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.display_image()

    def zoom(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        self.display_image()

    def pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def update_color_preview(self, canvas, color):
        hex_color = "#%02x%02x%02x" % color
        canvas.config(bg=hex_color)

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorChangerApp(root)
    root.mainloop()
