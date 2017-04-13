from distutils.core import setup, Extension


module = Extension("fdag",
                   sources = ["fdag.c"],
                   )

setup(name="ForceDirectedGraph",
      version="1.0",
      description="This is a package for FDAG",
      ext_modules=[module])
