from browser import document

def say_hello():
    document["output"].text = "Hello, Brython!"

document["button"].bind("click", say_hello)
