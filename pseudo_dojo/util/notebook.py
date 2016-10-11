"""Tools to produce jupyter notebooks """
from __future__ import print_function, division, unicode_literals

import os
import io

from monty.os.path import which


def write_notebook(pseudopath, with_validation=False, with_eos=False, tmpfile=None):
    """
    Read a pseudopotential file and write an ipython notebook.
    By default, the notebook is created in the same directory
    as pseudopath but with the extension `ipynb` unless `tmpfile` is set to True.
    In the later case, a temporay file is created.

    Args:
        pseudopath: Path to the pseudopotential file.
        with_validation: If True an ipython widget is added at the end of the notebook
          to validate the pseudopotential.
        with_eos: True if EOS plots are wanted.

    Returns:
        The path to the ipython notebook.

    See also:
        http://nbviewer.jupyter.org/github/maxalbert/auto-exec-notebook/blob/master/how-to-programmatically-generate-and-execute-an-ipython-notebook.ipynb
    """
    import nbformat
    nbf = nbformat.v4
    nb = nbf.new_notebook()

    nb.cells.extend([
        nbf.new_markdown_cell("# PseudoDojo notebook for %s" % os.path.basename(pseudopath)),
        nbf.new_code_cell("""\
from __future__ import print_function, division, unicode_literals
%matplotlib notebook"""),

        nbf.new_markdown_cell("Construct the pseudo object and get the DojoReport"),

        nbf.new_code_cell("""\
from pseudo_dojo.core.pseudos import dojopseudo_from_file
pseudo = dojopseudo_from_file('%s')
report = pseudo.dojo_report""" % os.path.abspath(pseudopath)),

        nbf.new_markdown_cell("## ONCVPSP Input File:"),
        nbf.new_code_cell("""\
input_file = pseudo.filepath.replace(".psp8", ".in")
%cat $input_file"""),

        nbf.new_code_cell("""\
# Get data from the output file
from pseudo_dojo.ppcodes.oncvpsp import OncvOutputParser, PseudoGenDataPlotter
onc_parser = OncvOutputParser(pseudo.filepath.replace(".psp8", ".out"))
# Parse the file and build the plotter
onc_parser.scan()
plotter = onc_parser.make_plotter()"""),

        nbf.new_markdown_cell("## AE and PS radial wavefunctions $\phi(r)$:"),
        nbf.new_code_cell("fig = plotter.plot_radial_wfs(show=False)"),

        nbf.new_markdown_cell("## Arctan of the logarithmic derivatives:\n "
                              "for a pseudo to qualify for a GW tag in general no deviations should be presend up to 8H\n"
                              "Real ghosts are mostly observed when two steps in a PS curve touch "),
        nbf.new_code_cell("fig = plotter.plot_atan_logders(show=False)"),

        nbf.new_markdown_cell("## Convergence in $G$-space estimated by ONCVPSP:\n"
                              "calculated in the atomic configuration"),
        nbf.new_code_cell("fig = plotter.plot_ene_vs_ecut(show=False)"),

        nbf.new_markdown_cell("## Projectors:\n"
                              "In general the second projector in any channel shoudl have one node more that the first.\n"
                              "Pushing the energy of hte second projector too high may cause an additional node.\n"
                              "This will most likely introduce ghosts"),
        nbf.new_code_cell("fig = plotter.plot_projectors(show=False)"),

        nbf.new_markdown_cell("## Core-Valence-Model charge densities:\n"
                              "Much better convergence propperties have been achieved using icmod 3"
                              "fcfact mainly determines the hight of the model core charge"
                              "rcfact mainly determines the width of the model core charge"),
        nbf.new_code_cell("fig = plotter.plot_densities(show=False)"),

        nbf.new_markdown_cell("## Local potential and $l$-dependent potentials:"),
        nbf.new_code_cell("fig = plotter.plot_potentials(show=False)"),

        #nbf.new_markdown_cell("## 1-st order derivative of $v_l$ and $v_{loc}$ computed via finite differences:"),
        #nbf.new_code_cell("""fig = plotter.plot_der_potentials(order=1, show=False)"""),
        #nbf.new_markdown_cell("## 2-nd order derivative of $v_l$ and $v_{loc}$ computed via finite differences:"),
        #nbf.new_code_cell("""fig = plotter.plot_der_potentials(order=2, show=False)"""),

        nbf.new_markdown_cell("## Model core charge and form factors computed by ABINIT"),
        nbf.new_code_cell("""\
with pseudo.open_pspsfile() as psps:
    fform_fig = psps.plot(show=False);
fform_fig"""),

        nbf.new_markdown_cell("## Ghosts Test\n"
                              "self consistent band stucture calculation on a regular mesh\n"
                              "The algorithem to detect ghosts is just an indication usually on the side of faslse positives.\n"
                              "Zoom in on the band plot to see if an actual ghost is there."),

        nbf.new_code_cell("fig = report.plot_ebands(with_soc=False, show=False); fig"),

        nbf.new_markdown_cell("## Convergence of the total energy:\n"
                              "# Convergence of the total energy (computed from the deltafactor runs at the Wien2K equilibrium volume)"),
        nbf.new_code_cell("""\
fig = report.plot_etotal_vs_ecut(show=False)"""),

        nbf.new_code_cell("fig = report.plot_etotal_vs_ecut(inv_ecut=True, show=False)"),

        nbf.new_markdown_cell("## Convergence of the deltafactor results:"),
        nbf.new_code_cell("""fig = report.plot_deltafactor_convergence(xc=pseudo.xc, what=("dfact_meV", "dfactprime_meV"), show=False)"""),
    ])

    # Add validation widget.
    if with_validation:
        nb.cells.extend([
            nbf.new_markdown_cell("## PseudoDojo validation:"),
            nbf.new_code_cell("report.ipw_validate()"),
       ])

    nb.cells.extend([
        nbf.new_markdown_cell("## Convergence of $\Delta v_0$, $\Delta b_0$, and $\Delta b_1$ (deltafactor tests)"),
        nbf.new_code_cell("""\
# Here we plot the difference wrt Wien2k results.
fig = report.plot_deltafactor_convergence(xc=pseudo.xc, what=("-dfact_meV", "-dfactprime_meV"), show=False)"""),

        nbf.new_markdown_cell("## Deltafactor EOS for the different cutoff energies:"),
        nbf.new_code_cell("fig = report.plot_deltafactor_eos(show=False)"),

        nbf.new_markdown_cell("## Convergence of the GBRV lattice parameters:"),
        nbf.new_code_cell("fig = report.plot_gbrv_convergence(show=False)"),

        nbf.new_markdown_cell("## Convergence of the phonon frequencies at $\Gamma$:"),
        nbf.new_code_cell("fig = report.plot_phonon_convergence(show=False)"),
    ])

    if with_eos:
        # Add EOS plots
        nb.cells.extend([
            nbf.new_markdown_cell("## GBRV EOS for the FCC structure:"),
            nbf.new_code_cell("""fig = report.plot_gbrv_eos(struct_type="fcc", show=False)"""),
            nbf.new_markdown_cell("## GBRV EOS for the BCC structure:"),
            nbf.new_code_cell("""fig = report.plot_gbrv_eos(struct_type="bcc", show=False)"""),
        ])

    if tmpfile is None:
        root, ext = os.path.splitext(pseudopath)
        nbpath = root + '.ipynb'
    else:
        import tempfile
        prefix = os.path.basename(pseudopath)
        _, nbpath = tempfile.mkstemp(prefix=prefix, suffix='.ipynb', text=True)

    with io.open(nbpath, 'wt', encoding="utf8") as f:
        nbformat.write(nb, f)

    return nbpath


def make_open_notebook(pseudopath, with_validation=False, with_eos=True):
    """
    Generate a jupyter notebook from the pseudopotential path and
    open it in the browser. Return system exit code.

    Raise:
        RuntimeError if jupyther is not in $PATH
    """
    path = write_notebook(pseudopath, with_validation=with_validation,
                          with_eos=with_eos, tmpfile=True)

    if which("jupyter") is None:
        raise RuntimeError("Cannot find jupyter in PATH. Install it with `pip install`")

    return os.system("jupyter notebook %s" % path)
