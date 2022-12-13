from pype import Controller
from pype import RuntimeObject as RO
from datetime import datetime
def know_my_cli(ctl):

    ctl.init_cd('./cli-simple')
    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype',
      '598b7a2b1201d138260c22119afd7b4d5449fe97',
      'temp_pype')
    ctl.export('done_ts', RO(None, lambda x:datetime.now()), datetime )
    
if __name__=='__main__':
    ctl = Controller()
    know_my_cli(ctl)
    ctl.build('$HOME/')
    ctl.pprint_stats()
    print('[DONE]',ctl.built['done_ts'].call())
