from AppKit import *
import commands
from Foundation import *
import Growl
import objc
from PyObjCTools import AppHelper

status_images = {'empty':'trash-empty.png', 'full':'trash-full.png'}

class Trashie(NSObject):
    images = {}
    statusbar = None
    count = None
    poll_seconds = 3
    notifier = None

    def notify(self, type, message):
        self.notifier.notify(type,'trashie',message)

    def update_trashie(self):
        current_count = self.count
        command = 'find ~/.Trash/ -not \( -name "*.DS_Store" \) | wc -l'
        count = commands.getstatusoutput(command)
        
        if count[0] == 0: 
            self.count = int(count[1].strip()) - 1

        if current_count != self.count:
            if self.count == 0:
                self.notify('empty', 'yay! the trash is empty!')
                self.statusitem.setImage_(self.images['empty'])
            if self.count == 1:
                self.notify('full', 'there is 1 thing in the trash')
                self.statusitem.setImage_(self.images['full'])
            if self.count > 1:
                self.notify('full', 'there are %s things in the trash' % str(self.count))
                self.statusitem.setImage_(self.images['full'])

        self.statusitem.setToolTip_('Trashie')
        self.statusitem.setTitle_('(%d)' % (self.count))

    def applicationDidFinishLaunching_(self, notification):
        notifier = Growl.GrowlNotifier()
        notifier.applicationName = 'trashie'
        notifier.applicationIcon = 'trashie.icns'
        notifier.notifications = ['initialized','empty','full']
        notifier.register()
        self.notifier = notifier

        statusbar = NSStatusBar.systemStatusBar()
        self.statusitem = statusbar.statusItemWithLength_(NSVariableStatusItemLength)

        for i in status_images.keys():
            self.images[i] = NSImage.alloc().initByReferencingFile_(status_images[i])
            self.statusitem.setHighlightMode_(1)

        menu = NSMenu.alloc().init()
        menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('View Trash', 'view:', ''))
        menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Empty Trash', 'empty:', ''))
        menu.addItem_(NSMenuItem.separatorItem())
        menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Count Trash Items', 'refresh:', ''))
        menu.addItem_(NSMenuItem.separatorItem())
        menu.addItem_(NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit Trashie', 'terminate:', ''))

        self.statusitem.setMenu_(menu)

        self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(NSDate.date(), self.poll_seconds, self, 'poll:', None, True)
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer.fire()

    def view_(self, notification):
        commands.getstatusoutput('open ~/.Trash/')

    def refresh_(self, notification):
        self.update_trashie()

    def empty_(self, notification):
        commands.getstatusoutput('rm -rf ~/.Trash/*')
        self.update_trashie()

    def poll_(self, notification):
        self.update_trashie()

if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = Trashie.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()