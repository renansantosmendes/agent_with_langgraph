from starlette.applications import Starlette
from starlette.responses import JSONResponse
import uvicorn

app = Starlette()

@app.route('/')
async def homepage(request):
    return JSONResponse({'hello': 'world'})

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)