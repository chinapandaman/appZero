# -*- coding: utf-8 -*-


import os
import shutil
import uuid

import pdfrw

from gluon import current


class PDFForm(object):
    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

    def __init__(self):
        self._uuid = uuid.uuid4().hex
        self._data_dict = {}

        self._template_path = os.path.join(
            current.request.folder, "temp", "template.pdf"
        )
        self._output_path = os.path.join(current.request.folder, "temp", "output.pdf")
        self._final_path_with_image = os.path.join(
            current.request.folder, "temp", "final_with_image.pdf"
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
        with open(self._output_path, "rb+") as f:
            self.pdf_stream = f.read()

    def _bools_to_checkboxes(self):
        for k, v in self._data_dict.items():
            if isinstance(v, bool):
                if not v:
                    self._data_dict[k] = None
                else:
                    self._data_dict[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

    def _remove_temp_file(self):
        os.remove(self._template_path)
        os.remove(self._output_path)

    def build_pdf(self, template_file, data_dict, canvas=False, global_font_size=8):
        if template_file:
            with open(self._template_path, "wb+") as f:
                shutil.copyfileobj(template_file, f)

        self._data_dict = data_dict
        self._bools_to_checkboxes()

        self._fill_pdf()

        self._remove_temp_file()
        return self
