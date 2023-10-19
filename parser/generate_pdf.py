from fpdf import FPDF
import datetime
import os


class Pdf:
    def __init__(self, test_details: dict):
        self.title = test_details["title"]
        self.output_dir: str = test_details["output_dir"]
        self.orion_version: str = test_details["orion_version"]

        self.pdf_filename = f"AB_testing_for_on_" \
                            f"{str(datetime.datetime.now())}.pdf"
        self.pdf = FPDF()
        self.add_page(f"{ self.title} on {str(datetime.datetime.now())}")
        data = {
            "Orion Version": test_details["orion_version"],
            "Detection Model Version": test_details["detection_model_version"],
            "Recognition Model Version": test_details["recognition_model_version"]
        }
        header: list = ["Artifacts", "Version"]
        self.add_table(data, "", header)

    def export(self):
        path = os.path.join(self.output_dir, self.pdf_filename)
        self.pdf.output(path)

    def add_page(self, title, orientation: str = "L"):
        self.pdf.add_page(orientation=orientation)
        self.pdf.set_font("Arial", size=15)
        self.pdf.cell(200, 10, txt=title, ln=1, align='C')

    def add_table(self, data: dict, title: str = "",
                  headers: list = ["Category", "Value"],
                  wrap_text: bool = False):
        if title:
            self.pdf.set_font("Arial", size=15)
            self.pdf.cell(200, 10, txt=title, ln=1, align='C')
        th = self.pdf.font_size
        epw = self.pdf.w - 2 * self.pdf.l_margin
        col_width = epw / 2
        col_width_val = epw / 2
        fill = False
        enable_multi_cell = False

        self.pdf.ln(th)
        fill = True
        self.pdf.set_fill_color(111, 141, 235)
        self.pdf.set_font_size(10)
        for header in headers:
            self.pdf.cell(col_width, th, str(header), border=1, fill=fill)

        fill = False
        for key, value in data.items():
            self.pdf.ln(th)
            val = value
            if type(value) == list:
                val = " | ".join(value)
                self.pdf.set_fill_color(230, 0, 0)
                self.pdf.set_font_size(10)
                fill = False
                col_width_val = 0
                if wrap_text:
                    enable_multi_cell = True
                else:
                    enable_multi_cell = False
            elif type(value) == dict:
                gt = int(value["gt"])
                pred = int(value["pred"])
                fill = True
                if gt == pred:
                    self.pdf.set_fill_color(0, 230, 0)
                    self.pdf.set_font_size(10)
                else:
                    self.pdf.set_fill_color(230, 0, 0)
                    self.pdf.set_font_size(10)
                val = f"{pred} / {gt}"
                enable_multi_cell = False
                col_width_val = col_width
            else:
                self.pdf.set_fill_color(230, 0, 0)
                self.pdf.set_font_size(10)
                enable_multi_cell = False
                col_width_val = col_width

            self.pdf.cell(col_width, th, str(key), border=1, fill=fill)
            if enable_multi_cell:
                self.pdf.multi_cell(col_width_val, th, str(val), border=1, fill=fill)
            else:
                self.pdf.cell(col_width, th, str(val), border=1, fill=fill)

        self.pdf.set_font_size(15)
        self.pdf.ln()