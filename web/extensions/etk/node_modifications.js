import {app} from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
    name: "ETK.NodeModifications",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.internal_state_display_code) {
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);
                // set the code of the editor to the message
                if (this.widgets) {
                    const editor = this.widgets.find((w) => w.name === "text_to_eval");
                    editor.changeSrc(message.text[0])

                }

            }

        }

    }
});
