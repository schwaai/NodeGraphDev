import {app} from "/scripts/app.js";
import {ComfyWidgets} from "/scripts/widgets.js";

class WidgetDefinitionExtension {
    constructor() {
        this.name = "WidgetDefinitionExtension";
    }

    async fetchWidgetDefsFromBackend() {
        // Fetch the widget definitions from the server
        const response = await fetch("/widgetdefs");
        const widgetDefs = await response.json();

        // Return the fetched widget definitions
        return widgetDefs;
    }

    async registerCustomWidgetNodesFromServer() {
        const widgetDefs = await this.fetchWidgetDefsFromBackend();
        this.registerCustomWidgetNodes(widgetDefs);
    }

    registerCustomWidgetNodes(widgetDefs) {
        for (const widgetDef of widgetDefs) {
            const {widgetId, name, type, properties, render} = widgetDef;

            const widgetNode = function () {
                const WidgetClass = ComfyWidgets[type]; // Get the widget constructor function
                const widget = new WidgetClass(properties);
                const renderElement = document.createElement("div");
                renderElement.innerHTML = render;
                this.addWidget(widget, renderElement);

                app.invokeExtensionsAsync("widgetCreated", widget);
            };


            widgetNode.title = name;
            widgetNode.category = "Custom Widgets";

            LiteGraph.registerNodeType(widgetId, widgetNode);
        }
    }
}

// Create an instance of the WidgetDefinitionExtension class
const widgetDefinitionExtension = new WidgetDefinitionExtension();

// Register the extension and load widget definitions from the server
//app.registerExtension(widgetDefinitionExtension);
//widgetDefinitionExtension.registerCustomWidgetNodesFromServer();

// Append the ComfyWidgets object with server-defined widgets
async function appendServerWidgets() {
    const widgetDefs = await widgetDefinitionExtension.fetchWidgetDefsFromBackend();

    for (const widgetDef of widgetDefs) {
        const {widgetId, name, type, properties, render} = widgetDef;

        // # example
        // INT(node, inputName, inputData) {
        //    const {val, config} = getNumberDefaults(inputData, 1);
        //    Object.assign(config, {precision: 0});
        //    return {
        //        widget: node.addWidget(
        //            "number",
        //            inputName,
        //            val,
        //            function (v) {
        //                const s = this.options.step / 10;
        //                this.value = Math.round(v / s) * s;
        //            },
        //           config
        //        ),
        //    };
        //}

        // create a const that is the exact return statement from the example above
        const widgetGenerator = {
            BAH(node, inputName, inputData) {
                const val = 1;
                const config = 2;
                //Object.assign(config, {precision: 0});
                return {
                    widget: node.addWidget(
                        "number",
                        inputName,
                        val,
                        function (v) {
                            this.value = 1;
                        },
                        config
                    ),

                };
            },

            // Add the widget class to the ComfyWidgets array
        }
        ComfyWidgets[type] = widgetGenerator;

        // Register the node type using the widgetId
        const baseClass = eval(widgetDef);
        LiteGraph.registerNodeType(widgetId, baseClass);
    }

}

// Call the function to append server-defined widgets
//appendServerWidgets();


