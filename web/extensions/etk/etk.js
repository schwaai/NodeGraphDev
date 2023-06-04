import {app} from "/scripts/app.js";
import {ComfyWidgets} from "/scripts/widgets.js";


const MultilineSymbol = Symbol();
const MultilineResizeSymbol = Symbol();

function addMultilineCodeWidget(node, name, opts, app) {
    const MIN_SIZE = 50;

    function computeSize(size) {
        if (node.widgets[0].last_y == null) return;

        let y = node.widgets[0].last_y;
        let freeSpace = size[1] - y;

        // Compute the height of all non customtext widgets
        let widgetHeight = 0;
        const multi = [];
        for (let i = 0; i < node.widgets.length; i++) {
            const w = node.widgets[i];
            if (w.type === "customtext") {
                multi.push(w);
            } else {
                if (w.computeSize) {
                    widgetHeight += w.computeSize()[1] + 4;
                } else {
                    widgetHeight += LiteGraph.NODE_WIDGET_HEIGHT + 4;
                }
            }
        }

        // See how large each text input can be
        freeSpace -= widgetHeight;
        freeSpace /= multi.length;

        if (freeSpace < MIN_SIZE) {
            // There isnt enough space for all the widgets, increase the size of the node
            freeSpace = MIN_SIZE;
            node.size[1] = y + widgetHeight + freeSpace * multi.length;
            node.graph.setDirtyCanvas(true);
        }

        // Position each of the widgets
        for (const w of node.widgets) {
            w.y = y;
            if (w.type === "customtext") {
                y += freeSpace;
            } else if (w.computeSize) {
                y += w.computeSize()[1] + 4;
            } else {
                y += LiteGraph.NODE_WIDGET_HEIGHT + 4;
            }
        }

        node.inputHeight = freeSpace;
    }


    const widget = {
        editor: null,
        type: "customtext",
        name,
        get value() {
            return this.inputEl.value;
        },
        set value(x) {
            this.inputEl.value = x;
        },
        // Called when the widget is added
        onAdded: function () {
            this.initializeEditor();
        },
        // Called when the node is created
        onNodeCreated: function () {
            this.initializeEditor();
        },
        initializeEditor: function () {
            // Create a container element for the code editor
            const editorContainer = document.createElement("div");
            editorContainer.className = "comfy-editor-container";

            // Add the container element to the DOM
            document.body.appendChild(editorContainer);

            // Initialize the Monaco Editor
            this.editor = monaco.editor.create(editorContainer, {
                value: this.inputEl.value,
                language: "python", // Set the desired programming language
                theme: "vs-dark", // Set the desired theme
                // Other configuration options...
            });

            // Handle value changes in the editor
            this.editor.onDidChangeModelContent((event) => {
                this.inputEl.value = this.editor.getValue();
                // Perform any other necessary actions
            });

            // Hide the textarea
            this.inputEl.hidden = true;
        },
        draw: function (ctx, _, widgetWidth, y, widgetHeight) {
            if (!this.parent.inputHeight) {
                // If we are initially offscreen when created we won't have received a resize event
                // Calculate it here instead
                computeSize(node.size);
            }
            const visible = app.canvas.ds.scale > 0.5 && this.type === "customtext";
            const margin = 10;
            const elRect = ctx.canvas.getBoundingClientRect();
            const transform = new DOMMatrix()
                .scaleSelf(elRect.width / ctx.canvas.width, elRect.height / ctx.canvas.height)
                .multiplySelf(ctx.getTransform())
                .translateSelf(margin, margin + y);
            if (this.editor) {
                // Update the visibility of the editor based on the scale and type
                if (visible && this.editor) {
                    // Show the editor container
                    this.editor.getDomNode().style.display = "block";
                    this.editor.layout({
                        width: widgetWidth - 20,
                        height: this.parent.inputHeight - 20,
                    });

                } else if (!visible && this.editor) {
                    // Hide the editor container
                    this.editor.getDomNode().style.display = "none";
                }

                // Set the style of the container element
                Object.assign(this.editor.getDomNode().style, {
                    transformOrigin: "0 0",
                    transform: transform,
                    left: "0px",
                    top: "0px",
                    position: "absolute",
                    zIndex: app.graph._nodes.indexOf(node),
                    color: "white",
                    height: this.parent.inputHeight-20 + "px",
                    width: widgetWidth - 20 + "px",
                });
            }
            else {
                this.initializeEditor();
            }
        },

        onRemove: function () {
            // Clean up the editor when the widget is removed
            if (this.editor) {
                this.editor.dispose(); // Dispose of the editor instance
                delete this.editor;
            }

            // Remove the editor container element from the DOM
            const editorContainer = document.querySelector(".comfy-editor-container");
            if (editorContainer) {
                editorContainer.remove();
            }
        },

    };
    widget.inputEl = document.createElement("textarea");
    widget.inputEl.className = "comfy-multiline-input";
    widget.inputEl.value = opts.defaultVal;
    widget.inputEl.placeholder = opts.placeholder || "";
    document.addEventListener("mousedown", function (event) {
        if (!widget.inputEl.contains(event.target)) {
            widget.inputEl.blur();
        }
    });
    widget.parent = node;
    document.body.appendChild(widget.inputEl);

    node.addCustomWidget(widget);

    app.canvas.onDrawBackground = function () {
        // Draw node isnt fired once the node is off the screen
        // if it goes off screen quickly, the input may not be removed
        // this shifts it off screen so it can be moved back if the node is visible.
        for (let n in app.graph._nodes) {
            n = graph._nodes[n];
            for (let w in n.widgets) {
                let wid = n.widgets[w];
                if (Object.hasOwn(wid, "inputEl")) {
                    wid.inputEl.style.left = -8000 + "px";
                    wid.inputEl.style.position = "absolute";
                }
            }
        }
    };

    node.onRemoved = function () {
        // When removing this node we need to remove the input from the DOM
        for (let y in this.widgets) {
            if (this.widgets[y].inputEl) {
                this.widgets[y].inputEl.remove();
            }
        }
    };

    widget.onRemove = () => {
        widget.inputEl?.remove();

        // Restore original size handler if we are the last
        if (!--node[MultilineSymbol]) {
            node.onResize = node[MultilineResizeSymbol];
            delete node[MultilineSymbol];
            delete node[MultilineResizeSymbol];
        }
    };

    if (node[MultilineSymbol]) {
        node[MultilineSymbol]++;
    } else {
        node[MultilineSymbol] = 1;
        const onResize = (node[MultilineResizeSymbol] = node.onResize);

        node.onResize = function (size) {
            computeSize(size);

            // Call original resizer handler
            if (onResize) {
                onResize.apply(this, arguments);
            }
        };
    }

    return {minWidth: 400, minHeight: 200, widget};
}

