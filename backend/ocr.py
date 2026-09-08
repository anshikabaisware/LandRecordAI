import pytesseract
from PIL import Image
import io
import fitz


def extract_text(file_bytes, filename):

    # -----------------------------
    # PDF
    # -----------------------------

    if filename.lower().endswith(".pdf"):

        pdf = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

        all_text = ""

        for page in pdf:

            # First try extracting existing PDF text
            text = page.get_text()

            if text.strip():

                all_text += text + "\n"

            else:

                # If scanned PDF, convert page to image
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                text = pytesseract.image_to_string(
                    image
                )

                all_text += text + "\n"

        pdf.close()

        return all_text


    # -----------------------------
    # IMAGE
    # -----------------------------

    else:

        image = Image.open(
            io.BytesIO(file_bytes)
        )

        return pytesseract.image_to_string(
            image
        )