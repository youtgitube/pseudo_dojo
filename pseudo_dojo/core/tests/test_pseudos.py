#!/usr/bin/env python
from __future__ import division, print_function, unicode_literals

from pprint import pprint
from pseudo_dojo.core.testing import PseudoDojoTest
from pseudo_dojo.core.pseudos import *
from pseudo_dojo.pseudos import dojotable_absdir


class DojoTableTest(PseudoDojoTest):

    def test_from_dojodir(self):
        """Initializing DojoTable from directory."""
<<<<<<< HEAD
        table = DojoTable.from_dojodir(dojotable_absdir("ONCVPSP-PBE-DEV"))
=======
        return
        table = DojoTable.from_dojodir(dojotable_absdir("ONCVPSP-PBE-PDv0.0"))
>>>>>>> origin/master

        # This table contains multiple pseudos for element!
        # and dojo_check_errors should detect it.
        md5dict = {p.basename: p.md5 for p in table}

        errors = table.dojo_find_errors(md5dict=md5dict, require_hints=False)
        pprint(errors)
        assert errors

    def test_from_djson(self):
        """Initializing DojoTable from djson file."""
<<<<<<< HEAD
        djson_path = os.path.join(dojotable_absdir("ONCVPSP-PBE-DEV"), "accuracy.djson")
        table = DojoTable.from_djson(djson_path)
=======
        return
        djson_path = os.path.join(dojotable_absdir("ONCVPSP-PBE-PDv0.0"), "accuracy.djson")
        table = DojoTable.from_djson_file(djson_path)
>>>>>>> origin/master

        # The table must have a dojo_info dict
        print(table.dojo_info)
        assert table.dojo_info


if __name__ == '__main__':
    import unittest
    unittest.main()