const myWidget = ComfyWidgets["STRING"];
myWidget.style = {
    background: "purple",
};

app.registerExtension({
    name: "ETK.widgets",
    async getCustomWidgets() {
        return [
            {
                "CODE": function (node, inputName, inputData, app) {
                    const defaultVal = inputData[1].default || "";

                    const tmp = addMultilineCodeWidget(node, inputName, {defaultVal, ...inputData[1]}, app);
                    tmp.widget.type = "customtext";
                    tmp.widget.inputEl.style.background = "purple";
                    return tmp;

                },
            },
        ][0];
    },
});


//
//     // make a copy of the widget "STRING"
//     // and change the name to "STRING2"
//     // and add it to the list of widgets
//     async beforeRegisterNodeDef(nodeType, nodeData, app) {
//         ComfyWidgets["CODE"] = function (node, inputName, inputData, app) {
//             const defaultVal = inputData[1].default || "";
//             const multiline = !!inputData[1].multiline;
//             return addMultilineWidget(node, inputName, {defaultVal, ...inputData[1]}, app);
//         };
//     },
//     async nodeCreated(node, app) {
//         const textWidget = node.widgets.find((w) => w.name === "text_to_eval");
//         //textWidget.style.display = 'none';
//         const stringWidget = widgets.find((w) => w.name === "STRING");
//         const stringWidgetCode = Object.assign({}, stringWidget);
//         stringWidgetCode.name = "CODE";
//         stringWidgetCode.color = "rgb(75, 0, 130)"; // Dark purple color
//         widgets.push(stringWidgetCode);
//     }
//     ,
//
// })
// ;

