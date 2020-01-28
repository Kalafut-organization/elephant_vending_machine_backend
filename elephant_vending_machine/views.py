from elephant_vending_machine import app

@app.route('/')
def index():
    return 'Hello Elephants!'