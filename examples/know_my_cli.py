from pype import Controller,RO,s
def know_my_cli(ctl):
    # x = RO('echo toml pyyaml',s)
    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install(
        'toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97')
    # ctl.RWC(run=lambda x:[][1])


if __name__=='__main__':
    ctl = Controller()
    know_my_cli(ctl)
    ctl.build()
    ctl.pprint_stats()
