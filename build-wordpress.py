"""Build the WordPress-ready copy of the Catalan-for-Spanish-speakers test.

WordPress (or a plugin on catalanwithbet.com) rewrites characters inside
inline <script> blocks on that page, which turns the test's JavaScript into
a SyntaxError. The built copy ships the script base64-encoded in a data
attribute and runs it through a one-line loader that contains no quotes,
ampersands or angle brackets, so there is nothing left to rewrite.

Usage: python3 build-wordpress.py
Edit prova-de-nivell-cast-cat.html, then rebuild and paste
wordpress/prova-de-nivell-cast-cat.html into the Custom HTML block.
"""
import base64
import re

SRC = "prova-de-nivell-cast-cat.html"
OUT = "wordpress/prova-de-nivell-cast-cat.html"

html = open(SRC, encoding="utf-8").read()
scripts = re.findall(r"<script>\n(.*?)</script>\n", html, flags=re.S)
assert len(scripts) == 2, "expected the error-reporter script and the main script"
main_js = scripts[1]

# Drop both inline scripts; append the encoded loader in their place.
html = re.sub(r"<script>\n.*?</script>\n", "", html, flags=re.S)
payload = base64.b64encode(main_js.encode("utf-8")).decode("ascii")
loader = (
    '<script data-cwb-js="' + payload + '">'
    "new Function(decodeURIComponent(escape(atob(document.currentScript.dataset.cwbJs))))()"
    "</script>\n"
)
assert html.rstrip().endswith("</div>")
html = html.rstrip()[: -len("</div>")] + loader + "</div>\n"
html = html.replace(
    "Pega este bloque en un bloque \"HTML personalizado\" de WordPress",
    "Pega este bloque en un bloque \"HTML personalizado\" de WordPress\n"
    "     (Fichero generado con build-wordpress.py: el JavaScript va codificado\n"
    "      para que WordPress no lo modifique. Edita prova-de-nivell-cast-cat.html.)",
)
open(OUT, "w", encoding="utf-8").write(html)
print(OUT, len(html), "bytes")
