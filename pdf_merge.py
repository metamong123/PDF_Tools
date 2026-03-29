import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2


class PDFMerge:
    PINK = "#FF8C9B"
    GRAY = "#E6E6E6"

    def __init__(self, root):
        self.root = root
        self.root.title('PDF Merge')
        self.pdf_list = []

        # Left - File name list box
        self.left_frame = tk.Frame(root, background=PDFMerge.PINK)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        self.listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, 
                                  background=PDFMerge.GRAY, relief="solid", borderwidth=0)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right - buttons
        self.right_frame = tk.Frame(root, padx=5, pady=5, background=PDFMerge.PINK)
        self.right_frame.pack(side=tk.RIGHT)

        # -/+ buttons
        self.button_frame = tk.Frame(self.right_frame, background=PDFMerge.PINK)
        self.button_frame.pack(anchor="nw")

        self.up_button = tk.Button(self.button_frame, text='▲', command=self.move_up, 
                                   background=PDFMerge.GRAY, relief="solid", borderwidth=0)
        self.up_button.pack(side="top", pady=(0, 5))

        self.down_button = tk.Button(self.button_frame, text='▼', command=self.move_down, 
                                     background=PDFMerge.GRAY, relief="solid", borderwidth=0)
        self.down_button.pack(side="top")

        self.null_frame = tk.Frame(self.right_frame, height=192, background=PDFMerge.PINK)
        self.null_frame.pack(anchor="center", fill="both", expand=True)

        # File select and save button
        self.action_frame = tk.Frame(self.right_frame, background=PDFMerge.PINK)
        self.action_frame.pack(anchor="s")

        self.save_button = tk.Button(self.action_frame, text="Save As...", command=self.save_file, 
                                     padx=9, background=PDFMerge.GRAY, relief="solid", borderwidth=0)
        self.save_button.pack(side=tk.BOTTOM)

        self.select_button = tk.Button(self.action_frame, text="Select Files", command=self.add_files, 
                                       padx=5, background=PDFMerge.GRAY, relief="solid", borderwidth=0)
        self.select_button.pack(side=tk.BOTTOM, expand=True, pady=(0, 5))


    # file selection dialog
    def add_files(self):
        files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF Files", "*.pdf")])
        if files:
            for file in files:
                self.pdf_list.append(file)
                self.listbox.insert(tk.END, file.split('/')[-1])

    # def move up
    def move_up(self):
        selected = self.listbox.curselection()
        if selected and selected[0] > 0:
            index = selected[0]
            self.pdf_list[index], self.pdf_list[index - 1] = self.pdf_list[index - 1], self.pdf_list[index]
            file_name = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(index - 1, file_name)
            self.listbox.select_set(index - 1)

    # def move down
    def move_down(self):
        selected = self.listbox.curselection()
        if selected and selected[0] < len(self.pdf_list) - 1:
            index = selected[0]
            self.pdf_list[index], self.pdf_list[index + 1] = self.pdf_list[index + 1], self.pdf_list[index]
            file_name = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(index + 1, file_name)
            self.listbox.select_set(index + 1)

    # save merged PDF
    def save_file(self):
        if not self.pdf_list:
            messagebox.showerror("Error", "Select PDF flies to merge.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if output_path:
            try:
                self.merge_pdfs(output_path)
                messagebox.showinfo("Success", f"PDF file saved as {output_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    # PDF merge
    def merge_pdfs(self, output_path):
        pdf_writer = PyPDF2.PdfWriter()

        for pdf in self.pdf_list:
            pdf_reader = PyPDF2.PdfReader(pdf)
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

        with open(output_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    root.configure(bg=PDFMerge.PINK)
    app = PDFMerge(root)
    root.mainloop()
