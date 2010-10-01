#!/usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#


import unittest
import lsst.utils.tests as utilsTests

import lsst.daf.persistence as dafPersist

class MinMapper(dafPersist.Mapper):
	def __init__(self):
		dafPersist.Mapper.__init__(self, policy="MinMapper.paf", module="daf_persistence",
								   policyDir="tests", root="tests")
		return

	def map_x(self, mapping, dataId):
		path = mapping.template % dataId
		return dafPersist.ButlerLocation(mapping.python, mapping.cpp, mapping.storage, path, {})

	def lookup_x(self, mapping, properties, dataId):
		return [1, 2, 3]

	def std_x(self, mapping, item, dataId):
		return float(item)

	def _transformId(self, dataId):
		return dataId

	def _extractDetectorName(self, dataId):
		return "Detector"

class MapperTestCase(unittest.TestCase):
	"""A test case for the mapper used by the data butler."""

	def setUp(self):
		self.mapper = MinMapper()

	def tearDown(self):
		del self.mapper

	def testGetDatasetTypes(self):
		self.assertEqual(set(self.mapper.getDatasetTypes()),
				set(["x", "badSourceHist"]))

	def testMap(self):
		loc = self.mapper.map("x", {"ccd": 27})
		self.assertEqual(loc.getPythonType(), "lsst.afw.image.BBox")
		self.assertEqual(loc.getCppType(), "lsst::afw::image::BBox")
		self.assertEqual(loc.getStorageName(), "PickleStorage")
		self.assertEqual(loc.getLocations(), ["foo27.pickle"])
		self.assertEqual(loc.getAdditionalData().toString(), "")

	def testQueryMetadata(self):
		self.assertEqual(self.mapper.queryMetadata("x", None, None, None),
			[1, 2, 3])

	def testStandardize(self):
		self.assertEqual(self.mapper.canStandardize("x"), True)
		self.assertEqual(self.mapper.canStandardize("badSourceHist"), False)
		self.assertEqual(self.mapper.canStandardize("notPresent"), False)
		result = self.mapper.standardize("x", 3, None)
		self.assertEqual(isinstance(result, float), True)
		self.assertEqual(result, 3.0)
		result = self.mapper.standardize("x", 3.14, None)
		self.assertEqual(isinstance(result, float), True)
		self.assertEqual(result, 3.14)
		result = self.mapper.standardize("x", "3.14", None)
		self.assertEqual(isinstance(result, float), True)
		self.assertEqual(result, 3.14)

def suite():
	utilsTests.init()

	suites = []
	suites += unittest.makeSuite(MapperTestCase)
	suites += unittest.makeSuite(utilsTests.MemoryTestCase)
	return unittest.TestSuite(suites)

def run(shouldExit = False):
	utilsTests.run(suite(), shouldExit)

if __name__ == '__main__':
	run(True)
