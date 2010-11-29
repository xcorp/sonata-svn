'''
This module uses one queue (and handler) per gui part.

PRO:
    - Thread only manages data
    - simple and completely safe
    - Each component add his own handler, so no complicate logic is required
CON:
    ??
'''

import threading
import time
import random
import Queue

import gtk
import gobject


def async_call(function, callback=None):
    queue = Queue.Queue()

    def wrapper(*args, **kwargs):
        try:
            res = function(*args, **kwargs)
        except Exception as exc:
            queue.put((exc,))
        else:
            queue.put((None, res))

    def cb_wrapper():
        if not queue.empty():
            res = queue.get()
            callback(res)
            return False
        else:
            return True

    print 'creating job'
    t = threading.Thread(target=wrapper)
    print t
    t.setDaemon(True)
    t.start()
    gobject.idle_add(cb_wrapper)


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
        #label1 receives info from queue1, which is populated by queue1
        #label2 is analogue, but queue2 is populated by two threads!
        #label3 is populated by a one-time long-running thread
        gtk.Window.__init__(self)
        box = gtk.VBox()

        self.label1 = gtk.Label('Empty')
        self.label2 = gtk.Label('Empty')
        self.label3 = gtk.Label('Empty')
        box.pack_start(self.label1)
        box.pack_start(self.label2)
        box.pack_start(self.label3)
        self.add(box)
        self.queue1 = Queue.Queue()
        self.queue2 = Queue.Queue()
        # threads can be started wherever you like
        # setDaemon allow you to close the app even if it is working
        t1 = ValueRetThread(self.queue1)
        t1.setDaemon(True)
        t1.start()

        t2 = ValueRetThread(self.queue2)
        t2.setDaemon(True)
        t2.start()
        t2_2 = ValueRetThread(self.queue2)
        t2_2.setDaemon(True)
        t2_2.start()

        # run _long_running_job in a thread, then
        # call populate_label3 IN THIS THREAD, so it can do gui actions
        async_call(self._long_running_job, self._populate_label3)

        gobject.idle_add(self._queue_handle1)
        gobject.idle_add(self._queue_handle2)

    # could have been a normal method. I've made it static just to underline
    # that it has no access to gui components
    @staticmethod
    def _long_running_job():
        time.sleep(6)
        print 'fatto eh'
        return 'asdfooblah'

    def _populate_label3(self, res):
        '''will be called when _long_running_job terminated'''
        exc, text = res
        if not exc:
            self.label3.set_text(text)
        else:
            self.label3.set_text("error")

    def _queue_handle1(self):
        '''
        Read from the queue, and do what appropriate
        '''
        while not self.queue1.empty():
            #"what's appropriate" has to be defined with some logic:
            #passing an id, or something like that. It is difficutlt to know
            #if app has to handle lot of threads, and even more difficult if
            #plugins are used
            obj = self.queue1.get()
            print 'GOT', obj
            self.label1.set_text(obj)
        #NOTE: if the method return False, it will be deleted from the loop
        return True

    def _queue_handle2(self):
        '''
        Read from the queue, and do what appropriate
        '''
        while not self.queue2.empty():
            #"what's appropriate" has to be defined with some logic:
            #passing an id, or something like that. It is difficutlt to know
            #if app has to handle lot of threads, and even more difficult if
            #plugins are used
            obj = self.queue2.get()
            print 'GOT', obj
            self.label2.set_text(obj)
        #NOTE: if the method return False, it will be deleted from the loop
        return True


if __name__ == '__main__':
    w = MyWindow()
    w.show_all()
    gobject.threads_init()
    gtk.main()
