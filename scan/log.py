#coding:utf8
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback

class LogMaster():
	'''
	fname: Name of the generated file
	errinfo: Error message
	level: Error level, the default value is 2
	'''
	def __init__(self, fname, errinfo, level=2):
		self.fname = fname,
		self.message = self.traceBack(errinfo),
		self.level = level
	'''
	Generating log master functions
	'''
	def buildLog(self):
		filename = r'/tmp/logs/%s'%(self.fname)
		logger = logging.getLogger()
		logger.setLevel(logging.INFO)
		fh = TimedRotatingFileHandler(filename,when='D',interval=1,backupCount=10)
		datefmt = '%a, %d %b %Y %H:%M:%S'
		format_str = '%(asctime)s %(levelno)s %(levelname)s %(message)s'
		formatter = logging.Formatter(format_str, datefmt)
		fh.setFormatter(formatter)
		fh.suffix = '%Y%M%d.log'
		logger.addHandler(fh)
		
		m = self.message
		if type(self.message) is tuple:
			m = " ".join(tuple(self.message))
		l = self.level
		result = {  
		  1: lambda msg: logging.debug(m),
		  2: lambda msg: logging.info(m),
		  3: lambda msg: logging.warning(m),
		  4: lambda msg: logging.error(m),
		  5: lambda msg: logging.critical(m)
		}[l](m)
		logging.getLogger().handlers = []

	'''
	Auxiliary function
	Get error details
	'''
	def traceBack(self,info):
		errinfo = ''
		for file, lineno, function, text in traceback.extract_tb(info[2]):
			temp = file, "line:"+str(lineno), "in", str(function), str(text)
			errinfo += " ".join(tuple(temp))
		errinfo += " ** %s: %s" % info[:2]
		return errinfo


# if __name__ == '__main__':
# 	import sys
# 	try:
# 	    print aaa
# 	except:
# 	    info = sys.exc_info()
# 	    level = 2
#     	lylog = lyLog('test_log',info,level)
#     	lylog.buildLog()


