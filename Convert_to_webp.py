import os
from PIL import Image

# Indiquez le chemin du dossier contenant vos images PNG actuelles
input_dir = "./cartes"  # Dossier source
output_dir = "./carteswebp"   # Dossier de destination

# Crée le dossier de destination s'il n'existe pas
os.makedirs(output_dir, exist_ok=True)

count = 0
for filename in os.listdir(input_dir):
    if filename.lower().endswith(".png"):
        input_path = os.path.join(input_dir, filename)
        # Change l'extension en .webp
        output_filename = os.path.splitext(filename)[0] + ".webp"
        output_path = os.path.join(output_dir, output_filename)
        
        with Image.open(input_path) as img:
            # Sauvegarde en WebP (quality=80 offre un compromis parfait visuel / poids plume)
            img.save(output_path, "WEBP", quality=80, method=6)
        count += 1

print(f"Conversion terminée ! {count} images converties avec succès dans '{output_dir}'.")