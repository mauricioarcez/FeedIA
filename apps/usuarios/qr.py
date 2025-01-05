import qrcode

def generar_codigo_qr():
    # URL que deseas codificar
    url = 'http://127.0.0.1:8000/encuestas/ingresar-codigo/'

    # Generar el código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Crear una imagen del código QR
    img = qr.make_image(fill_color="black", back_color="white")

    # Guardar la imagen
    img.save('codigo_qr_encuestas.png')

if __name__ == "__main__":
    generar_codigo_qr()
