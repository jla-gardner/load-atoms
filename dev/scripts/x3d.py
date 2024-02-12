"""
Adapted from ASE
TODO remove this once these changes are merged into ASE
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

import numpy as np
from ase.data import covalent_radii
from ase.data.colors import jmol_colors


def visualisation_for(atoms):
    x3d_style = {"width": "400px", "height": "300px"}
    x3dstyle = " ".join(f'{k}="{v}";' for k, v in x3d_style.items())

    scene = x3d_atoms(atoms.copy())
    document = X3DOM_template.format(scene=pretty_print(scene), style=x3dstyle)
    return document


def x3d_atom(atom):
    """Represent an atom as an x3d, coloured sphere."""

    x, y, z = atom.position
    r, g, b = jmol_colors[atom.number]
    radius = covalent_radii[atom.number]

    material = element("material", diffuseColor=f"{r} {g} {b}")

    appearance = element("appearance", child=material)
    sphere = element("sphere", radius=f"{radius}")

    shape = element("shape", children=(appearance, sphere))
    return translate(shape, x, y, z)


def x3d_wireframe_box(box):
    """x3d wireframe representation of a box (3x3 array).

    To draw a box, spanned by vectors a, b and c, it is necessary to
    draw 4 faces, each of which is a parallelogram. The faces are:
    (start from) , (vectors spanning the face)
    1. (0), (a, b)
    2. (c), (a, b) # opposite face to 1.
    3. (0), (a, c)
    4. (b), (a, c) # opposite face to 3."""

    # box may not be a cube, hence not just using the diagonal
    a, b, c = box
    faces = [
        wireframe_face(a, b),
        wireframe_face(a, b, origin=c),
        wireframe_face(a, c),
        wireframe_face(a, c, origin=b),
    ]
    return group(faces)


def wireframe_face(vec1, vec2, origin=(0, 0, 0)):
    """x3d wireframe representation of a face spanned by vec1 and vec2."""

    x1, y1, z1 = vec1
    x2, y2, z2 = vec2

    material = element("material", diffuseColor="0 0 0")
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


def x3d_atoms(atoms):
    """Convert an atoms object into an x3d representation."""
    # first, ensure that the atoms are within the cell
    if atoms.pbc.any():
        atoms.wrap()
    else:
        atoms.center(vacuum=0.1)

    atom_spheres = group([x3d_atom(atom) for atom in atoms])
    wireframe = x3d_wireframe_box(atoms.cell)
    cell = group((wireframe, atom_spheres))

    # we want the cell to be in the middle of the viewport
    # so that we can (a) see the whole cell and (b) rotate around the center
    # therefore we translate so that the center of the cell is at the origin
    cell_center = atoms.cell.sum(axis=0) / 2
    cell = translate(cell, *(-cell_center))

    # we want the cell, and all atoms, to be visible
    # - sometimes atoms appear outside the cell
    # - sometimes atoms only take up a small part of the cell
    # location of the viewpoint therefore takes both of these into account:
    # the scene is centered on the cell, so we find the furthest point away
    # from the cell center, and use this to determine the
    # distance of the viewpoint
    points = np.vstack((atoms.positions, atoms.cell[:]))
    max_xyz_extent = get_maximum_extent(points - cell_center)

    # the largest separation between two points in any of x, y or z
    max_dim = max(max_xyz_extent)
    # put the camera twice as far away as the largest extent
    pos = f"0 0 {max_dim * 2.5}"
    # NB. viewpoint needs to contain an (empty) child to be valid x3d
    viewpoint = element("viewpoint", position=pos, child=element("group"))

    return element("scene", children=(viewpoint, cell))


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


X3DOM_template = """\
<X3D {style}>

<!--Inserting Generated X3D Scene-->
{scene}
<!--End of Inserted Scene-->

</X3D>
"""
