"""Build the WordPress-ready copy of the Catalan-for-Spanish-speakers test.

WordPress (or a plugin on catalanwithbet.com) rewrites the quotes inside
inline <script> blocks on that page, which turns the test's JavaScript into
a SyntaxError. The built copy ships the script HTML-escaped in a data
attribute (attribute values aren't rewritten) and runs it through a one-line
loader that contains no quotes or ampersands, so there is nothing to rewrite.

Usage: python3 build-wordpress.py
Edit prova-de-nivell-cast-cat.html, then rebuild and paste
wordpress/prova-de-nivell-cast-cat.html into the Custom HTML block.
"""
import html as htmllib
import re

SRC = "prova-de-nivell-cast-cat.html"
OUT = "wordpress/prova-de-nivell-cast-cat.html"

html = open(SRC, encoding="utf-8").read()
scripts = re.findall(r"<script>\n(.*?)</script>\n", html, flags=re.S)
assert len(scripts) == 2, "expected the error-reporter script and the main script"
main_js = scripts[1]

# Drop both inline scripts; append the encoded loader in their place.
html = re.sub(r"<script>\n.*?</script>\n", "", html, flags=re.S)
payload = htmllib.escape(main_js, quote=True).replace("&#x27;", "'")
loader = (
    '<script data-cwb-js="' + payload + '">'
    "new Function(document.currentScript.dataset.cwbJs)()"
    "</script>\n"
)
assert html.rstrip().endswith("</div>")
html = html.rstrip()[: -len("</div>")] + loader + "</div>\n"
html = html.replace(
    "Pega este bloque en un bloque \"HTML personalizado\" de WordPress",
    "Pega este bloque en un bloque \"HTML personalizado\" de WordPress\n"
    "     (Fichero generado con build-wordpress.py: el JavaScript va dentro del\n"
    "      atributo data-cwb-js para que WordPress no cambie sus comillas.)",
)
open(OUT, "w", encoding="utf-8").write(html)
print(OUT, len(html), "bytes")
