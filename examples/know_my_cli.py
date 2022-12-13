from pype import Controller
from pype import RuntimeObject as RO
def know_my_cli(ctl, host, user):
    '''
    [TBC] adds lazy_apt_update to avoid 
    update too often and not doing update.

    https://superuser.com/questions/1524610/detect-if-apt-get-update-is-necessary
    '''

    ctl.lazy_apt_install('nano git proxychains4'.split())
    ctl.lazy_pip_install('toml pyyaml'.split())
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype',
    '598b7a2b1201d138260c22119afd7b4d5449fe97',
    'temp_pype')
    ctl.RWC(run = lambda x:
    open('connect.sh','w').write(
    f'''
    ssh -p22 {user}@{host} 
    '''))
    ctl.export('connect.sh', RO(ctl).rundir, str)
    
if __name__=='__main__':
    
    ctl = Controller.from_func(know_my_cli, '127.0.0.1', 'ubuntu')

    ### same as
    # ctl = Controller()
    # know_my_cli(ctl, '127.0.0.1', 'ubuntu')

    ctl.build()
    ctl.pprint_stats()