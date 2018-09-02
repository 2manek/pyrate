#!/usr/bin/env/python
"""
Pyrate - Optical raytracing based on Python

Copyright (C) 2014-2018
               by     Moritz Esslinger moritz.esslinger@web.de
               and    Johannes Hartung j.hartung@gmx.net
               and    Uwe Lippmann  uwe.lippmann@web.de
               and    Thomas Heinze t.heinze@uni-jena.de
               and    others

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from pyrateoptics.core.base import (ClassWithOptimizableVariables,
                                    OptimizableVariable)
from pyrateoptics.core.functionobject import FunctionObject
from pyrateoptics.optimize.optimize import Optimizer
from pyrateoptics.optimize.optimize_backends import (ScipyBackend,
                                                     Newton1DBackend)

import numpy as np

# class ExampleSubClass(ClassWithOptimizableVariables):
#     def __init__(self):
#         self.a = 10.
#
# class ExampleSuperClass(ClassWithOptimizableVariables):
#     def __init__(self):
#         super(ExampleSuperClass, self).__init__()
#         self.b = 20.
#         self.c = ClassWithOptimizableVariables()
#         self.c.addVariable("blubberbla", OptimizableVariable("Variable",
#                                                               value=5.0))
#         self.addVariable("blubberdieblub", OptimizableVariable("Variable",
#                                                                 value=10.0))


def test_variables_pickups_externals():
    """
    Check whether pickups are also working for strings
    """

    sum_fo = FunctionObject("f = lambda p, q: p + q", ["f"])

    p = OptimizableVariable("Variable", value="glass1")
    q = OptimizableVariable("Variable", value="glass2")
    r = OptimizableVariable("Pickup", functionobject=(sum_fo, "f"),
                            args=(p, q))
    s = OptimizableVariable("External", functionobject=(sum_fo, "f"),
                            args=(1.0, 6.0))

    assert p() == "glass1"
    assert q() == "glass2"
    assert r() == "glass1glass2"
    assert s() == 7.0

    p.setvalue("glass5")
    q.setvalue("glass6")

    assert r() == "glass5glass6"

    r.parameters["functionobject"] = (
            FunctionObject("f = lambda x, y: x*3 + y*4", ["f"]), "f")

    assert r() == "glass5glass5glass5glass6glass6glass6glass6"


def test_optimization():

    class ExampleOS(ClassWithOptimizableVariables):
        def __init__(self):
            super(ExampleOS, self).__init__()
            self.X = OptimizableVariable(name="X",
                                         variable_type="variable",
                                         value=3.0)
            self.Y = OptimizableVariable(name="Y",
                                         variable_type="variable",
                                         value=20.0)
            self.Z = OptimizableVariable(
                    name="Z",
                    variable_type="pickup",
                    functionobject=(
                            FunctionObject("f = lambda x, y: x**2 + y**2",
                                           ["f"]),
                            "f"),
                    args=(self.X, self.Y))

    def testmerit(s):
        # let x, y being on a circle of radius 5
        return (s.X()**2 + s.Y()**2 - 5.**2)**2

    def testmerit2(s):
        # let x**2 + y**2 + z**2 be minimized with
        # the pickup constraint z = x**2 + y**2
        return s.X()**2 + s.Y()**2 + s.Z()**2

    os = ExampleOS()

    optimi = Optimizer(os, testmerit,
                       backend=ScipyBackend(method="Nelder-Mead",
                                            options={"maxiter": 1000,
                                                     "disp": False},
                                            name="scipybackend"),
                       name="optimizer")
    optimi.run()
    assert np.isclose(os.X()**2 + os.Y()**2, 25.0)
    optimi.meritfunction = testmerit2
    optimi.run()
    assert np.isclose(os.X()**2 + os.Y()**2, os.Z())
    optimi.backend = Newton1DBackend(dx=1e-6, iterations=500)
    optimi.meritfunction = testmerit
    optimi.run()
    assert np.isclose(os.X()**2 + os.Y()**2, 25.0)
    optimi.meritfunction = testmerit2
    optimi.run()
    assert np.isclose(os.X()**2 + os.Y()**2, os.Z())