// async beforeRegisterNodeDef(nodeType, nodeData, app) {
//     if (nodeData.internal_state_display) {
//         const onExecuted = nodeType.prototype.onExecuted;
//         nodeType.prototype.onExecuted = function (message) {
//             onExecuted?.apply(this, arguments);
//
//             if (this.widgets) {
//                 const pos = this.widgets.findIndex((w) => w.name === "text");
//                 if (pos !== -1) {
//                     for (let i = pos; i < this.widgets.length; i++) {
//                         this.widgets[i].onRemove?.();
//                     }
//                     this.widgets.length = pos;
//                 }
//             }
//
//             for (const list of message.text) {
//                 const w = ComfyWidgets["STRING"](this, "text", ["STRING", {multiline: true}], app).widget;
//                 w.inputEl.readOnly = true;
//                 w.inputEl.style.opacity = 0.6;
//                 w.value = list;
//             }
//
//             this.onResize?.(this.size);
//         };
//     }
// };
// async nodeCreated(node, app) {
//     const textWidget = node.widgets.find((w) => w.name === "text_to_eval");
//     //textWidget.style.display = 'none';
//     monkeyPatch(node, 'ace_editor', {defaultVal: textWidget.value}, app);
//
//     const editorDiv = document.createElement('div');
//     editorDiv.style.width = '100%';
//     editorDiv.style.height = '100%';
//     textWidget.inputEl.appendChild(editorDiv);
//
//     const editor = ace.edit(editorDiv, {
//         mode: "ace/mode/python",
//         theme: "ace/theme/monokai",
//         fontSize: "8pt"
//     });
//     editor.setValue(textWidget.value);
//     editor.session.on('change', function() {
//         textWidget.value = editor.getValue();
//     });
// };


// function monkeyPatch(node, name, opts, app) {
//     const widget = {
//         type: "customtext",
//         name,
//         get value() {
//             return this.aceEditor.getValue();
//         },
//         set value(x) {
//             this.aceEditor.setValue(x);
//         },
//         draw: function (ctx, _, widgetWidth, y, widgetHeight) {
//             const visible = app.canvas.ds.scale > 0.5 && this.type === "customtext";
//             const margin = 10;
//             const elRect = ctx.canvas.getBoundingClientRect();
//             const transform = new DOMMatrix()
//                 .scaleSelf(elRect.width / ctx.canvas.width, elRect.height / ctx.canvas.height)
//                 .multiplySelf(ctx.getTransform())
//                 .translateSelf(margin, margin + y);
//
//             Object.assign(this.inputEl.style, {
//                 transformOrigin: "0 0",
//                 transform: transform,
//                 left: "0px",
//                 top: "0px",
//                 width: `${widgetWidth - (margin * 2)}px`,
//                 height: `${this.parent.inputHeight - (margin * 2)}px`,
//                 position: "absolute",
//                 background: (!node.color) ? '' : node.color,
//                 color: (!node.color) ? '' : 'white',
//                 zIndex: app.graph._nodes.indexOf(node),
//             });
//             this.inputEl.hidden = !visible;
//             this.aceEditor.resize();
//         },
//     };
//
//     widget.inputEl = document.createElement("div");
//     widget.inputEl.className = "comfy-multiline-input";
//
//     const wrapperDiv = document.createElement('div');
//     wrapperDiv.style.width = '100%';
//     wrapperDiv.style.height = '100%';
//     widget.inputEl.appendChild(wrapperDiv);
//
//     widget.aceEditor = ace.edit(wrapperDiv, {
//         mode: "ace/mode/python",
//         theme: "ace/theme/monokai",
//         minLines: 5,
//         maxLines: Infinity,
//     });
//
//     widget.aceEditor.setValue(opts.defaultVal);
//
//     document.addEventListener("mousedown", function (event) {
//         if (!widget.inputEl.contains(event.target)) {
//             widget.inputEl.blur();
//         }
//     });
//
//     widget.parent = node;
//     document.body.appendChild(widget.inputEl);
//
//     node.addCustomWidget(widget);
//
//     widget.onRemove = () => {
//         widget.inputEl?.remove();
//     };
//
//     return {minWidth: 400, minHeight: 200, widget};
// }
