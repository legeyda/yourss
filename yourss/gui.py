from yourss.client import FileWriter
from yourss.youtube import Feed
from . import client
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .valid import default_feed_parameter_values, FeedParameters, ParameterException, OutputParameter


def dict_ensure(data, key, default_value=None):
	"""ensure that dict contains key, sets default_value if needed, and returns value"""
	if not key in data: data[key]=default_value
	return data[key]

# abstract widget, adds create_child method to create and immediately grid crated widget, acestors should implement grid_child_at
class Box(ttk.Frame):
	def __init__(self, *args, **kwargs):
		ttk.Frame.__init__(self, *args, **kwargs)
		self._index=0
	def create_child(self, constructor, *args, **kwargs):
		grid_args=kwargs.pop('grid_args', [])
		grid_kwargs=kwargs.pop('grid_kwargs', {})
		for key in ('sticky','ipadx','ipady','padx','pady'):
			value=kwargs.pop(key, None)
			if value: grid_kwargs[key]=value
		widget=constructor(self, *args, **kwargs)
		self.grid_child(widget, self._index, grid_args, grid_kwargs)
		self._index+=1
		return widget
	def grid_child(self, child, index, grid_args=[], grid_kwargs={}):
		if not isinstance(child, (ttk.Frame, tk.Frame)):
			if not 'padx' in grid_kwargs: grid_kwargs['padx']=5
			if not 'pady' in grid_kwargs: grid_kwargs['pady']=5
		pos=self.get_child_pos(index)
		child.grid(row=pos['row'], column=pos['column'], *grid_args, **grid_kwargs)
		self.on_row(pos['row'])
		self.on_column(pos['column'])
	def on_row(self, index):
		weight = self.get_row_weight(index)
		if weight is not None: self.rowconfigure(index, weight=weight)
	def on_column(self, index):
		weight = self.get_column_weight(index)
		if weight is not None: self.columnconfigure(index, weight=weight)
	def get_row_weight(self, index):
		return 1
	def get_column_weight(self, index):
		return 1
	def get_child_pos(self, index):
		pass

# place children in a row vertically
class VBox(Box):
	def get_child_pos(self, index):
		return {'row': index, 'column': 0}

# place children in a row vertically
class HBox(Box):
	def get_child_pos(self, index):
		return {'row': 0, 'column': index}

