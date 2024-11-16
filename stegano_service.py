from PIL import Image

def encode_message(original_image_path, message, encoded_image_path):
    image = Image.open(original_image_path)
    image = image.convert('RGB')

    message += "##END##"
    binary_message = ''.join([format(ord(char), '08b') for char in message])

    if len(binary_message) > image.size[0] * image.size[1] * 3:
        raise ValueError("Le message est trop long pour être caché dans cette image.")

    pixels = image.load()
    binary_index = 0

    for row in range(image.size[1]):
        for col in range(image.size[0]):
            if binary_index < len(binary_message):
                r, g, b = pixels[col, row]

                if binary_index < len(binary_message):
                    r = (r & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                if binary_index < len(binary_message):
                    g = (g & ~1) | int(binary_message[binary_index])
                    binary_index += 1
                if binary_index < len(binary_message):
                    b = (b & ~1) | int(binary_message[binary_index])
                    binary_index += 1

                pixels[col, row] = (r, g, b)

    image.save(encoded_image_path)


def decode_message(encoded_image_path):
    image = Image.open(encoded_image_path)
    image = image.convert('RGB')

    binary_message = ''
    pixels = image.load()

    for row in range(image.size[1]):
        for col in range(image.size[0]):
            r, g, b = pixels[col, row]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)

    chars = [chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8)]
    message = ''.join(chars)

    end_marker = "##END##"
    if end_marker in message:
        return message.split(end_marker)[0]
    else:
        raise ValueError("Aucun message valide trouvé.")
