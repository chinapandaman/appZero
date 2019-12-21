# -*- coding: utf-8 -*-


import os
import shutil
import uuid

import pdfrw
from PIL import Image
from reportlab.pdfgen import canvas

from gluon import current


class PDFForm(object):
    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

    _LAYER_SIZE_X = 800.27
    _LAYER_SIZE_Y = 841.89

    def __init__(self):
        self._uuid = uuid.uuid4().hex
        self._data_dict = {}

        self._template_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )
        self._output_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )
        self._final_path_with_image = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )
        self._final_path = os.path.join(
            current.request.folder, "temp", self._uuid + ".pdf"
        )

        self.pdf_stream = ""

    def _fill_pdf(self):
        template_pdf = pdfrw.PdfReader(self._template_path)

        for i in range(len(template_pdf.pages)):
            annotations = template_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for annotation in annotations:
                    if (
                        annotation[self._SUBTYPE_KEY] == self._WIDGET_SUBTYPE_KEY
                        and annotation[self._ANNOT_FIELD_KEY]
                    ):
                        key = annotation[self._ANNOT_FIELD_KEY][1:-1]
                        if key in self._data_dict.keys():
                            annotation.update(
                                pdfrw.PdfDict(
                                    V="{}".format(self._data_dict[key]),
                                    AS=self._data_dict[key],
                                )
                            )

        pdfrw.PdfWriter().write(self._output_path, template_pdf)

    def _bools_to_checkboxes(self):
        for k, v in self._data_dict.items():
            if isinstance(v, bool):
                if not v:
                    self._data_dict[k] = None
                else:
                    self._data_dict[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

    def _assign_uuid(self):
        generated_pdf = pdfrw.PdfReader(self._output_path)

        for i in range(len(generated_pdf.pages)):
            annotations = generated_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for annotation in annotations:
                    if self._ANNOT_FIELD_KEY in annotation.keys():
                        annotation.update(
                            pdfrw.PdfDict(
                                T="{}_{}".format(
                                    annotation[self._ANNOT_FIELD_KEY][1:-1], self._uuid,
                                ),
                                Ff=pdfrw.PdfObject(1),
                            )
                        )

        pdfrw.PdfWriter().write(self._final_path, generated_pdf)

    def _build_file_stream(self):
        with open(self._final_path, "rb+") as f:
            self.pdf_stream = f.read()

        os.remove(self._template_path)
        os.remove(self._output_path)
        os.remove(self._final_path)

    def __add__(self, other):
        if not self.pdf_stream:
            return other

        writer = pdfrw.PdfWriter()

        self_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )
        other_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )

        with open(self_path, "wb+") as f:
            f.write(self.pdf_stream)

        with open(other_path, "wb+") as f:
            f.write(other.pdf_stream)

        writer.addpages(pdfrw.PdfReader(self_path).pages)
        writer.addpages(pdfrw.PdfReader(other_path).pages)

        new_final_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )
        writer.write(new_final_path)

        new_obj = self.__class__()
        with open(new_final_path, "rb+") as f:
            new_obj.pdf_stream = f.read()

        os.remove(self_path)
        os.remove(other_path)
        os.remove(new_final_path)

        return new_obj

    def draw_image(self, page_number, image_file, x, y, width, height, rotation=0):
        image_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".jpg"
        )
        with open(image_path, "wb+") as f:
            f.write(image_file.read())

        if rotation:
            image = Image.open(image_path)
            image.rotate(rotation, expand=True).save(image_path)

        layer_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )

        canv = canvas.Canvas(
            layer_path, pagesize=(self._LAYER_SIZE_X, self._LAYER_SIZE_Y)
        )
        canv.drawImage(image_path, x, y, width=width, height=height)
        canv.save()

        layer = pdfrw.PdfReader(layer_path)
        output_file = pdfrw.PdfFileWriter()

        input_path = os.path.join(
            current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
        )
        with open(input_path, "wb+") as f:
            f.write(self.pdf_stream)

        input_file = pdfrw.PdfReader(input_path)

        for i in range(len(input_file.pages)):
            if i == page_number - 1:
                merger = pdfrw.PageMerge(input_file.pages[i])
                merger.add(layer.pages[0]).render()

        output_file.write(self._final_path_with_image, input_file)

        with open(self._final_path_with_image, "rb+") as f:
            self.pdf_stream = f.read()

        os.remove(image_path)
        os.remove(layer_path)
        os.remove(input_path)
        os.remove(self._final_path_with_image)

    def build_pdf(self, template_file, data_dict, canvas=False, global_font_size=8):
        if template_file:
            with open(self._template_path, "wb+") as f:
                shutil.copyfileobj(template_file, f)
                template_file.seek(0)

        self._data_dict = data_dict
        self._bools_to_checkboxes()

        self._fill_pdf()
        self._assign_uuid()

        self._build_file_stream()
        return self
