import tkinter as tk

root = tk.Tk()
root.title("Test")
root.geometry("200x100")
tk.Label(root, text="Hei!").pack(padx=10, pady=5)
tk.Entry(root, bd=1, relief="solid").pack(padx=10, pady=5)
root.mainloop()
