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
	"""prducer puts this into queue to identify end of sequence"""
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
	def __init__(self, action):
		self.action=action
	def clean_queue(self, queue):
		try:
			while True: queue.get(False)
		except Empty: return
	def __iter__(self):
		queue = Queue(10 * 1024 * 1024)  # 10Mb buffer
		buffer = FakeStdout(queue)
		# producer thread
		def producer():
			try:
				with redirect(buffer): self.action()
			finally: queue.put(PoisonPill, True)
		thread=Thread(target=producer)
		thread.start()
		iterator = QueueIterator(queue)
		# whenever guard thread detects consumer does not consume (for whatever reason: hangs or failed), turn off queing
		def guard():
			while True:
				sleep(60)
				if iterator.idle_time()>60*10:
					LOGGER.warning('consumer idle for 10 minutes, turning off its queue')
					buffer.disable()
					try: # empty queue to spare memory
						while True: queue.get(False)
					except Empty: pass
		Thread(target=guard).start()
		return iterator


def generate_stdout(action):
	queue = Queue(10*1024*1024) # 10Mb buffer
	buffer=FakeStdout(queue)

	def producer():
		try:
			with redirect(buffer): action()
		finally:
			queue.put(PoisonPill, True)
	thread=Thread(target=producer)
	thread.start()

	def guard():
		sleep(5)
		while not thread.is_alive():

			sleep(5)
	Thread(target=guard).start()

	while True:
		got=queue.get(True)
		if got == PoisonPill: break
		yield got
