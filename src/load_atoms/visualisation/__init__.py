from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from xml.dom import minidom

import numpy as np
from ase import Atom, Atoms
from ase.data import covalent_radii
from ase.data.colors import jmol_colors
from ase.neighborlist import natural_cutoffs, neighbor_list
from IPython.core.display import HTML

BOND_RADIUS = 0.17
MIN_ATOM_RADIUS = BOND_RADIUS + 0.1


def view(
    atoms: Atoms,
    show_bonds: bool = False,
    start_rotation: bool | None = None,
):
    """
    Generate an interactive visualisation of an :class:`ase.Atoms` object.

    Parameters
    ----------
    atoms:
        The atoms object to visualise.
    show_bonds:
        Whether to show bonds between atoms.
    start_rotation:
        Whether to start the visualisation rotating. If :code:`None`, the
        default is to start rotating if there are fewer than 400 atoms.

    Example
    -------
    Visualise an ethanol molecule in a Jupyter notebook:

    .. code-block:: python
        :emphasize-lines: 5

        from ase.build import molecule
        from load_atoms import view

        ethanol = molecule("CH3CH2OH")
        view(ethanol, show_bonds=True)

    .. raw:: html
        :file: ../../../docs/source/_static/ethanol.html

    Save the visualisation to an :code:`html` file:

    .. code-block:: python
        :emphasize-lines: 3

        from pathlib import Path

        viz = view(ethanol, show_bonds=True)
        Path("ethanol.html").write_text(viz.data)
    """
    scene = x3d_scene(atoms, show_bonds, width="300px", height="300px")

    if start_rotation is None:
        start_rotation = len(atoms) <= 400

    uid = unique_variable_name()
    js_file = Path(__file__).parent / "view.js"
    config = {
        "id": uid,
        "currentlyRotating": start_rotation,
        "rotationSpeed": 0.3,
    }
    js = js_file.read_text()
    # replace everythong between "    // start of replace me" and
    # "    // end of replace me" with the config
    lines = js.splitlines()
    start = lines.index("    // start of replace me") + 1
    end = lines.index("    // end of replace me")
    replacement = "    const config = " + json.dumps(config) + ";"
    js = "\n".join(lines[:start] + [replacement] + lines[end + 1 :])

    x3d_script = (Path(__file__).parent / "x3d.script").read_text()

    return HTML(
        f"""\
<html>
    <body>
    {x3d_script}
    <div id="{uid}">
        {scene}
    </div>
    <script>
        {js}
    </script>
    </body>
</html>
"""
    )


def x3d_scene(
    structure: Atoms,
    show_bonds: bool = False,
    **css_style: str,
) -> str:
    style = {"width": "300px", "height": "300px"}
    style.update(css_style)
    style = " ".join(f'{k}="{v}";' for k, v in style.items())

    scene = x3d_atoms(structure.copy(), show_bonds=show_bonds)

    document = f"""\
<X3D {style}>
<param name="showProgress" value="false" />

<!--Inserting Generated X3D Scene-->
{pretty_print(scene)}
<!--End of Inserted Scene-->

</X3D>
"""
    return document


def x3d_atom(atom: Atom, scale: float = 1.0):
    """Represent an atom as a coloured sphere."""

    radius = max(covalent_radii[atom.number] * scale, MIN_ATOM_RADIUS)
    shape = element(
        "shape",
        children=(appearance_for(atom), element("sphere", radius=f"{radius}")),
    )

    x, y, z = atom.position
    return translate(shape, x, y, z)


def appearance_for(atom: Atom):
    r, g, b = jmol_colors[atom.number]
    return element(
        "appearance",
        child=element("material", diffuseColor=f"{r} {g} {b}"),
    )


def x3d_wireframe_box(box):
    """
    Wireframe representation of a box (3x3 array).

    To draw a box, spanned by vectors a, b and c, it is necessary to
    draw 4 faces, each of which is a parallelogram. The faces are:
    (start from) , (vectors spanning the face)
    1. (0), (a, b)
    2. (c), (a, b) # opposite face to 1.
    3. (0), (a, c)
    4. (b), (a, c) # opposite face to 3.
    """

    a, b, c = box
    faces = [
        wireframe_face(a, b),
        wireframe_face(a, b, origin=c),
        wireframe_face(a, c),
        wireframe_face(a, c, origin=b),
    ]
    return group(faces)


def wireframe_face(vec1, vec2, origin=(0, 0, 0)):
    """Wireframe representation of a face spanned by vec1 and vec2."""

    x1, y1, z1 = vec1
    x2, y2, z2 = vec2

    material = element(
        "material", diffuseColor="0 0 0"
    )  # TODO: make this work in both dark and light mode
    appearance = element("appearance", child=material)

    points = [
        (0, 0, 0),
        (x1, y1, z1),
        (x1 + x2, y1 + y2, z1 + z2),
        (x2, y2, z2),
        (0, 0, 0),
    ]
    points = " ".join(f"{x} {y} {z}" for x, y, z in points)

    coordinates = element("coordinate", point=points)
    lineset = element("lineset", vertexCount="5", child=coordinates)
    shape = element("shape", children=(appearance, lineset))

    x, y, z = origin
    return translate(shape, x, y, z)


