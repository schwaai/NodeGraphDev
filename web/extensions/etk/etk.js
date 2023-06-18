import {app} from "/scripts/app.js";

function addTextBox(node) {
    // create the textbox widget
    const widget = {
        type: "text",
        name: "MyTextBox",
        value: "Default Text",
        size: 20,  // text size
    };

    // add the widget to the node
    node.addWidget(widget.type, widget.name, widget.value, function (value) {
        // callback function to handle changes in the textbox
        // this can be left empty if you don't need to handle changes
        console.log(`New value: ${value}`);
    }, widget.size);
}

app.registerExtension({
    name: "Comfy.ETK.nodes.EvalWidget",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // check if this has exec in its name

        if (nodeData.name == "Eval Widget") {

            // // when the original node is defined, we can add our textbox
            // // replace the widget at input.required.text_to_eval with our own
            // const codeWidget = nodeData.input.required.text_to_eval;
            //
            // if (codeWidget) {
            //     // replace the CODE widget with our own
            //     //nodeData.input[codeWidget[0]] = ["MyTextBox"];
            //     // make sure its gone visually
            //     // this should be of type STRING
            //     nodeData.input.required.text_to_eval =
            //         ["STRING", node.addWidget(widget.type, widget.name, widget.value, function (value) {
            //         // callback function to handle changes in the textbox
            //         // this can be left empty if you don't need to handle changes
            //         console.log(`New value: ${value}`);
            //     }, widget.size)];
            //
            //
            // }

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // call our function to add the textbox
                addTextBox(this);

                return r;
            };
        }
    }
});
