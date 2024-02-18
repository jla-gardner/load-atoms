/**
This script is used to rotate the 3D model of the molecule.

Concretely, we:
  1. grab the rotation element from the x3d scene with id "atoms-rotation" 
        this wraps the entire scene, and so we can dynamically set the rotation
        attribute to rotate the entire scene
  2. set an animation step function that rotates the scene by a
        certain speed (rotationSpeed_uid)
  3. add an event listener to the scene that pauses rotation when the user
        is interacting in a click-and-drag manner, and toggles the rotation
        when the user clicks on the scene

This script is modified before use to replace all instances of the string
"uid" with a unique (and variable-name allowable) identifier. This is to
ensure that the script can be used multiple times on the same page without
conflicting with itself.

See load_atoms.visualise for how exactly this is done.
*/

// ~~~~~~~~
// ROTATION
// ~~~~~~~~

const rotationSpeed_uid = 0.3; // rad/s
let currentlyRotating_uid = true;
let previousTimeStamp_uid = performance.now();
const x3dScene_uid = document
    .getElementById("uid")
    .getElementsByTagName("x3d")[0];

// find child element with id "atoms-rotation"
const rotationElement_uid = x3dScene_uid.querySelector("#atoms-rotation");

function animationStep_uid(timeStamp) {
    // calculate the time difference
    const deltaTime = timeStamp - previousTimeStamp_uid;
    previousTimeStamp_uid = timeStamp;

    // update rotation
    if (!currentlyRotating_uid) {
        // request the next frame
        window.requestAnimationFrame(animationStep_uid);
        return;
    }

    // turn `x, y, z, angle` into `x, y, z, angle + speed * deltaTime`
    const parts = rotationElement_uid.getAttribute("rotation").split(", ");
    parts[3] = String(
        parseFloat(parts[3]) + (rotationSpeed_uid * deltaTime) / 1000
    );
    rotationElement_uid.setAttribute("rotation", parts.join(", "));

    // request the next frame
    window.requestAnimationFrame(animationStep_uid);
}
window.requestAnimationFrame(animationStep_uid);

// ~~~~~~~~
// INTERACTION
// ~~~~~~~~

let clickStart_uid, wasRotatingBeforeClick_uid;

x3dScene_uid.addEventListener("mousedown", function () {
    clickStart_uid = performance.now();
    wasRotatingBeforeClick_uid = currentlyRotating_uid;
    currentlyRotating_uid = false;
    console.log(wasRotatingBeforeClick_uid, currentlyRotating_uid);

    x3dScene_uid.addEventListener("mouseup", function () {
        if (performance.now() - clickStart_uid < 200) {
            // short click: toggle rotation
            currentlyRotating_uid = !wasRotatingBeforeClick_uid;
        } else {
            // long click: maintain rotation
            currentlyRotating_uid = wasRotatingBeforeClick_uid;
        }
    });
});
