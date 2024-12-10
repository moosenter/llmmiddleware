from fasthtml.common import Script, Link, FastHTML, uvicorn, Div, H1, Input, Body, Form, Group, Button, Title, picolink, Template, Style, partial
from fasthtml.components import Zero_md
import asyncio
import requests
import yaml

# Set up the app, including daisyui and tailwind for the chat component
tlink = Script(src="https://cdn.tailwindcss.com"),
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
app = FastHTML(hdrs=(tlink, dlink, picolink), exts='ws')

# Set up a chat model client and list of messages (https://claudette.answer.ai/)
# cli = Client(models[-1])
# sp = """You are a helpful and concise assistant."""
messages = []
with open("config/AppConfig.yaml", "r") as file:
    config = yaml.safe_load(file)
configured_llms = config["llms"]

def render_local_md(md, css = ''):
    css_template = Template(Style(css), data_append=True)
    return Zero_md(css_template, Script(md, type="text/markdown"))

css = '.markdown-body {background-color: unset !important; color: unset !important;}'
_render_local_md = partial(render_local_md, css=css)

# Chat message component (renders a chat bubble)
def ChatMessage(msg, render_md_fn=lambda x: x):
    md = render_md_fn(msg['content'])
    print(md)
    bubble_class = "chat-bubble-primary" if msg['role']=='user' else 'chat-bubble-secondary'
    chat_class = "chat-end" if msg['role']=='user' else 'chat-start'
    return Div(
            Div(msg['role'], cls="chat-header"),
            Div(md, cls=f"chat-bubble {bubble_class}"),
            cls=f"chat {chat_class}"
        )

# The input field for the user message. Also used to clear the
# input field after sending a message via an OOB swap
def ChatInput():
    return Input(type="text", name='msg', id='msg-input',
                 placeholder="Type a message",
                 cls="input input-bordered w-full", hx_swap_oob='true')

# The main screen
@app.route("/")
def get():

    page = Body(H1('LLM for Enterprise'),
                Div(*[ChatMessage(msg, render_md_fn=_render_local_md) for msg in messages],
                    id="chatlist", cls="chat-box h-[73vh] overflow-y-auto"),
                Form(Group(ChatInput(), Button("Send", cls="btn btn-primary")),
                    ws_send=True, hx_ext="ws", ws_connect="/wscon",
                    cls="flex space-x-2 mt-2",
                ),
                cls="p-4 max-w-lg mx-auto",
                )
    return Title('LLM for Enterprise'), page


@app.ws('/wscon')
async def ws(msg:str, send):

    # Send the user message to the user (updates the UI right away)
    messages.append({"role":"user", "content":msg.rstrip()})
    await send(Div(ChatMessage(messages[-1]), hx_swap_oob='beforeend', id="chatlist"))

    # Send the clear input field command to the user
    await send(ChatInput())

    # Simulate a delay
    await asyncio.sleep(1)

    print(messages)

    try:
        response = requests.post('http://backend:8000/generate', json=messages).json()['response']
    except:
        response = requests.post('http://localhost:8000/generate', json=messages).json()['response']
    print(
        f"Response from {configured_llms[0]['name']}: {response}"
    )

    messages.append({"role":"assistant", "content":response})

    await send(Div(ChatMessage(messages[-1]), hx_swap_oob='beforeend', id="chatlist"))

if __name__ == '__main__': 
    uvicorn.run("ws:app", host='0.0.0.0', port=8080, reload=True)