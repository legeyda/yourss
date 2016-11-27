from threading import Thread, Timer
from queue import Queue, Empty
from contextlib import redirect_stdout as redirect

class PoisonPill(object):
	pass

class FakeStdout(object):
	def __init__(self, queue):
		self.queue=queue
	def write(self, data):
		self.queue.put(data)
	def fileno(self, *args, **kwargs):
		return 0
	def flush(self):
		pass


def generate_stdout(action):
	q = Queue(1024*1024) # 1Mb buffer
	buf=FakeStdout(q)
	def f():
		try:
			with redirect(buf): action()
		finally:
			q.put(PoisonPill, True)
	thread=Thread(target=f)
	thread.start()
	def guard():
		"""dispose the queue"""
		if thread.is_alive():
			while PoisonPill==q.get(True): pass
	#Timer(600, guard).start() # if
	# todo protect from unexpectedly exited consumer
	while True:
		got=q.get(True)
		if got == PoisonPill: break
		yield got

def redirect_stdout(action, callback):
	q = Queue(1024*1024) # 1Mb buffer
	buf=FakeStdout(q)
	def f():
		try:
			with redirect(buf): action()
		finally:
			q.put(PoisonPill, True)
	Thread(target=f).start()
	dry_run=False
	while True:
		got = q.get(True)
		if got == PoisonPill: break
		if not dry_run:
			try:
				dry_run = callback(got)
			except:
				dry_run = True
