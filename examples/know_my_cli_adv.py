from pype import Controller
from pype import RuntimeObject as RO
from pype import PlaceHolder
import yaml
import os
def know_my_cli(ctl, host, user, key, password_file):
    '''
    [TBC] adds lazy_apt_update to avoid 
    update too often and not doing update.

    https://superuser.com/questions/1524610/detect-if-apt-get-update-is-necessary
    '''
    ctl.runtime_initer('host',host,str)
    ctl.runtime_initer('user',user,str)
    ctl.runtime_initer('key',key,str)
    ctl.init_cd('./cli/')
    def load_pass(x):
        with open(password_file,'r') as f:
            v = yaml.safe_load(f.read())
            ctl.runtime_setter("passwds",v,object) 
        
    ctl.RWC(run=load_pass)

    ctl.lazy_apt_install('nano git proxychains4'.split())

    ### skipper criteria needs rewrite
    # ctl.lazy_pip_install('toml pyyaml'.split())  
     
    ctl.lazy_git_url_commit('https://github.com/shouldsee/pype',
    '598b7a2b1201d138260c22119afd7b4d5449fe97',
    'temp_pype')
    SH_CONN = RO(ctl).rundir +'/connect-' + ctl.runtime['key'] +'.sh'
    ctl.RWC(run = lambda rt:
        open( SH_CONN(),'w').write(
        f'''
        sshpass -p "{rt["passwds"][rt["key"]]}" | ssh -p22 {rt["user"]}@{rt["host"]} -vvv 
        ''')
    )
    ctl.export('SH_CONN', SH_CONN, str)
    
if __name__=='__main__':
    
    key = PlaceHolder('key')
    host = PlaceHolder('host')
    user = PlaceHolder('user')
    ctl = Controller.from_func(know_my_cli, host.built, user.built, key.built, 
        os.path.realpath('examples/passwd.yaml'))
    for k,h,u in [
        'here 127.0.0.1 ubuntu'.split(),
        'remote 192.168.12.133 ubuntu'.split()

    ]:
        key.put(k)
        host.put(h)
        user.put(u)
        ctl.build('$HOME/')
        
    ### same as
    # ctl = Controller()
    # know_my_cli(ctl, '127.0.0.1', 'ubuntu')
    # ctl.build()
    ctl.pprint_stats()
    '''
+--------------------+-------------+--------+---------+--------+--------+-----------------------------------+
| name               | co_name     | lineno | skipped | cur_ms | run_ms | file                              |
+--------------------+-------------+--------+---------+--------+--------+-----------------------------------+
| _PYPE_START        | None        | None   | -1      | -1     | -1     | None                              |
| _defaul_key_0      | know_my_cli | 22     | 0       | 1      | 1      | /root/cli/examples/know_my_cli.py |
| lazy_apt_install/1 | know_my_cli | 24     | 1       | 13     | -1     | /root/cli/examples/know_my_cli.py |
| lazy_git/2         | know_my_cli | 29     | 1       | 10     | 1787   | /root/cli/examples/know_my_cli.py |
| _defaul_key_3      | know_my_cli | 33     | 0       | 1      | 1      | /root/cli/examples/know_my_cli.py |
| SH_CONN            | know_my_cli | 39     | 0       | 0      | 0      | /root/cli/examples/know_my_cli.py |
| _PYPE_END          | None        | None   | -1      | -1     | -1     | None                              |
+--------------------+-------------+--------+---------+--------+--------+-----------------------------------+
    '''

    '''
$ls $HOME/cli
drwxr-xr-x 6 root root  165 10月 27 02:41 temp_pype
-rwxr-xr-x 1 root root    0 10月 27 02:41 PYPE.json.lock
-rw-r--r-- 1 root root 3.7K 10月 27 02:41 PYPE.json.last
-rw-r--r-- 1 root root   71 10月 27 02:41 connect-here.sh
-rw-r--r-- 1 root root 3.7K 10月 27 02:41 PYPE.json
-rw-r--r-- 1 root root   75 10月 27 02:41 connect-remote.sh

    '''