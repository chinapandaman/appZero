# -*- coding: utf-8 -*-


import shutil
import uuid
from tempfile import NamedTemporaryFile

import pdfrw
from PyPDF2 import PdfFileReader


class PDFForm(object):
    _ANNOT_KEY = "/Annots"
    _ANNOT_FIELD_KEY = "/T"
    _ANNOT_VAL_KEY = "/V"
    _ANNOT_RECT_KEY = "/Rect"
    _SUBTYPE_KEY = "/Subtype"
    _WIDGET_SUBTYPE_KEY = "/Widget"

    def __init__(self):
        self._template_file = NamedTemporaryFile(suffix=".pdf")
        self._output_file = NamedTemporaryFile(suffix=".pdf")
        self._final_file_with_image = NamedTemporaryFile(suffix=".pdf")
        self._final_file = NamedTemporaryFile(suffix=".pdf")

        self._uuid = uuid.uuid4().hex
        self._data_dict = {}

    def _fill_pdf(self):
        template_pdf = pdfrw.PdfReader(self._template_file.name)
        num_of_pages = PdfFileReader(self._template_file).getNumPages()

        for i in range(num_of_pages):
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

        pdfrw.PdfWriter().write(self._output_file.name, template_pdf)

    def bools_to_checkboxes(self):
        for k, v in self._data_dict.items():
            if isinstance(v, bool):
                if not v:
                    self._data_dict[k] = None
                else:
                    self._data_dict[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

    def build_pdf(self, template_file, data_dict, canvas=False, global_font_size=8):
        if template_file:
            shutil.copyfileobj(template_file, self._template_file)

        self._data_dict = data_dict
        self.bools_to_checkboxes()

        self._fill_pdf()

        return self
