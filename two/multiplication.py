from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MultiplicationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.operation_name = "Multiplication"
        self.all_inputs = []
        self.current_theme = "dark"  # Track current theme
        self.setup_ui()
        self.update_styles()  # Add this line to initialize styles

    def update_theme(self, theme):
        self.current_theme = theme
        self.update_styles()
        if hasattr(self, 'last_values'):
            self.update_display()

    def update_styles(self, text_color=None):
        is_dark = self.current_theme == "dark"
        bg_color = "#0d1117" if is_dark else "#ffffff"
        border_color = "#30363d" if is_dark else "#d0d7de"
        focus_color = "#58a6ff"  # GitHub blue

        input_style = f"""
            QLineEdit {{
                background: {bg_color};
                color: {("#c9d1d9" if is_dark else "#1f1f1f")};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {focus_color};
            }}
        """
        # Apply to all inputs
        for inp in self.all_inputs:
            inp.setStyleSheet(input_style)

        # Preserve and update web view content
        if hasattr(self, 'last_html'):
            self.web_view.setHtml(self.get_mathjax_template(self.last_html, bg_color, text_color))

    def update_web_view_content(self, html):
        # Now update with current theme colors
        is_dark = self.current_theme == "dark"
        bg_color = "#0d1117" if is_dark else "#ffffff"
        text_color = "#c9d1d9" if is_dark else "#1f1f1f"

        # Preserve scroll position
        self.web_view.page().runJavaScript(
            "window.scrollY",
            lambda pos: self.apply_theme_with_scroll(pos, html, bg_color, text_color)
        )

    def apply_theme_with_scroll(self, scroll_pos, html, bg_color, text_color):
        # Update content with current theme
        styled_html = self.get_mathjax_template(html, bg_color, text_color)
        self.web_view.setHtml(styled_html)

        # Restore scroll position
        self.web_view.page().runJavaScript(f"window.scrollTo(0, {scroll_pos});")

    def get_mathjax_template(self, content="", bg_color="#0d1117", text_color="white"):
        return f"""
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{ 
                    background-color: {bg_color}; 
                    color: {text_color};
                    font-family: 'Lucida Console', monospace;
                    line-height: 1.6;
                    padding: 20px;
                }}
                hr {{
                    border: 0.5px solid {text_color}33;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """

    def format_number(self, num):
        """Remove .0 for whole numbers, keep 1 decimal otherwise"""
        if isinstance(num, float) and num.is_integer():
            return int(num)
        return round(num, 2)



    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Input Grid
        input_layout = QHBoxLayout()
        self.matrix_a, inputs_a = self.create_matrix_input()
        self.matrix_b, inputs_b = self.create_matrix_input()

        # Combine all inputs
        self.all_inputs = inputs_a + inputs_b  # Contains 8 elements

        input_layout.addWidget(self.matrix_a)
        input_layout.addWidget(QLabel("✖️"))
        input_layout.addWidget(self.matrix_b)
        layout.addLayout(input_layout)

        # Calculate Button
        btn = QPushButton("Calculate")
        btn.setStyleSheet("""
            QPushButton {
                background: #238636;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        btn.clicked.connect(self.calculate)
        layout.addWidget(btn)

        # Steps Display
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.get_mathjax_template())
        layout.addWidget(self.web_view, 1)  # Add stretch factor

    def create_matrix_input(self):
        matrix = QWidget()
        grid = QGridLayout(matrix)
        grid.setSpacing(10)
        inputs = []
        for row in range(2):
            for col in range(2):
                inp = QLineEdit()
                inp.setPlaceholderText("0")
                inputs.append(inp)
                grid.addWidget(inp, row, col)
        return matrix, inputs

    def calculate(self):
        try:
            values = [float(inp.text()) for inp in self.all_inputs]
            a, b, c, d, e, f, g, h = values
            steps = self.generate_steps(a, b, c, d, e, f, g, h)

            # Store HTML content
            self.last_html = steps
            is_dark = self.current_theme == "dark"
            bg_color = "#0d1117" if is_dark else "#ffffff"
            text_color = "#c9d1d9" if is_dark else "#1f1f1f"

            self.web_view.setHtml(self.get_mathjax_template(steps, bg_color, text_color))

        except ValueError as e:
            error_html = self.get_mathjax_template(
                f"<div style='color: red'>⚠️ Please check and enter an integer value in each field correctly. All fields are required.</div>",
                "#0d1117" if self.current_theme == "dark" else "#ffffff",
                "#c9d1d9" if self.current_theme == "dark" else "#1f1f1f"
            )
            self.web_view.setHtml(error_html)

    def update_display(self):
        """Refresh display with current theme"""
        if hasattr(self, 'last_values'):
            steps = self.generate_steps(*self.last_values)
            self.web_view.setHtml(self.get_mathjax_template(steps))

    def generate_steps(self, a, b, c, d, e, f, g, h):
        is_dark = self.current_theme == "dark"
        colors = {
            'header': "#4192f0" if is_dark else "#d60326",
            'matrix': "#db2c52" if is_dark else "#400612",
            'calculation': "#0d9e66" if is_dark else "#bc4c00",
            'final': "#291be3" if is_dark else "#8250df"
        }

        format_num = lambda x: str(int(x)) if x.is_integer() else f"{x:.2f}"

        # Format matrix elements
        a_f, b_f, c_f, d_f = map(format_num, [a, b, c, d])
        e_f, f_f, g_f, h_f = map(format_num, [e, f, g, h])

        # Step 1: Matrix definitions
        step1 = (
            fr"\large\color{{{colors['header']}}}\text{{Matrix A = }}"
            fr"\color{{{colors['matrix']}}}"
            fr"\begin{{vmatrix}} {a_f} & {b_f} \\ {c_f} & {d_f} \end{{vmatrix}}"
        )
        step2 = (
            fr"\large\color{{{colors['header']}}}\text{{Matrix B = }}"
            fr"\color{{{colors['matrix']}}}"
            fr"\begin{{vmatrix}} {e_f} & {f_f} \\ {g_f} & {h_f} \end{{vmatrix}}"
        )

        # Step 2: Multiplication expression
        step3 = (
            fr"\large\color{{{colors['header']}}}\text{{A × B = }}"
            fr"\color{{{colors['matrix']}}}"
            fr"\left( \begin{{vmatrix}} {a_f} & {b_f} \\ {c_f} & {d_f} \end{{vmatrix}} "
            fr"\times \begin{{vmatrix}} {e_f} & {f_f} \\ {g_f} & {h_f} \end{{vmatrix}} \right)"
        )

        # Step 3: Multiplication expansion
        step4_lines = [
            fr"({a_f}×{e_f} + {b_f}×{g_f}) & ({a_f}×{f_f} + {b_f}×{h_f}) \\ ",
            fr"({c_f}×{e_f} + {d_f}×{g_f}) & ({c_f}×{f_f} + {d_f}×{h_f})"
        ]
        step4 = (
            fr"\large\color{{{colors['calculation']}}}\text{{A × B = }}"
            fr"\begin{{vmatrix}} {''.join(step4_lines)} \end{{vmatrix}}"
        )

        # Step 4: Calculate products and sums
        elements = []
        rows_a = [[a, b], [c, d]]
        cols_b = [[e, g], [f, h]]  # Columns of matrix B

        for row in rows_a:
            for col in cols_b:
                term1_val = row[0] * col[0]
                term1_str = f"{format_num(row[0])}×{format_num(col[0])}"
                term2_val = row[1] * col[1]
                term2_str = f"{format_num(row[1])}×{format_num(col[1])}"
                total = term1_val + term2_val
                elements.append((total, f"{term1_str} + {term2_str}"))

        step5_lines = [
            fr"{elements[0][1]} & {elements[1][1]} \\ ",
            fr"{elements[2][1]} & {elements[3][1]}"
        ]
        step5 = (
            fr"\large\color{{{colors['calculation']}}}\text{{Calculate Products:}}"
            fr"\begin{{vmatrix}} {''.join(step5_lines)} \end{{vmatrix}}"
        )

        # Step 5: Sum results
        step6_lines = [
            fr"{format_num(elements[0][0])} & {format_num(elements[1][0])} \\ ",
            fr"{format_num(elements[2][0])} & {format_num(elements[3][0])}"
        ]
        step6 = (
            fr"\large\color{{{colors['calculation']}}}\text{{Sum Results:}}"
            fr"\begin{{vmatrix}} {''.join(step6_lines)} \end{{vmatrix}}"
        )

        # Final result
        final = lambda x: format_num(x)
        step7 = (
            fr"\large\color{{{colors['final']}}}\text{{A × B = }}"
            fr"\begin{{vmatrix}} "
            fr"{final(elements[0][0])} & {final(elements[1][0])} \\ "
            fr"{final(elements[2][0])} & {final(elements[3][0])}"
            fr"\end{{vmatrix}}"
        )

        return f"""
            <div class="steps">
                <div class="step">
                    <div class="step-number">Step 1: Define Matrices</div>
                    \[{step1}\]
                    \[{step2}\]
                </div>
                <div class="step">
                    <div class="step-number">Step 2: Multiply Matrices</div>
                    \[{step3}\]
                </div>
                <div class="step">
                    <div class="step-number">Step 3: Expand Multiplication</div>
                    \[{step4}\]
                </div>
                <div class="step">
                    <div class="step-number">Step 4: Calculate Products</div>
                    \[{step5}\]
                </div>
                <div class="step">
                    <div class="step-number">Step 5: Sum Results</div>
                    \[{step6}\]
                </div>
                <div class="final-result">
                    \[{step7}\]
                </div>
            </div>
        """

    def get_mathjax_template(self, content="", bg_color="#0d1117", text_color="white"):
            return f"""
            <html>
            <head>
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                <style>
                    body {{
                        background-color: {bg_color};
                        color: {text_color};
                        font-family: 'Lucida Console', monospace;
                        line-height: 1.6;
                        padding: 20px;
                    }}
                    .step-header {{
                        color: {("#58a6ff" if bg_color == "#0d1117" else "#0366d6")};
                        font-size: 18px;
                        margin-top: 15px;
                    }}
                    .calculation-step {{
                        color: {("#ff9b72" if bg_color == "#0d1117" else "#bc4c00")};
                    }}
                    .final-result {{
                        color: {("#d2a8ff" if bg_color == "#0d1117" else "#8250df")};
                        font-size: 20px;
                    }}
                    hr {{
                        border-color: {("#30363d" if bg_color == "#0d1117" else "#d0d7de")};
                    }}
                </style>
            </head>
            <body>
                {content}
            </body>
            </html>
            """
