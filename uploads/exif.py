from PIL import Image, ExifTags

def view_exif_data(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                print("EXIF Data for", image_path, ":")
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    print(f"{tag_name}: {value}")
            else:
                print("No EXIF data found.")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)

# Replace 'image.jpg' with your image file path
image_path = 'DSCN0010.jpg'
view_exif_data(image_path)


