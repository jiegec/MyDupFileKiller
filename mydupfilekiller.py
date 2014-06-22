__author__ = "Wiadufa Chen <wiadufachen@gmail.com>"
__all__ = ["find", "find_and_delete", "gui", "main"]
from hashlib import md5
import collections
from tkinter.messagebox import *
import getopt
import os
import sys
import time
import threading


def find(paths, output=False, skip_empty_files=True, follow_links=False):
    """
    A simple method to find all duplicate files.
    :param paths:  A list of paths.
    :type paths: list
    :param output: If True, it outputs the result to the console.
    :type output: bool
    :param skip_empty_files: It True, it skips empty files.
    :type skip_empty_files: bool
    :param follow_links: See https://docs.python.org/3/library/os.html#os.walk.
    :type follow_links: bool
    :return: A tuple of (file_num,dict). The dict is like {hash : (paths)}
    :rtype: dict
    """
    hashes = collections.defaultdict(set)
    num = 0
    for path in paths:
        path = os.path.abspath(path)
        for root, dirs, files in os.walk(path, followlinks=follow_links):
            for name in files:
                filename = os.path.join(root, name)
                m = md5()
                f = open(filename, 'rb')
                buffer = 8192
                while 1:
                    chunk = f.read(buffer)
                    if not chunk:
                        break
                    m.update(chunk)
                f.close()
                digest = m.hexdigest()
                hashes[digest].add(filename)
                num += 1
                if output:
                    print("Processed %d files." % num)
    if skip_empty_files:
        m = md5()
        zero = m.hexdigest()
        if zero in hashes:
            del hashes[zero]
    if output:
        print("Done.")
        for key in hashes:
            set_ = hashes[key]
            if len(set_) > 1:
                print("File hash: %s" % key)
                for file in set_:
                    print(file)
                print('')
    return num, hashes


def default_choose_callback(files):
    """
    Default choose callback. Ask the user to determine.
    :param files: A list of duplicate file paths.
    :type files: list
    :return: A set of subscripts to remove.
    :rtype: set
    """
    print('Choose files to delete [0-%d]:' % (len(files) - 1))
    num = 0
    for file in files:
        print('%d: %s' % (num, file))
        num += 1
    s = input("Input number to delete, separated by whitespace:")
    ret = set()
    numbers = s.split(" ")
    for num in numbers:
        if not (0 <= num <= len(files) - 1):
            continue
        ret.add(int(num))
    return ret


def find_and_delete(paths,
                    choose_callback=default_choose_callback,
                    output=False,
                    skip_empty_files=True,
                    follow_links=False):
    """
    Find the duplicate files and call choose_callback to delete files.
    :param paths: The paths to find.
    :type paths: list
    :param choose_callback: A callback like default_choose_callback, return files to delete.
    :type choose_callback: function
    :param output: If True, it outputs the result to the console.
    :type output: bool
    :param skip_empty_files: It True, it skips empty files.
    :type skip_empty_files: bool
    :param follow_links: See https://docs.python.org/3/library/os.html#os.walk.
    :type follow_links: bool
    :return: A tuple (files_deleted, bytes_freed).
    :rtype: tuple
    """
    files_deleted = list()
    bytes_freed = 0
    try:
        num, hashes = find(paths,
                           output,
                           skip_empty_files,
                           follow_links)
        files_deleted = list()
        bytes_freed = 0
        for key in hashes:
            set_ = hashes[key]
            if len(set_) > 1:
                files_to_remove = choose_callback(set_)
                for subscript in files_to_remove:
                    if not (0 <= subscript <= len(set_) - 1):
                        pass
                    files_deleted.append(set_[subscript])
                    bytes_freed += os.path.getsize(set_[subscript])
                    os.remove(set_[subscript])
        if output:
            print("Deleted %d files and freed %d bytes. Enjoy your free space!"
                  % (len(files_deleted), bytes_freed))
    except:
        pass
    return files_deleted, bytes_freed

