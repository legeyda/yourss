from threading import Thread, Lock
from queue import Queue, Empty
from contextlib import redirect_stdout as redirect
from time import sleep, time as now
import logging
LOGGER=logging.getLogger(__file__)

class Volatile(object):
	"""thread safe value holder"""
	def __init__(self, value=None):
		self._value=value
		self.lock=Lock()
	def get(self):
		with self.lock: return self._value
	def set(self, value):
		with self.lock: self._value=value

class PoisonPill(object):
	"""producer puts this into queue to identify end of producing"""
	pass

class FakeStdout(object):
	"""fake stdout-like object puts all data into queue"""
	def __init__(self, queue):
		self.queue=queue
		self.enabled=Volatile(True)
	def disable(self):
		self.enabled.set(False)
	def write(self, data):
		if self.enabled.get():
			self.queue.put(data)
	def fileno(self, *args, **kwargs):
		return 0
	def flush(self):
		pass

class QueueIterator(object):
	"""iterate over blocking queue"""
	def __init__(self, queue):
		self.queue=queue
		self.last_active=Volatile(now())
	def idle_time(self):
		return now() - self.last_active.get()
	def __next__(self):
		self.last_active.set(now())
		got = self.queue.get(True)
		if got == PoisonPill: raise StopIteration
		return got


class StdoutRedirector(object):
	def __init__(self, action, queue_size=10*1024*1024, timeout=10*60):
		self.action=action
		self.queue_size=queue_size
		self.timeout=timeout
	def clean_queue(self, queue):
		try:
			while True: queue.get(False)
		except Empty: return
	def __iter__(self):
		queue = Queue(self.queue_size)
		buffer = FakeStdout(queue)
		# producer thread
		def action():
			try:
				with redirect(buffer): self.action()
			finally: queue.put(PoisonPill, True)
		producer=Thread(target=action)
		producer.start()
		iterator = QueueIterator(queue)
		# whenever guard thread detects consumer does not consume (for whatever reason: hangs or failed), turn off queing
		def guard():
			while True:
				sleep(60)
				if not queue.empty() and iterator.idle_time()>self.timeout:
					LOGGER.warning('consumer idle for %s seconds, turning off its queue' % (self.timeout, ))
					buffer.disable()
					try: # empty queue to spare memory
						while True: queue.get(False)
					except Empty: pass
					break
		Thread(target=guard).start()
		return iterator

