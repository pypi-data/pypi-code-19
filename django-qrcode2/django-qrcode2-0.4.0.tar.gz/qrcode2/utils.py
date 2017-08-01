import base64
import io


def img_to_base64_data(img):
    in_mem_file = io.BytesIO()
    img.save(in_mem_file, format='PNG')
    in_mem_file.seek(0)
    img_bytes = in_mem_file.read()
    return 'data:image/png;base64,' + base64.b64encode(img_bytes).decode('utf-8')
