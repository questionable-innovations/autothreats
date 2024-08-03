from typing import Annotated
from fastapi import FastAPI
from fastapi.responses import Response
from subprocess import run
from datetime import datetime

PAPER_HEIGHT = 148
PAPER_WIDTH = 210
MARGIN = 20

with open("test.tex", "r") as file:
    TEMPLATE = file.read()

app = FastAPI()

@app.get("/submit")
def submit(title: str, first_name: str, last_name: str, address_line_1: str, address_line_2: str, suburb: str, city: str, postcode: str, description: str):
    
    data = TEMPLATE.replace("%FONT%", "Un_funny Death Threat")

    document = f"""\\noindent {title} {first_name} {last_name}\\\\
{address_line_1}\\\\
"""
    
    if address_line_2 != "":
        document += f"{address_line_2}\\\\\n"
    
    document += f"""{suburb}
{city} {postcode} \\\\
\\newline
\\noindent {description}
"""
    
    data = data.replace("%DOC%", document)

    print(data)

    now = int(datetime.now().timestamp())
    with open(f"/tmp/deaththreat-{now}.tex", "+w") as file:
        file.write(data)
    
    run(["xelatex", f"deaththreat-{now}.tex"], cwd="/tmp")

    run(["/usr/bin/inkscape", "--export-text-to-path",f"--export-plain-svg=/tmp/deaththreat-p-{now}.svg",f"/tmp/deaththreat-{now}.pdf"])

    data = open(f"/tmp/deaththreat-p-{now}.svg", "r").read()

    return Response(content = data, media_type="image/svg+xml")
