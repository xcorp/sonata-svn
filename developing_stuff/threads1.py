'''
In this module, thread safety is implemented with a global queue where values
are passed.
This is good for small applications, or when it's easy to dispatch messages
read from the queue to the right handling function.

PRO:
    - threads only care about data, not GUI
    - simple design, completely safe
CON:
    - the application must know what to do with every message on the queue
'''

import threading
import time
import random
import Queue

import gtk
import gobject


class ValueRetThread(threading.Thread):
    '''
    This thread will periodically return values.
    It won't even try to touch gtk.
    '''
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            sleeping = random.randint(2, 9)
            print 'S', sleeping
            time.sleep(sleeping)
            print 'P'
            self.queue.put('After %d sec, %d say: %d' %\
                    (sleeping, self.ident, random.randint(10, 30)))


class MyWindow(gtk.Window):
    def __init__(self):
        '''build the gui'''
        gtk.Window.__init__(self)
        self.label = gtk.Label('Empty')
        self.add(self.label)
        self.queue = Queue.Queue()
        # threads can be started wherever you like
        # setDaemon allow you to close the app even if it is working
        t = ValueRetThread(self.queue)
        t.setDaemon(True)
        t.start()
        t = ValueRetThread(self.queue)
        t.setDaemon(True)
        t.start()
        gobject.idle_add(self._queue_handle)

    def _queue_handle(self):
        '''
        Read from the queue, and do what appropriate
        '''
        while not self.queue.empty():
            #"what's appropriate" has to be defined with some logic:
            #passing an id, or something like that. It is difficutlt to know
            #if app has to handle lot of threads, and even more difficult if
            #plugins are used
            obj = self.queue.get()
            print 'GOT', obj
            self.label.set_text(obj)
        #NOTE: if the method return False, it will be deleted from the loop
        return True


if __name__ == '__main__':
    w = MyWindow()
    w.show_all()
    gobject.threads_init()
    gtk.main()