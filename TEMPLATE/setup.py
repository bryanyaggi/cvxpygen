from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from glob import glob
from subprocess import call, check_output
import os
import sys


class get_pybind_include(object):

    def __init__(self, user=False):
        try:
            import pybind11
            pybind11
        except ImportError:
            if call([sys.executable, '-m', 'pip', 'install', 'pybind11']):
                raise RuntimeError('pybind11 install failed.')
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


# Add parameters to cmake_args and define_macros
cmake_args = ['-DCMAKE_POSITION_INDEPENDENT_CODE=ON', '-G', 'Unix Makefiles']
lib_name = 'libcpg.a'

# Compile CPG using CMake
current_dir = os.getcwd()
cpg_dir = os.path.join(current_dir, 'c',)
cpg_build_dir = os.path.join(cpg_dir, 'build')
cpg_lib = [cpg_build_dir, 'out'] + [lib_name]
cpg_lib = os.path.join(*cpg_lib)


class build_ext_cpg(build_ext):
    def build_extensions(self):

        # Create build directory
        if not os.path.exists(cpg_build_dir):
            os.makedirs(cpg_build_dir)
        os.chdir(cpg_build_dir)

        try:
            check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed.")

        # Compile static library with CMake
        call(['cmake'] + cmake_args + ['..'])
        call(['cmake', '--build', '.', '--target', 'cpg'])

        # Change directory back to the python interface
        os.chdir(current_dir)

        # Run extension
        build_ext.build_extensions(self)


cpg = Extension('cpg_module',
                sources=glob(os.path.join('cpp', '*.cpp')),
                include_dirs=['c',
                              os.path.join('c', 'OSQP_code', 'include'),
                              get_pybind_include(),
                              get_pybind_include(user=False)],
                language='c++',
                extra_compile_args=['-std=c++11', '-O3'],
                extra_objects=[cpg_lib])


setup(name='cpg_module',
      version='0.0.0',
      author='tbd',
      author_email='tbd',
      description='tbd',
      long_description='tbd',
      long_description_content_type='text/markdown',
      package_dir={'cpg': 'module'},
      include_package_data=False,
      setup_requires=["setuptools>=18.0", "pybind11"],
      install_requires=["numpy >= 1.7", "scipy >= 0.13.2"],
      license='Apache 2.0',
      url="https://github.com/cvxgrp/codegen",
      cmdclass={'build_ext': build_ext_cpg},
      ext_modules=[cpg],
      )
