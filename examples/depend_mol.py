'''
Last Updated: 2022-10-22
Author: shouldsee <shouldsee@qq.com>

This script build an environment, including
  - a gromacs installation, with gmxapi
  - a nglview installation

This script depends on
  - bash
  - markov_lm.util_check
  - apt
  - git
  - python3.7
  - ngm

It is meant to mix dependency with runtime code in the same script,
 so as to bootstrap an environment from different machine states
'''

# import pype
from pype import (
    SEXE,
    s,
    Controller,
    PY_DUMP_ENV_TOML,
    config_extract_keys,
    is_pypack_installed,
    run_load_env_from_bash_script,
    sc,
    CWD,
    THIS,
    )


from pype import check_write_single_target as CWST
from pype import RuntimeObject as RO


import io
import os,sys,toml
import multiprocessing

def main():
    # ctl = prepare_run()
    ctl.run()
    ctl.pprint_stats()

def know_gromacs(ctl):
    '''
    prepare a recipe for compiling gromacs
    '''
    RWC = ctl.register_node
    # CWST = check_write_single_target
    GROMACS_DGMX_GPU='CUDA'
    DGMX_THREAD_MPI='ON'

    NCORE = multiprocessing.cpu_count() - 1
#    NCORE = 4

    if 0:
        ctl.lazy_git_url_commit('http://github.com/shouldsee/spiper','6f549bd360cd77f33f30d1d7befc16348607aef1')
    ctl.lazy_apt_install('libopenmpi-dev libfftw3-dev grace')

    ### CMake 3.16.3 or higher is required
    RWC([ ( RO('cmake --version',s) > 'cmake version 3.16.3'), None ], run = '''
        version=3.24
        build=1
        limit=3.20
        os="linux" ### "Linux" for <3.20
        mkdir -p ./temp; cd ./temp
        wget https://cmake.org/files/v$version/cmake-$version.$build-$os-x86_64.sh
        sudo mkdir -p /opt/cmake
        sudo sh cmake-$version.$build-$os-x86_64.sh --prefix=/opt/cmake
        sudo ln -sf /opt/cmake/*/bin/cmake `which cmake`
    ''', name = 'gromacs/check_cmake_version')

    if DGMX_THREAD_MPI=='ON':
        ctl.lazy_pip_install('mpi4py'.split(),pre_cmd=f'''
        ### [shouldsee] is this required before compiling GROMACS???
        MPICC=`which mpicc` MPICXX=`which mpic++`''')
    else:
        pass

    TARGET_DIR = f'{os.getcwd()}/gromacs-tmpi'
    GMX = TARGET_DIR+'/bin/gmx'
    if 1:
        x = ctl.lazy_wget('ftp://ftp.gromacs.org/pub/gromacs/gromacs-2022.tar.gz')
        x = x.built.call()
        RWC( CWST, x+'.done', run=f'''tar -xvf {x}; echo 1 >{x}.done''')
        # 'gromacs-tmpi'
        # Build and install thread-MPI GROMACS to your home directory.
        # Make sure the compiler toolchain matches that of mpi4py as best we can.
        CFLAGS = f'../gromacs-2022 -DCMAKE_INSTALL_PREFIX={TARGET_DIR} -DGMX_THREAD_MPI={DGMX_THREAD_MPI} \
           -DGMX_GPU={GROMACS_DGMX_GPU} \
            -DCMAKE_C_COMPILER=`which mpicc` -DCMAKE_CXX_COMPILER=`which mpic++`'

        RWC(CWST, GMX, (f'''
        set -e
        mkdir -p build && cd build
         cmake --trace {CFLAGS}
         make -j{NCORE} install
        '''), name ='gromacs', built=TARGET_DIR)

        ### check cmake version for gromacs
        # Activate the GROMACS installation.
        template = '''
        GMXPREFIX=/root/catsmile/prot/gromacs-tmpi
        GMXBIN=${GMXPREFIX}/bin
        GMXLDLIB=${GMXPREFIX}/lib
        GMXMAN=${GMXPREFIX}/share/man
        GMXDATA=${GMXPREFIX}/share/gromacs
        GMXTOOLCHAINDIR=${GMXPREFIX}/share/cmake
        GROMACS_DIR=${GMXPREFIX}

        LD_LIBRARY_PATH=$(replace_in_path "${LD_LIBRARY_PATH}" "${GMXLDLIB}" "${OLD_GMXLDLIB}")
        PKG_CONFIG_PATH=$(replace_in_path "${PKG_CONFIG_PATH}" "${GMXLDLIB}/pkgconfig" "${OLD_GMXLDLIB}/pkgconfig")
        PATH=$(replace_in_path "${PATH}" "${GMXBIN}" "${OLD_GMXBIN}")
        MANPATH=$(replace_in_path "${MANPATH}" "${GMXMAN}" "${OLD_GMXMAN}")
        '''

        RWC(run=run_load_env_from_bash_script(f'{TARGET_DIR}/bin/GMXRC.bash', keys=config_extract_keys(template)))



    ctl.lazy_pip_install('gmxapi'.split())

    return ctl

def know_ngl(ctl):
    ctl.lazy_pip_install('nglview'.split())

    # x = ctl.lazy_git_url_commit('https://github.com/nglviewer/nglview','c3fe543f6c9bf4104d9e779f5c268b643ac84ee7')
    x = ctl.lazy_git_url_commit('https://github.com/nglviewer/ngl','ffa0bacf433114bd5debaf08e3fb0cd8850daa64',name='git/ngl')
#    ctl.RWC( CWST, './node_modules/ngl/dist/ngl.js', 'npm install ngl',name='init_ngl')
    # ctl.RWC( CWST, './node_modules/ngl/dist/ngl.js', 'npm install ngl',name='init_ngl')


ctl = Controller()
RO(ctl, know_ngl)()
RO(ctl, know_gromacs)()

# ctl = prepare_run()
# main()
if __name__ == '__main__':
    main()
