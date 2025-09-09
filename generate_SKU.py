import tkinter as tk
from tkinter import messagebox
import os, random
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

try:
    font_large = ImageFont.truetype("Arial.ttf", 48)
    font_small = ImageFont.truetype("Arial.ttf", 24)
except Exception:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# EAN-13 generator
def generate_unique_random_eans(prefix="703018", total=25):
    used = set()
    eans = []
    while len(eans) < total:
        rand_part = str(random.randint(0, 999999)).zfill(6)
        base = prefix + rand_part
        if base in used:
            continue
        used.add(base)
        checksum = (10 - sum((int(d) if i % 2 == 0 else int(d)*3)
                            for i, d in enumerate(base)) % 10) % 10
        full_ean = base + str(checksum)
        eans.append(full_ean)
    return eans

# Label drawing
def create_labels(collection, products, sizes, colors):
    # Base directories
    output_dir   = "sku_labels_ui"
    barcodes_dir = os.path.join(output_dir, "barcodes")
    collection_dir = os.path.join(barcodes_dir, collection)
    os.makedirs(collection_dir, exist_ok=True)

    all_combinations = []
    for p in products:
        for size, var in sizes.items():
            if var.get():
                for color_name, (color_code, varc) in colors.items():
                    if varc.get():
                        all_combinations.append(
                            (p["code"], p["name"], size, color_code, color_name)
                        )

    eans = generate_unique_random_eans(total=len(all_combinations))

    for i, (code, name, size, color_code, color_name) in enumerate(all_combinations):
        # Create folder per product inside collection
        product_folder = os.path.join(collection_dir, name)
        os.makedirs(product_folder, exist_ok=True)

        sku      = f"{code}-{color_code}-{size}"
        ean_data = eans[i]

        # strekkode i høy oppløsning uten utjevning
        ean = barcode.get("ean13", ean_data, writer=ImageWriter())
        barcode_path = os.path.join(product_folder, sku)
        options = {"dpi": 300, "module_width": 0.3, "quiet_zone": 6.5}
        actual_path = ean.save(barcode_path, options)
        with Image.open(actual_path) as bc_img:
            barcode_img = bc_img.convert("RGB")

        # etikett
        width, height     = 600, 300
        upper_row_height  = 100
        col1_width, col2_width = 200, 200

        # skaler strekkoden for å utnytte tilgjengelig plass
        max_w = width * 2 // 3 - 20
        max_h = height - upper_row_height - 20
        scale = min(max_w / barcode_img.width, max_h / barcode_img.height)
        if scale != 1:
            new_size = (
                int(barcode_img.width * scale),
                int(barcode_img.height * scale),
            )
            barcode_img = barcode_img.resize(new_size, resample=Image.NEAREST)

        img  = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # rammer
        draw.rectangle([(0, 0), (width-1, height-1)], outline="black", width=3)
        draw.line((0, upper_row_height, width, upper_row_height), fill="black", width=3)
        draw.line((col1_width, 0, col1_width, upper_row_height), fill="black", width=3)
        draw.line((col1_width+col2_width, 0, col1_width+col2_width, upper_row_height), fill="black", width=3)
        draw.line((width*2//3, upper_row_height, width*2//3, height), fill="black", width=3)

        # øverste rad
        boxes = [
            (sku, 0, col1_width),
            (name, col1_width, col2_width),
            (color_name.upper(), col1_width + col2_width, width - (col1_width + col2_width)),
        ]
        for text, left, box_width in boxes:
            bbox = draw.textbbox((0, 0), text, font=font_small)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            x = left + (box_width - text_w) / 2
            y = (upper_row_height - text_h) / 2
            draw.text((x, y), text, font=font_small, fill="black")

        # nederste rad
        paste_x = (width * 2 // 3 - barcode_img.width) // 2
        paste_y = upper_row_height + (height - upper_row_height - barcode_img.height) // 2
        img.paste(barcode_img, (paste_x, paste_y))

        bbox = draw.textbbox((0,0), size, font=font_large)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = width*2//3 + (width//3 - text_w)//2
        y = upper_row_height + (height-upper_row_height-text_h)//2
        draw.text((x, y), size, font=font_large, fill="black")
        
        img_path = os.path.join(product_folder, f"{sku}.png")
        img.save(img_path, dpi=(300, 300))
        pdf_path = os.path.join(product_folder, f"{sku}.pdf")
        img.save(pdf_path, "PDF", resolution=300)

def run_gui():
    root = tk.Tk()
    root.title("SKU Generator")
    root.geometry("800x500")  # noe høyere for ny input
    root.resizable(False, False)

    # -- Kolleksjon --
    coll_frame = tk.Frame(root, padx=10, pady=10)
    coll_frame.pack(fill="x", padx=10, pady=5)
    tk.Label(coll_frame, text="Kolleksjon:").grid(row=0, column=0, sticky="e", padx=5)
    coll_entry = tk.Entry(coll_frame, width=40, bd=1, relief="solid")
    coll_entry.grid(row=0, column=1, padx=5)

    # -- Produkter --
    product_frame = tk.LabelFrame(root, text="Produkter", padx=10, pady=10)
    product_frame.pack(fill="x", padx=10, pady=5)
    product_frame.columnconfigure(1, weight=1)

    tk.Label(product_frame, text="Navn:").grid(row=0, column=0, sticky="e", padx=5)
    name_entry = tk.Entry(product_frame, width=30, bd=1, relief="solid")
    name_entry.grid(row=0, column=1, sticky="ew", padx=5)

    tk.Label(product_frame, text="Kode:").grid(row=0, column=2, sticky="e", padx=5)
    code_entry = tk.Entry(product_frame, width=10, bd=1, relief="solid")
    code_entry.grid(row=0, column=3, padx=5)

    products = []
    product_list = tk.Listbox(product_frame, width=60, height=4)
    product_list.grid(row=1, column=0, columnspan=4, pady=(10,0), sticky="ew")

    def add_product():
        name = name_entry.get().strip()
        code = code_entry.get().strip()
        if not name or not code:
            messagebox.showwarning("Feil", "Fyll ut både navn og kode")
            return
        products.append({"name": name.upper(), "code": code})
        product_list.insert(tk.END, f"{code} – {name.upper()}")
        name_entry.delete(0, tk.END)
        code_entry.delete(0, tk.END)

    tk.Button(product_frame, text="Legg til produkt", command=add_product).grid(row=0, column=4, padx=10)

    # --- Størrelser ---
    size_frame = tk.LabelFrame(root, text="Størrelser", padx=10, pady=10)
    size_frame.pack(fill="x", padx=10, pady=5)
    sizes = {s: tk.BooleanVar(value=True) for s in ["XS","S","M","L","XL","XXL"]}
    for i, s in enumerate(sizes):
        tk.Checkbutton(size_frame, text=s, variable=sizes[s]).grid(row=0, column=i, padx=5)

    # --- Farger ---
    color_frame = tk.LabelFrame(root, text="Farger", padx=10, pady=10)
    color_frame.pack(fill="x", padx=10, pady=5)
    color_codes = {
        "Black": ("B", tk.BooleanVar(value=True)),
        "White": ("W", tk.BooleanVar(value=False)),
        "Blue":  ("BL", tk.BooleanVar(value=False)),
        "Green": ("GN", tk.BooleanVar(value=False)),
        "Gray":  ("GY", tk.BooleanVar(value=False))
    }
    for i, (cname, (_, var)) in enumerate(color_codes.items()):
        tk.Checkbutton(color_frame, text=cname, variable=var).grid(row=0, column=i, padx=5)

    def on_generate():
        coll = coll_entry.get().strip()
        if not coll:
            messagebox.showwarning("Feil", "Fyll ut navn på kolleksjon")
            return
        if not products:
            messagebox.showwarning("Feil", "Legg til minst ett produkt")
            return
        create_labels(coll, products, sizes, color_codes)
        messagebox.showinfo("Ferdig", f"Etiketter generert under 'sku_labels_ui/barcodes/{coll}'")

    tk.Button(root, text="Generer Etiketter", command=on_generate,
              bg="green", fg="black", width=20).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
