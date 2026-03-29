import io
import os

import tkinter as tk
from tkinter import filedialog, messagebox

import fitz
from PIL import Image, ImageTk
from PyPDF2 import PdfReader, PdfWriter


class PDFManager:
    # Default Values: Preview Size, Color, Pad
    PREVIEW_W = 320
    PREVIEW_H = 452

    PINK = "#FF8C9B"
    GRAY = "#E6E6E6"
    PAD = 5

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Page Selector")
        self.root.configure(bg=PDFManager.PINK)

        self.pdf_path = ""
        self.pdf_doc = None
        self.selected_indices = []
        
        # --- Top Section: File Selection ---
        top_frame = tk.Frame(self.root, bg=PDFManager.PINK)
        top_frame.pack(side="top", fill="x", padx=PDFManager.PAD, pady=(PDFManager.PAD, 0))

        self.btn_select = tk.Button(top_frame, text="Select Files", bg=PDFManager.GRAY, 
                                    command=self.load_pdf, relief="flat", padx=PDFManager.PAD)
        self.btn_select.pack(side="left", fill="y")

        self.label_filename = tk.Label(top_frame, text="...", bg=PDFManager.GRAY, font=("Arial", 8), anchor="w")
        self.label_filename.pack(side="left", fill="both", expand=True, padx=(PDFManager.PAD, 0))

        # --- Main Section ---
        main_frame = tk.Frame(self.root, bg=PDFManager.PINK)
        main_frame.pack(fill="both", expand=True, padx=PDFManager.PAD, pady=PDFManager.PAD)

        # [Left] Image Preview
        preview_container = tk.Frame(main_frame, bg=PDFManager.PINK)
        preview_container.pack(side="left", fill="y")
        tk.Label(preview_container, text="Preview", bg=PDFManager.PINK).pack()
        
        self.img_frame = tk.Frame(preview_container, bg=PDFManager.PINK, width=PDFManager.PREVIEW_W, height=PDFManager.PREVIEW_H)
        self.img_frame.pack_propagate(False) 
        self.img_frame.pack()

        self.preview_label = tk.Label(self.img_frame, bg=PDFManager.GRAY, highlightthickness=0, borderwidth=0)
        self.preview_label.pack(fill="both", expand=True)

        # [Right] Workspace (Total -> Buttons -> Selected -> Save)
        right_main_container = tk.Frame(main_frame, bg=PDFManager.PINK)
        right_main_container.pack(side="left", fill="both", expand=True, padx=(PDFManager.PAD, 0))

        # [Right] 1. Total Pages
        tk.Label(right_main_container, text="Total Pages", bg=PDFManager.PINK).pack()
        self.total_listbox = tk.Listbox(right_main_container, bg=PDFManager.GRAY, relief="flat", exportselection=False)
        self.total_listbox.pack(fill="both", expand=True)
        self.total_listbox.bind('<<ListboxSelect>>', lambda e: self.update_preview_from_list(self.total_listbox))

        # [Right] 2. Move Buttons
        btn_frame = tk.Frame(right_main_container, bg=PDFManager.PINK)
        btn_frame.pack(fill="x", pady=PDFManager.PAD)
        
        inner_btn_center = tk.Frame(btn_frame, bg=PDFManager.PINK)
        inner_btn_center.pack(anchor="center")
        
        tk.Button(inner_btn_center, text="▼", bg=PDFManager.GRAY, width=2,
                  command=self.add_page, relief="flat").pack(side="left", padx=PDFManager.PAD)
        tk.Button(inner_btn_center, text="▲", bg=PDFManager.GRAY, width=2,
                  command=self.remove_page, relief="flat").pack(side="left", padx=PDFManager.PAD)

        # [Right] 3. Selected Pages
        tk.Label(right_main_container, text="Selected Pages", bg=PDFManager.PINK).pack()
        self.selected_listbox = tk.Listbox(right_main_container, bg=PDFManager.GRAY, relief="flat", exportselection=False)
        self.selected_listbox.pack(fill="both", expand=True)
        self.selected_listbox.bind('<<ListboxSelect>>',
                                   lambda e: self.update_preview_from_list(self.selected_listbox, is_selected_list=True))

        # [Right] 4. Save Button
        self.btn_save = tk.Button(right_main_container, text="Save As...", bg=PDFManager.GRAY, 
                                 command=self.save_pdf, relief="flat")
        self.btn_save.pack(fill="x", pady=(PDFManager.PAD*2, 0))

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.label_filename.config(text=os.path.basename(path))
            self.pdf_doc = fitz.open(path)
            
            self.total_listbox.delete(0, tk.END)
            self.selected_listbox.delete(0, tk.END)
            self.selected_indices = []
            
            for i in range(len(self.pdf_doc)):
                self.total_listbox.insert(tk.END, str(i + 1))

    def show_preview(self, index):
        if self.pdf_doc:
            page = self.pdf_doc[index]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Resize to maintain aspect ratio
            img.thumbnail((PDFManager.PREVIEW_W, PDFManager.PREVIEW_H), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo

    def update_preview_from_list(self, listbox, is_selected_list=False):
        selection = listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        actual_index = self.selected_indices[idx] if is_selected_list else idx
        self.show_preview(actual_index)

    def add_page(self):
        selection = self.total_listbox.curselection()
        if not selection: return
        
        index = selection[0]
        self.selected_indices.append(index)
        self.selected_listbox.insert(tk.END, str(index + 1))

    def remove_page(self):
        selection = self.selected_listbox.curselection()
        if not selection: return
        
        idx_in_list = selection[0]
        self.selected_listbox.delete(idx_in_list)
        self.selected_indices.pop(idx_in_list)

    def save_pdf(self):
        if not self.selected_indices:
            messagebox.showwarning("Warning", "Please select the pages you want to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()
            for index in self.selected_indices:
                writer.add_page(reader.pages[index])
            
            with open(save_path, "wb") as f:
                writer.write(f)
            messagebox.showinfo("Success", "The file has been saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFManager(root)
    root.mainloop()