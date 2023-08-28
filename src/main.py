from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from orders.router import router as order_router
from products.router import router as product_router
from auth.router import router as auth_router

from db_config import init, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init()
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(order_router)
app.include_router(product_router)
app.include_router(auth_router)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/orders/1/ws");
            ws.onmessage = function(event) {
                const data = event.data;
                if (data === 'ping') {
                    ws.send('pong');
                } else {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                }
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get('/')
def wwq():
    return HTMLResponse(html)
