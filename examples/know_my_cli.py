from pype import Controller,RO,s
def know_my_cli(ctl):
    # x = RO('echo toml pyyaml',s)
    ctl.init_cd('cli/')    
    x = RO(None)
    # x = x.chain_with(lambda y,x=x:x.print_call_stack())
    # x = x.chain_with(lambda y,x=x:x.print_call_stack())

    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install(
        'toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype','598b7a2b1201d138260c22119afd7b4d5449fe97')
    # ctl.RWC(run=lambda x:[][1])
    # x = 
    # x.call()
    ctl.RWC(run=lambda y,x=x:x.call)


if __name__=='__main__':
    ctl = Controller()
    know_my_cli(ctl)
    ctl.build('/tmp/')
    ctl.pprint_stats()