gui = None
try:
    import wx
    from wx import xrc

    class SkipException(BaseException):
        pass

    def call_and_wait(target, *args, **kwargs):
        if wx.IsMainThread():
            return target(*args, **kwargs)
        else:
            context = dict()
            context['event'] = threading.Event()
            wx.CallAfter(call_in_main_thread, context, target, *args, **kwargs)
            context['event'].wait()
            if 'exception' in context:
                raise SkipException()
            return context['result']

    def call_in_main_thread(context, target, *args, **kwargs):
        try:
            context['result'] = target(*args, **kwargs)
        except:
            context['exception'] = True
        context['event'].set()

    def main_thread(func, *args, **kwargs):
        '''''ensure func invoked in main thread'''
        def _func(*args, **kwargs):
            return call_and_wait(func, *args, **kwargs)
        return _func

    class App(wx.App):

        def OnInit(self):
            self.res = xrc.XmlResource('wx_gui.xrc')
            self.init_frame()
            return True

        def init_frame(self):
            self.frame = self.res.LoadFrame(None, 'MainFrame')
            self.frame.SetSize((800, 600))
            self.path = xrc.XRCCTRL(self.frame, 'path')
            self.add = xrc.XRCCTRL(self.frame, 'add')
            self.delete = xrc.XRCCTRL(self.frame, 'delete')
            self.list = xrc.XRCCTRL(self.frame, 'paths')
            self.skip_empty_files = xrc.XRCCTRL(self.frame, 'skip_empty_files')
            self.follow_links = xrc.XRCCTRL(self.frame, 'follow_links')
            self.start = xrc.XRCCTRL(self.frame, 'start')
            self.status_bar = xrc.XRCCTRL(self.frame, 'status_bar')

            self.status_bar.SetFieldsCount(1)
            self.status_bar.SetStatusWidths([-1])
            self.status_bar.SetStatusText("Ready.")

            self.add.Bind(wx.EVT_BUTTON, self.OnAdd)
            self.start.Bind(wx.EVT_BUTTON, self.OnStart)
            self.delete.Bind(wx.EVT_BUTTON, self.OnDelete)

            self.skip_empty_files.SetValue(True)

            self.frame.Show()
            self.paths = []

            self.frame.Bind(wx.EVT_CLOSE, self.OnClose)

        def OnClose(self, event):
            self.Destroy()
            sys.exit()

        def OnDelete(self, event):
            selections = list(self.list.GetSelections())
            selections.reverse()
            for index in selections:
                self.list.Delete(index)
                self.paths.pop(index)

        def OnAdd(self, event):
            path = self.path.GetPath()
            path = os.path.abspath(path)
            if (not os.path.exists(path)) or (not os.path.isdir(path)):
                wx.MessageBox("Wrong path!",
                              "My Duplicate File Killer", wx.OK | wx.ICON_ERROR)
                return
            if path in self.paths:
                wx.MessageBox("Path already exists!",
                              "My Duplicate File Killer", wx.OK | wx.ICON_ERROR)
                return
            self.paths.append(path)
            self.list.Append(path)

        def OnStart(self, event):
            self.start.Disable()
            threading.Thread(target=self.timing_function).start()
            threading.Thread(target=self.working_function).start()

        def timing_function(self):
            times = 0
            while not self.start.IsEnabled():
                self.status_bar.SetStatusText("Finding" + '.' * times)
                times += 1
                times %= 10
                time.sleep(1)
            self.status_bar.SetStatusText("Ready.")

        def working_function(self):
            find_and_delete(self.paths, self.choose_callback,
                            False, self.skip_empty_files.GetValue(), self.follow_links.GetValue())
            self.start.Enable()

        @main_thread
        def choose_callback(self, files):
            print(files)
            self.dialog = self.res.LoadDialog(None, 'ChooseDialog')
            self.dialog_list = xrc.XRCCTRL(self.dialog, 'list')
            self.dialog_delete = xrc.XRCCTRL(self.dialog, 'delete')
            self.dialog_skip = xrc.XRCCTRL(self.dialog, 'skip')
            self.dialog_skip_all = xrc.XRCCTRL(self.dialog, 'skip_all')
            self.dialog_list.Clear()
            for path in files:
                self.dialog_list.Append(path)
            self.dialog.Bind(wx.EVT_CLOSE, self.OnDialogSkip)
            self.dialog_skip.Bind(wx.EVT_BUTTON, self.OnDialogSkip)
            self.dialog_delete.Bind(wx.EVT_BUTTON, self.OnDialogDelete)
            self.dialog_skip_all.Bind(wx.EVT_BUTTON, self.OnDialogSkipAll)
            self.result = set()
            self.raise_exception = False
            self.dialog.ShowModal()
            if self.raise_exception:
                raise SkipException()
            return self.result

        def OnDialogSkip(self, event):
            self.dialog.Destroy()

        def OnDialogDelete(self, event):
            self.result = set(self.list.GetSelections())
            self.dialog.Destroy()

        def OnDialogSkipAll(self, event):
            self.raise_exception = True
            self.dialog.Destroy()

    def wx_gui():
        app = App()
        app.MainLoop()

    gui = wx_gui
except ImportError:
    wx = None

    def require_wx():
        showerror("My Duplicate File Killer",
                  "No wxPython-Phoenix installed. Please type pip install --pre -f \
                http://wxpython.org/Phoenix/snapshot-builds wxpython-phoenix --upgrade.")
    gui = require_wx


def usage():
    print("usage: %s [-h|-l] [--help] ..." % sys.argv[0])
    print("Options and arguments:")
    print("-l     : only list duplicate files.")
    print("arg ...: paths to find duplicate files.")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "lh", ["help"])
        delete = True
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt == "-l":
                delete = False
            else:
                assert False, "Unrecognized option"
        if len(args) == 0:
            print("Please specify at least one path.")
            sys.exit()
        if delete:
            find_and_delete(args, output=True)
        else:
            find(args, output=True)

    except getopt.GetoptError:
        usage()


if __name__ == "__main__":
    gui()
