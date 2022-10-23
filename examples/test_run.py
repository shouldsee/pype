from pype import Controller
def know_task(ctl):
	ctl.RWC(run='echo [hi]')
ctl = Controller()
know_task(ctl)
ctl.build()
ctl.build()
