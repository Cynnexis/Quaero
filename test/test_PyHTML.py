from unittest import TestCase

from qr.pyhtml import PyHTML


class TestPyHTML(TestCase):
	
	def test_feed(self):
		parser = PyHTML(
			"""<!DOCTYPE html>
			<html lang="en">
				<head>
					<meta charset="UTF-8"/>
					<title>Test</title>
					<style>
					html, body {
						width: 100%;
					}
					
					h1 {
						font-size: 20pt;
					}
					</style>
				</head>
				
				<body>
					<h1>Test<br/></h1>
					
					<script language="javascript">
						alert('Test');
					</script>
				</body>
			</html>
			""")
