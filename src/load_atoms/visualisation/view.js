/**
This script is used to rotate the 3D model of the molecule.

Concretely, we:
  1. grab the rotation element from the x3d scene with id "atoms-rotation" 
        this wraps the entire scene, and so we can dynamically set the rotation
        attribute to rotate the entire scene
  2. set an animation step function that rotates the scene by a
        certain speed (rotationSpeed)
  3. add an event listener to the scene that pauses rotation when the user
        is interacting in a click-and-drag manner, and toggles the rotation
        when the user clicks on the scene

This script is modified before use to replace all instances of the string
"uid" with a unique (and variable-name allowable) identifier. This is to
ensure that the script can be used multiple times on the same page without
conflicting with itself.

See load_atoms.visualise for how exactly this is done.
*/

// wrap in an IIFE to avoid polluting the global scope
// and to allow for multiple instances of this script
(function () {
    // start of replace me
    const config = {
        currentlyRotating: true,
        rotationSpeed: 0.3, // rad/s
        id: "_uid",
    };
    // end of replace me

    // ~~~~~~~~
    // ROTATION
    // ~~~~~~~~
    let previousTimeStamp = performance.now();
    const x3dScene = document
        .getElementById(config.id)
        .getElementsByTagName("x3d")[0];

    // find child element with id "atoms-rotation"
    const rotationElement = x3dScene.querySelector("#atoms-rotation");

    function animationStep(timeStamp) {
        // calculate the time difference
        const deltaTime = timeStamp - previousTimeStamp;
        previousTimeStamp = timeStamp;

        // update rotation
        if (!config.currentlyRotating) {
            // request the next frame
            window.requestAnimationFrame(animationStep);
            return;
        }

        // turn `x, y, z, angle` into `x, y, z, angle + speed * deltaTime`
        const parts = rotationElement.getAttribute("rotation").split(", ");
        parts[3] = String(
            parseFloat(parts[3]) + (config.rotationSpeed * deltaTime) / 1000
        );
        rotationElement.setAttribute("rotation", parts.join(", "));

        // request the next frame
        window.requestAnimationFrame(animationStep);
    }
    window.requestAnimationFrame(animationStep);

    // ~~~~~~~~
    // INTERACTION
    // ~~~~~~~~
    let clickStart, wasRotatingBeforeClick;

    x3dScene.addEventListener("mousedown", function () {
        clickStart = performance.now();
        wasRotatingBeforeClick = config.currentlyRotating;
        config.currentlyRotating = false;
        console.log(wasRotatingBeforeClick, config.currentlyRotating);

        x3dScene.addEventListener("mouseup", function () {
            if (performance.now() - clickStart < 200) {
                // short click: toggle rotation
                config.currentlyRotating = !wasRotatingBeforeClick;
            } else {
                // long click: maintain rotation
                config.currentlyRotating = wasRotatingBeforeClick;
            }
        });
    });
})();