def x3d_atoms(atoms: Atoms, show_bonds: bool = False):
    """Convert an atoms object into an x3d representation."""

    # first, ensure that the atoms are within the cell
    if atoms.pbc.any():
        atoms.wrap()
        show_cell = True
    else:
        atoms.center(vacuum=0.1 if len(atoms) > 1 else 2.5)
        show_cell = False

    scale = 0.6 if show_bonds else 1.0

    atom_spheres = group([x3d_atom(atom, scale) for atom in atoms])  # type: ignore
    bonds = x3d_bonds(atoms, scale) if show_bonds else empty_element()
    wireframe = x3d_wireframe_box(atoms.cell) if show_cell else empty_element()
    cell = group((wireframe, atom_spheres, bonds))

    # we want the cell to be in the middle of the viewport
    # so that we can (a) see the whole cell and (b) rotate around the center
    # therefore we translate so that the center of the cell is at the origin
    cell_center = atoms.cell.sum(axis=0) / 2  # type: ignore
    cell = translate(cell, *(-cell_center))
    # rotate the cell about y (we grab this later to start spinning it)
    cell = rotate(cell, 0, 1, 0, 0.1, id="atoms-rotation")

    # we want the cell, and all atoms, to be visible
    # - sometimes atoms appear outside the cell
    # - sometimes atoms only take up a small part of the cell
    # location of the viewpoint therefore takes both of these into account:
    # the scene is centered on the cell, so we find the furthest point away
    # from the cell center, and use this to determine the
    # distance of the viewpoint
    points = np.vstack((atoms.positions, atoms.cell[:]))  # type: ignore
    max_xyz_extent = get_maximum_extent(points - cell_center)

    # put the camera 2.2x as far away as
    # the largest separation between two points in any of x, y or z
    max_dim = max(max_xyz_extent)
    pos = f"0, 0, {max_dim * 2.2}"

    # NB. viewpoint needs to contain an (empty) child to be valid x3d
    viewpoint = element("viewpoint", position=pos, child=empty_element())

    return element("scene", children=(viewpoint, cell), id="atoms-scene")


def empty_element():
    return element("group")


def x3d_bonds(atoms: Atoms, scale: float = 1.0):
    # set pbc off so that we don't try to draw bonds across periodic boundaries
    atoms = atoms.copy()
    atoms.pbc = False
    i, j = neighbor_list("ij", atoms, cutoff=natural_cutoffs(atoms, mult=1.2))  # type: ignore
    bond_index = list(zip(i.tolist(), j.tolist()))

    return group([x3d_bond(atoms[a], atoms[b], scale) for a, b in bond_index])  # type: ignore


def atom_size(atom: Atom, scale: float = 1.0):
    return max(covalent_radii[atom.number] * scale, MIN_ATOM_RADIUS)


def x3d_bond(a: Atom, b: Atom, scale: float = 1.0):
    # if same element: draw a single cylinder connecting the two
    if a.number == b.number:
        return cyclinder_between(a.position, b.position, appearance_for(a))

    # otherwise, draw two cylinders, one from each atom to a suitable
    # point in the middle, and coloured according the respective atoms
    dist = np.linalg.norm(a.position - b.position)
    r_a = atom_size(a, scale)
    r_b = atom_size(b, scale)
    frac = r_a / dist + (0.5 * (dist - r_a - r_b)) / dist
    halfway = a.position + frac * (b.position - a.position)

    a_to_center = cyclinder_between(a.position, halfway, appearance_for(a))
    center_to_b = cyclinder_between(halfway, b.position, appearance_for(b))

    return group([a_to_center, center_to_b])


def cyclinder_between(a, b, appearance):
    halfway = (a + b) / 2

    z = np.array([0, 1, 0])
    v = b - a
    d = np.linalg.norm(v)
    v = v / d
    angle = np.arccos(z.dot(v))
    axis = np.cross(z, v)

    cylinder = element(
        "shape",
        children=[
            appearance,
            element("cylinder", radius=f"{BOND_RADIUS}", height=f"{d}"),
        ],
    )
    return translate(rotate(cylinder, *axis, angle), *halfway)  # type: ignore


def element(name, child=None, children=None, **attributes) -> ET.Element:
    """Convenience function to make an XML element.

    If child is specified, it is appended to the element.
    If children is specified, they are appended to the element.
    You cannot specify both child and children."""

    # make sure we don't specify both child and children
    if child is not None:
        assert children is None, "Cannot specify both child and children"
        children = [child]
    else:
        children = children or []

    element = ET.Element(name, **attributes)
    for child in children:
        element.append(child)
    return element


def translate(thing, x, y, z):
    """Translate a x3d element by x, y, z."""
    return element("transform", translation=f"{x} {y} {z}", child=thing)


def rotate(thing, x, y, z, angle, **attributes):
    return element(
        "transform",
        rotation=f"{x}, {y}, {z}, {angle}",
        child=thing,
        **attributes,
    )


def group(things):
    """Group a (list of) x3d elements."""
    return element("group", children=things)


def pretty_print(element: ET.Element, indent: int = 2):
    """Pretty print an XML element."""

    byte_string = ET.tostring(element, "utf-8")
    parsed = minidom.parseString(byte_string)
    prettied = parsed.toprettyxml(indent=" " * indent)
    # remove first line - contains an extra, un-needed xml declaration
    lines = prettied.splitlines()[1:]
    return "\n".join(lines)


def get_maximum_extent(xyz):
    """Get the maximum extent of an array of 3d set of points."""

    return np.max(xyz, axis=0) - np.min(xyz, axis=0)


def unique_variable_name():
    now = str(datetime.now().timestamp())
    now = now.replace(".", "")
    return "".join(chr(97 + int(digit)) for digit in now)
