from threading import Thread
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

def redirect_stdout(action):
	q = Queue(1024*1024) # 1Mb buffer
	buf=FakeStdout(q)
	def f():
		try:
			with redirect(buf): action()
		finally:
			q.put(PoisonPill, True)
	Thread(target=f).start()
	while True:
		got=q.get(True)
		if got == PoisonPill: break
		yield got


