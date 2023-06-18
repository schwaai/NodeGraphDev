// import {app} from "/scripts/app.js";
//
// app.registerExtension({
//     name: "ETK.CheckboxWidget",
//     init(app) {
//         // Nothing to do in the initialization phase for this extension
//     },
//     setup(app) {
//         // Nothing to do in the setup phase for this extension
//     },
//
//     beforeRegisterNodeDef(nodeType, nodeData, app) {
//         // Monkey patch onExecute to update the checkbox widget value
//         const onExecute = nodeType.prototype.onExecute;
//         nodeType.prototype.onExecute = function () {
//             const r = onExecute ? onExecute.apply(this, arguments) : undefined;
//             return r;
//         };
//
//         const onNodeCreated = nodeType.prototype.onNodeCreated;
//         nodeType.prototype.onNodeCreated = function () {
//             const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
//             const my_node = this
//             this.setProperty('CHECKBOX', false);
//             this.serialize_widgets = true;
//             const my_widget = {
//                 name: 'CHECKBOX',
//                 type: 'checkbox',
//
//                 set value(v) {
//                     my_node.properties["CHECKBOX"] = v;
//                 },
//                 get value() {
//                     return my_node.properties["CHECKBOX"];
//                 },
//
//
//             };
//
//             this.addCustomWidget(my_widget);
//             this.onRemoved = function () {
//                 const widgetIndex = this.widgets.findIndex(w => w.name === 'CHECKBOX');
//                 if (widgetIndex !== -1) {
//                     //this.widgets[widgetIndex].element.remove();
//                 }
//             };
//             this.onSelected = function () {
//                 this.selected = true
//             }
//             this.onDeselected = function () {
//                 this.selected = false
//             }
//             const widgetIndex = this.widgets.findIndex(w => w.name === 'CHECKBOX');
//             if (widgetIndex !== -1) {
//                 const widget = this.widgets[widgetIndex];
//             }
//             return r;
//         };
//     },
//     registerCustomNodes(app) {
//         // Nothing to do here for this extension
//     },
//     loadedGraphNode(node, app) {
//         // Nothing to do here for this extension
//     },
//     nodeCreated(node, app) {
//         // Nothing to do here for this extension
//     }
// });
