from __future__ import unicode_literals

import io
import logging

import PyPDF2
import weasyprint
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.response import Response
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger("weasyprint")
logger.addHandler(logging.FileHandler("weasyprint.log"))


class Pdf:
    pdf = None

    def generate_pdf(
        self,
        request,
        selected_template,
        context=None,
        page_size="A4",
        layout="portrait",
    ):
        context = {} if context is None else context
        font_config = FontConfiguration()
        html_string = render_to_string(f"{selected_template}.html", context)
        css = weasyprint.CSS(
            string="""
                @page { size: %s %s; margin: 1cm; }
                table {
                    page-break-inside: auto !important;
                }
                """
            % (page_size, layout)
        )

        self.pdf = HTML(
            string=html_string, base_url=request.build_absolute_uri()
        ).write_pdf(
            font_config=font_config,
            presentational_hints=True,
            stylesheets=[
                css,
                CSS(
                    settings.STATIC_ROOT + f"/css/{selected_template}.css",
                    font_config=font_config,
                ),
            ],
        )

        return self

    def generate_pdf_from_file(self, filename):
        fs = FileSystemStorage()

        if fs.exists(filename):
            with fs.open(filename) as pdf:
                response = HttpResponse(pdf, content_type="application/pdf")
                response["Content-Disposition"] = f"inline; filename={filename}"
                return response
        return Response({"error": "The requested resource was not found"})

    def read(self, stream):
        pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(stream))
        pdf_writer = PyPDF2.PdfFileWriter()

        for page_number in range(pdf_reader.numPages):
            pdf_writer.addPage(pdf_reader.getPage(page_number))

        out = io.BytesIO()
        pdf_writer.write(out)

        self.pdf = out.getvalue()

        return self

    def encrypt(self, password):
        pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(self.pdf))
        pdf_writer = PyPDF2.PdfFileWriter()

        for page_number in range(pdf_reader.numPages):
            pdf_writer.addPage(pdf_reader.getPage(page_number))

        pdf_writer.encrypt(password)
        out = io.BytesIO()
        pdf_writer.write(out)

        self.pdf = out.getvalue()

        return self

    def to_response(self, filename="document.pdf", disposition="inline"):
        response = HttpResponse(self.pdf, content_type="application/pdf;")
        response["Content-Disposition"] = f"{disposition}; filename={filename}"
        response["Content-Transfer-Encoding"] = "binary"

        return response

    def get(self):
        return self.pdf


def pdf_from_file():
    image = settings.STATIC_ROOT + "logo.png"
    font_config = FontConfiguration()

    html_string = render_to_string(
        "invoice.html", {"invoice_number": "123456", "image": image}
    )

    pdfFileName = "invoice.pdf"

    HTML(string=html_string).write_pdf(
        target="media/exports/%s" % (pdfFileName),
        font_config=font_config,
        presentational_hints=True,
        stylesheets=[
            CSS(settings.STATIC_ROOT + "/css/invoice.css", font_config=font_config),
        ],
    )

    fs = FileSystemStorage("")

    with fs.open("media/exports/" + pdfFileName) as pdf:
        response = HttpResponse(pdf, content_type="application/pdf")
        # to display pdf in browser, change attachment to inline below
        response["Content-Disposition"] = "inline; filename=invoice.pdf"
        return response
