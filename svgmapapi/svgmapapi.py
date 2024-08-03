import re 
import prettymaps
from fastapi import FastAPI, HTTPException, Response
from io import StringIO
import matplotlib
import numpy as np
import matplotlib.patches as patches

app = FastAPI()

matplotlib.use('agg')

# make it http api thingmajig
# remove copyright box
# make colours good

@app.get("/")
def main(q: str | None = None):
    if q is None:
        raise HTTPException(status_code=404, detail="no query specified!")
    print(q)
    if re.match(r"\([-\d.]+, ?[-\d.]+\)", q):
        query = (float(q[1:q.find(",") - 1]),float(q[q.find(","):len(q)-1]))
    else: 
        query = q
    
    f = StringIO()
    try:
        plot = prettymaps.plot(
            query,
            preset='cb-bf-f',
            radius=500.0,
            circle=True,
            credit=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error occurred {e}")

    circ = patches.Circle((0.5, 0.5), 0.03, color=(0,0,0,0), lw=4, ec='#000')
    plot.fig.add_artist(circ)
    
    plot.fig.savefig(f, format="svg")
    return Response(content=f.getvalue(), media_type="image/svg+xml")
