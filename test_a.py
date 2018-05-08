import us

class Fake(object):
  def __init__(self, **attrs):
    [setattr(self, attr_name, attrs.get(attr_name))
     for attr_name in attrs.keys()]

def helper_function_inside():
  print "Helper function"

def test_a():
  a = Fake(id=1, a=5)
  helper_function_inside()
  us.helper_function_module()
  print "Test function"

