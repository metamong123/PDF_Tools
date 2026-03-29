import io
import os

import tkinter as tk
from tkinter import filedialog, messagebox

import fitz  # PyMuPDF
from PIL import Image, ImageTk
from PyPDF2 import PdfReader, PdfWriter


class PDFManager:
    # Default UI Constants: Preview Size, Colors, and Padding
    PREVIEW_W = 320
    PREVIEW_H = 452

    PINK = "#FF8C9B"
    GRAY = "#E6E6E6"
    PAD = 5

    def __init__(self, root):
        self.root = root
        self.root.title("PDF Page Selector")
        self.root.configure(bg=PDFManager.PINK)

        # Data variables
        self.pdf_path = ""
        self.pdf_doc = None
        self.selected_indices = []
        
        # --- Top Section: File Selection ---
        top_frame = tk.Frame(self.root, bg=PDFManager.PINK)
        top_frame.pack(side="top", fill="x", padx=PDFManager.PAD, pady=(PDFManager.PAD, 0))

        self.btn_select = tk.Button(top_frame, text="Select Files", bg=PDFManager.GRAY, 
                                    command=self.load_pdf, relief="flat", padx=PDFManager.PAD)
        self.btn_select.pack(side="left", fill="y")

        self.label_filename = tk.Label(top_frame, text="No file selected", bg=PDFManager.GRAY, font=("Arial", 8), anchor="w")
        self.label_filename.pack(side="left", fill="both", expand=True, padx=(PDFManager.PAD, 0))

        # --- Main Section ---
        main_frame = tk.Frame(self.root, bg=PDFManager.PINK)
        main_frame.pack(fill="both", expand=True, padx=PDFManager.PAD, pady=PDFManager.PAD)

        # [Left] Image Preview Section
        preview_container = tk.Frame(main_frame, bg=PDFManager.PINK)
        preview_container.pack(side="left", fill="y")
        tk.Label(preview_container, text="Preview", bg=PDFManager.PINK).pack()
        
        self.img_frame = tk.Frame(preview_container, bg=PDFManager.PINK, width=PDFManager.PREVIEW_W, height=PDFManager.PREVIEW_H)
        self.img_frame.pack_propagate(False) 
        self.img_frame.pack()

        self.preview_label = tk.Label(self.img_frame, bg=PDFManager.GRAY, highlightthickness=0, borderwidth=0)
        self.preview_label.pack(fill="both", expand=True)

        # [Right] Workspace Section
        right_main_container = tk.Frame(main_frame, bg=PDFManager.PINK)
        right_main_container.pack(side="left", fill="both", expand=True, padx=(PDFManager.PAD, 0))

        # [Right] 1. Total Pages List
        tk.Label(right_main_container, text="Total Pages", bg=PDFManager.PINK).pack()
        self.total_listbox = tk.Listbox(right_main_container, bg=PDFManager.GRAY, relief="flat", exportselection=False)
        self.total_listbox.pack(fill="both", expand=True)
        self.total_listbox.bind('<<ListboxSelect>>', lambda e: self.update_preview_from_list(self.total_listbox))

        # [Right] 2. Add/Remove Buttons
        btn_frame = tk.Frame(right_main_container, bg=PDFManager.PINK)
        btn_frame.pack(fill="x", pady=PDFManager.PAD)
        
        inner_btn_center = tk.Frame(btn_frame, bg=PDFManager.PINK)
        inner_btn_center.pack(anchor="center")
        
        tk.Button(inner_btn_center, text="▼", bg=PDFManager.GRAY, width=2,
                  command=self.add_page, relief="flat").pack(side="left", padx=PDFManager.PAD)
        tk.Button(inner_btn_center, text="▲", bg=PDFManager.GRAY, width=2,
                  command=self.remove_page, relief="flat").pack(side="left", padx=PDFManager.PAD)

        # [Right] 3. Selected Pages List
        tk.Label(right_main_container, text="Selected Pages", bg=PDFManager.PINK).pack()
        self.selected_listbox = tk.Listbox(right_main_container, bg=PDFManager.GRAY, relief="flat", exportselection=False)
        self.selected_listbox.pack(fill="both", expand=True)
        self.selected_listbox.bind('<<ListboxSelect>>',
                                   lambda e: self.update_preview_from_list(self.selected_listbox, is_selected_list=True))

        # [Right] 4. Reorder Buttons (Up/Down)
        move_btn_frame = tk.Frame(right_main_container, bg=PDFManager.PINK)
        move_btn_frame.pack(fill="x", pady=(1, 0))
        
        inner_move_btn_center = tk.Frame(move_btn_frame, bg=PDFManager.PINK)
        inner_move_btn_center.pack(fill="x", expand=True)
        
        tk.Button(inner_move_btn_center, text="▲ Up", bg=PDFManager.GRAY, width=9,
                  command=lambda: self.move_page(-1), relief="flat").pack(side="left")
        tk.Button(inner_move_btn_center, text="▼ Down", bg=PDFManager.GRAY, width=9,
                  command=lambda: self.move_page(1), relief="flat").pack(side="left", padx=(1, 0)) # padx=PDFManager.PAD

        # [Right] 5. Save Button
        self.btn_save = tk.Button(right_main_container, text="Save As...", bg=PDFManager.GRAY, 
                                 command=self.save_pdf, relief="flat")
        self.btn_save.pack(fill="x", pady=(PDFManager.PAD*2, 0))

    def load_pdf(self):
        # Open a file dialog to select a PDF and initialize the page list
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.label_filename.config(text=os.path.basename(path))
            self.pdf_doc = fitz.open(path)
            
            # Clear existing data
            self.total_listbox.delete(0, tk.END)
            self.selected_listbox.delete(0, tk.END)
            self.selected_indices = []
            
            # Fill the total pages listbox
            for i in range(len(self.pdf_doc)):
                self.total_listbox.insert(tk.END, f"{i + 1}")

    def show_preview(self, index):
        # Render a specific page of the PDF to the preview label
        if self.pdf_doc:
            page = self.pdf_doc[index]
            # Use matrix for better rendering quality
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Resize image while maintaining aspect ratio
            img.thumbnail((PDFManager.PREVIEW_W, PDFManager.PREVIEW_H), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo

    def update_preview_from_list(self, listbox, is_selected_list=False):
        # Handle listbox selection events to update the preview image
        selection = listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        # If the selection is from the 'Selected' list, map it to the original index
        actual_index = self.selected_indices[idx] if is_selected_list else idx
        self.show_preview(actual_index)

    def add_page(self):
        # Add the currently selected page from the total list to the selection list
        selection = self.total_listbox.curselection()
        if not selection: return
        
        index = selection[0]
        self.selected_indices.append(index)
        self.selected_listbox.insert(tk.END, f"{index + 1}")

    def remove_page(self):
        # Remove the selected item from the selection list
        selection = self.selected_listbox.curselection()
        if not selection: return
        
        idx_in_list = selection[0]
        self.selected_listbox.delete(idx_in_list)
        self.selected_indices.pop(idx_in_list)

    def move_page(self, direction):
        # Change the order of selected pages
        selection = self.selected_listbox.curselection()
        if not selection: return
        
        curr_idx = selection[0]
        new_idx = curr_idx + direction
        
        # Check if the move is within valid bounds
        if 0 <= new_idx < self.selected_listbox.size():
            # 1. Swap data in the internal index list
            self.selected_indices[curr_idx], self.selected_indices[new_idx] = \
                self.selected_indices[new_idx], self.selected_indices[curr_idx]
            
            # 2. Update UI: Remove and re-insert the listbox item
            item_text = self.selected_listbox.get(curr_idx)
            self.selected_listbox.delete(curr_idx)
            self.selected_listbox.insert(new_idx, item_text)
            
            # 3. Maintain selection on the moved item
            self.selected_listbox.selection_clear(0, tk.END)
            self.selected_listbox.selection_set(new_idx)
            self.selected_listbox.activate(new_idx)

    def save_pdf(self):
        # Create a new PDF file based on the items and order in selected_indices
        if not self.selected_indices:
            messagebox.showwarning("Warning", "Please select at least one page to save.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if save_path:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()
            
            # Add pages according to the custom order in self.selected_indices
            for index in self.selected_indices:
                writer.add_page(reader.pages[index])
            
            try:
                with open(save_path, "wb") as f:
                    writer.write(f)
                messagebox.showinfo("Success", "The PDF has been saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFManager(root)
    root.mainloop()