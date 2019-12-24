# -*- coding: utf-8 -*-


import os
import shutil
import uuid

import pdfrw
from PIL import Image
from reportlab.pdfgen import canvas

from gluon import current


class PDFForm(object):
    # TODO: checkboxes, even pages rotation?

    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

    _LAYER_SIZE_X = 800.27
    _LAYER_SIZE_Y = 841.89

    _CANVAS_FONT = "Helvetica"

    def __init__(self, canvas=False, global_font_size=12, max_txt_length=100):
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

        self._canvas = canvas
        self._global_font_size = global_font_size
        self._max_txt_length = max_txt_length

        self.pdf_stream = ""

    def _fill_pdf_canvas(self):
        template_pdf = pdfrw.PdfReader(self._template_path)
        layers = []

        for i in range(len(template_pdf.pages)):
            layer_path = os.path.join(
                current.request.folder, "temp", uuid.uuid4().hex + ".pdf"
            )
            layers.append(layer_path)

            canv = canvas.Canvas(
                layer_path, pagesize=(self._LAYER_SIZE_X, self._LAYER_SIZE_Y)
            )
            canv.setFont(self._CANVAS_FONT, self._global_font_size)

            annotations = template_pdf.pages[i][self._ANNOT_KEY]
            if annotations:
                for j in reversed(range(len(annotations))):
                    annotation = annotations[j]

                    if (
                        annotation[self._SUBTYPE_KEY] == self._WIDGET_SUBTYPE_KEY
                        and annotation[self._ANNOT_FIELD_KEY]
                    ):
                        key = annotation[self._ANNOT_FIELD_KEY][1:-1]
                        if key in self._data_dict.keys():
                            if self._data_dict[key] in [
                                pdfrw.PdfName.Yes,
                                pdfrw.PdfName.Off,
                            ]:
                                annotation.update(
                                    pdfrw.PdfDict(
                                        AS=self._data_dict[key], Ff=pdfrw.PdfObject(1)
                                    )
                                )
                            else:
                                coordinates = annotation[self._ANNOT_RECT_KEY]
                                annotations.pop(j)
                                if len(self._data_dict[key]) < self._max_txt_length:
                                    canv.drawString(
                                        float(coordinates[0]),
                                        (float(coordinates[1]) + float(coordinates[3]))
                                        / 2
                                        - 2,
                                        self._data_dict[key],
                                    )
                                else:
                                    txt_obj = canv.beginText(0, 0)

                                    start = 0
                                    end = self._max_txt_length

                                    while end < len(self._data_dict[key]):
                                        txt_obj.textLine(
                                            (self._data_dict[key][start:end])
                                        )
                                        start += self._max_txt_length
                                        end += self._max_txt_length
                                    txt_obj.textLine(self._data_dict[key][start:])
                                    canv.saveState()
                                    canv.translate(
                                        float(coordinates[0]),
                                        (float(coordinates[1]) + float(coordinates[3]))
                                        / 2
                                        - 2,
                                    )
                                    canv.drawText(txt_obj)
                                    canv.restoreState()
                        else:
                            annotations.pop(j)

            canv.save()
        pdfrw.PdfWriter().write(self._output_path, template_pdf)

        output_file = pdfrw.PdfFileWriter()
        input_file = pdfrw.PdfReader(self._output_path)

        for i in range(len(template_pdf.pages)):
            layer_pdf = pdfrw.PdfReader(layers[i])
            os.remove(layers[i])
            input_page = input_file.pages[i]
            merger = pdfrw.PageMerge(input_page)
            if len(layer_pdf.pages) > 0:
                merger.add(layer_pdf.pages[0]).render()

        output_file.write(self._final_path, input_file)

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

        return self

    def build_pdf(self, template_file, data_dict):
        if template_file:
            with open(self._template_path, "wb+") as f:
                shutil.copyfileobj(template_file, f)
                template_file.seek(0)

        self._data_dict = data_dict
        self._bools_to_checkboxes()

        if self._canvas:
            self._fill_pdf_canvas()
        else:
            self._fill_pdf()
            self._assign_uuid()

        self._build_file_stream()
        return self