class Grid(Box):
	def __init__(self, *args, **kwargs):
		self.column_count=kwargs.pop('column_count', 2)
		Box.__init__(self, *args, **kwargs)
	def get_child_pos(self, index):
		return {'row': index//self.column_count, 'column': index%self.column_count}

# adds get_value and set_value to tk.Entry, no need to setup variable
class ValuedEntry(tk.Entry):
	def __init__(self, master, *args, **kwargs):
		self.var = kwargs.pop('variable', kwargs.pop('textvariable', tk.StringVar(master)))
		kwargs['validate']='all'
		kwargs['validatecommand']=(master.register(self.validate), '%P')
		self.var.set(kwargs.pop('value', ''))
		self._change=kwargs.pop('change', None)
		#if change: self.var.trace('w', change)
		kwargs['textvariable']=self.var
		self.var.trace('w', self.change)
		tk.Entry.__init__(self, master, *args, **kwargs)
	def change(self, *args, **kwargs):
		if self._change:
			self._change()
	def validate(self, value):
		return True
	def set_value(self, value):
		self.var.set(value)
	def get_value(self):
		return self.var.get()

# adds get_value and set_value to tk.Entry, no need to setup variable
class ValuedIntEntry(ValuedEntry):
	def __init__(self, master, *args, **kwargs):
		dict_ensure(kwargs, 'variable', tk.IntVar(master))
		ValuedEntry.__init__(self, master, *args, **kwargs)
	def validate(self, value):
		try:
			int(value)
			return True
		except ValueError:
			return False

# adds get_value and set_value to.Checkbutton, no need to setup variable
class ValuedCheckbutton(tk.Checkbutton):
	def __init__(self, master, *args, **kwargs):
		self.var=dict_ensure(kwargs, 'variable', tk.IntVar(master))
		self.var.set(kwargs.pop('value', 0))
		change=kwargs.pop('change', None)
		if change: self.var.trace('w', change)
		tk.Checkbutton.__init__(self, master, *args, **kwargs)
	def set_value(self, value):
		self.var.set(value)
	def get_value(self):
		return self.var.get()

# adds get_value and set_value to.Checkbutton, no need to setup variable
class ValuedOptionMenu(tk.OptionMenu):
	def __init__(self, master, variable=None, items=[], value=None, change=None):
		titles=[]
		self.title_by_value_index={}
		self.value_by_title_index={}
		for item in items:
			if isinstance(item, (list, tuple)): 
				value=item[0]
				title=item[1]
			else: 
				value=str(item) 
				title=str(item)
			titles.append(title)
			if value in self.title_by_value_index: raise Exception('values not unique')
			self.title_by_value_index[value]=title
			if title in self.value_by_title_index: raise Exception('titles not unique') 
			self.value_by_title_index[title]=value
		if not variable:
			variable=tk.StringVar(master)
		self.var=variable
		self.set_value(value)
		if change: self.var.trace('w', change)
		tk.OptionMenu.__init__(self, master, self.var, *titles)
	def set_value(self, value):
		self.var.set(self.title_by_value_index.get(value, None))
	def get_value(self):
		return self.value_by_title_index.get(self.var.get(), None)


class FileEntry(HBox):
	def __init__(self, master, *args, **kwargs):
		entry_args=kwargs.pop('entry_args', [])
		entry_kwargs={'sticky': tk.E+tk.W}
		entry_value=kwargs.pop('value', None)
		if entry_value: entry_kwargs['value']=entry_value
		entry_variable=kwargs.pop('variable', None)
		if entry_variable: entry_kwargs['variable']=entry_variable
		entry_kwargs.update(kwargs.pop('entry_kwargs', {}))
		entry_change=kwargs.pop('change', None)

		button_args=kwargs.pop('button_args', [])
		button_kwargs={'text':'...', 'width':3, 'command': self.choose_file}
		button_kwargs.update(kwargs.pop('button_kwargs', {}))

		self.filedialog_args=kwargs.pop('filedialog_args', [])
		self.filedialog_kwargs={
			'defaultextension': '.xml', 
			'filetypes': [('All files', '.*'), ('XML-files', '.xml')],
			'parent': self,
			'title': 'select target file',
			'confirmoverwrite': False
		}
		self.filedialog_kwargs.update(kwargs.pop('filedialog_kwargs', {}))
		HBox.__init__(self, master, *args, **kwargs)
		if not entry_variable:
			entry_variable=tk.StringVar(master)	
		entry_kwargs['variable']=entry_variable
		if entry_change:
			entry_variable.trace('w', entry_change)

		self.entry=self.create_child(ValuedEntry, *entry_args, **entry_kwargs)
		self.create_child(ttk.Button, *button_args, **button_kwargs)
	def get_value(self):
		return self.entry.get_value()
	def set_value(self, value):
		self.entry.set_value(value)
	def choose_file(self):
		self.set_value(filedialog.asksaveasfilename(**self.filedialog_kwargs))
	def get_column_weight(self, index):
		return 1 if index==0 else 0


# entry with label
class LabeledEntry(VBox):
	def __init__(self, master, *args, **kwargs):
		label_args=kwargs.pop('label_args', [])
		label_kwargs={'text': kwargs.pop('label', 'Value'), 'sticky':tk.W}
		label_kwargs.update(kwargs.pop('label_kwargs', {}))

		entry_change=kwargs.pop('change', None)
		entry_variable=kwargs.pop('variable', None)
		entry_args=kwargs.pop('entry_args', [])
		entry_kwargs={'value': kwargs.pop('value', ''), 'sticky':tk.W+tk.E}
		if entry_change: entry_kwargs['change']=entry_change
		entry_kwargs.update(kwargs.pop('entry_kwargs', {}))
		
		entry_constructor=kwargs.pop('entry_constructor', ValuedEntry)
		VBox.__init__(self, master, *args, **kwargs)

		if entry_variable: entry_kwargs['variable']=entry_variable

		self.create_child(tk.Label, *label_args, **label_kwargs)
		self.entry = self.create_child(entry_constructor, *entry_args, **entry_kwargs)
	def get_value(self):
		return self.entry.get_value()
	def set_value(self, value):
		self.entry.set_value(value)


class Application(VBox):
	def __init__(self, master=None):
		super().__init__(master)
		self.master=master
		self.create_widgets()
		master.update()
		master.minsize(master.winfo_width(), master.winfo_height())
		self.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
		self.file_dialog=None

	def get_text_from_clipboard(self):
		data = self.master.clipboard_get()
		if data.startswith('http'):
			return data
		return ''

	def create_widgets(self):
		self.url=self.create_child(LabeledEntry, label='Url of the page containg media', sticky=tk.E+tk.W, value=self.get_text_from_clipboard(), change=self.validate)

		self.output=self.create_child(LabeledEntry, entry_constructor=FileEntry, label='Output file', sticky=tk.E+tk.W, change=self.validate)

		add_param_frame = self.create_child(VBox, sticky=tk.E+tk.W)
		self.add_param_checkbutton=add_param_frame.create_child(ValuedCheckbutton, text='Additional parameters', value=0, command=self.show_add_param, sticky=tk.W)
		self.add_param_hide_frame = add_param_frame.create_child(Grid, sticky=tk.E+tk.W, pady=10, padx=10)
		self.add_param_hide_frame.grid_remove()

		self.title        = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, label='Override title', change=self.validate)
		self.thumbnail    = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, label='Override thumbnail', change=self.validate)
		self.match_title  = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, label='Match titles regular expression', change=self.validate)
		self.ignore_title = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, label='Ignore titles regular expression', change=self.validate)

		self.page       = self.add_param_hide_frame.create_child(HBox, sticky=tk.E+tk.W+tk.N+tk.S)
		self.page_size  = self.page.create_child(LabeledEntry, entry_constructor=ValuedIntEntry, sticky=tk.E+tk.W, label='Page Size', value=default_feed_parameter_values['page_size'], change=self.validate)
		self.page_index = self.page.create_child(LabeledEntry, entry_constructor=ValuedIntEntry, sticky=tk.E+tk.W, label='Page Index', value=default_feed_parameter_values['page_index'], change=self.validate)

		link_styles=[
			("direct",  'Direct link to video extracted by youtube_dl'),
			("webpage", 'Link to webpage containing episode'),
			("proxy",   'Link to yourss proxy')
		]
		self.link_style = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, entry_constructor=ValuedOptionMenu, entry_kwargs={'items': link_styles, 'value': default_feed_parameter_values['link_type']}, change=self.validate)

		format          = self.add_param_hide_frame.create_child(HBox, sticky=tk.E+tk.W+tk.N+tk.S)
		self.media_type = format.create_child(LabeledEntry, sticky=tk.E+tk.W, entry_constructor=ValuedOptionMenu, entry_kwargs={'items': [('video', 'Video'), ('audio', 'Audio')], 'value': default_feed_parameter_values['media_type']}, change=self.validate)
		self.quality    = format.create_child(LabeledEntry, sticky=tk.E+tk.W, entry_constructor=ValuedOptionMenu, entry_kwargs={'items': [('low', 'Low'), ('high', 'High')], 'value':default_feed_parameter_values['quality']}, change=self.validate)

		self.format = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, label="youtube_dl format (see youtube_dl's format manual):")

		self.base_url   = self.add_param_hide_frame.create_child(LabeledEntry, sticky=tk.E+tk.W, label='Yourss url', value='https://yourss.legeyda.com', change=self.validate)
		
		self.run_button = self.create_child(ttk.Button, text='generate feed', command=self.run)
		
		# for i in range(4):
		# 	self.rowconfigure(i, weight=1)
		self.validate()

	def show_add_param(self):
		if 1==self.add_param_checkbutton.get_value():
			self.add_param_hide_frame.grid()
		else:
			self.add_param_hide_frame.grid_remove()

	def is_form_ok(self):
		return not self.get_parameters().message()

	def validate(self, *args, **kwargs):
		if 'run_button' in self.__dict__:
			self.run_button['state']='normal' if self.is_form_ok() else 'disabled'

	def get_parameters(self):
		return FeedParameters(
			self.url.get_value(),
			self.match_title.get_value(),
			self.ignore_title.get_value(),
			self.page_index.get_value(),
			self.page_size.get_value(),
			self.media_type.get_value(),
			self.quality.get_value(),
			self.format.get_value(),
			self.link_style.get_value(),
			self.title.get_value(),
			self.thumbnail.get_value(),
			self.base_url.get_value(),
			None, None
		)

	def run(self):
		arguments=None
		try: arguments=self.get_parameters().valid_value()
		except ParameterException as e: messagebox.showerror('Wrong parameters', str(e.message))
		else:
			try: feed=arguments.apply(Feed)
			except Exception as e: messagebox.showerror('Error initializing feed parser', str(e))
			else:
				try: FileWriter(OutputParameter(self.output.get_value()).valid_value()).consume(feed.generate())
				except Exception as e: messagebox.showerror('Error writing', str(e))



def run():
	root = tk.Tk()
	root.rowconfigure(0, weight=1)
	root.columnconfigure(0, weight=1)
	app = Application(root)
	app.mainloop()

def main(*args):
	if 0<len(args):
		print('ignoring args')
	run()

if __name__=='__main__':
	from sys import argv
	main(*argv[1:])