from wand.image import Image
import img2pdf

def pdf2Image(pdfFile):
    """
    pdf转图片
    :param pdfFile:
    :return:
    """

    with(Image(filename=pdfFile,resolution=200)) as source:
        images=source.sequence
        pages=len(images)
        for i in range(pages):
            Image(images[i]).save(filename=pdfFile.split(".")[0] + str(i) + '.png')


def images2Pdf(pdfFile, *images):
    """
    图片转pdf
    :param pdfFile:
    :param images:
    :return:
    """
    pdf_bytes = img2pdf.convert(images)

    file = open(pdfFile, "wb")
    file.write(pdf_bytes)